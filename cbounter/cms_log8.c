//-----------------------------------------------------------------------------
// Author: Filip Stefanak <f.stefanak@rare-technologies.com>
// Copyright (C) 2017 Rare Technologies
//
// This code is distributed under the terms and conditions
// from the MIT License (MIT).

#define CMS_TYPE CMS_Log8
#define CMS_TYPE_STRING "CMS_Log8"
#define CMS_CELL_TYPE uint8_t

#include "cms_common.c"

static inline int CMS_VARIANT(should_inc)(CMS_CELL_TYPE value)
{
    if (value >= 16)
    {
        uint8_t shift = 33 - (value >> 3);
        uint32_t mask = 0xFFFFFFFF >> shift;
        uint32_t r = rand();
        if (mask & 0x00008000)
            r += rand() << 15;
        if (mask & r) return 0;
    }
    return 1;
}

static inline long long CMS_VARIANT(decode)(CMS_CELL_TYPE value)
{
    if (value <= 16)
        return value;
    else
        return (8 + (value & 7)) << ((value >> 3) - 1);
}