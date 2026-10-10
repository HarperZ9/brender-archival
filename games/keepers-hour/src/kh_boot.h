/* The Keeper's Hour: reading the night script and checking it against the rooms.
 * SPDX-License-Identifier: MIT */
#ifndef KH_BOOT_H
#define KH_BOOT_H

#include "kh_script.h"

/* Read data/night.txt beside the program, check every link and every room
 * name. 0 on success; problems are logged. */
int kh_boot_load(kh_script *s);

#endif
