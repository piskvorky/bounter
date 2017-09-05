//-----------------------------------------------------------------------------
// Author: Filip Stefanak <f.stefanak@rare-technologies.com>
// Copyright (C) 2017 Rare Technologies
//
// This code is distributed under the terms and conditions
// from the MIT License (MIT).

#include <stdint.h>
#include <Python.h>
#include "structmember.h"
#include "murmur3.h"
#include <math.h>
#include <stdint.h>
#include <stdio.h>

typedef uint32_t cell_t;

typedef struct {
    PyObject_HEAD
    short int depth;
    uint32_t width;
    uint32_t hash_mask;
    cell_t ** table;
} CMS_Conservative;

static void
CMS_Conservative_dealloc(CMS_Conservative* self)
{
    for (int i = 0; i < self->depth; i++)
    {
        free(self->table[i]);
    }
    free(self->table);
    #if PY_MAJOR_VERSION >= 3
    Py_TYPE(self)->tp_free((PyObject*) self);
    #else
    self->ob_type->tp_free((PyObject*) self);
    #endif
}

static PyObject *
CMS_Conservative_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    CMS_Conservative *self;
    self = (CMS_Conservative *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static int
CMS_Conservative_init(CMS_Conservative *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"width", "depth", NULL};

    uint32_t w;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "i|i", kwlist,
				      &w, &self->depth)) {
        return -1;
    }

    if (self->depth  < 1 || self->depth > 32) {
        char * msg = "Depth must be in the range 1-16";
        PyErr_SetString(PyExc_ValueError, msg);
    }

    short int hash_length = -1;
    while (0 != w)
        hash_length++, w >>= 1;
    if (hash_length < 0)
        hash_length = 0;
    self->width = 1 << hash_length;
    self->hash_mask = self->width - 1;

    uint32_t a = 0;

    self->table = (cell_t **) malloc(self->depth * sizeof(cell_t *));
    for (int i = 0; i < self->depth; i++)
    {
        self->table[i] = (cell_t *) calloc(self->width, sizeof(cell_t));
    }
    return 0;
}

static PyMemberDef CMS_Conservative_members[] = {
    {NULL} /* Sentinel */
};

/* Adds an element to the cardinality estimator. */
static PyObject *
CMS_Conservative_increment(CMS_Conservative *self, PyObject *args)
{
    const char *data;
    const uint32_t dataLength;
    uint32_t buckets[32];
    cell_t values[32];
    uint32_t hash;
    cell_t min_value = -1;

    if (!PyArg_ParseTuple(args, "s#", &data, &dataLength))
        return NULL;

    for (int i = 0; i < self->depth; i++)
    {
        MurmurHash3_x86_32((void *) data, dataLength, i, (void *) &hash);
        uint32_t bucket = hash & self->hash_mask;
        buckets[i] = bucket;
        cell_t value = self->table[i][bucket];
        if (value < min_value)
            min_value = value;
        values[i] = self->table[i][bucket];
    }

    for (int i = 0; i < self->depth; i++)
        if (values[i] == min_value)
            self->table[i][buckets[i]] = min_value + 1;

    Py_INCREF(Py_None);
    return Py_None;
};

/* Retrieves a value. */
static PyObject *
CMS_Conservative_getitem(CMS_Conservative *self, PyObject *args)
{
    const char *data;
    const uint32_t dataLength;

    if (!PyArg_ParseTuple(args, "s#", &data, &dataLength))
        return NULL;

    uint32_t hash;
    cell_t min_value = -1;
    for (int i = 0; i < self->depth; i++)
    {
        MurmurHash3_x86_32((void *) data, dataLength, i, (void *) &hash);
        uint32_t bucket = hash & self->hash_mask;
        cell_t value = self->table[i][bucket];
        if (value < min_value)
            min_value = value;
    }

    return Py_BuildValue("i", min_value);
}

static PyMethodDef CMS_Conservative_methods[] = {
    {"get", (PyCFunction)CMS_Conservative_getitem, METH_VARARGS,
    "Retrieve value."
    },
    {"increment", (PyCFunction)CMS_Conservative_increment, METH_VARARGS,
     "Increase counter by one."
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject CMS_ConservativeType = {
    #if PY_MAJOR_VERSION >= 3
    PyVarObject_HEAD_INIT(NULL, 0)
    #else
    PyObject_HEAD_INIT(NULL)
    0,                               /* ob_size */
    #endif
    "CMSC.CMS_Conservative",      /* tp_name */
    sizeof(CMS_Conservative),        /* tp_basicsize */
    0,                               /* tp_itemsize */
    (destructor)CMS_Conservative_dealloc, /* tp_dealloc */
    0,                               /* tp_print */
    0,                               /* tp_getattr */
    0,                               /* tp_setattr */
    0,                               /* tp_compare */
    0,                               /* tp_repr */
    0,                               /* tp_as_number */
    0,                               /* tp_as_sequence */
    0,                               /* tp_as_mapping */
    0,                               /* tp_hash */
    0,                               /* tp_call */
    0,                               /* tp_str */
    0,                               /* tp_getattro */
    0,                               /* tp_setattro */
    0,                               /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,         /* tp_flags */
    "CMS Conservative object",            /* tp_doc */
    0,		                     /* tp_traverse */
    0,		                     /* tp_clear */
    0,		                     /* tp_richcompare */
    0,		                     /* tp_weaklistoffset */
    0,		                     /* tp_iter */
    0,		                     /* tp_iternext */
    CMS_Conservative_methods,             /* tp_methods */
    CMS_Conservative_members,             /* tp_members */
    0,                               /* tp_getset */
    0,                               /* tp_base */
    0,                               /* tp_dict */
    0,                               /* tp_descr_get */
    0,                               /* tp_descr_set */
    0,                               /* tp_dictoffset */
    (initproc)CMS_Conservative_init,      /* tp_init */
    0,                               /* tp_alloc */
    CMS_Conservative_new,                 /* tp_new */
};

#if PY_MAJOR_VERSION >= 3
static PyModuleDef CMS_Conservativemodule = {
    PyModuleDef_HEAD_INIT,
    "CMS_Conservative",
    "A space efficient frequency counter.",
    -1,
    NULL, NULL, NULL, NULL, NULL
};

#else
static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};
#endif

#if PY_MAJOR_VERSION >=3
PyMODINIT_FUNC
PyInit_CMSC(void)
#else
    #ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
        #define PyMODINIT_FUNC void
    #endif
PyMODINIT_FUNC initCMSC(void)
#endif
{
    PyObject* m;
    if (PyType_Ready(&CMS_ConservativeType) < 0) {

    #if PY_MAJOR_VERSION >= 3
        return NULL;
    }

    m = PyModule_Create(&CMS_Conservativemodule);
    #else
        return;
    }

    char *description = "CMS frequency estimator.";
    m = Py_InitModule3("CMSC", module_methods, description);
    #endif

    if (m == NULL)
        #if PY_MAJOR_VERSION >= 3
        return NULL;
        #else
        return;
        #endif

    Py_INCREF(&CMS_ConservativeType);
    PyModule_AddObject(m, "CMS_Conservative", (PyObject *)&CMS_ConservativeType);

    #if PY_MAJOR_VERSION >= 3
    return m;
    #endif
}