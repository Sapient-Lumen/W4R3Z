#include "test_harness.hpp"

#include "iotox/state_store.hpp"

#include <cstdint>
#include <filesystem>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

IOTOX_TEST("state store replaces files atomically with private permissions") {
    const std::filesystem::path directory =
        std::filesystem::temp_directory_path() /
        ("iotox-state-test-" + std::to_string(static_cast<long long>(::getpid())));
    const std::filesystem::path path = directory / "identity.toxsave";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);

    const std::vector<std::uint8_t> first = {1, 2, 3};
    IOTOX_CHECK(iotox::StateStore::write_atomic(path, first).ok());
    auto first_read = iotox::StateStore::read(path);
    IOTOX_CHECK(first_read);
    IOTOX_CHECK(first_read.value() == first);

    const std::vector<std::uint8_t> second = {9, 8, 7, 6, 5};
    IOTOX_CHECK(iotox::StateStore::write_atomic(path, second).ok());
    auto second_read = iotox::StateStore::read(path);
    IOTOX_CHECK(second_read);
    IOTOX_CHECK(second_read.value() == second);

    struct stat metadata {};
    IOTOX_CHECK(::stat(path.c_str(), &metadata) == 0);
    IOTOX_CHECK((metadata.st_mode & 0777) == 0600);
    IOTOX_CHECK(::stat(directory.c_str(), &metadata) == 0);
    IOTOX_CHECK((metadata.st_mode & 0777) == 0700);

    for (const auto &entry : std::filesystem::directory_iterator(directory)) {
        IOTOX_CHECK(entry.path() == path);
    }

    const auto nested = directory / "nested" / "private" / "state";
    IOTOX_CHECK(iotox::StateStore::write_atomic(nested, first).ok());
    IOTOX_CHECK(::stat((directory / "nested").c_str(), &metadata) == 0);
    IOTOX_CHECK((metadata.st_mode & 0777) == 0700);
    IOTOX_CHECK(::stat((directory / "nested" / "private").c_str(),
                       &metadata) == 0);
    IOTOX_CHECK((metadata.st_mode & 0777) == 0700);

    std::filesystem::remove_all(directory, ignored);

    const auto missing = iotox::StateStore::read(path);
    IOTOX_CHECK(!missing);
    IOTOX_CHECK(missing.status().code() == iotox::ErrorCode::not_found);

    const std::filesystem::path blocking_parent = directory / "regular-parent";
    IOTOX_CHECK(iotox::StateStore::write_atomic(blocking_parent, first).ok());
    const auto blocked = iotox::StateStore::write_atomic(blocking_parent / "state", first);
    IOTOX_CHECK(!blocked.ok());
    IOTOX_CHECK(blocked.code() == iotox::ErrorCode::io_error);

    const std::filesystem::path directory_target = directory / "directory-target";
    std::filesystem::create_directory(directory_target);
    const auto rename_refused = iotox::StateStore::write_atomic(directory_target, first);
    IOTOX_CHECK(!rename_refused.ok());
    IOTOX_CHECK(rename_refused.code() == iotox::ErrorCode::io_error);

    std::filesystem::remove_all(directory, ignored);
}
