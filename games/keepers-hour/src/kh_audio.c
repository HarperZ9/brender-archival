/* The Keeper's Hour: a small sound mixer on an SDL3 audio stream.
 *
 * Wind is filtered noise that breathes slowly; the lamp room adds the
 * clockwork's tick every four seconds, in step with the beam; the radio room
 * adds a faint crackle. One-shot sounds are short enveloped tones and noise
 * bursts. Mono, 44.1 kHz, float. Deterministic: the noise is a fixed
 * xorshift, so a given sequence of calls renders the same samples.
 * SPDX-License-Identifier: MIT */
#include <math.h>
#include <stdio.h>
#include <string.h>

#include <SDL3/SDL.h>
#include "kh_audio.h"

#define RATE  44100
#define MAX_SHOTS 8
#define TWO_PI 6.28318530718f

typedef struct shot { int active; kh_sound s; int pitch; int t; } shot;

static struct {
    SDL_AudioStream *stream;
    float            volume;
    kh_ambience      ambience;
    shot             shots[MAX_SHOTS];
    unsigned int     noise;
    float            low, low2;
    long             clock;
} A = {NULL, 0.6f, KH_AMB_LAMP, {{0}}, 1998u, 0, 0, 0};

static float noise(void)
{
    A.noise ^= A.noise << 13;
    A.noise ^= A.noise >> 17;
    A.noise ^= A.noise << 5;
    return (float)(A.noise & 0xFFFF) / 32768.0f - 1.0f;
}

static float env(int t, int attack, int length) /* a short rise and an exponential fall */
{
    if (t < attack) return (float)t / attack;
    return t < length ? expf(-5.0f * (float)(t - attack) / (length - attack)) : 0.0f;
}

static float shot_sample(shot *s)
{
    static const float line_hz[4] = {196.0f, 262.0f, 330.0f, 440.0f};
    float t = (float)s->t / RATE, v = 0.0f;
    switch (s->s) {
    case KH_SND_LINE:
        v = 0.18f * sinf(TWO_PI * line_hz[s->pitch & 3] * t) * env(s->t, 200, 5000);
        if (s->t >= 5000) s->active = 0;
        break;
    case KH_SND_DICE: /* two wooden clicks */
        v = 0.35f * noise() * (env(s->t, 20, 900) + env(s->t - 4000 > 0 ? s->t - 4000 : 0, 20, 900) * (s->t > 4000));
        if (s->t >= 6000) s->active = 0;
        break;
    case KH_SND_DOOR:
        v = 0.45f * sinf(TWO_PI * 70.0f * t) * env(s->t, 400, 14000) + 0.08f * noise() * env(s->t, 50, 3000);
        if (s->t >= 14000) s->active = 0;
        break;
    case KH_SND_DAWN: /* three slow notes, a chord opening */
        v = 0.12f * (sinf(TWO_PI * 262.0f * t) * env(s->t, 2000, 60000) + sinf(TWO_PI * 330.0f * t) * env(s->t > 8000 ? s->t - 8000 : 0, 2000, 52000) * (s->t > 8000)
                     + sinf(TWO_PI * 392.0f * t) * env(s->t > 16000 ? s->t - 16000 : 0, 2000, 44000) * (s->t > 16000));
        if (s->t >= 60000) s->active = 0;
        break;
    }
    s->t++;
    return v;
}

static float ambience_sample(void)
{
    float breath = 0.6f + 0.4f * sinf(TWO_PI * (float)A.clock / (RATE * 7.0f));
    float wind_level = A.ambience == KH_AMB_OUTSIDE ? 0.30f : 0.07f, v;
    A.low += 0.02f * (noise() - A.low);  /* two one-pole low-passes: wind */
    A.low2 += 0.05f * (A.low - A.low2);
    v = wind_level * breath * A.low2 * 6.0f;
    if (A.ambience == KH_AMB_LAMP) { /* the clockwork, once a sweep */
        long phase = A.clock % (RATE * 4);
        if (phase < 600) v += 0.15f * noise() * (1.0f - phase / 600.0f);
    }
    if (A.ambience == KH_AMB_RADIO && (A.noise & 0x3FF) == 7)
        v += 0.25f * noise(); /* a crackle now and then */
    return v;
}

void kh_audio_render(float *out, int n)
{
    int i, k;
    for (i = 0; i < n; i++, A.clock++) {
        float v = ambience_sample();
        for (k = 0; k < MAX_SHOTS; k++)
            if (A.shots[k].active) v += shot_sample(&A.shots[k]);
        out[i] = tanhf(v * A.volume); /* a soft limit: loud moments round off instead of clipping */
    }
}

static void SDLCALL feed(void *user, SDL_AudioStream *stream, int additional, int total)
{
    float buf[1024];
    (void)user;
    (void)total;
    while (additional > 0) {
        int n = additional / (int)sizeof(float);
        if (n > 1024) n = 1024;
        if (n <= 0) break;
        kh_audio_render(buf, n);
        SDL_PutAudioStreamData(stream, buf, n * (int)sizeof(float));
        additional -= n * (int)sizeof(float);
    }
}

int kh_audio_open(void)
{
    SDL_AudioSpec spec = {SDL_AUDIO_F32, 1, RATE};
    if (!SDL_InitSubSystem(SDL_INIT_AUDIO))
        return -1;
    A.stream = SDL_OpenAudioDeviceStream(SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK, &spec, feed, NULL);
    if (A.stream == NULL)
        return -1;
    SDL_ResumeAudioStreamDevice(A.stream);
    return 0;
}

void kh_audio_close(void)
{
    if (A.stream) SDL_DestroyAudioStream(A.stream);
    A.stream = NULL;
}

void kh_audio_volume(int level)
{
    if (A.stream) SDL_LockAudioStream(A.stream);
    A.volume = (level < 0 ? 0 : level > 10 ? 10 : level) / 10.0f;
    if (A.stream) SDL_UnlockAudioStream(A.stream);
}

void kh_audio_ambience(kh_ambience a)
{
    if (A.stream) SDL_LockAudioStream(A.stream);
    A.ambience = a;
    if (A.stream) SDL_UnlockAudioStream(A.stream);
}

void kh_audio_play(kh_sound s, int pitch)
{
    int k;
    if (A.stream) SDL_LockAudioStream(A.stream);
    for (k = 0; k < MAX_SHOTS; k++)
        if (!A.shots[k].active) {
            A.shots[k] = (shot){1, s, pitch, 0};
            break;
        }
    if (A.stream) SDL_UnlockAudioStream(A.stream);
}

int kh_audio_check(void)
{
    static float buf[RATE * 2];
    float peak = 0.0f, energy = 0.0f;
    int a, s, i, clipped = 0;
    SDL_AudioStream *keep = A.stream;
    A.stream = NULL; /* offline: no device lock */
    for (a = KH_AMB_INSIDE; a <= KH_AMB_OUTSIDE; a++) {
        A.ambience = (kh_ambience)a;
        for (s = KH_SND_LINE; s <= KH_SND_DAWN; s++)
            kh_audio_play((kh_sound)s, s & 3);
        kh_audio_render(buf, RATE * 2);
        for (i = 0; i < RATE * 2; i++) {
            float v = fabsf(buf[i]);
            peak = v > peak ? v : peak;
            energy += buf[i] * buf[i];
            clipped += v >= 1.0f;
        }
    }
    A.stream = keep;
    printf("keepers audio: peak %.3f, rms %.4f, %d clipped samples\n", peak, sqrtf(energy / (RATE * 8.0f)), clipped);
    return (peak <= 0.0f || peak > 1.0f || clipped > RATE / 100) ? 1 : 0;
}
