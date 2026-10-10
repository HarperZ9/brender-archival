/* The Keeper's Hour: the five rooms of the tower, as data.
 * A talker's node is a script node, or "@room" for a way through to a room.
 * SPDX-License-Identifier: MIT */
#include <string.h>

#include "kh_rooms.h"

#define BOX(x, z, turn, w, y0, y1, r, g, b) {KH_PRISM, 4, w, w, y0, y1, r, g, b, x, z, turn, NULL, NULL}
#define TALK_BOX(x, z, turn, w, y0, y1, r, g, b, who, node) {KH_PRISM, 4, w, w, y0, y1, r, g, b, x, z, turn, who, node}
#define PANEL(x, z, turn, w, y0, y1, r, g, b, who, node) {KH_PANEL, 0, w, w, y0, y1, r, g, b, x, z, turn, who, node, NULL}
#define PICTURE(x, z, turn, w, y0, y1, tex, who, node) {KH_PANEL, 0, w, w, y0, y1, 255, 255, 255, x, z, turn, who, node, tex}
#define TEX_BOX(x, z, turn, w, y0, y1, tex, who, node) {KH_PRISM, 4, w, w, y0, y1, 255, 255, 255, x, z, turn, who, node, tex}

static const kh_prop lamp_room[] = {
    {KH_PRISM, 8, 0.9f, 0.6f, 0.0f, 1.4f, 196, 152, 64, 0.0f, 0.0f, 0, "the lamp", "lamp"},
    BOX(3.2f, -2.0f, 45, 0.9f, 0.0f, 0.9f, 104, 72, 46),
    TALK_BOX(3.2f, -2.0f, 20, 0.32f, 0.9f, 1.0f, 120, 36, 30, "the logbook", "logbook"),
    BOX(-3.0f, 2.6f, 0, 0.45f, 0.0f, 0.8f, 104, 72, 46),
    {KH_PRISM, 10, 0.32f, 0.18f, 0.8f, 1.25f, 150, 156, 160, -3.0f, 2.6f, 0, "the kettle", "kettle"},
    TALK_BOX(-3.4f, -2.8f, 30, 0.75f, 0.0f, 0.06f, 30, 26, 22, "the stairs down", "@stairs"),
    TALK_BOX(4.4f, 2.8f, 57, 0.5f, 0.0f, 2.6f, 70, 48, 32, "the gallery door", "@gallery"),
    PANEL(5.5f, 0.0f, 0, 1.5f, 1.4f, 3.2f, 22, 30, 52, NULL, NULL),
    PANEL(0.0f, 5.5f, -90, 1.5f, 1.4f, 3.2f, 22, 30, 52, NULL, NULL),
    PANEL(-5.5f, 0.0f, -180, 1.5f, 1.4f, 3.2f, 22, 30, 52, NULL, NULL),
    PANEL(0.0f, -5.5f, -270, 1.5f, 1.4f, 3.2f, 22, 30, 52, NULL, NULL),
};

static const kh_prop stairs_room[] = {
    {KH_PRISM, 8, 0.8f, 0.8f, 0.0f, 4.2f, 255, 255, 255, 0.0f, 0.0f, 0, NULL, NULL, "stone"},
    BOX(1.3f, 0.0f, 0, 0.45f, 0.0f, 0.25f, 96, 70, 44),
    BOX(0.9f, 0.9f, 45, 0.45f, 0.25f, 0.5f, 96, 70, 44),
    BOX(0.0f, 1.3f, 90, 0.45f, 0.5f, 0.75f, 96, 70, 44),
    BOX(-0.9f, 0.9f, 135, 0.45f, 0.75f, 1.0f, 96, 70, 44),
    BOX(-1.3f, 0.0f, 180, 0.45f, 1.0f, 1.25f, 96, 70, 44),
    BOX(-0.9f, -0.9f, 225, 0.45f, 1.25f, 1.5f, 96, 70, 44),
    TALK_BOX(2.6f, 2.4f, 10, 0.45f, 0.0f, 0.22f, 130, 96, 60, "the step that creaks", "step"),
    PICTURE(5.5f, 0.0f, 0, 1.4f, 1.2f, 2.6f, "painting-tower", "the first painting", "painting_one"),
    PICTURE(-3.9f, 3.9f, -135, 1.4f, 1.2f, 2.6f, "portrait", "the second painting", "painting_two"),
    TALK_BOX(-3.6f, -3.0f, 40, 0.75f, 0.0f, 0.06f, 30, 26, 22, "the stairs up", "@lamp"),
    TALK_BOX(3.4f, -3.2f, 40, 0.75f, 0.0f, 0.06f, 30, 26, 22, "the stairs down", "@keeper"),
    TALK_BOX(-4.6f, 0.4f, 0, 0.5f, 0.0f, 2.6f, 70, 48, 32, "the radio room door", "@radio"),
};

static const kh_prop radio_room[] = {
    TALK_BOX(0.0f, -3.4f, 0, 1.0f, 0.0f, 1.2f, 70, 76, 70, "the radio", "radio"),
    {KH_GLOW, 6, 0.18f, 0.18f, 1.2f, 1.3f, 120, 230, 160, 0.4f, -3.0f, 0, NULL, NULL},
    BOX(0.0f, -1.8f, 0, 0.45f, 0.0f, 0.55f, 90, 64, 42),
    PICTURE(-5.5f, 0.0f, -180, 2.2f, 1.0f, 3.0f, "chart", "the chart", "chart"),
    TALK_BOX(3.0f, 3.0f, 30, 0.5f, 0.0f, 0.45f, 120, 110, 90, "the box of letters", "letters_box"),
    TALK_BOX(4.4f, -1.2f, 0, 0.5f, 0.0f, 2.6f, 70, 48, 32, "the door to the stairs", "@stairs"),
};

static const kh_prop keeper_room[] = {
    BOX(-3.0f, -2.4f, 30, 1.0f, 0.0f, 0.5f, 140, 130, 120),
    TALK_BOX(-2.2f, -1.6f, 30, 1.0f, 0.0f, 0.55f, 160, 150, 140, "the bed", "bed"),
    BOX(2.8f, -2.6f, 45, 0.8f, 0.0f, 0.85f, 104, 72, 46),
    TEX_BOX(2.8f, -2.6f, 10, 0.3f, 0.85f, 0.88f, "letter", "the letter", "letter"),
    PICTURE(5.5f, 0.0f, 0, 0.9f, 1.4f, 2.4f, "photograph", "the photograph", "photo"),
    TALK_BOX(-3.4f, 3.0f, 40, 0.75f, 0.0f, 0.06f, 30, 26, 22, "the stairs up", "@stairs"),
};

static const kh_prop gallery[] = {
    {KH_PRISM, 8, 3.0f, 3.0f, 0.0f, 5.0f, 255, 255, 255, 0.0f, 0.0f, 0, NULL, NULL, "stone"},
    {KH_PRISM, 16, 5.8f, 5.8f, 0.0f, 0.9f, 60, 64, 70, 0.0f, 0.0f, 0, NULL, NULL},
    {KH_GLOW, 4, 0.35f, 0.0f, -2.5f, -1.6f, 255, 214, 140, -26.0f, -4.0f, 0, NULL, NULL},
    {KH_GLOW, 4, 0.35f, 0.0f, -2.5f, -1.6f, 255, 200, 120, -27.0f, 0.0f, 0, NULL, NULL},
    {KH_GLOW, 4, 0.35f, 0.0f, -2.5f, -1.6f, 255, 230, 170, -25.0f, 3.0f, 0, NULL, NULL},
    {KH_GLOW, 4, 0.35f, 0.0f, -2.5f, -1.6f, 255, 210, 150, -28.0f, 6.0f, 0, NULL, NULL},
    {KH_GLOW, 4, 0.35f, 0.0f, -2.5f, -1.6f, 255, 214, 140, -24.0f, 9.0f, 0, NULL, NULL},
    {KH_GLOW, 4, 0.35f, 0.0f, -2.5f, -1.6f, 255, 200, 120, -29.0f, -7.0f, 0, NULL, NULL},
    {KH_GLOW, 4, 0.35f, 0.0f, -2.5f, -1.6f, 255, 230, 170, -26.0f, 12.0f, 0, NULL, NULL},
    TALK_BOX(-5.3f, 1.2f, 0, 0.3f, 0.0f, 0.95f, 80, 84, 90, "the town lights", "town"),
    TALK_BOX(0.0f, -5.3f, 0, 0.3f, 0.0f, 0.95f, 80, 84, 90, "the railing", "railing"),
    TALK_BOX(3.8f, 3.6f, 0, 0.3f, 0.0f, 0.95f, 150, 150, 150, "the gull's place", "gull"),
    TALK_BOX(3.3f, 0.0f, 0, 0.5f, 0.0f, 2.6f, 70, 48, 32, "the gallery door", "@lamp"),
};

#define ROOM(id, title, walled, radius, inner, props, lamp, w, f, s) \
    {id, title, walled, radius, inner, {w}, {f}, {s}, props, (int)(sizeof(props) / sizeof(props[0])), lamp}
#define RGB3(r, g, b) r, g, b

const kh_room kh_rooms[] = {
    ROOM("lamp", "the lamp room", 1, 5.2f, 0.0f, lamp_room, 1, RGB3(112, 104, 92), RGB3(82, 60, 42), RGB3(6, 7, 12)),
    ROOM("stairs", "the stairs", 1, 5.2f, 1.6f, stairs_room, 0, RGB3(104, 98, 90), RGB3(70, 64, 58), RGB3(6, 7, 12)),
    ROOM("radio", "the radio room", 1, 5.2f, 0.0f, radio_room, 0, RGB3(92, 100, 96), RGB3(64, 58, 50), RGB3(6, 7, 12)),
    ROOM("keeper", "the keeper's room", 1, 5.2f, 0.0f, keeper_room, 0, RGB3(118, 108, 98), RGB3(88, 66, 48), RGB3(6, 7, 12)),
    ROOM("gallery", "the gallery", 0, 5.4f, 3.6f, gallery, 0, RGB3(0, 0, 0), RGB3(58, 60, 66), RGB3(10, 14, 30)),
};
const int kh_room_count = (int)(sizeof(kh_rooms) / sizeof(kh_rooms[0]));

int kh_room_find(const char *id)
{
    int i;
    for (i = 0; i < kh_room_count; i++)
        if (strcmp(kh_rooms[i].id, id) == 0)
            return i;
    return -1;
}
