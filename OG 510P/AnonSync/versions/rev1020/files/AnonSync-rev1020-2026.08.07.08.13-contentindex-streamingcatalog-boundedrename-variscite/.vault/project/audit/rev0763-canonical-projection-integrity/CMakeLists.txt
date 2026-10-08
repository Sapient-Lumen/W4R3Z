cmake_minimum_required(VERSION 3.16)
project(anonsync_rev0763_projection_guard LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
find_package(SQLite3 REQUIRED)
add_library(canonical_projection_verifier
  ../../src/persistence/canonical_projection_verifier.cpp
  ../../src/persistence/sqlite_projection_decoder.cpp)
target_include_directories(canonical_projection_verifier PUBLIC ../../src/persistence)
target_link_libraries(canonical_projection_verifier PUBLIC SQLite::SQLite3)
target_compile_options(canonical_projection_verifier PRIVATE -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion)
add_executable(canonical_projection_verifier_tests
  ../../tests/persistence/canonical_projection_verifier_tests.cpp)
target_link_libraries(canonical_projection_verifier_tests PRIVATE canonical_projection_verifier)
target_compile_options(canonical_projection_verifier_tests PRIVATE -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion)
enable_testing()
add_test(NAME canonical_projection_verifier_tests COMMAND canonical_projection_verifier_tests)

add_executable(sqlite_projection_decoder_tests
  ../../tests/persistence/sqlite_projection_decoder_tests.cpp)
target_link_libraries(sqlite_projection_decoder_tests PRIVATE canonical_projection_verifier)
target_compile_options(sqlite_projection_decoder_tests PRIVATE -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion)
add_test(NAME sqlite_projection_decoder_tests COMMAND sqlite_projection_decoder_tests)
