/* The Keeper's Hour: capturing frames for films and checks, with no wall clock.
 *
 *   KEEPERS_SHOT=file.ppm     one still, then quit
 *   KEEPERS_RECORD=dir        numbered frames dir/frame-00000.ppm ..., then quit
 *   KEEPERS_FPS=30            frames per second of game time (record)
 *   KEEPERS_SECONDS=4         length of the recording (4 s is one lamp sweep)
 *   KEEPERS_CLOCK=1.0         game clock at the first frame, in seconds; the lamp
 *                             turns 90 degrees a second (default 1.0 for a
 *                             still, 0 for a recording)
 *   KEEPERS_YAW=0             camera yaw in degrees at the first frame
 *   KEEPERS_YAW_SPEED=0       camera turn in degrees per second of game time
 *   KEEPERS_CAPTURE_UI=1      also draw the room title and any open conversation
 *
 * Frame n of a recording shows game time CLOCK + n / FPS exactly: the frames
 * do not depend on how fast the machine draws them.
 * SPDX-License-Identifier: MIT */
#ifndef KH_CAPTURE_H
#define KH_CAPTURE_H

#include <brender.h>

int   kh_capture_init(void);    /* reads the environment; 1 if capturing */
int   kh_capture_active(void);
int   kh_capture_ui(void);
float kh_capture_clock(void);   /* the game clock for the frame being drawn */
float kh_capture_yaw(void);     /* the camera yaw for the frame being drawn */

/* Call after the frame is drawn. Writes it when due; returns 1 when the
 * capture is finished and the program should quit. *problems counts failed writes. */
int kh_capture_frame(br_pixelmap *pm, int hw_accel, int *problems);

#endif
