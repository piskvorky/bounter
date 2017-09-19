//-----------------------------------------------------------------------------
// Author: Filip Stefanak <f.stefanak@rare-technologies.com>
// Copyright (C) 2017 Rare Technologies
//
// This code is distributed under the terms and conditions
// from the MIT License (MIT).

#define GLUE(x,y) x##y
#define GLUE_I(x,y) GLUE(x, y)
#define CMS_VARIANT(suffix) GLUE_I(CMS_TYPE, suffix)

#include <Python.h>
#include "structmember.h"
#include "murmur3.h"
#include "hll.h"
#include <math.h>
#include <stdint.h>

typedef struct {
    PyObject_HEAD
    short int depth;
    uint32_t width;
    uint32_t hash_mask;
    long long total;
    CMS_CELL_TYPE ** table;
    HyperLogLog hll;
} CMS_TYPE;

/* Destructor invoked by python. */
static void
CMS_VARIANT(_dealloc)(CMS_TYPE* self)
{
    // free our own tables
    int i;
    for (i = 0; i < self->depth; i++)
    {
        free(self->table[i]);
    }
    free(self->table);
    // then deallocate hll
    HyperLogLog_dealloc(&self->hll);
    // finally, destroy itself
    #if PY_MAJOR_VERSION >= 3
    Py_TYPE(self)->tp_free((PyObject*) self);
    #else
    self->ob_type->tp_free((PyObject*) self);
    #endif
}

static PyObject *
CMS_VARIANT(_new)(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    CMS_TYPE *self;
    self = (CMS_TYPE *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static int
CMS_VARIANT(_init)(CMS_TYPE *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"width", "depth", NULL};

    uint32_t w;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "ii", kwlist,
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

    HyperLogLog_init(&self->hll, 16);

    self->table = (CMS_CELL_TYPE **) malloc(self->depth * sizeof(CMS_CELL_TYPE *));
    int i;
    for (i = 0; i < self->depth; i++)
    {
        self->table[i] = (CMS_CELL_TYPE *) calloc(self->width, sizeof(CMS_CELL_TYPE));
    }
    return 0;
}

static PyMemberDef CMS_VARIANT(_members[]) = {
    {NULL} /* Sentinel */
};

static inline int CMS_VARIANT(should_inc)(CMS_CELL_TYPE value);

/* Adds an element to the frequency estimator. */
static PyObject *
CMS_VARIANT(_increment)(CMS_TYPE *self, PyObject *args)
{
    const char *data;
    const uint32_t dataLength;
    uint32_t buckets[32];
    CMS_CELL_TYPE values[32];
    uint32_t hash;
    CMS_CELL_TYPE min_value = -1;
    long long increment = 1;

    if (!PyArg_ParseTuple(args, "s#|L", &data, &dataLength, &increment))
        return NULL;

    if (increment <= 0)
    {
        char * msg = "Increment must be positive!.";
        PyErr_SetString(PyExc_ValueError, msg);
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS

    self->total += increment;

    int i;
    for (i = 0; i < self->depth; i++)
    {
        MurmurHash3_x86_32((void *) data, dataLength, i, (void *) &hash);
        uint32_t bucket = hash & self->hash_mask;
        buckets[i] = bucket;
        CMS_CELL_TYPE value = self->table[i][bucket];
        if (value < min_value)
            min_value = value;
        values[i] = self->table[i][bucket];

        if (i == 0)
            HyperLogLog_add(&self->hll, hash);
    }

    CMS_CELL_TYPE result = min_value;
    for (; increment > 0; increment--)
        result += CMS_VARIANT(should_inc)(result);

    if (result > min_value)
    {
        int i;
        for (i = 0; i < self->depth; i++)
            if (values[i] < result)
                self->table[i][buckets[i]] = result;
    }

    Py_END_ALLOW_THREADS
    Py_INCREF(Py_None);
    return Py_None;
};

static inline long long CMS_VARIANT(decode)(CMS_CELL_TYPE value);

/* Retrieves estimate for the frequency of a single element. */
static PyObject *
CMS_VARIANT(_getitem)(CMS_TYPE *self, PyObject *args)
{
    const char *data;
    const uint32_t dataLength;

    if (!PyArg_ParseTuple(args, "s#", &data, &dataLength))
        return NULL;

    uint32_t hash;
    CMS_CELL_TYPE min_value = -1;
    int i;
    for (i = 0; i < self->depth; i++)
    {
        MurmurHash3_x86_32((void *) data, dataLength, i, (void *) &hash);
        uint32_t bucket = hash & self->hash_mask;
        CMS_CELL_TYPE value = self->table[i][bucket];
        if (value < min_value)
            min_value = value;
    }

    return Py_BuildValue("i", CMS_VARIANT(decode) (min_value));
}

/* Retrieves estimate of the set cardinality */
static PyObject *
CMS_VARIANT(_cardinality)(CMS_TYPE *self, PyObject *args)
{
   double cardinality = HyperLogLog_cardinality(&self->hll);
   return Py_BuildValue("i", (long long) cardinality);
}

/* Retrieves the total number of increments */
static PyObject *
CMS_VARIANT(_total)(CMS_TYPE *self, PyObject *args)
{
   return Py_BuildValue("i", self->total);
}

static inline CMS_CELL_TYPE CMS_VARIANT(_merge_value) (CMS_CELL_TYPE v1, CMS_CELL_TYPE v2, uint32_t merge_seed);

/**
  * Merges another CMS instance into this one.
  * This instance is incremented by values of the other instance, which remains unaffected
  */
CMS_VARIANT(_merge)(CMS_TYPE *self, PyObject *args)
{
    CMS_TYPE *other;
    if (!PyArg_ParseTuple(args, "O!", ((PyObject *) self)->ob_type, &other))
    {
        char * msg = "Object to merge must be an instance of CMS with the same algorithm.";
        PyErr_SetString(PyExc_TypeError, msg);
        return NULL;
    }
    if (other->width != self->width || other->depth != self->depth)
    {
        char * msg = "CMS to merge must use the same width and depth.";
        PyErr_SetString(PyExc_ValueError, msg);
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    uint32_t i,j;
    uint32_t merge_seed = rand_32b();
    for (i = 0; i < self->depth; i++)
    {
        for (j = 0; j < self->width; j++)
        {
            CMS_CELL_TYPE v1 = self->table[i][j];
            CMS_CELL_TYPE v2 = other->table[i][j];
            self->table[i][j] = CMS_VARIANT(_merge_value)(v1, v2, merge_seed);
        }
    }

    self->total += other->total;
    HyperLogLog_merge(&self->hll, &other->hll);

    Py_END_ALLOW_THREADS
    Py_INCREF(Py_None);
    return Py_None;
}

/* Serialization function for pickling. */
static PyObject *
CMS_VARIANT(_reduce)(CMS_TYPE *self)
{
    PyObject *args = Py_BuildValue("(ii)", self->width, self->depth);
    PyObject *state_table = PyList_New(self->depth + 2);
    int i;
    for (i = 0; i < self->depth; i++)
    {
        PyObject *row = PyByteArray_FromStringAndSize(self->table[i], self->width * sizeof(CMS_CELL_TYPE));
        if (!row)
            return NULL;
        PyList_SetItem(state_table, i, row);
    }
    PyObject *hll = PyByteArray_FromStringAndSize(self->hll.registers, self->hll.size);
    if (!hll)
        return NULL;
    PyList_SetItem(state_table, self->depth, hll);
    PyList_SetItem(state_table, self->depth + 1, Py_BuildValue("i", self->total));
    return Py_BuildValue("(OOO)", Py_TYPE(self), args, state_table);
}

/* De-serialization function for pickling. */
static PyObject *
CMS_VARIANT(_set_state)(CMS_TYPE * self, PyObject * state)
{
    PyObject *state_table;

    if (!PyArg_ParseTuple(state, "O:setstate", &state_table))
        return NULL;

    Py_ssize_t rowlen = self->width * sizeof(CMS_CELL_TYPE);
    CMS_CELL_TYPE *row_buffer;
    hll_cell_t *hll_buffer;

    int i;
    for (i = 0; i < self->depth; i++)
    {
        PyObject *row = PyList_GetItem(state_table, i);
        row_buffer = PyByteArray_AsString(row);
        if (!row_buffer)
            return NULL;
        memcpy(self->table[i], row_buffer, rowlen);
    }

    PyObject *row = PyList_GetItem(state_table, self->depth);
    hll_buffer = PyByteArray_AsString(row);
    if (!hll_buffer)
        return NULL;
    memcpy(self->hll.registers, hll_buffer, self->hll.size);

    self->total = PyLong_AsLongLong(PyList_GetItem(state_table, self->depth + 1));

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef CMS_VARIANT(_methods)[] = {
    {"increment", (PyCFunction)CMS_VARIANT(_increment), METH_VARARGS,
     "Increase counter by one."
    },
    {"get", (PyCFunction)CMS_VARIANT(_getitem), METH_VARARGS,
    "Retrieves estimate for the frequency of a single element."
    },
    {"cardinality", (PyCFunction)CMS_VARIANT(_cardinality), METH_NOARGS,
    "Retrieves estimate of the set cardinality."
    },
    {"total", (PyCFunction)CMS_VARIANT(_total), METH_NOARGS,
    "Retrieves the total number of increments."
    },
    {"merge", (PyCFunction)CMS_VARIANT(_merge), METH_VARARGS,
    "Merges another CMS instance into this one."
    },
    {"__reduce__", (PyCFunction)CMS_VARIANT(_reduce), METH_NOARGS,
     "Serialization function for pickling."
    },
    {"__setstate__", (PyCFunction)CMS_VARIANT(_set_state), METH_VARARGS,
    "De-serialization function for pickling."
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject CMS_VARIANT(Type) = {
    #if PY_MAJOR_VERSION >= 3
    PyVarObject_HEAD_INIT(NULL, 0)
    #else
    PyObject_HEAD_INIT(NULL)
    0,                               /* ob_size */
    #endif
    "cmsc." CMS_TYPE_STRING,      /* tp_name */
    sizeof(CMS_TYPE),        /* tp_basicsize */
    0,                               /* tp_itemsize */
    (destructor)CMS_VARIANT(_dealloc), /* tp_dealloc */
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
    CMS_TYPE_STRING " object",            /* tp_doc */
    0,		                     /* tp_traverse */
    0,		                     /* tp_clear */
    0,		                     /* tp_richcompare */
    0,		                     /* tp_weaklistoffset */
    0,		                     /* tp_iter */
    0,		                     /* tp_iternext */
    CMS_VARIANT(_methods),             /* tp_methods */
    CMS_VARIANT(_members),             /* tp_members */
    0,                               /* tp_getset */
    0,                               /* tp_base */
    0,                               /* tp_dict */
    0,                               /* tp_descr_get */
    0,                               /* tp_descr_set */
    0,                               /* tp_dictoffset */
    (initproc)CMS_VARIANT(_init),      /* tp_init */
    0,                               /* tp_alloc */
    CMS_VARIANT(_new),                 /* tp_new */
};