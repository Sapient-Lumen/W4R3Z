#include "test_harness.hpp"
#include "iotox/update_service.hpp"

#include <charconv>
#include <cstddef>
#include <cstdlib>
#include <exception>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>

namespace {

bool parse_size(std::string_view text, std::size_t &value) {
    if (text.empty()) {
        return false;
    }
    std::size_t parsed = 0U;
    const char *begin = text.data();
    const char *end = begin + text.size();
    const auto result = std::from_chars(begin, end, parsed);
    if (result.ec != std::errc{} || result.ptr != end) {
        return false;
    }
    value = parsed;
    return true;
}

bool set_fixture_path(const char *name, const char *value) {
    return ::setenv(name, value, 1) == 0;
}

}  // namespace

int main(int argc, char **argv) {
    if (argc == 2 &&
        std::string_view(argv[1]) ==
            iotox::update::kInternalUpdateServiceChildArgument) {
        return iotox::update::run_internal_update_service_child();
    }
    std::size_t shard_index = 0U;
    std::size_t shard_count = 1U;
    std::optional<std::string> name_filter;

    for (int index = 1; index < argc; ++index) {
        const std::string_view option(argv[index]);
        const auto require_value = [&]() -> const char * {
            if (index + 1 >= argc) {
                return nullptr;
            }
            ++index;
            return argv[index];
        };

        if (option == "--mock-toxcore") {
            const char *value = require_value();
            if (value == nullptr || !set_fixture_path("IOTOX_TEST_MOCK_TOXCORE", value)) {
                std::cerr << "unable to set IOTOX_TEST_MOCK_TOXCORE\n";
                return EXIT_FAILURE;
            }
        } else if (option == "--mock-argon2") {
            const char *value = require_value();
            if (value == nullptr || !set_fixture_path("IOTOX_TEST_MOCK_ARGON2", value)) {
                std::cerr << "unable to set IOTOX_TEST_MOCK_ARGON2\n";
                return EXIT_FAILURE;
            }
        } else if (option == "--wordlist") {
            const char *value = require_value();
            if (value == nullptr || !set_fixture_path("IOTOX_TEST_RECALL_WORDLIST", value)) {
                std::cerr << "unable to set IOTOX_TEST_RECALL_WORDLIST\n";
                return EXIT_FAILURE;
            }
        } else if (option == "--shard-index") {
            const char *value = require_value();
            if (value == nullptr || !parse_size(value, shard_index)) {
                std::cerr << "invalid --shard-index\n";
                return EXIT_FAILURE;
            }
        } else if (option == "--shard-count") {
            const char *value = require_value();
            if (value == nullptr || !parse_size(value, shard_count) || shard_count == 0U) {
                std::cerr << "invalid --shard-count\n";
                return EXIT_FAILURE;
            }
        } else if (option == "--filter") {
            const char *value = require_value();
            if (value == nullptr || std::string_view(value).empty()) {
                std::cerr << "invalid --filter\n";
                return EXIT_FAILURE;
            }
            name_filter = value;
        } else {
            std::cerr << "unknown test option: " << option << '\n';
            return EXIT_FAILURE;
        }
    }

    if (shard_index >= shard_count) {
        std::cerr << "test shard index must be smaller than shard count\n";
        return EXIT_FAILURE;
    }

    int failures = 0;
    std::size_t selected = 0U;
    const auto &tests = iotox::test::registry();
    for (std::size_t index = 0U; index < tests.size(); ++index) {
        if ((index % shard_count) != shard_index) {
            continue;
        }
        const auto &test = tests[index];
        if (name_filter && test.name.find(*name_filter) == std::string::npos) {
            continue;
        }
        ++selected;
        try {
            test.function();
            std::cout << "PASS " << test.name << '\n';
        } catch (const std::exception &exception) {
            ++failures;
            std::cerr << "FAIL " << test.name << ": " << exception.what() << '\n';
        } catch (...) {
            ++failures;
            std::cerr << "FAIL " << test.name << ": unknown exception\n";
        }
    }

    std::cout << "tests=" << tests.size() << " selected=" << selected
              << " shard=" << shard_index << '/' << shard_count
              << " failures=" << failures << '\n';
    return failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
