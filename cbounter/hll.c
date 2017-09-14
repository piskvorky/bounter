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

#include <stdint.h>
#include "hll.h"
#include <math.h>
#include <stdlib.h>

void HyperLogLog_init(HyperLogLog *self, uint32_t k)
{
    self->k = k;
    self->size = 1 << self->k;
    self->registers = (hll_cell_t *) calloc(self->size, sizeof(char));
}

void HyperLogLog_dealloc(HyperLogLog* self)
{
    free(self->registers);
}

/* Adds a hash to the cardinality estimator. */
void HyperLogLog_add(HyperLogLog *self, uint32_t hash)
{
    uint32_t index;
    uint32_t rank;

    /* Use the first k bits as a zero based index */
    index = (hash >> (32 - self->k));

    /* Compute the rank, lzc + 1, of the remaining 32 - k bits */
    rank = leadingZeroCount((hash << self->k) >> self->k) - self->k + 1;

    if (rank > self->registers[index])
        self->registers[index] = rank;
}

/* Gets a cardinality estimate. */
double HyperLogLog_cardinality(HyperLogLog *self)
{
    static const double two_32 = 4294967296.0;
    static const double neg_two_32 = -4294967296.0;

    double alpha = 0.0;
    switch (self->size) {
      case 16:
          alpha = 0.673;
          break;
      case 32:
          alpha = 0.697;
          break;
      case 64:
          alpha = 0.709;
          break;
      default:
          alpha = 0.7213/(1.0 + 1.079/(double) self->size);
          break;
    }

    uint32_t i;
    double rank;
    double sum = 0.0;
    for (i = 0; i < self->size; i++) {
        rank = (double) self->registers[i];
        sum = sum + pow(2, -1*rank);
    }

    double estimate = alpha * (1/sum) * self->size * self->size;

    if (estimate <= 2.5 * self->size) {
        uint32_t zeros = 0;
    uint32_t i;

    for (i = 0; i < self->size; i++) {
            if (self->registers[i] == 0) {
                zeros += 1;
            }
    }

        if (zeros != 0) {
            double size = (double) self->size;
            estimate = size * log(size / (double) zeros);
        }
    }

    if (estimate > (1.0/30.0) * two_32) {
        estimate = neg_two_32 * log(1.0 - estimate/two_32);
    }
    return estimate;
}

/* Merges another HyperLogLog into the current HyperLogLog. The registers of
 * the other HyperLogLog are unaffected.
 */
int HyperLogLog_merge(HyperLogLog *self, HyperLogLog *hll)
{
    if (hll->size != self->size) {
        return 1;
    }

    uint32_t i;
    for (i = 0; i < self->size; i++) {
        if (self->registers[i] < hll->registers[i])
            self->registers[i] = hll->registers[i];
    }

    return 0;
}

/* Get the number of leading zeros. */
uint32_t leadingZeroCount(uint32_t x) {
  x |= (x >> 1);
  x |= (x >> 2);
  x |= (x >> 4);
  x |= (x >> 8);
  x |= (x >> 16);
  return (32 - ones(x));
}

/* Get the number of bits set to 1. */
uint32_t ones(uint32_t x) {
  x -= (x >> 1) & 0x55555555;
  x = ((x >> 2) & 0x33333333) + (x & 0x33333333);
  x = ((x >> 4) + x) & 0x0F0F0F0F;
  x += (x >> 8);
  x += (x >> 16);
  return(x & 0x0000003F);
}
