cmake_minimum_required(VERSION 3.20)

project(bzip4 VERSION 0.0.1 LANGUAGES CXX)

option(BZIP4_BUILD_TESTS "Build bzip4 C++ tests" ON)
option(BZIP4_BUILD_TOOLS "Build corpus benchmark and redundancy probe tools" ON)
option(BZIP4_ENABLE_SANITIZERS "Enable AddressSanitizer and UndefinedBehaviorSanitizer" OFF)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)
find_package(Threads REQUIRED)

add_library(bzip4_codec STATIC
    src/libbz3.cpp
    src/codec.cpp
)
add_library(bzip4::codec ALIAS bzip4_codec)

target_include_directories(bzip4_codec
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)
target_compile_definitions(bzip4_codec PRIVATE VERSION="1.5.3" PTHREAD)
target_link_libraries(bzip4_codec PUBLIC Threads::Threads)
set_target_properties(bzip4_codec PROPERTIES
    OUTPUT_NAME bzip4
    EXPORT_NAME codec
    POSITION_INDEPENDENT_CODE ON
)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(bzip4_codec PRIVATE
        -Wall -Wextra -Wpedantic
        -Wno-sign-compare
        -Wno-unused-function
    )
endif()

add_executable(bzip4 src/main.cpp)
target_include_directories(bzip4 PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)
target_compile_definitions(bzip4 PRIVATE VERSION="1.5.3" PTHREAD)
target_link_libraries(bzip4 PRIVATE bzip4_codec)
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(bzip4 PRIVATE -Wall -Wextra -Wpedantic -Wno-sign-compare)
endif()

if(BZIP4_ENABLE_SANITIZERS)
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        foreach(target bzip4_codec bzip4)
            target_compile_options(${target} PRIVATE -fno-omit-frame-pointer -fsanitize=address,undefined)
            target_link_options(${target} PRIVATE -fno-omit-frame-pointer -fsanitize=address,undefined)
        endforeach()
    else()
        message(FATAL_ERROR "BZIP4_ENABLE_SANITIZERS currently supports GCC and Clang")
    endif()
endif()

install(TARGETS bzip4 bzip4_codec
    EXPORT bzip4Targets
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(EXPORT bzip4Targets
    FILE bzip4Targets.cmake
    NAMESPACE bzip4::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/bzip4
)

configure_package_config_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/bzip4Config.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/bzip4Config.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/bzip4
)
write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/bzip4ConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)
install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/bzip4Config.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/bzip4ConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/bzip4
)

if(BZIP4_BUILD_TOOLS)
    add_executable(bzip4_bench tools/corpus_bench.cpp)
    target_link_libraries(bzip4_bench PRIVATE bzip4_codec)

    add_executable(bzip4_probe tools/corpus_probe.cpp)

    install(TARGETS bzip4_bench bzip4_probe
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    )

    if(BZIP4_ENABLE_SANITIZERS AND CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        foreach(target bzip4_bench bzip4_probe)
            target_compile_options(${target} PRIVATE -fno-omit-frame-pointer -fsanitize=address,undefined)
            target_link_options(${target} PRIVATE -fno-omit-frame-pointer -fsanitize=address,undefined)
        endforeach()
    endif()
endif()

if(BZIP4_BUILD_TESTS)
    include(CTest)
    enable_testing()

    add_executable(bzip4_cpp_api_test tests/cpp_api_roundtrip.cpp)
    target_link_libraries(bzip4_cpp_api_test PRIVATE bzip4_codec)
    if(BZIP4_ENABLE_SANITIZERS AND CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        target_compile_options(bzip4_cpp_api_test PRIVATE -fno-omit-frame-pointer -fsanitize=address,undefined)
        target_link_options(bzip4_cpp_api_test PRIVATE -fno-omit-frame-pointer -fsanitize=address,undefined)
    endif()
    add_test(NAME cpp_api_roundtrip COMMAND bzip4_cpp_api_test)

    add_executable(bzip4_cli_test tests/cli_roundtrip.cpp)
    if(BZIP4_ENABLE_SANITIZERS AND CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        target_compile_options(bzip4_cli_test PRIVATE -fno-omit-frame-pointer -fsanitize=address,undefined)
        target_link_options(bzip4_cli_test PRIVATE -fno-omit-frame-pointer -fsanitize=address,undefined)
    endif()
    add_test(NAME cli_roundtrip COMMAND bzip4_cli_test $<TARGET_FILE:bzip4>)
endif()
