#include "test_harness.hpp"

#include <algorithm>

int main() {
    auto& tests = test::registry();
    std::sort(tests.begin(), tests.end(), [](const auto& left, const auto& right) {
        return std::string_view(left.name) < std::string_view(right.name);
    });
    std::size_t failures{};
    for (const auto& test_case : tests) {
        try {
            test_case.function();
            std::cout << "PASS " << test_case.name << '\n';
        } catch (const std::exception& error) {
            ++failures;
            std::cerr << "FAIL " << test_case.name << ": " << error.what() << '\n';
        }
    }
    std::cout << "tests=" << tests.size() << " failures=" << failures << '\n';
    return failures == 0U ? 0 : 1;
}
