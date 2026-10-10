/* The Keeper's Hour: the night script (dialogue nodes, choices, voice checks).
 * SPDX-License-Identifier: MIT */
#ifndef KH_SCRIPT_H
#define KH_SCRIPT_H

#include <stddef.h>

#define KH_MAX_NODES   128
#define KH_MAX_LINES   12
#define KH_MAX_CHOICES 6
#define KH_ID_LEN      32
#define KH_TEXT_LEN    240

typedef enum kh_voice { KH_LENS, KH_LEDGER, KH_TIDE, KH_STATIC, KH_VOICE_COUNT, KH_NO_VOICE = -1 } kh_voice;

typedef struct kh_line {
    char speaker[KH_ID_LEN];
    char text[KH_TEXT_LEN];
} kh_line;

typedef struct kh_choice {
    char     text[KH_TEXT_LEN];
    kh_voice voice;              /* KH_NO_VOICE: no check */
    int      target;             /* two dice plus the rating must reach this */
    char     pass[KH_ID_LEN];    /* node on success, or "END" */
    char     fail[KH_ID_LEN];    /* node on failure (checks only) */
    char     needs[KH_ID_LEN];   /* shown only after this node was visited; "" always */
} kh_choice;

typedef struct kh_node {
    char      id[KH_ID_LEN];
    kh_line   lines[KH_MAX_LINES];
    int       nlines;
    kh_choice choices[KH_MAX_CHOICES];
    int       nchoices;
} kh_node;

typedef struct kh_script {
    int     ratings[KH_VOICE_COUNT];
    kh_node nodes[KH_MAX_NODES];
    int     nnodes;
} kh_script;

/* Parse a script. Returns 0, or -1 with a message naming the line in err. */
int kh_script_parse(kh_script *s, const char *text, char *err, size_t err_len);

/* Every choice must lead to a node that exists, or to END. Returns the
 * number of broken links and names the first one in err. */
int kh_script_check_links(const kh_script *s, char *err, size_t err_len);

const kh_node *kh_script_find(const kh_script *s, const char *id);
const char    *kh_voice_name(kh_voice v);

#endif
