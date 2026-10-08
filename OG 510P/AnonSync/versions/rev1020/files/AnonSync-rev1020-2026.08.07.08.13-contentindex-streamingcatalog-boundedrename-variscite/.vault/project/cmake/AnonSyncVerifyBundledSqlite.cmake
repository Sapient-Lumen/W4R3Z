# Native verification for AnonSync's closed bundled-SQLite profile.
#
# This module is consumed twice: during ordinary project configuration and by a
# phony build dependency that re-runs the same checks before the amalgamation
# target can build. Keeping the verifier in script-compatible CMake closes the
# configure/build mutation window without making the native build depend on
# Python or on a retained build tree.

function(anonsync_verify_bundled_sqlite_profile source_root)
  if(NOT IS_ABSOLUTE "${source_root}")
    message(FATAL_ERROR
      "Bundled SQLite verification requires an absolute source root: ${source_root}")
  endif()

  foreach(profile_variable IN ITEMS
      ANONSYNC_BUNDLED_SQLITE_VERSION
      ANONSYNC_BUNDLED_SQLITE_VERSION_NUMBER
      ANONSYNC_BUNDLED_SQLITE_RELEASE_DATE
      ANONSYNC_BUNDLED_SQLITE_SOURCE_ID
      ANONSYNC_BUNDLED_SQLITE_AMALGAMATION_ARCHIVE
      ANONSYNC_BUNDLED_SQLITE_AMALGAMATION_ARCHIVE_SHA3_256
      ANONSYNC_BUNDLED_SQLITE_RETAINED_FILES
      ANONSYNC_BUNDLED_SQLITE_C_SHA256
      ANONSYNC_BUNDLED_SQLITE_C_SHA3_256
      ANONSYNC_BUNDLED_SQLITE_H_SHA256
      ANONSYNC_BUNDLED_SQLITE_EXT_H_SHA256
      ANONSYNC_BUNDLED_SQLITE_LICENSE_SHA256
      ANONSYNC_BUNDLED_SQLITE_PROVENANCE_SHA256)
    if(NOT DEFINED ${profile_variable} OR "${${profile_variable}}" STREQUAL "")
      message(FATAL_ERROR
        "Bundled SQLite profile variable is missing or empty: ${profile_variable}")
    endif()
  endforeach()

  if(NOT ANONSYNC_BUNDLED_SQLITE_VERSION MATCHES
      "^[0-9]+[.][0-9]+[.][0-9]+$")
    message(FATAL_ERROR
      "Bundled SQLite profile version is not a canonical dotted release: "
      "${ANONSYNC_BUNDLED_SQLITE_VERSION}")
  endif()
  if(NOT "${ANONSYNC_BUNDLED_SQLITE_VERSION_NUMBER}" MATCHES "^[0-9]+$")
    message(FATAL_ERROR
      "Bundled SQLite profile version number is not decimal: "
      "${ANONSYNC_BUNDLED_SQLITE_VERSION_NUMBER}")
  endif()
  string(REPLACE "." ";" version_parts
    "${ANONSYNC_BUNDLED_SQLITE_VERSION}")
  list(GET version_parts 0 version_major)
  list(GET version_parts 1 version_minor)
  list(GET version_parts 2 version_patch)
  math(EXPR expected_version_number
    "${version_major} * 1000000 + ${version_minor} * 1000 + ${version_patch}")
  if(NOT "${ANONSYNC_BUNDLED_SQLITE_VERSION_NUMBER}" STREQUAL
      "${expected_version_number}")
    message(FATAL_ERROR
      "Bundled SQLite profile numeric version does not encode its dotted "
      "release: expected ${expected_version_number}, observed "
      "${ANONSYNC_BUNDLED_SQLITE_VERSION_NUMBER}")
  endif()
  if(NOT "${ANONSYNC_BUNDLED_SQLITE_RELEASE_DATE}" MATCHES
      "^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$")
    message(FATAL_ERROR
      "Bundled SQLite profile release date is not canonical ISO text: "
      "${ANONSYNC_BUNDLED_SQLITE_RELEASE_DATE}")
  endif()
  string(LENGTH "${ANONSYNC_BUNDLED_SQLITE_SOURCE_ID}" source_id_length)
  if(NOT source_id_length EQUAL 84 OR
     NOT "${ANONSYNC_BUNDLED_SQLITE_SOURCE_ID}" MATCHES
       "^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9] [0-9a-f]+$")
    message(FATAL_ERROR
      "Bundled SQLite profile source ID is not canonical timestamp plus "
      "64-character lowercase hexadecimal identity: "
      "${ANONSYNC_BUNDLED_SQLITE_SOURCE_ID}")
  endif()
  math(EXPR expected_archive_code
    "${version_major} * 1000000 + ${version_minor} * 10000 + ${version_patch} * 100")
  set(expected_archive "sqlite-amalgamation-${expected_archive_code}.zip")
  if(NOT "${ANONSYNC_BUNDLED_SQLITE_AMALGAMATION_ARCHIVE}" STREQUAL
      "${expected_archive}")
    message(FATAL_ERROR
      "Bundled SQLite profile archive name does not encode its dotted release: "
      "expected ${expected_archive}, observed "
      "${ANONSYNC_BUNDLED_SQLITE_AMALGAMATION_ARCHIVE}")
  endif()

  set(vendor_dir
    "${source_root}/third_party/sqlite-${ANONSYNC_BUNDLED_SQLITE_VERSION}")
  if(IS_SYMLINK "${vendor_dir}" OR NOT IS_DIRECTORY "${vendor_dir}")
    message(FATAL_ERROR
      "Bundled SQLite vendor directory is missing, non-directory, or a symlink: "
      "${vendor_dir}")
  endif()

  set(expected_files ${ANONSYNC_BUNDLED_SQLITE_RETAINED_FILES})
  list(LENGTH expected_files expected_file_count)
  set(unique_files ${expected_files})
  list(REMOVE_DUPLICATES unique_files)
  list(LENGTH unique_files unique_file_count)
  if(NOT expected_file_count EQUAL unique_file_count)
    message(FATAL_ERROR
      "Bundled SQLite profile retained-file inventory contains duplicates: "
      "${ANONSYNC_BUNDLED_SQLITE_RETAINED_FILES}")
  endif()
  foreach(relative_path IN LISTS expected_files)
    if(NOT relative_path MATCHES "^[A-Za-z0-9][A-Za-z0-9._-]*$")
      message(FATAL_ERROR
        "Bundled SQLite profile retained-file path is not a flat safe basename: "
        "${relative_path}")
    endif()
  endforeach()
  list(SORT expected_files)

  file(GLOB_RECURSE observed_entries
    LIST_DIRECTORIES true
    RELATIVE "${vendor_dir}"
    "${vendor_dir}/*")
  list(SORT observed_entries)
  if(NOT "${observed_entries}" STREQUAL "${expected_files}")
    message(FATAL_ERROR
      "Bundled SQLite retained-file inventory mismatch: expected "
      "[${expected_files}], observed [${observed_entries}]")
  endif()

  foreach(relative_path IN LISTS expected_files)
    set(absolute_path "${vendor_dir}/${relative_path}")
    if(IS_SYMLINK "${absolute_path}")
      message(FATAL_ERROR
        "Bundled SQLite retained file must not be a symlink: ${absolute_path}")
    endif()
    if(NOT EXISTS "${absolute_path}" OR IS_DIRECTORY "${absolute_path}")
      message(FATAL_ERROR
        "Bundled SQLite retained entry must be a file: ${absolute_path}")
    endif()
  endforeach()

  foreach(digest_variable IN ITEMS
      ANONSYNC_BUNDLED_SQLITE_AMALGAMATION_ARCHIVE_SHA3_256
      ANONSYNC_BUNDLED_SQLITE_C_SHA256
      ANONSYNC_BUNDLED_SQLITE_C_SHA3_256
      ANONSYNC_BUNDLED_SQLITE_H_SHA256
      ANONSYNC_BUNDLED_SQLITE_EXT_H_SHA256
      ANONSYNC_BUNDLED_SQLITE_LICENSE_SHA256
      ANONSYNC_BUNDLED_SQLITE_PROVENANCE_SHA256)
    string(LENGTH "${${digest_variable}}" digest_length)
    if(NOT digest_length EQUAL 64 OR
       NOT "${${digest_variable}}" MATCHES "^[0-9a-f]+$")
      message(FATAL_ERROR
        "Bundled SQLite profile digest must be 64 lowercase hexadecimal "
        "characters: ${digest_variable}=${${digest_variable}}")
    endif()
  endforeach()

  set(hash_specs
    "SHA256|sqlite3.c|${ANONSYNC_BUNDLED_SQLITE_C_SHA256}"
    "SHA3_256|sqlite3.c|${ANONSYNC_BUNDLED_SQLITE_C_SHA3_256}"
    "SHA256|sqlite3.h|${ANONSYNC_BUNDLED_SQLITE_H_SHA256}"
    "SHA256|sqlite3ext.h|${ANONSYNC_BUNDLED_SQLITE_EXT_H_SHA256}"
    "SHA256|LICENSE.md|${ANONSYNC_BUNDLED_SQLITE_LICENSE_SHA256}"
    "SHA256|UPSTREAM-PROVENANCE.md|${ANONSYNC_BUNDLED_SQLITE_PROVENANCE_SHA256}")
  foreach(hash_spec IN LISTS hash_specs)
    string(REPLACE "|" ";" hash_fields "${hash_spec}")
    list(GET hash_fields 0 algorithm)
    list(GET hash_fields 1 relative_path)
    list(GET hash_fields 2 expected)
    list(FIND expected_files "${relative_path}" retained_file_index)
    if(retained_file_index EQUAL -1)
      message(FATAL_ERROR
        "Bundled SQLite hash gate references a file outside the closed profile: "
        "${relative_path}")
    endif()
    set(absolute_path "${vendor_dir}/${relative_path}")
    file(${algorithm} "${absolute_path}" observed)
    if(NOT "${observed}" STREQUAL "${expected}")
      message(FATAL_ERROR
        "Bundled SQLite ${ANONSYNC_BUNDLED_SQLITE_VERSION} ${relative_path} "
        "${algorithm} mismatch: expected ${expected}, observed ${observed}")
    endif()
  endforeach()

  set(ANONSYNC_BUNDLED_SQLITE_VERIFIED_DIR "${vendor_dir}" PARENT_SCOPE)
endfunction()

function(anonsync_add_bundled_sqlite_build_gate target_name source_root)
  if(NOT TARGET "${target_name}")
    message(FATAL_ERROR
      "Cannot attach bundled SQLite build gate to missing target: ${target_name}")
  endif()
  set(gate_target "${target_name}_bundled_sqlite_profile_gate")
  if(TARGET "${gate_target}")
    message(FATAL_ERROR
      "Bundled SQLite build gate target already exists: ${gate_target}")
  endif()
  add_custom_target("${gate_target}"
    COMMAND "${CMAKE_COMMAND}"
      "-DANONSYNC_SOURCE_ROOT:PATH=${source_root}"
      -P "${source_root}/cmake/AnonSyncVerifyBundledSqliteAtBuild.cmake"
    COMMENT "Re-attesting closed bundled SQLite profile before compilation"
    VERBATIM)
  add_dependencies("${target_name}" "${gate_target}")
endfunction()
