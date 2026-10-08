# Toolchain and proof limits

The full GCC Debug production build and 56-test CTest suite completed against
the bundled SQLite 3.53.3 amalgamation. The focused Clang lane applies strict
conversion warnings to first-party C++; the third-party C amalgamation is not
compiled with Clang `-Werror` because upstream currently has an unused formal
parameter under that profile.

The GCC optimized and sanitizer lanes compile the path-security owner, seal
owner, and focused test directly, then link the reviewed bundled SQLite archive
from the full Debug build. The sanitizer lane intentionally leaves the
amalgamation uninstrumented. A fresh `-O3` amalgamation compilation did not
finish inside the command window, so no full optimized-build completion is
claimed.

Tests prove deterministic rejection and byte/VFS identity in this Linux/POSIX
cloud container. They do not establish equivalent behavior on an untested VFS,
filesystem, operating system, or hostile privileged kernel.
