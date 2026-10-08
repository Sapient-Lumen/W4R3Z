# Rev0801 validation commands

The build directories were kept outside the package root.

```bash
cmake -S AnonSync -B /mnt/data/anonsync-rev0801-build-focused -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug -DANONSYNC_USE_BUNDLED_SQLITE=ON \
  -DCMAKE_CXX_FLAGS=-Werror
cmake --build /mnt/data/anonsync-rev0801-build-focused --parallel 4
ctest --test-dir /mnt/data/anonsync-rev0801-build-focused \
  --output-on-failure --parallel 4
```

Focused repetition covered the process incarnation, persistence fork authority,
existing SQLite process authority, snapshot seal, and verification budget
executables. Separate GCC ASan/UBSan, Clang strict conversion/sign-conversion/
shadow, and GCC `-O3 -DNDEBUG -Werror` build directories repeated the same five
proofs five times each.

All registered Python source audits were also executed directly from the source
root. The rev0800 archive was extracted separately and passed to rev0801's
package verifier as an expected-failure negative proof.
