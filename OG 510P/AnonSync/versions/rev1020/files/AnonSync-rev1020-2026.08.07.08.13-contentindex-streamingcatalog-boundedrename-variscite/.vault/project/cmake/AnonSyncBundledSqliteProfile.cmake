# Single reviewed trust contract for the bundled SQLite build.
#
# CMake consumes these values to select and hash the vendored files. The C++
# runtime gate consumes a generated header from the same values and rejects a
# linked runtime whose version or SQLITE_SOURCE_ID diverges. Keep dependency
# updates isolated: replace the complete upstream bundle, update this record,
# run the independent profile verifier, then run all SQLite/VFS/process lanes.
set(ANONSYNC_BUNDLED_SQLITE_VERSION "3.53.3")
set(ANONSYNC_BUNDLED_SQLITE_VERSION_NUMBER 3053003)
set(ANONSYNC_BUNDLED_SQLITE_RELEASE_DATE "2026-06-26")
set(ANONSYNC_BUNDLED_SQLITE_SOURCE_ID
  "2026-06-26 20:14:12 d4c0e51e4aeb96955b99185ab9cde75c339e2c29c3f3f12428d364a10d782c62")
set(ANONSYNC_BUNDLED_SQLITE_AMALGAMATION_ARCHIVE
  "sqlite-amalgamation-3530300.zip")
set(ANONSYNC_BUNDLED_SQLITE_AMALGAMATION_ARCHIVE_SHA3_256
  "d45c688a8cb23f68611a894a756a12d7eb6ab6e9e2468ca70adbeab3808b5ab9")
# Closed flat inventory of every retained file under the selected vendor
# directory. Native configure rejects additions, deletions, directories, and
# symlink substitutions; the independent verifier additionally requires every
# retained entry to be a regular file.
set(ANONSYNC_BUNDLED_SQLITE_RETAINED_FILES
  "LICENSE.md;UPSTREAM-PROVENANCE.md;sqlite3.c;sqlite3.h;sqlite3ext.h")
set(ANONSYNC_BUNDLED_SQLITE_C_SHA256
  "87497ab605bedd0dbee27a209c1eeff8c89b229b13f921a7efdbb81a13f779fd")
set(ANONSYNC_BUNDLED_SQLITE_C_SHA3_256
  "28e484abdaa43630e34040ef6ed92be973a1ad54107803d8af5145b889c23ed7")
set(ANONSYNC_BUNDLED_SQLITE_H_SHA256
  "4ff81af4849acabc76fc8349abb926814395072617ca18e08800abf734ab7612")
set(ANONSYNC_BUNDLED_SQLITE_EXT_H_SHA256
  "ac9645e5c9ff0cf176efdd6e75cb5e98f46295d38e02db5c4d208826a39ab4be")
set(ANONSYNC_BUNDLED_SQLITE_LICENSE_SHA256
  "ee6af51062b30d532991face5164136ae6f84e265ecf8abe89dc69dac45ca1e7")
# Filled after UPSTREAM-PROVENANCE.md is changed. The configure gate and the
# independent verifier both require an exact value; an empty value is invalid.
set(ANONSYNC_BUNDLED_SQLITE_PROVENANCE_SHA256
  "9c170cfb5aec090860dd2ee2c3439c70cff953d6e1633eee113443cc46bf5121")
