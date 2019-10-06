//-----------------------------------------------------------------------------
// Author: Filip Stefanak <f.stefanak@rare-technologies.com>
// Copyright (C) 2017 Rare Technologies
//
// This code is distributed under the terms and conditions
// from the MIT License (MIT).

#include <stdlib.h>
#include <stdint.h>
#include "ht_basic.c"

#if PY_MAJOR_VERSION >= 3
static PyModuleDef htc_module = {
    PyModuleDef_HEAD_INIT,
    "bounter_htc",
    "C implementation of a hashtable for counting short strings.",
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
PyInit_bounter_htc(void)
#else
    #ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
        #define PyMODINIT_FUNC void
    #endif
PyMODINIT_FUNC initbounter_htc(void)
#endif
{
    PyObject* m;
    if (PyType_Ready(&HT_BasicType) < 0 || PyType_Ready(&HT_Basic_ITER_TYPE_Type) < 0) {

    #if PY_MAJOR_VERSION >= 3
        return NULL;
    }

    m = PyModule_Create(&htc_module);
    #else
        return;
    }

    char *description = "C implementation of a hashtable for counting short strings";
    m = Py_InitModule3("bounter_htc", module_methods, description);
    #endif

    if (m == NULL)
        #if PY_MAJOR_VERSION >= 3
        return NULL;
        #else
        return;
        #endif

    Py_INCREF(&HT_BasicType);
    PyModule_AddObject(m, "HT_Basic", (PyObject *)&HT_BasicType);

    Py_INCREF(&HT_Basic_ITER_TYPE_Type);
    PyModule_AddObject(m, "HT_Basic_iter", (PyObject *)&HT_Basic_ITER_TYPE_Type);

    #if PY_MAJOR_VERSION >= 3
    return m;
    #endif
}
