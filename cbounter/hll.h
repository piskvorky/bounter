//-----------------------------------------------------------------------------
// Author: Filip Stefanak <f.stefanak@rare-technologies.com>
// Copyright (C) 2017 Rare Technologies
//
// This code is distributed under the terms and conditions
// from the MIT License (MIT).
//
// Using modified code from HLL package by Joshua Andersen, also distributed under MIT License:
// https://github.com/ascv/HyperLogLog
//
// Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#ifndef HLL_H
#define HLL_H

uint32_t leadingZeroCount(uint32_t x);

uint32_t ones(uint32_t x);

typedef unsigned char hll_cell_t;

typedef struct {
    short int k;      /* size = 2^k */
    uint32_t size;    /* number of registers */
    hll_cell_t * registers; /* ranks */
} HyperLogLog;

void HyperLogLog_init(HyperLogLog *self, uint32_t k);

void HyperLogLog_dealloc(HyperLogLog* self);

/* Adds a hash to the cardinality estimator. */
void HyperLogLog_add(HyperLogLog *self, uint32_t hash);

/* Gets a cardinality estimate. */
double HyperLogLog_cardinality(HyperLogLog *self);

/* Merges another HyperLogLog into the current HyperLogLog. The registers of
 * the other HyperLogLog are unaffected.
 * Returns 0 when successful, 1 otherwise
 */
int HyperLogLog_merge(HyperLogLog *self, HyperLogLog *hll);

#endif
