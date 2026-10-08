#pragma once

#include <cmath>
#include <cstddef>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

namespace anonsync {

// Dependency-light in-memory JSON value shared by the parser and focused
// document codecs.  Keep this representation free of crypto, SQLite, and the
// public domain model so a schema leaf does not inherit the runtime umbrella.
struct Json final {
    enum class Type { Null, Bool, Number, String, Array, Object } type = Type::Null;
    bool b = false;
    double n = 0.0;
    std::string s;
    std::vector<Json> a;
    std::map<std::string, Json> o;

    [[nodiscard]] bool is_null() const noexcept { return type == Type::Null; }
    [[nodiscard]] bool is_bool() const noexcept { return type == Type::Bool; }
    [[nodiscard]] bool is_number() const noexcept { return type == Type::Number; }
    [[nodiscard]] bool is_string() const noexcept { return type == Type::String; }
    [[nodiscard]] bool is_array() const noexcept { return type == Type::Array; }
    [[nodiscard]] bool is_object() const noexcept { return type == Type::Object; }

    [[nodiscard]] const Json& at(const std::string& key) const {
        static const Json null_json;
        if (!is_object()) return null_json;
        const auto found = o.find(key);
        return found == o.end() ? null_json : found->second;
    }

    [[nodiscard]] const Json& at(std::size_t index) const {
        static const Json null_json;
        if (!is_array() || index >= a.size()) return null_json;
        return a[index];
    }

    [[nodiscard]] std::string str(const std::string& fallback = "") const {
        return is_string() ? s : fallback;
    }

    [[nodiscard]] bool boolean(bool fallback = false) const noexcept {
        return is_bool() ? b : fallback;
    }

    [[nodiscard]] long long integer(long long fallback = 0) const {
        if (!is_number()) return fallback;
        constexpr double kMaximumExactJsonInteger = 9007199254740991.0;
        if (!std::isfinite(n) || std::trunc(n) != n ||
            n < -kMaximumExactJsonInteger || n > kMaximumExactJsonInteger) {
            throw std::runtime_error(
                "JSON number is not an exact interoperable signed integer");
        }
        return static_cast<long long>(n);
    }
};

}  // namespace anonsync
