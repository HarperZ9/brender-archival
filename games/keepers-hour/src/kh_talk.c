/* The Keeper's Hour: a conversation in progress, and how it is drawn.
 * SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <string.h>

#include "kh_tex.h"
#include "kh_audio.h"
#include "kh_talk.h"

static int roll_die(kh_talk *t)
{
    /* xorshift32: the same seed replays the same night */
    t->rng ^= t->rng << 13;
    t->rng ^= t->rng >> 17;
    t->rng ^= t->rng << 5;
    return (int)(t->rng % 6u) + 1;
}

void kh_talk_init(kh_talk *t, const kh_script *s, unsigned int seed)
{
    memset(t, 0, sizeof(*t));
    t->script = s;
    t->rng = seed ? seed : 1998u;
}

/* Each voice has its own note when its line appears: the Tide low, the Lens high. */
static void line_sound(const kh_talk *t)
{
    const char *who = t->node->lines[t->line - 1].speaker;
    int pitch = strcmp(who, "TIDE") == 0 ? 0 : strcmp(who, "LEDGER") == 0 ? 2 : strcmp(who, "LENS") == 0 ? 3 : 1;
    if (t->node->nlines > 0)
        kh_audio_play(KH_SND_LINE, pitch);
}

int kh_talk_open(kh_talk *t, const char *node_id)
{
    const kh_node *n = kh_script_find(t->script, node_id);
    if (n == NULL)
        return -1;
    t->node = n;
    t->line = 1;
    t->selected = 0;
    t->choosing = n->nlines <= 1;
    t->visited[n - t->script->nodes] = 1;
    snprintf(t->last, sizeof(t->last), "%s", n->id);
    line_sound(t);
    return 0;
}

int  kh_talk_open_p(const kh_talk *t) { return t->node != NULL; }
void kh_talk_close(kh_talk *t) { t->node = NULL; t->check[0] = '\0'; }

int kh_talk_visited(const kh_talk *t, const char *node_id)
{
    const kh_node *n = kh_script_find(t->script, node_id);
    return n != NULL && t->visited[n - t->script->nodes];
}

static int available(const kh_talk *t, const kh_choice *c) { return c->needs[0] == '\0' || kh_talk_visited(t, c->needs); }

int kh_talk_visible_count(const kh_talk *t)
{
    int i, count = 0;
    for (i = 0; t->node != NULL && i < t->node->nchoices; i++)
        count += available(t, &t->node->choices[i]);
    return count;
}

int kh_talk_visible(const kh_talk *t, int visible_index)
{
    int i;
    for (i = 0; t->node != NULL && i < t->node->nchoices; i++)
        if (available(t, &t->node->choices[i]) && visible_index-- == 0)
            return i;
    return -1;
}

void kh_talk_advance(kh_talk *t)
{
    if (t->node == NULL || t->choosing)
        return;
    if (++t->line >= t->node->nlines)
        t->choosing = 1;
    if (t->line <= t->node->nlines)
        line_sound(t);
}

static const char *roll(kh_talk *t, const kh_choice *c)
{
    int a = roll_die(t), b = roll_die(t), rating = t->script->ratings[c->voice];
    int total = rating + a + b, pass = total >= c->target;
    snprintf(t->check, sizeof(t->check), "%s %d + dice %d + %d = %d against %d: %s", kh_voice_name(c->voice), rating, a, b, total,
             c->target, pass ? "success" : "failure");
    kh_audio_play(KH_SND_DICE, 0);
    t->asked[c->voice]++;
    t->heard[c->voice] += pass;
    return pass ? c->pass : c->fail;
}

void kh_talk_choose(kh_talk *t, int visible_index)
{
    int index = kh_talk_visible(t, visible_index);
    const kh_choice *c;
    const char *next;
    if (t->node == NULL || !t->choosing || index < 0)
        return;
    c = &t->node->choices[index];
    t->check[0] = '\0';
    next = c->voice != KH_NO_VOICE ? roll(t, c) : c->pass;
    if (next[0] == '@') {
        snprintf(t->go, sizeof(t->go), "%s", next + 1);
        t->node = NULL;
    } else if (strcmp(next, "END") == 0 || kh_talk_open(t, next) != 0) {
        t->node = NULL;
    }
}

/* Draw text wrapped to width; returns the y below the last row. */
static br_int_32 wrapped(br_pixelmap *pm, br_int_32 x, br_int_32 y, br_int_32 width, br_colour colour, const char *text)
{
    char row[256];
    br_int_32 step = BrPixelmapTextHeight(pm, BrFontProp7x9) + 4;
    const char *p = text;
    while (*p) {
        size_t n = 0, last_space = 0;
        while (p[n] && n < sizeof(row) - 1) {
            memcpy(row, p, n + 1);
            row[n + 1] = '\0';
            if (BrPixelmapTextWidth(pm, BrFontProp7x9, row) > width)
                break;
            if (p[n] == ' ')
                last_space = n;
            n++;
        }
        if (p[n] && last_space > 0)
            n = last_space;
        memcpy(row, p, n);
        row[n] = '\0';
        kh_text(pm, x, y, colour, row);
        y += step;
        p += n;
        while (*p == ' ') p++;
    }
    return y;
}

void kh_talk_draw(const kh_talk *t, br_pixelmap *pm, br_colour ink, br_colour accent, br_colour panel)
{
    br_int_32 left = -pm->origin_x, top = pm->height - pm->origin_y;
    br_int_32 width = pm->width < 900 ? pm->width - 40 : 860, x = left + (pm->width - width) / 2;
    br_int_32 height, y;
    int i, rows;
    char label[KH_TEXT_LEN + 16];

    if (t->node == NULL)
        return;
    /* size the panel to what it holds: about two rows a line, one a choice */
    rows = (t->check[0] ? 2 : 0) + 2 * t->line + (t->choosing ? 2 * kh_talk_visible_count(t) : 1);
    height = 24 + 13 * rows;
    y = top - height - 16;
    BrPixelmapRectangleFill(pm, x - 12, y - 12, width + 24, height + 8, panel);
    if (t->check[0])
        y = wrapped(pm, x, y, width, accent, t->check) + 4;
    for (i = 0; i < t->line && i < t->node->nlines; i++) {
        const kh_line *l = &t->node->lines[i];
        snprintf(label, sizeof(label), "%s", l->speaker);
        kh_text(pm, x, y, accent, label);
        y = wrapped(pm, x + 72, y, width - 72, ink, l->text) + 2;
    }
    if (!t->choosing) {
        kh_text(pm, x, y + 4, accent, "Space, E or A: continue");
        return;
    }
    for (i = 0; i < kh_talk_visible_count(t); i++) {
        const kh_choice *c = &t->node->choices[kh_talk_visible(t, i)];
        if (c->voice != KH_NO_VOICE)
            snprintf(label, sizeof(label), "%c %d. [%s %d] %s", i == t->selected ? '>' : ' ', i + 1, kh_voice_name(c->voice), c->target, c->text);
        else
            snprintf(label, sizeof(label), "%c %d. %s", i == t->selected ? '>' : ' ', i + 1, c->text);
        y = wrapped(pm, x, y + 2, width, i == t->selected ? accent : ink, label);
    }
}
