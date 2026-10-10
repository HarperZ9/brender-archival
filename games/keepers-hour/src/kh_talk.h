/* The Keeper's Hour: a conversation in progress, and how it is drawn.
 * SPDX-License-Identifier: MIT */
#ifndef KH_TALK_H
#define KH_TALK_H

#include <brender.h>
#include "kh_script.h"

typedef struct kh_talk {
    const kh_script *script;
    const kh_node   *node;     /* NULL when no conversation is open */
    int              line;     /* lines shown so far in this node */
    int              choosing; /* all lines shown; waiting for a choice */
    int              selected; /* highlighted choice, for gamepad and keys */
    char             check[160]; /* the last roll, shown in full */
    unsigned int     rng;
    int              visited[KH_MAX_NODES];
    char             go[KH_ID_LEN]; /* set when a choice leads to "@room": the room to walk to */
} kh_talk;

void kh_talk_init(kh_talk *t, const kh_script *s, unsigned int seed);
int  kh_talk_open(kh_talk *t, const char *node_id); /* 0, or -1 if the node is missing */
void kh_talk_advance(kh_talk *t);                    /* next line, or show the choices */
void kh_talk_choose(kh_talk *t, int index);          /* roll if checked, then follow */
void kh_talk_close(kh_talk *t);
int  kh_talk_open_p(const kh_talk *t);

void kh_talk_draw(const kh_talk *t, br_pixelmap *pm, br_colour ink, br_colour accent, br_colour panel);

#endif
