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
        if (mask & rand_32b()) return 0;
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

#include <stdio.h>

static inline CMS_CELL_TYPE CMS_VARIANT(_merge_value) (CMS_CELL_TYPE v1, CMS_CELL_TYPE v2, uint32_t merge_seed)
{
    long long decoded = CMS_VARIANT(decode)(v1);
    decoded += CMS_VARIANT(decode)(v2);

    if (decoded <= 16)
        return decoded;

    // calculate the log base, preserving 4 most significant bytes as steps between next counter value
    CMS_CELL_TYPE log_result = 1;
    long long h = decoded;
    while (h >= 16)
    {
        log_result += 1;
        h = h >> 1;
    }

    // When "decoded" is converted to logcounter value, there is an unconverted remainder.
    // Increase logcounter value by 1 with probability ( remainder / step ),
    // where step is the difference to next logcounter value.
    // In other words, 28 + 7 (35) becomes 36 with p=0.75 and 32 with p=0.25
    uint8_t shift = 33 - log_result;
    uint32_t mask = 0xFFFFFFFF >> shift;

    uint32_t r;
    MurmurHash3_x86_32  ((void *) &decoded, 8, merge_seed, (void *) &r);
    uint32_t remainder = mask & decoded;

    return (log_result << 3) + (h & 7) + ((mask & r) < remainder);
}
