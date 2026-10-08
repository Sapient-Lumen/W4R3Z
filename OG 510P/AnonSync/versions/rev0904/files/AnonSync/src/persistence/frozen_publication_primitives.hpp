#pragma once

#include <array>
#include <charconv>
#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>

namespace anonsync::persistence::publication_detail {

// Small dependency-free primitives shared by exact signed-publication owners.
// They deliberately avoid streams: security-relevant decimal, hexadecimal,
// framing, and JSON bytes must not inherit the process-global C++ locale.
class BoundedMachineText final {
public:
    explicit BoundedMachineText(
        std::size_t maximum_bytes,
        std::string label = "publication machine text")
        : maximum_bytes_(maximum_bytes), label_(std::move(label)) {
        value_.reserve(maximum_bytes_ < 4096 ? maximum_bytes_ : 4096);
    }

    void append(std::string_view text) {
        if (value_.size() > maximum_bytes_ ||
            text.size() > maximum_bytes_ - value_.size()) {
            throw std::runtime_error(label_ + " exceeds byte budget");
        }
        value_.append(text);
    }

    void append(char c) {
        if (value_.size() >= maximum_bytes_) {
            throw std::runtime_error(label_ + " exceeds byte budget");
        }
        value_.push_back(c);
    }

    template <typename Integer>
    void append_decimal(Integer value) {
        std::array<char, 32> buffer{};
        const auto result =
            std::to_chars(buffer.data(), buffer.data() + buffer.size(), value);
        if (result.ec != std::errc{}) {
            throw std::runtime_error(label_ + " integer formatting failed");
        }
        append(std::string_view(
            buffer.data(),
            static_cast<std::size_t>(result.ptr - buffer.data())));
    }

    [[nodiscard]] std::string finish() && { return std::move(value_); }

private:
    std::size_t maximum_bytes_;
    std::string label_;
    std::string value_;
};

inline bool is_lower_hex_sha256(std::string_view value) noexcept {
    if (value.size() != 64) return false;
    for (const char c : value) {
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) {
            return false;
        }
    }
    return true;
}

inline bool is_sha256_or_genesis(std::string_view value) noexcept {
    return value == "GENESIS" || is_lower_hex_sha256(value);
}

inline bool contains_ascii_control(std::string_view value) noexcept {
    for (const unsigned char c : value) {
        if (c < 0x20U || c == 0x7fU) return true;
    }
    return false;
}

inline bool is_well_formed_utf8(std::string_view value) noexcept {
    const auto* bytes =
        reinterpret_cast<const unsigned char*>(value.data());
    std::size_t index = 0;
    while (index < value.size()) {
        const unsigned char lead = bytes[index];
        if (lead <= 0x7fU) {
            ++index;
            continue;
        }

        std::size_t continuation_count = 0;
        std::uint32_t code_point = 0;
        std::uint32_t minimum = 0;
        if (lead >= 0xc2U && lead <= 0xdfU) {
            continuation_count = 1;
            code_point = lead & 0x1fU;
            minimum = 0x80U;
        } else if (lead >= 0xe0U && lead <= 0xefU) {
            continuation_count = 2;
            code_point = lead & 0x0fU;
            minimum = 0x800U;
        } else if (lead >= 0xf0U && lead <= 0xf4U) {
            continuation_count = 3;
            code_point = lead & 0x07U;
            minimum = 0x10000U;
        } else {
            return false;
        }
        if (continuation_count > value.size() - index - 1) return false;

        for (std::size_t offset = 1; offset <= continuation_count; ++offset) {
            const unsigned char next = bytes[index + offset];
            if ((next & 0xc0U) != 0x80U) return false;
            code_point = (code_point << 6U) | (next & 0x3fU);
        }
        if (code_point < minimum || code_point > 0x10ffffU ||
            (code_point >= 0xd800U && code_point <= 0xdfffU)) {
            return false;
        }
        index += continuation_count + 1;
    }
    return true;
}

inline bool is_base64url_without_padding(std::string_view value) noexcept {
    if (value.empty()) return false;
    for (const char c : value) {
        if (!((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
              (c >= '0' && c <= '9') || c == '-' || c == '_')) {
            return false;
        }
    }
    return true;
}

inline int two_digits(std::string_view text, std::size_t pos) noexcept {
    if (pos + 1 >= text.size() || text[pos] < '0' || text[pos] > '9' ||
        text[pos + 1] < '0' || text[pos + 1] > '9') {
        return -1;
    }
    return (text[pos] - '0') * 10 + (text[pos + 1] - '0');
}

inline int four_digits(std::string_view text, std::size_t pos) noexcept {
    int value = 0;
    for (std::size_t i = 0; i < 4; ++i) {
        if (pos + i >= text.size() || text[pos + i] < '0' ||
            text[pos + i] > '9') {
            return -1;
        }
        value = value * 10 + (text[pos + i] - '0');
    }
    return value;
}

inline bool is_leap_year(int year) noexcept {
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

inline int days_in_month(int year, int month) noexcept {
    static constexpr std::array<int, 13> days{
        0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    if (month == 2) return is_leap_year(year) ? 29 : 28;
    if (month < 1 || month > 12) return 0;
    return days[static_cast<std::size_t>(month)];
}

inline bool is_canonical_utc(std::string_view text) noexcept {
    if (text.size() != 20 || text[4] != '-' || text[7] != '-' ||
        text[10] != 'T' || text[13] != ':' || text[16] != ':' ||
        text[19] != 'Z') {
        return false;
    }
    const int year = four_digits(text, 0);
    const int month = two_digits(text, 5);
    const int day = two_digits(text, 8);
    const int hour = two_digits(text, 11);
    const int minute = two_digits(text, 14);
    const int second = two_digits(text, 17);
    return year >= 1970 && month >= 1 && month <= 12 && day >= 1 &&
           day <= days_in_month(year, month) && hour >= 0 && hour <= 23 &&
           minute >= 0 && minute <= 59 && second >= 0 && second <= 59;
}

inline void require_nonempty_bounded_control_free(
    std::string_view value,
    std::size_t maximum_bytes,
    std::string_view label) {
    if (value.empty()) {
        throw std::runtime_error(std::string(label) + " is empty");
    }
    if (value.size() > maximum_bytes) {
        throw std::runtime_error(std::string(label) + " exceeds byte budget");
    }
    if (contains_ascii_control(value)) {
        throw std::runtime_error(
            std::string(label) + " contains an ASCII control");
    }
    if (!is_well_formed_utf8(value)) {
        throw std::runtime_error(
            std::string(label) + " is not well-formed UTF-8");
    }
}

inline void append_line(BoundedMachineText& out, std::string_view value) {
    out.append(value);
    out.append('\n');
}

inline void append_component(BoundedMachineText& out, std::string_view value) {
    out.append_decimal(value.size());
    out.append(':');
    out.append(value);
}

inline void append_named_component(BoundedMachineText& out,
                                   std::string_view name,
                                   std::string_view value) {
    append_component(out, name);
    append_component(out, value);
}

inline std::string decimal_text(std::int64_t value) {
    BoundedMachineText out(32, "publication decimal text");
    out.append_decimal(value);
    return std::move(out).finish();
}

inline void append_json_string(BoundedMachineText& out,
                               std::string_view value) {
    static constexpr char hex[] = "0123456789abcdef";
    out.append('"');
    for (const unsigned char c : value) {
        switch (c) {
            case '"': out.append("\\\""); break;
            case '\\': out.append("\\\\"); break;
            case '\b': out.append("\\b"); break;
            case '\f': out.append("\\f"); break;
            case '\n': out.append("\\n"); break;
            case '\r': out.append("\\r"); break;
            case '\t': out.append("\\t"); break;
            default:
                if (c < 0x20U) {
                    out.append("\\u00");
                    out.append(hex[(c >> 4U) & 0x0fU]);
                    out.append(hex[c & 0x0fU]);
                } else {
                    out.append(static_cast<char>(c));
                }
        }
    }
    out.append('"');
}

inline void append_json_member_prefix(BoundedMachineText& out,
                                      std::string_view indentation,
                                      std::string_view name) {
    out.append(indentation);
    append_json_string(out, name);
    out.append(": ");
}

}  // namespace anonsync::persistence::publication_detail
