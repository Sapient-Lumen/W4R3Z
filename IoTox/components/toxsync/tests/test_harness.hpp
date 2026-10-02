#pragma once

#include <exception>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace test {
using Function = void (*)();
struct Case { const char* name; Function function; };
inline std::vector<Case>& registry() { static std::vector<Case> value; return value; }
struct Register { Register(const char* name, Function fn) { registry().push_back({name, fn}); } };

inline void require(bool condition, const char* expression, const char* file, int line) {
    if (!condition) throw std::runtime_error(std::string(file) + ':' + std::to_string(line) + ": requirement failed: " + expression);
}

template <typename FunctionType>
void require_throws(FunctionType&& function, const char* file, int line) {
    try { function(); } catch (const std::exception&) { return; }
    throw std::runtime_error(std::string(file) + ':' + std::to_string(line) + ": expected exception");
}
} // namespace test

#define TOXSYNC_TEST(name) \
    static void name(); \
    static ::test::Register name##_registration(#name, &name); \
    static void name()
#define REQUIRE(expression) ::test::require(static_cast<bool>(expression), #expression, __FILE__, __LINE__)
#define REQUIRE_THROWS(expression) ::test::require_throws([&] { static_cast<void>(expression); }, __FILE__, __LINE__)
