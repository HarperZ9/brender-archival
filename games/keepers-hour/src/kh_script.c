/* The Keeper's Hour: night script parser.
 *
 *   voices: lens 3, ledger 4, tide 2, static 1
 *   == node_id
 *   SPEAKER: a line of dialogue
 *   * A plain choice -> next_node
 *   * [LEDGER 9] A checked choice -> on_success | on_failure
 *
 * Lines starting with # are comments. END closes the conversation.
 * SPDX-License-Identifier: MIT */
#include <ctype.h>
#include <stdio.h>
#include <string.h>

#include "kh_script.h"

static const char *voice_names[KH_VOICE_COUNT] = {"LENS", "LEDGER", "TIDE", "STATIC"};

const char *kh_voice_name(kh_voice v) { return (v >= 0 && v < KH_VOICE_COUNT) ? voice_names[v] : ""; }

static kh_voice voice_from(const char *word)
{
    int i;
    for (i = 0; i < KH_VOICE_COUNT; i++) {
        const char *a = word, *b = voice_names[i];
        while (*a && *b && toupper((unsigned char)*a) == *b) { a++; b++; }
        if (*b == '\0' && !isalpha((unsigned char)*a))
            return (kh_voice)i;
    }
    return KH_NO_VOICE;
}

static void trim_copy(char *dst, size_t len, const char *src, size_t n)
{
    while (n > 0 && isspace((unsigned char)*src)) { src++; n--; }
    while (n > 0 && isspace((unsigned char)src[n - 1])) n--;
    if (n >= len) n = len - 1;
    memcpy(dst, src, n);
    dst[n] = '\0';
}

static int parse_voices(kh_script *s, const char *p)
{
    while (*p) {
        kh_voice v;
        int rating;
        while (*p && !isalpha((unsigned char)*p)) p++;
        if (!*p) break;
        v = voice_from(p);
        while (*p && isalpha((unsigned char)*p)) p++;
        if (v == KH_NO_VOICE || sscanf(p, "%d", &rating) != 1) return -1;
        s->ratings[v] = rating;
        while (*p && *p != ',') p++;
    }
    return 0;
}

static int parse_choice(kh_choice *c, const char *p)
{
    const char *arrow = strstr(p, "->"), *bar;
    memset(c, 0, sizeof(*c));
    c->voice = KH_NO_VOICE;
    if (arrow == NULL) return -1;
    while (isspace((unsigned char)*p)) p++;
    if (*p == '[') {
        char word[16] = {0};
        if (sscanf(p + 1, "%15s %d]", word, &c->target) != 2) return -1;
        if ((c->voice = voice_from(word)) == KH_NO_VOICE) return -1;
        if ((p = strchr(p, ']')) == NULL) return -1;
        p++;
    }
    trim_copy(c->text, sizeof(c->text), p, (size_t)(arrow - p));
    arrow += 2;
    bar = strchr(arrow, '|');
    if (c->voice != KH_NO_VOICE && bar == NULL) return -1;
    trim_copy(c->pass, sizeof(c->pass), arrow, bar ? (size_t)(bar - arrow) : strlen(arrow));
    if (bar) trim_copy(c->fail, sizeof(c->fail), bar + 1, strlen(bar + 1));
    return c->pass[0] ? 0 : -1;
}

static int parse_line(kh_script *s, kh_node **node, const char *p)
{
    const char *colon;
    while (isspace((unsigned char)*p)) p++;
    if (*p == '\0' || *p == '#') return 0;
    if (strncmp(p, "voices:", 7) == 0) return parse_voices(s, p + 7);
    if (strncmp(p, "==", 2) == 0) {
        if (s->nnodes >= KH_MAX_NODES) return -1;
        *node = &s->nodes[s->nnodes++];
        memset(*node, 0, sizeof(**node));
        trim_copy((*node)->id, sizeof((*node)->id), p + 2, strlen(p + 2));
        return (*node)->id[0] ? 0 : -1;
    }
    if (*node == NULL) return -1;
    if (*p == '*') {
        if ((*node)->nchoices >= KH_MAX_CHOICES) return -1;
        return parse_choice(&(*node)->choices[(*node)->nchoices++], p + 1);
    }
    if ((colon = strchr(p, ':')) == NULL || (*node)->nlines >= KH_MAX_LINES) return -1;
    {
        kh_line *l = &(*node)->lines[(*node)->nlines++];
        trim_copy(l->speaker, sizeof(l->speaker), p, (size_t)(colon - p));
        trim_copy(l->text, sizeof(l->text), colon + 1, strlen(colon + 1));
    }
    return 0;
}

int kh_script_parse(kh_script *s, const char *text, char *err, size_t err_len)
{
    kh_node *node = NULL;
    char line[512];
    int number = 0;
    memset(s, 0, sizeof(*s));
    while (*text) {
        size_t n = strcspn(text, "\r\n");
        number++;
        trim_copy(line, sizeof(line), text, n);
        if (parse_line(s, &node, line) != 0) {
            snprintf(err, err_len, "night script line %d: cannot read \"%.60s\"", number, line);
            return -1;
        }
        text += n;
        if (*text == '\r') text++;
        if (*text == '\n') text++;
    }
    return 0;
}

const kh_node *kh_script_find(const kh_script *s, const char *id)
{
    int i;
    for (i = 0; i < s->nnodes; i++)
        if (strcmp(s->nodes[i].id, id) == 0)
            return &s->nodes[i];
    return NULL;
}

/* "@room" moves the keeper to a room; the game checks room names itself. */
static int link_ok(const kh_script *s, const char *id) { return strcmp(id, "END") == 0 || id[0] == '@' || kh_script_find(s, id) != NULL; }

int kh_script_check_links(const kh_script *s, char *err, size_t err_len)
{
    int i, j, broken = 0;
    for (i = 0; i < s->nnodes; i++)
        for (j = 0; j < s->nodes[i].nchoices; j++) {
            const kh_choice *c = &s->nodes[i].choices[j];
            const char *bad = !link_ok(s, c->pass) ? c->pass : (c->fail[0] && !link_ok(s, c->fail)) ? c->fail : NULL;
            if (bad && broken++ == 0)
                snprintf(err, err_len, "node %s links to missing node %s", s->nodes[i].id, bad);
        }
    return broken;
}
