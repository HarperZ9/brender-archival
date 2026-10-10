/* The Keeper's Hour: a small sound mixer on an SDL3 audio stream.
 * Every sound is synthesised here; there are no sound files.
 * SPDX-License-Identifier: MIT */
#ifndef KH_AUDIO_H
#define KH_AUDIO_H

typedef enum kh_sound {
    KH_SND_LINE,   /* a line of dialogue appears; pitch follows the voice */
    KH_SND_DICE,   /* two dice for a skill check */
    KH_SND_DOOR,   /* a door, a hatch, the stairs */
    KH_SND_DAWN,   /* the end of the night */
} kh_sound;

typedef enum kh_ambience { KH_AMB_INSIDE, KH_AMB_LAMP, KH_AMB_RADIO, KH_AMB_OUTSIDE } kh_ambience;

/* Open the default playback device. Returns 0, or -1 when there is no audio
 * (the game then runs silent; nothing else changes). */
int  kh_audio_open(void);
void kh_audio_close(void);
void kh_audio_volume(int level);          /* 0 to 10 */
void kh_audio_ambience(kh_ambience a);
void kh_audio_play(kh_sound s, int pitch); /* pitch: 0 to 3, low to high */

/* Render n mono samples at 44.1 kHz without a device: for tests and for
 * checking that the mixer stays inside [-1, 1]. */
void kh_audio_render(float *out, int n);

/* Render every sound in every ambience offline and check the mixer stays in
 * [-1, 1] and is not silent. Prints the result; returns the problems found. */
int kh_audio_check(void);

#endif
