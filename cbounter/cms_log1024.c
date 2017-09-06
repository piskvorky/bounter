//-----------------------------------------------------------------------------
// Author: Filip Stefanak <f.stefanak@rare-technologies.com>
// Copyright (C) 2017 Rare Technologies
//
// This code is distributed under the terms and conditions
// from the MIT License (MIT).

#define CMS_TYPE CMS_Log1024
#define CMS_TYPE_STRING "CMS_Log1024"
#define CMS_CELL_TYPE uint16_t

#include "cms_common.c"

static inline int CMS_VARIANT(should_inc)(CMS_CELL_TYPE value)
{
    if (value >= 2048)
    {
        uint8_t shift = 33 - (value >> 10);
        uint32_t mask = 0xFFFFFFFF >> shift;
        uint32_t r = rand();
        if (mask & 0x00010000)
            r += rand() << 15;
        if (mask & r) return 0;
    }
    return 1;
}

static inline long long CMS_VARIANT(decode)(CMS_CELL_TYPE value)
{
    if (value <= 2048)
        return value;
    else
        {
            uint64_t foo = value;
            return (1024 + (value & 1023)) << ((value >> 10) - 1);
        }
}