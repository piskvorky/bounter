//-----------------------------------------------------------------------------
// Author: Filip Stefanak <f.stefanak@rare-technologies.com>
// Copyright (C) 2017 Rare Technologies
//
// This code is distributed under the terms and conditions
// from the MIT License (MIT).

#define GLUE(x,y) x##y
#define GLUE_I(x,y) GLUE(x, y)
#define HT_VARIANT(suffix) GLUE_I(HT_TYPE, suffix)

#include <Python.h>
#include "structmember.h"
#include "murmur3.h"
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>

typedef struct {
    char* key;
    uint32_t count;
} HT_VARIANT(_cell_t);

typedef struct {
    PyObject_HEAD
    uint32_t buckets;
    uint32_t hash_mask;
    uint64_t str_allocated;
    long long total;
    uint32_t size;
    HT_VARIANT(_cell_t) * table;
} HT_TYPE;

#define ITER_RESULT_KEYS 1
#define ITER_RESULT_VALUES 2
#define ITER_RESULT_KV_PAIRS 3

typedef struct {
  PyObject_HEAD
  HT_TYPE * hashtable;
  uint32_t i;
  char result_type;
} HT_VARIANT(_ITER_TYPE);

/* Destructor invoked by python. */
static void
HT_VARIANT(_dealloc)(HT_TYPE* self)
{
    HT_VARIANT(_cell_t) * table = self->table;
    // free the strings
    uint32_t i;
    for (i = 0; i < self->buckets; i++)
    {
        if (table[i].key)
        {
            free(table[i].key);
        }
    }

    // free the hashtable
    free(table);

    // finally, destroy itself
    #if PY_MAJOR_VERSION >= 3
    Py_TYPE(self)->tp_free((PyObject*) self);
    #else
    self->ob_type->tp_free((PyObject*) self);
    #endif
}

static PyObject *
HT_VARIANT(_new)(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    HT_TYPE *self;
    self = (HT_TYPE *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static int
HT_VARIANT(_init)(HT_TYPE *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"buckets", NULL};
    uint32_t w;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "i", kwlist,
				      &w)) {
        return -1;
    }

    short int hash_length = -1;
    while (0 != w)
        hash_length++, w >>= 1;
    if (hash_length < 0)
        hash_length = 0;
    self->buckets = 1 << hash_length;
    self->hash_mask = self->buckets - 1;

    self->table = (HT_VARIANT(_cell_t) *) calloc(self->buckets, sizeof(HT_VARIANT(_cell_t)));
    self->total = 0;
    self->size = 0;

    return 0;
}

static PyMemberDef HT_VARIANT(_members[]) = {
    {NULL} /* Sentinel */
};

static inline HT_VARIANT(_cell_t) * HT_VARIANT(_find_cell)(HT_TYPE * self, char * data, uint32_t dataLength)
{
    uint32_t bucket;
    MurmurHash3_x86_32((void *) data, dataLength, 42, (void *) &bucket);
    bucket &= self->hash_mask;
    const HT_VARIANT(_cell_t) * table = self->table;

    while (table[bucket].key && strcmp(table[bucket].key, data))
    {
        bucket = (bucket + 1) & self->hash_mask;
    }
    return &table[bucket];
}

static inline HT_VARIANT(_cell_t) * HT_VARIANT(_allocate_cell)(HT_TYPE * self, char * data, uint32_t dataLength)
{
    HT_VARIANT(_cell_t) * cell = HT_VARIANT(_find_cell)(self, data, dataLength);

    if (!cell->key)
    {
        if (self->size == self->hash_mask)
        {
            char * msg = "Table is full!";
            PyErr_SetString(PyExc_ValueError, msg);
            return NULL;
        }

        self->size += 1;
        self->str_allocated += dataLength + 1;
        char * key = malloc(dataLength + 1);
        memcpy(key, data, dataLength + 1);
        cell->key = key;
    }
    return cell;
}

static inline int HT_VARIANT(_checkString)(char * value, uint32_t length)
{
    if (strlen(value) < length)
    {
        char * msg = "String contains null bytes!";
        PyErr_SetString(PyExc_ValueError, msg);
        return 0;
    }
    return 1;
}

/* Adds a string to the counter. */
static PyObject *
HT_VARIANT(_increment)(HT_TYPE *self, PyObject *args)
{
    const char *data;
    const uint32_t dataLength;

    long long increment = 1;

    if (!PyArg_ParseTuple(args, "s#|L", &data, &dataLength, &increment))
        return NULL;
    if (!HT_VARIANT(_checkString)(data, dataLength))
        return NULL;

    if (increment <= 0)
    {
        char * msg = "Increment must be positive!";
        PyErr_SetString(PyExc_ValueError, msg);
        return NULL;
    }

    self->total += increment;

    HT_VARIANT(_cell_t) * cell = HT_VARIANT(_allocate_cell)(self, data, dataLength);

    if (cell)
    {
        cell->count += increment;
        Py_INCREF(Py_None);
        return Py_None;
    }

    return NULL;
}

/* Sets count for a single string. */
static int
HT_VARIANT(_setitem)(HT_TYPE *self, PyObject *pKey, PyObject *pValue)
{
    const char *data;
    const uint32_t dataLength;
    long long value;

    if (!PyArg_Parse(pKey, "s#", &data, &dataLength))
        return -1;
    if (!HT_VARIANT(_checkString)(data, dataLength))
        return -1;

    if (pValue) // set value
    {
        if (!PyArg_Parse(pValue, "L", &value))
            return -1;

        HT_VARIANT(_cell_t) * cell = HT_VARIANT(_allocate_cell)(self, data, dataLength);

        if (cell)
        {
            self->total += value - cell->count;
            cell->count = value;
            return 0;
        }
    }
    else // delete value
    {
        HT_VARIANT(_cell_t) * cell = HT_VARIANT(_find_cell)(self, data, dataLength);
        if (cell)
        {
            self->str_allocated -= strlen(cell->key) + 1;
            free(cell->key);
            cell->key = 0;
            self->total -= cell->count;
            cell->count = 0;
            self->size--;
        }
        return 0;
    }

    return -1;
}

/* Retrieves count for a single string. */
static PyObject *
HT_VARIANT(_getitem)(HT_TYPE *self, PyObject *key)
{
    const char *data;
    const uint32_t dataLength;

    if (!PyArg_Parse(key, "s#", &data, &dataLength))
        return NULL;
    if (!HT_VARIANT(_checkString)(data, dataLength))
        return NULL;

    HT_VARIANT(_cell_t) * cell = HT_VARIANT(_find_cell)(self, data, dataLength);
    uint32_t value = cell ? cell->count : 0;

    return Py_BuildValue("i", value);
}

static PyObject *
HT_VARIANT(_total)(HT_TYPE *self)
{
    return Py_BuildValue("L", self->total);
}

static Py_ssize_t
HT_VARIANT(_size)(HT_TYPE *self)
{
    return self->size;
}

/* Serialization function for pickling. */
static PyObject *
HT_VARIANT(_reduce)(HT_TYPE *self)
{
    PyObject *args = Py_BuildValue("(i)", self->buckets);
    HT_VARIANT(_cell_t) * table = self->table;

    PyObject * hashtable_row = PyByteArray_FromStringAndSize(table, self->buckets * sizeof(HT_VARIANT(_cell_t)));

    PyByteArrayObject * strings_row = (PyByteArrayObject *) PyByteArray_FromStringAndSize(NULL, self->str_allocated);

    char * result_index = strings_row->ob_bytes;
    uint32_t i;
    for (i = 0; i < self->buckets; i++)
    {
        char* key = table[i].key;
        if (key)
        {
            int length = strlen(key) + 1;
            memcpy(result_index, key, length);
            result_index += length;
        }
    }

    PyObject *state = Py_BuildValue("(LLIOO)", self->total, self->str_allocated, self->size, hashtable_row, strings_row);
    return Py_BuildValue("(OOO)", Py_TYPE(self), args, state);
}

/* De-serialization function for pickling. */
static PyObject *
HT_VARIANT(_set_state)(HT_TYPE * self, PyObject * args)
{
    PyObject * hashtable_row_o;
    PyObject * strings_row_o;

    if (!PyArg_ParseTuple(args, "(LLIOO)", &self->total, &self->str_allocated, &self->size, &hashtable_row_o, &strings_row_o))
        return NULL;

    char * hashtable_row = PyByteArray_AsString(hashtable_row_o);
    if (!hashtable_row)
        return NULL;

    HT_VARIANT(_cell_t) * table = self->table;

    memcpy(table, hashtable_row, self->buckets * sizeof(HT_VARIANT(_cell_t)));

    char * string_row = PyByteArray_AsString(strings_row_o);
    uint64_t total_length = PyByteArray_Size(strings_row_o);
    char * current_word = string_row;
    uint32_t i;
    for (i = 0; i < self->buckets; i++)
    {
        if (table[i].key) // the imported key is garbage, we replace it with a real pointer
        {
            if (current_word >= string_row + total_length)
            {
                return NULL; // overflow!
            }

            int current_length = strlen(current_word) + 1;
            char * current_target = malloc(current_length);
            table[i].key = current_target;
            memcpy(current_target, current_word, current_length);
            current_word += current_length;
        }
    }

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject* HT_VARIANT(_ITER_iter)(PyObject *self)
{
  Py_INCREF(self);
  return self;
}

#define ITER_RESULT_KEYS 1
#define ITER_RESULT_VALUES 2
#define ITER_RESULT_KV_PAIRS 3


PyObject* HT_VARIANT(_ITER_iternext)(HT_VARIANT(_ITER_TYPE) *self)
{
    HT_VARIANT(_cell_t) * table = self->hashtable->table;
    uint32_t buckets = self->hashtable->buckets;
    uint32_t i = self->i;
    while (i < buckets && table[i].key == 0)
        i++;

    if (i < buckets)
    {
        PyObject * result;
        if (self->result_type == ITER_RESULT_KEYS)
            result = Py_BuildValue("s", table[i].key);
        else if (self->result_type == ITER_RESULT_KV_PAIRS)
            result = Py_BuildValue("(sl)", table[i].key, table[i].count);
        else
        {
            char * msg = "Invalid iteration type!";
            PyErr_SetString(PyExc_SystemError, msg);
            return NULL;
        }
        self->i = i + 1;
        return result;
    }

    /* Raising of standard StopIteration exception with empty value. */
    self->i = buckets;
    PyErr_SetNone(PyExc_StopIteration);
    return NULL;
}

/* Destructor invoked by python. */
static void
HT_VARIANT(_ITER_dealloc)(HT_VARIANT(_ITER_TYPE) * self)
{
    Py_DECREF(self->hashtable);

    // finally, destroy itself
    #if PY_MAJOR_VERSION >= 3
    Py_TYPE(self)->tp_free((PyObject*) self);
    #else
    self->ob_type->tp_free((PyObject*) self);
    #endif
}

static PyTypeObject HT_VARIANT(_ITER_TYPE_Type) = {
    #if PY_MAJOR_VERSION >= 3
    PyVarObject_HEAD_INIT(NULL, 0)
    #else
    PyObject_HEAD_INIT(NULL)
    0,                               /* ob_size */
    #endif
    "HTC." HT_TYPE_STRING "_iter",             /*tp_name*/
    sizeof(HT_VARIANT(_ITER_TYPE)), /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)HT_VARIANT(_ITER_dealloc), /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    #if PY_MAJOR_VERSION >= 3
    Py_TPFLAGS_DEFAULT,
    #else
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_ITER,
      /* tp_flags: Py_TPFLAGS_HAVE_ITER tells python to
         use tp_iter and tp_iternext fields. */
    #endif
    "Internal HTC iterator object.",           /* tp_doc */
    0,  /* tp_traverse */
    0,  /* tp_clear */
    0,  /* tp_richcompare */
    0,  /* tp_weaklistoffset */
    HT_VARIANT(_ITER_iter),  /* tp_iter: __iter__() method */
    HT_VARIANT(_ITER_iternext)  /* tp_iternext: next() method */
};

static inline HT_VARIANT(_ITER_TYPE) *
HT_VARIANT(_make_iterator)(HT_TYPE *self, char result_type)
{
    HT_VARIANT(_ITER_TYPE) * iterator = PyObject_New(HT_VARIANT(_ITER_TYPE), &HT_VARIANT(_ITER_TYPE_Type));
    if (!iterator)
        return NULL;

    if (!PyObject_Init((PyObject *)iterator, &HT_VARIANT(_ITER_TYPE_Type))) {
        Py_DECREF(iterator);
        return NULL;
    }

    iterator->i = 0;
    iterator->hashtable = self;
    iterator->result_type = result_type;
    Py_INCREF(self);
    return iterator;
}

static HT_VARIANT(_ITER_TYPE) *
HT_VARIANT(_HT_iter_KV)(HT_TYPE *self)
{
    return HT_VARIANT(_make_iterator)(self, ITER_RESULT_KV_PAIRS);
}

static HT_VARIANT(_ITER_TYPE) *
HT_VARIANT(_HT_iter_K)(HT_TYPE *self)
{
    return HT_VARIANT(_make_iterator)(self, ITER_RESULT_KEYS);
}


static PyMethodDef HT_VARIANT(_methods)[] = {
    {"increment", (PyCFunction)HT_VARIANT(_increment), METH_VARARGS,
     "Adds a string to the counter."
    },
    {"total", (PyCFunction)HT_VARIANT(_total), METH_NOARGS,
     "Returns sum of all counts in the counter."
    },
    {"items", (PyCFunction)HT_VARIANT(_HT_iter_KV), METH_NOARGS,
     "Iterates over all key-value pairs."
    },
    {"__reduce__", (PyCFunction)HT_VARIANT(_reduce), METH_NOARGS,
     "Serialization function for pickling."
    },
    {"__setstate__", (PyCFunction)HT_VARIANT(_set_state), METH_VARARGS,
    "De-serialization function for pickling."
    },
    {NULL}  /* Sentinel */
};

static PyMappingMethods HT_VARIANT(_map_methods) = {
    (lenfunc) HT_VARIANT(_size),
    (binaryfunc) HT_VARIANT(_getitem),
    (objobjargproc) HT_VARIANT(_setitem),
};

static PyTypeObject HT_VARIANT(Type) = {
    #if PY_MAJOR_VERSION >= 3
    PyVarObject_HEAD_INIT(NULL, 0)
    #else
    PyObject_HEAD_INIT(NULL)
    0,                               /* ob_size */
    #endif
    "HTC." HT_TYPE_STRING,      /* tp_name */
    sizeof(HT_TYPE),        /* tp_basicsize */
    0,                               /* tp_itemsize */
    (destructor)HT_VARIANT(_dealloc), /* tp_dealloc */
    0,                               /* tp_print */
    0,                               /* tp_getattr */
    0,                               /* tp_setattr */
    0,                               /* tp_compare */
    0,                               /* tp_repr */
    0,                               /* tp_as_number */
    0,                               /* tp_as_sequence */
    &HT_VARIANT(_map_methods),        /* tp_as_mapping */
    0,                               /* tp_hash */
    0,                               /* tp_call */
    0,                               /* tp_str */
    0,                               /* tp_getattro */
    0,                               /* tp_setattro */
    0,                               /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,         /* tp_flags */
    HT_TYPE_STRING " object",            /* tp_doc */
    0,		                     /* tp_traverse */
    0,		                     /* tp_clear */
    0,		                     /* tp_richcompare */
    0,		                     /* tp_weaklistoffset */
    HT_VARIANT(_HT_iter_K),       /* tp_iter */
    0,		                     /* tp_iternext */
    HT_VARIANT(_methods),             /* tp_methods */
    HT_VARIANT(_members),             /* tp_members */
    0,                               /* tp_getset */
    0,                               /* tp_base */
    0,                               /* tp_dict */
    0,                               /* tp_descr_get */
    0,                               /* tp_descr_set */
    0,                               /* tp_dictoffset */
    (initproc)HT_VARIANT(_init),      /* tp_init */
    0,                               /* tp_alloc */
    HT_VARIANT(_new),                 /* tp_new */
};
