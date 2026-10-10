/* The Keeper's Hour: the five rooms of the tower, as data.
 * SPDX-License-Identifier: MIT */
#ifndef KH_ROOMS_H
#define KH_ROOMS_H

typedef enum kh_prop_kind { KH_PRISM, KH_GLOW, KH_PANEL } kh_prop_kind;

typedef struct kh_prop {
    kh_prop_kind  kind;
    int           sides;            /* KH_PRISM, KH_GLOW */
    float         r0, r1, y0, y1;   /* radii and heights; KH_PANEL uses r0 as width */
    unsigned char r, g, b;
    float         x, z, turn;
    const char   *talker;           /* NULL: scenery */
    const char   *node;             /* script node, or "@room" for a way through */
} kh_prop;

typedef struct kh_room {
    const char    *id;
    const char    *title;
    int            walled;          /* 0: outside, no walls (the gallery) */
    float          radius;          /* how far the keeper can walk from the centre */
    float          inner;           /* how close to the centre (the tower, outside) */
    unsigned char  wall[3], floor[3], sky[3];
    const kh_prop *props;
    int            nprops;
    int            lamp;            /* 1: the turning lens and its beam are here */
} kh_room;

extern const kh_room kh_rooms[];
extern const int     kh_room_count;

int kh_room_find(const char *id);

#endif
