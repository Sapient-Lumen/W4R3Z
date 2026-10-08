# Rev1015 authority incidents

Several orphaned rev1014/rev1015 validators recreated or erased mutable build directories. One CMake cache was moved after configuration and therefore retained an obsolete absolute source/build prefix. Those interrupted processes and path-contaminated cache operations are excluded. Final GCC and Clang results are bound to an exact final Git tree; the moved GCC cache was used only after its original absolute prefix was restored as a local validation symlink.

The protected project directory also inherited a setgid bit from a shared validation location. Exact wrapper reconstruction detected the single mode difference. The directory was restored to the sealed parent mode 0755 and complete path/byte/type/mode reconstruction was rerun successfully.
