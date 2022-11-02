//-----------------------------------------------------------------------------
// Author: Filip Stefanak <f.stefanak@rare-technologies.com>
// Copyright (C) 2017 Rare Technologies
//
// This code is distributed under the terms and conditions
// from the MIT License (MIT).

#define CMS_TYPE CMS_Log1024
#define CMS_TYPE_STRING "CMS_Log1024"
#define CMS_CELL_TYPE uint16_t

#include "cms_common.h"

static inline int CMS_VARIANT(should_inc)(CMS_CELL_TYPE value)
{
    if (value >= 2048)
    {
        uint8_t shift = 33 - (value >> 10);
        uint32_t mask = 0xFFFFFFFF >> shift;
        if (mask & rand_32b())
            return 0;
    }
    return 1;
}

static inline long long CMS_VARIANT(decode)(CMS_CELL_TYPE value)
{
    if (value <= 2048)
        return value;
    else
        return (1024 + (value & 1023)) << ((value >> 10) - 1);
}

static inline CMS_CELL_TYPE CMS_VARIANT(_merge_value)(CMS_CELL_TYPE v1, CMS_CELL_TYPE v2, uint32_t merge_seed)
{
    long long decoded = CMS_VARIANT(decode)(v1);
    decoded += CMS_VARIANT(decode)(v2);

    if (decoded <= 2048)
        return decoded;

    // calculate the log base, preserving 11 most significant bytes as steps between next counter value
    CMS_CELL_TYPE log_result = 1;
    long long h = decoded;
    while (h >= 2048)
    {
        log_result += 1;
        h = h >> 1;
    }

    // When "decoded" is converted to logcounter value, there is an unconverted remainder.
    // Increase logcounter value by 1 with probability ( remainder / step ),
    // where step is the difference to next logcounter value.
    // In other words, 4096 + 3 (4099) becomes 4100 with p=0.75 and 4096 with p=0.25
    uint8_t shift = 33 - log_result;
    uint32_t mask = 0xFFFFFFFF >> shift;

    uint32_t r;
    MurmurHash3_x86_32((void *)&decoded, 8, merge_seed, (void *)&r);
    uint32_t remainder = mask & decoded;

    return (log_result << 10) + (h & 1023) + ((mask & r) < remainder);
}

#undef CMS_TYPE
#undef CMS_TYPE_STRING
#undef CMS_CELL_TYPE