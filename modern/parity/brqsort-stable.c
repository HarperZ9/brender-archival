/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 Zain Dana Harper.
 *
 * BrQsort as a stable merge sort, for -DPARITY_STABLE_SORT=ON
 * (modern/parity/stable-sort.cmake). BRender 1.4's BrQsort calls the C
 * library's qsort, and the MSVC and glibc runtimes leave equal keys in
 * different orders. core/v1db/prepmesh.c sums the face normals of each
 * shared vertex in the order the sort leaves them, so the two builds round
 * those sums differently in the last bit. One stable sort on both platforms
 * takes the runtime out. See modern/parity/README.md, "Where the last pixels
 * come from".
 */

#include "brender.h"

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

static void merge_pass(unsigned char *src, unsigned char *dst, unsigned int n, unsigned int size,
                       unsigned int width, br_qsort_cbfn *comp)
{
    unsigned int lo;

    for(lo = 0; lo < n; lo += 2 * width) {
        unsigned int mid = lo + width < n ? lo + width : n;
        unsigned int hi  = lo + 2 * width < n ? lo + 2 * width : n;
        unsigned int l = lo, r = mid, k = lo;

        /* take from the right run only when it is strictly smaller: stable */
        while(l < mid && r < hi) {
            if(comp(src + (size_t)r * size, src + (size_t)l * size) < 0)
                memcpy(dst + (size_t)k++ * size, src + (size_t)r++ * size, size);
            else
                memcpy(dst + (size_t)k++ * size, src + (size_t)l++ * size, size);
        }
        if(l < mid)
            memcpy(dst + (size_t)k * size, src + (size_t)l * size, (size_t)(mid - l) * size);
        else if(r < hi)
            memcpy(dst + (size_t)k * size, src + (size_t)r * size, (size_t)(hi - r) * size);
    }
}

void BR_RESIDENT_ENTRY BrQsort(void *basep, unsigned int nelems, unsigned int size, br_qsort_cbfn *comp)
{
    unsigned char *a = basep, *tmp, *src, *dst;
    unsigned int   width;

    if(nelems < 2)
        return;

    tmp = malloc((size_t)nelems * size);
    if(tmp == NULL) {
        /* no silent fallback to the runtime's order: that is what this file removes */
        fprintf(stderr, "BrQsort: out of memory sorting %u elements\n", nelems);
        abort();
    }

    src = a;
    dst = tmp;
    for(width = 1; width < nelems; width *= 2) {
        unsigned char *t;
        merge_pass(src, dst, nelems, size, width, comp);
        t   = src;
        src = dst;
        dst = t;
    }
    if(src != a)
        memcpy(a, src, (size_t)nelems * size);
    free(tmp);
}
