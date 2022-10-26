//-----------------------------------------------------------------------------
// Author: Filip Stefanak <f.stefanak@rare-technologies.com>
// Copyright (C) 2017 Rare Technologies
//
// This code is distributed under the terms and conditions
// from the MIT License (MIT).

#include <stdlib.h>
#include <stdint.h>


static inline uint32_t rand_32b()
{
    uint32_t r = rand();
    #if RAND_MAX < 0x8000
        r += rand() << 15;
    #endif
    return r;
}

#include "cms_conservative.h"
#include "cms64_conservative.h"
#include "cms_log8.c"
#include "cms_log1024.c"
#include <time.h>

#if PY_MAJOR_VERSION >= 3
static PyModuleDef CMSC_module = {
    PyModuleDef_HEAD_INIT,
    "bounter-cmsc",
    "C implementation of Count-Min Sketch.",
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
PyInit_bounter_cmsc(void)
#else
    #ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
        #define PyMODINIT_FUNC void
    #endif
PyMODINIT_FUNC initbounter_cmsc(void)
#endif
{
    PyObject* m;
    if (PyType_Ready(&CMS_ConservativeType) < 0
        || PyType_Ready(&CMS64_ConservativeType) < 0
        || PyType_Ready(&CMS_Log8Type) < 0
        || PyType_Ready(&CMS_Log1024Type) < 0) {

    #if PY_MAJOR_VERSION >= 3
        return NULL;
    }

    m = PyModule_Create(&CMSC_module);
    #else
        return;
    }

    char *description = "C implementation of CMS";
    m = Py_InitModule3("bounter_cmsc", module_methods, description);
    #endif

    if (m == NULL)
        #if PY_MAJOR_VERSION >= 3
        return NULL;
        #else
        return;
        #endif

    Py_INCREF(&CMS_ConservativeType);
    PyModule_AddObject(m, "CMS_Conservative", (PyObject *)&CMS_ConservativeType);

    Py_INCREF(&CMS64_ConservativeType);
    PyModule_AddObject(m, "CMS64_Conservative", (PyObject *)&CMS64_ConservativeType);

    srand(time(NULL));

    Py_INCREF(&CMS_Log8Type);
    PyModule_AddObject(m, "CMS_Log8", (PyObject *)&CMS_Log8Type);

    Py_INCREF(&CMS_Log1024Type);
    PyModule_AddObject(m, "CMS_Log1024", (PyObject *)&CMS_Log1024Type);


    #if PY_MAJOR_VERSION >= 3
    return m;
    #endif
}
