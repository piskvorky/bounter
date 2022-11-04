//-----------------------------------------------------------------------------
// Author: Filip Stefanak <f.stefanak@rare-technologies.com>
// Copyright (C) 2017 Rare Technologies
//
// This code is distributed under the terms and conditions
// from the MIT License (MIT).

#ifndef _CMS_CONSERVATIE_H_
#define _CMS_CONSERVATIE_H_

#define CMS_TYPE CMS_Conservative
#define CMS_TYPE_STRING "CMS_Conservative"
#define CMS_CELL_TYPE uint32_t

#include "cms_common.h"

static inline int CMS_VARIANT(should_inc)(CMS_CELL_TYPE value)
{
    return 1;
}

static inline long long CMS_VARIANT(decode)(CMS_CELL_TYPE value)
{
    return value;
}

static inline CMS_CELL_TYPE CMS_VARIANT(_merge_value)(CMS_CELL_TYPE v1, CMS_CELL_TYPE v2, uint32_t merge_seed)
{
    return v1 + v2;
}

#undef CMS_TYPE
#undef CMS_TYPE_STRING
#undef CMS_CELL_TYPE

#endif /* _CMS_CONSERVATIE_H_ */