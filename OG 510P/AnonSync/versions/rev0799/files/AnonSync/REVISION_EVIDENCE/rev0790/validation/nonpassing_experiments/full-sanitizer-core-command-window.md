The full sanitizer target remained incomplete after four separate 300-second command windows.
Each command window reached or resumed first-party compilation; the remaining step is:
ninja: Entering directory `/mnt/data/anonsync_build_rev0790_san'
[1/3] Building CXX object CMakeFiles/anonsync_core_lib.dir/src/sync_domain.cpp.o
[2/3] Linking CXX static library libanonsync_core_lib.a
[3/3] Linking CXX executable anonsync_core

This limitation is not counted as a passing release gate. The extracted exact-value and projection boundaries were fully built and repeated under GCC ASan/UBSan.
