cmake_minimum_required(VERSION 3.20)
project(iotox_toxcore_provider_fixture LANGUAGES C)

if(NOT DEFINED TOXCORE_SOURCE_DIR OR
   NOT EXISTS "${TOXCORE_SOURCE_DIR}/CMakeLists.txt")
    message(FATAL_ERROR "TOXCORE_SOURCE_DIR must name an extracted c-toxcore tree")
endif()

find_package(PkgConfig REQUIRED)
pkg_check_modules(SODIUM REQUIRED IMPORTED_TARGET libsodium)
set(BUILD_TOXAV OFF CACHE BOOL "" FORCE)
set(MUST_BUILD_TOXAV OFF CACHE BOOL "" FORCE)
set(BOOTSTRAP_DAEMON OFF CACHE BOOL "" FORCE)
set(DHT_BOOTSTRAP OFF CACHE BOOL "" FORCE)
set(BUILD_FUN_UTILS OFF CACHE BOOL "" FORCE)
set(BUILD_FUZZ_TESTS OFF CACHE BOOL "" FORCE)
set(BUILD_MISC_TESTS OFF CACHE BOOL "" FORCE)
set(AUTOTEST OFF CACHE BOOL "" FORCE)
set(UNITTEST OFF CACHE BOOL "" FORCE)
set(ENABLE_SHARED OFF CACHE BOOL "" FORCE)
set(ENABLE_STATIC ON CACHE BOOL "" FORCE)
add_subdirectory("${TOXCORE_SOURCE_DIR}" toxcore-build EXCLUDE_FROM_ALL)

add_executable(iotox-toxcore-provider-fixture fixture.c)
target_compile_features(iotox-toxcore-provider-fixture PRIVATE c_std_11)
target_compile_options(iotox-toxcore-provider-fixture PRIVATE
    -Wall -Wextra -Wpedantic -Werror)
target_include_directories(iotox-toxcore-provider-fixture PRIVATE
    "${TOXCORE_SOURCE_DIR}")
target_link_libraries(iotox-toxcore-provider-fixture PRIVATE
    toxcore_static PkgConfig::SODIUM)
install(TARGETS iotox-toxcore-provider-fixture RUNTIME DESTINATION bin)
