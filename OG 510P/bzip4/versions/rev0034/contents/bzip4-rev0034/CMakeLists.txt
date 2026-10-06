cmake_minimum_required(VERSION 3.20)
project(bzip4 VERSION 0.34.0 LANGUAGES C CXX)

include(CTest)
include(CheckIPOSupported)
find_package(Threads REQUIRED)

option(BZIP4_ENABLE_SANITIZERS "Enable AddressSanitizer and UndefinedBehaviorSanitizer" OFF)
option(BZIP4_WARNINGS_AS_ERRORS "Treat project warnings as errors" ON)
option(BZIP4_ENABLE_IPO "Enable supported interprocedural optimization for production targets" OFF)
option(BZIP4_POISON_CODEC_WORKSPACE
    "Fill codec scratch storage before each BWT operation to prove overwrite contracts" OFF)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

if(BZIP4_ENABLE_SANITIZERS)
    if(NOT CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        message(FATAL_ERROR "Sanitizer preset currently supports GCC and Clang")
    endif()
    add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer)
    add_link_options(-fsanitize=address,undefined -fno-omit-frame-pointer)
endif()

function(bzip4_project_warnings target)
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        target_compile_options(${target} PRIVATE
            -Wall -Wextra -Wpedantic -Wshadow -Wconversion -Wsign-conversion
            -Wformat=2 -Wnull-dereference -Wdouble-promotion)
        if(BZIP4_WARNINGS_AS_ERRORS)
            target_compile_options(${target} PRIVATE -Werror)
        endif()
    endif()
endfunction()

add_library(bzip4_codec_core STATIC
    src/frame_envelope.cpp
    src/libbz3.cpp)
target_include_directories(bzip4_codec_core
    PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include
    PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_definitions(bzip4_codec_core PRIVATE VERSION="1.5.3-bzip4-cpp20-rev0034")
if(BZIP4_POISON_CODEC_WORKSPACE)
    target_compile_definitions(bzip4_codec_core PRIVATE BZIP4_POISON_CODEC_WORKSPACE=1)
endif()
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(bzip4_codec_core PRIVATE
        -Wall -Wextra -Wpedantic -Werror
        -Wno-sign-conversion -Wno-conversion -Wno-shadow -Wno-unused-function)
endif()

add_library(bzip4 STATIC
    src/activation.cpp
    src/atomic_file.cpp
    src/codec.cpp
    src/frame_source.cpp
    src/parallel_codec.cpp
    src/pinned_file.cpp
    src/profile.cpp
    src/release_audit.cpp
    src/resource_plan.cpp
    src/sha256.cpp
    src/zip_preflight.cpp)
target_include_directories(bzip4 PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(bzip4 PUBLIC bzip4_codec_core Threads::Threads)
bzip4_project_warnings(bzip4)

if(BZIP4_ENABLE_IPO)
    check_ipo_supported(RESULT BZIP4_IPO_SUPPORTED OUTPUT BZIP4_IPO_ERROR LANGUAGES C CXX)
    if(NOT BZIP4_IPO_SUPPORTED)
        message(FATAL_ERROR "BZIP4_ENABLE_IPO requested but unsupported: ${BZIP4_IPO_ERROR}")
    endif()
    set_property(TARGET bzip4_codec_core bzip4 PROPERTY INTERPROCEDURAL_OPTIMIZATION TRUE)
endif()

foreach(tool IN ITEMS codec cube_preflight release_audit activation_probe)
    add_executable(bzip4_${tool} tools/bzip4_${tool}.cpp)
    target_link_libraries(bzip4_${tool} PRIVATE bzip4)
    bzip4_project_warnings(bzip4_${tool})
    if(BZIP4_ENABLE_IPO)
        set_property(TARGET bzip4_${tool} PROPERTY INTERPROCEDURAL_OPTIMIZATION TRUE)
    endif()
endforeach()

if(BUILD_TESTING)
    add_library(bzip3_upstream_oracle STATIC upstream/bzip3-1.5.3-53984ef/src/libbz3.c)
    target_include_directories(bzip3_upstream_oracle PRIVATE upstream/bzip3-1.5.3-53984ef/include)
    target_compile_definitions(bzip3_upstream_oracle PRIVATE
        VERSION="1.5.3-oracle-53984ef"
        bz3_version=oracle_bz3_version
        bz3_last_error=oracle_bz3_last_error
        bz3_strerror=oracle_bz3_strerror
        bz3_new=oracle_bz3_new
        bz3_free=oracle_bz3_free
        bz3_bound=oracle_bz3_bound
        bz3_compress=oracle_bz3_compress
        bz3_decompress=oracle_bz3_decompress
        bz3_min_memory_needed=oracle_bz3_min_memory_needed
        bz3_encode_block=oracle_bz3_encode_block
        bz3_decode_block=oracle_bz3_decode_block
        bz3_encode_blocks=oracle_bz3_encode_blocks
        bz3_decode_blocks=oracle_bz3_decode_blocks
        bz3_orig_size_sufficient_for_decode=oracle_bz3_orig_size_sufficient_for_decode)
    if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
        target_compile_options(bzip3_upstream_oracle PRIVATE
            -Wno-unused-function
            $<$<BOOL:${BZIP4_ENABLE_SANITIZERS}>:-fno-sanitize=undefined>)
    endif()

    add_executable(bzip4_tests tests/test_main.cpp)
    target_include_directories(bzip4_tests PRIVATE tests src)
    target_link_libraries(bzip4_tests PRIVATE bzip4 bzip3_upstream_oracle)
    bzip4_project_warnings(bzip4_tests)
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        # Keep the very large assertion harness cheap to compile. Production
        # libraries and tools retain the selected build-type optimization.
        target_compile_options(bzip4_tests PRIVATE -O0)
    endif()
    add_test(NAME bzip4_tests COMMAND bzip4_tests)
endif()
