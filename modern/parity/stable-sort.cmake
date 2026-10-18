# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Zain Dana Harper.
#
# parity_stable_sort(<copy>): in a copy of BRender 1.4's tree, replace
# core/fw/brqsort.c, which calls the C library's qsort, with a stable merge
# sort (modern/parity/brqsort-stable.c), for -DPARITY_STABLE_SORT=ON.
#
# core/v1db/prepmesh.c sums the face normals of each shared vertex in the
# order BrQsort leaves them. The MSVC and glibc qsort order equal keys
# differently, so 1.4's Windows and Linux builds round those sums apart in the
# last bit, and four scenes differ by a pixel. With one stable sort on both,
# the frames are the same bytes. See modern/parity/README.md, "Where the last
# pixels come from".

function(parity_stable_sort copy)
  set(file "${copy}/core/fw/brqsort.c")
  file(READ "${file}" text)
  string(FIND "${text}" "PARITY_STABLE_SORT" done)
  if(NOT done EQUAL -1)
    return()
  endif()
  string(FIND "${text}" "    qsort(basep, nelems, size, comp);" at)
  if(at EQUAL -1)
    message(FATAL_ERROR "PARITY_STABLE_SORT: ${file} does not call qsort as the pinned commit does")
  endif()
  file(READ "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/brqsort-stable.c" stable)
  file(WRITE "${file}" "/* PARITY_STABLE_SORT: replaced by modern/parity/brqsort-stable.c */\n${stable}")
endfunction()
