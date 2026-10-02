#pragma once

#include <functional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace iotox::test {

using TestFunction = void (*)();

struct TestCase {
    std::string name;
    TestFunction function;
};

inline std::vector<TestCase> &registry() {
    static std::vector<TestCase> tests;
    return tests;
}

class Registrar {
  public:
    Registrar(std::string name, TestFunction function) {
        registry().push_back({std::move(name), function});
    }
};

[[noreturn]] inline void fail(
    const char *expression, const char *file, int line,
    const std::string &detail = {}) {
    std::ostringstream message;
    message << file << ':' << line << ": check failed: " << expression;
    if (!detail.empty()) {
        message << " (" << detail << ')';
    }
    throw std::runtime_error(message.str());
}

}  // namespace iotox::test

#define IOTOX_TEST_JOIN_INNER(a, b) a##b
#define IOTOX_TEST_JOIN(a, b) IOTOX_TEST_JOIN_INNER(a, b)
#define IOTOX_TEST(name)                                                              \
    static void IOTOX_TEST_JOIN(iotox_test_function_, __LINE__)();                    \
    static ::iotox::test::Registrar IOTOX_TEST_JOIN(iotox_test_registrar_, __LINE__)( \
        name, &IOTOX_TEST_JOIN(iotox_test_function_, __LINE__));                      \
    static void IOTOX_TEST_JOIN(iotox_test_function_, __LINE__)()

#define IOTOX_CHECK(expression)                                                     \
    do {                                                                            \
        if (!(expression)) {                                                        \
            ::iotox::test::fail(#expression, __FILE__, __LINE__);                   \
        }                                                                           \
    } while (false)

#define IOTOX_CHECK_MSG(expression, detail)                                         \
    do {                                                                            \
        if (!(expression)) {                                                        \
            ::iotox::test::fail(#expression, __FILE__, __LINE__, (detail));         \
        }                                                                           \
    } while (false)
