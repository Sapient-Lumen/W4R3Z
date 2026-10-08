cmake_minimum_required(VERSION 3.20)

if(NOT DEFINED ANONSYNC_SOURCE_ROOT OR "${ANONSYNC_SOURCE_ROOT}" STREQUAL "")
  message(FATAL_ERROR "ANONSYNC_SOURCE_ROOT is required")
endif()
get_filename_component(ANONSYNC_SOURCE_ROOT
  "${ANONSYNC_SOURCE_ROOT}" REALPATH BASE_DIR "${CMAKE_CURRENT_LIST_DIR}")

include("${ANONSYNC_SOURCE_ROOT}/cmake/AnonSyncBundledSqliteProfile.cmake")
include("${ANONSYNC_SOURCE_ROOT}/cmake/AnonSyncVerifyBundledSqlite.cmake")
anonsync_verify_bundled_sqlite_profile("${ANONSYNC_SOURCE_ROOT}")
message(STATUS
  "Build-time bundled SQLite ${ANONSYNC_BUNDLED_SQLITE_VERSION} profile attestation passed")
