/*
 * SPDX-License-Identifier: MIT
 * Inside vkprim: the wrapper objects. Each starts with a dispatch table, as
 * every BRender DDI object does, and holds the softprim object it wraps.
 */
#ifndef VKPRIM_IP_H
#define VKPRIM_IP_H

#define BR_PRIMITIVE_LIBRARY_PRIVATE 1
#define BR_PRIMITIVE_STATE_PRIVATE   1

#include "brender.h"
#include "brddi.h"
#include "priminfo.h"

typedef struct br_primitive_library {
    struct br_primitive_library_dispatch *dispatch;
    struct br_primitive_library          *inner;
} vkp_library;

typedef struct br_primitive_state {
    struct br_primitive_state_dispatch *dispatch;
    struct br_primitive_state          *inner;
} vkp_pstate;

extern const struct br_primitive_library_dispatch vkp_plib_dispatch;
extern const struct br_primitive_state_dispatch   vkp_state_dispatch;

#endif
