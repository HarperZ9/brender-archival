# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Zain Dana Harper.
#
# parity_period_sine(<BRender 1.4 source> <copy>): copy BRender 1.4's tree and
# give the copy BRender 1.3.2's sine and cosine, for -DPARITY_PERIOD_SINE=ON.
#
# The two versions turn an angle into sin and cos differently, and the
# results differ in the last bit:
# - 1.3.2, FLOAT build (inc/angles.h:46 and 54): the angle is an unsigned
#   16-bit count, so a negative angle wraps to nearly a whole turn; the
#   radian, count * (PI / 32768.0), is rounded to float; sin() and cos() run
#   in double and are rounded to float.
# - 1.4 (core/inc/angles.h:20, 29 and 30): PI is a float constant
#   (core/inc/scalar.h:202), the radian is the float product
#   angle * (2.0f * PI), and sinf() and cosf() give the result.
# A last bit in a rotation moves a vertex or a lit colour by a last bit, and
# now and then that tips a pixel. The copy keeps every other line of 1.4.
# See modern/parity/README.md, "Where the last pixels come from".

function(parity_period_sine source copy)
  set(header "${copy}/core/inc/angles.h")
  if(NOT EXISTS "${header}")
    file(COPY "${source}/" DESTINATION "${copy}" PATTERN ".git" EXCLUDE)
  endif()
  file(READ "${header}" text)
  string(FIND "${text}" "PARITY_PERIOD_SINE" done)
  if(NOT done EQUAL -1)
    return()
  endif()
  set(old_sin "#define BR_SIN(a)           ((br_scalar)sinf(BrAngleToRadian(a)))")
  set(old_cos "#define BR_COS(a)           ((br_scalar)cosf(BrAngleToRadian(a)))")
  string(FIND "${text}" "${old_sin}" at_sin)
  string(FIND "${text}" "${old_cos}" at_cos)
  if(at_sin EQUAL -1 OR at_cos EQUAL -1)
    message(FATAL_ERROR "PARITY_PERIOD_SINE: ${header} does not define BR_SIN and BR_COS as the pinned commit does")
  endif()
  set(radian "#define BR_PARITY_PERIOD_RADIAN(a) ((br_scalar)((double)(((long)floor((double)(a) * 65536.0 + 0.5)) & 0xffff) * (3.14159265358979323846 / 32768.0)))")
  string(REPLACE "${old_sin}" "/* PARITY_PERIOD_SINE: BRender 1.3.2's FLOAT sine and cosine (modern/parity/period-sine.cmake) */\n${radian}\n#define BR_SIN(a)           ((br_scalar)sin((double)BR_PARITY_PERIOD_RADIAN(a)))" text "${text}")
  string(REPLACE "${old_cos}" "#define BR_COS(a)           ((br_scalar)cos((double)BR_PARITY_PERIOD_RADIAN(a)))" text "${text}")
  file(WRITE "${header}" "${text}")
endfunction()
