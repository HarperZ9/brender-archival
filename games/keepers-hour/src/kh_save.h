/* The Keeper's Hour: saving the night at each room, and the end of the night.
 * SPDX-License-Identifier: MIT */
#ifndef KH_SAVE_H
#define KH_SAVE_H

#include <brender.h>
#include "kh_talk.h"

/* The save file in the player's preferences folder. */
const char *kh_save_path(void);
int  kh_save_write(const char *path, const char *room, const kh_talk *t); /* 0 on success */
int  kh_save_read(const char *path, char *room, size_t room_len, kh_talk *t);
int  kh_save_exists(const char *path);
void kh_save_forget(const char *path);

/* The three endings: their node, their title. */
const char *kh_ending_title(const char *node_id); /* NULL if not an ending */

/* Draw the card shown at dawn: the ending, and which voices you listened to. */
void kh_end_card(br_pixelmap *pm, const kh_talk *t, br_colour ink, br_colour accent, br_colour panel);

/* Reach every ending by a fixed route and round-trip a save; for the smoke
 * run. Returns the number of problems and prints what it checked. */
int kh_end_check(const kh_script *s);

#endif
