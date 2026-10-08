#include "anonsync_json_parser.hpp"

#include <charconv>
#include <cctype>
#include <cstddef>
#include <cmath>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <utility>

namespace anonsync {
namespace {

class JsonParser {
  public:
    explicit JsonParser(std::string text) : text_(std::move(text)) {}

    Json parse() {
        Json v = parse_value();
        skip_ws();
        if (pos_ != text_.size()) throw std::runtime_error("trailing JSON content at byte " + std::to_string(pos_));
        return v;
    }

  private:
    std::string text_;
    size_t pos_ = 0;
    int depth_ = 0;
    static constexpr int kMaxJsonDepth = 256;

    void enter_container(const char* label) {
        depth_++;
        if (depth_ > kMaxJsonDepth) {
            throw std::runtime_error(std::string("JSON nesting depth exceeded while parsing ") + label);
        }
    }
    void leave_container() {
        if (depth_ > 0) depth_--;
    }

    void skip_ws() {
        while (pos_ < text_.size()) {
            const char c = text_[pos_];
            if (c != ' ' && c != '\t' && c != '\r' && c != '\n') break;
            pos_++;
        }
    }
    char peek() const { return pos_ < text_.size() ? text_[pos_] : '\0'; }
    char get() {
        if (pos_ >= text_.size()) throw std::runtime_error("unexpected end of JSON");
        return text_[pos_++];
    }
    void expect(char c) {
        char got = get();
        if (got != c) throw std::runtime_error(std::string("expected '") + c + "' but got '" + got + "'");
    }
    bool consume_literal(const std::string& literal) {
        if (text_.compare(pos_, literal.size(), literal) == 0) {
            pos_ += literal.size();
            return true;
        }
        return false;
    }
    Json parse_value() {
        skip_ws();
        char c = peek();
        if (c == 'n') {
            if (!consume_literal("null")) throw std::runtime_error("invalid null literal");
            return Json{};
        }
        if (c == 't') {
            if (!consume_literal("true")) throw std::runtime_error("invalid true literal");
            Json v; v.type = Json::Type::Bool; v.b = true; return v;
        }
        if (c == 'f') {
            if (!consume_literal("false")) throw std::runtime_error("invalid false literal");
            Json v; v.type = Json::Type::Bool; v.b = false; return v;
        }
        if (c == '"') return parse_string_json();
        if (c == '[') return parse_array();
        if (c == '{') return parse_object();
        if (c == '-' || std::isdigit(static_cast<unsigned char>(c))) return parse_number();
        throw std::runtime_error("invalid JSON value at byte " + std::to_string(pos_));
    }
    Json parse_string_json() {
        Json v; v.type = Json::Type::String; v.s = parse_string(); return v;
    }
    static void append_utf8(std::string& out, uint32_t cp) {
        if (cp > 0x10FFFF || (cp >= 0xD800 && cp <= 0xDFFF)) {
            throw std::runtime_error("invalid Unicode scalar value in JSON string");
        }
        if (cp <= 0x7F) out.push_back(static_cast<char>(cp));
        else if (cp <= 0x7FF) {
            out.push_back(static_cast<char>(0xC0 | ((cp >> 6) & 0x1F)));
            out.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
        } else if (cp <= 0xFFFF) {
            out.push_back(static_cast<char>(0xE0 | ((cp >> 12) & 0x0F)));
            out.push_back(static_cast<char>(0x80 | ((cp >> 6) & 0x3F)));
            out.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
        } else {
            out.push_back(static_cast<char>(0xF0 | ((cp >> 18) & 0x07)));
            out.push_back(static_cast<char>(0x80 | ((cp >> 12) & 0x3F)));
            out.push_back(static_cast<char>(0x80 | ((cp >> 6) & 0x3F)));
            out.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
        }
    }
    uint32_t parse_hex4() {
        uint32_t cp = 0;
        for (int i = 0; i < 4; ++i) {
            char h = get();
            cp <<= 4;
            if (h >= '0' && h <= '9') cp |= static_cast<uint32_t>(h - '0');
            else if (h >= 'a' && h <= 'f') cp |= static_cast<uint32_t>(10 + h - 'a');
            else if (h >= 'A' && h <= 'F') cp |= static_cast<uint32_t>(10 + h - 'A');
            else throw std::runtime_error("bad unicode escape");
        }
        return cp;
    }
    void append_validated_raw_utf8(std::string& out, unsigned char first) {
        auto continuation = [&]() -> unsigned char {
            const unsigned char next = static_cast<unsigned char>(get());
            if ((next & 0xC0U) != 0x80U) throw std::runtime_error("invalid UTF-8 continuation byte in JSON string");
            return next;
        };
        out.push_back(static_cast<char>(first));
        if (first >= 0xC2U && first <= 0xDFU) {
            out.push_back(static_cast<char>(continuation()));
            return;
        }
        if (first >= 0xE0U && first <= 0xEFU) {
            const unsigned char second = continuation();
            if ((first == 0xE0U && second < 0xA0U) || (first == 0xEDU && second > 0x9FU)) {
                throw std::runtime_error("invalid or surrogate UTF-8 sequence in JSON string");
            }
            out.push_back(static_cast<char>(second));
            out.push_back(static_cast<char>(continuation()));
            return;
        }
        if (first >= 0xF0U && first <= 0xF4U) {
            const unsigned char second = continuation();
            if ((first == 0xF0U && second < 0x90U) || (first == 0xF4U && second > 0x8FU)) {
                throw std::runtime_error("out-of-range UTF-8 sequence in JSON string");
            }
            out.push_back(static_cast<char>(second));
            out.push_back(static_cast<char>(continuation()));
            out.push_back(static_cast<char>(continuation()));
            return;
        }
        throw std::runtime_error("invalid UTF-8 leading byte in JSON string");
    }

    std::string parse_string() {
        expect('"');
        std::string out;
        while (true) {
            char c = get();
            if (c == '"') break;
            const unsigned char uc = static_cast<unsigned char>(c);
            if (uc < 0x20U) {
                throw std::runtime_error("unescaped control character in JSON string");
            }
            if (c == '\\') {
                char e = get();
                switch (e) {
                    case '"': out.push_back('"'); break;
                    case '\\': out.push_back('\\'); break;
                    case '/': out.push_back('/'); break;
                    case 'b': out.push_back('\b'); break;
                    case 'f': out.push_back('\f'); break;
                    case 'n': out.push_back('\n'); break;
                    case 'r': out.push_back('\r'); break;
                    case 't': out.push_back('\t'); break;
                    case 'u': {
                        uint32_t cp = parse_hex4();
                        if (cp >= 0xD800 && cp <= 0xDBFF) {
                            if (get() != '\\' || get() != 'u') throw std::runtime_error("high surrogate without following low surrogate");
                            uint32_t low = parse_hex4();
                            if (low < 0xDC00 || low > 0xDFFF) throw std::runtime_error("high surrogate not followed by low surrogate");
                            cp = 0x10000 + (((cp - 0xD800) << 10) | (low - 0xDC00));
                        } else if (cp >= 0xDC00 && cp <= 0xDFFF) {
                            throw std::runtime_error("low surrogate without preceding high surrogate");
                        }
                        append_utf8(out, cp);
                        break;
                    }
                    default: throw std::runtime_error("bad escape in string");
                }
            } else if (uc < 0x80U) {
                out.push_back(c);
            } else {
                append_validated_raw_utf8(out, uc);
            }
        }
        return out;
    }

    Json parse_number() {
        size_t start = pos_;
        if (peek() == '-') pos_++;
        if (!std::isdigit(static_cast<unsigned char>(peek()))) {
            throw std::runtime_error("invalid JSON number: missing integer digit");
        }
        if (peek() == '0') {
            pos_++;
            if (std::isdigit(static_cast<unsigned char>(peek()))) {
                throw std::runtime_error("invalid JSON number: leading zero");
            }
        } else {
            while (std::isdigit(static_cast<unsigned char>(peek()))) pos_++;
        }
        if (peek() == '.') {
            pos_++;
            if (!std::isdigit(static_cast<unsigned char>(peek()))) {
                throw std::runtime_error("invalid JSON number: missing fractional digit");
            }
            while (std::isdigit(static_cast<unsigned char>(peek()))) pos_++;
        }
        if (peek() == 'e' || peek() == 'E') {
            pos_++;
            if (peek() == '+' || peek() == '-') pos_++;
            if (!std::isdigit(static_cast<unsigned char>(peek()))) {
                throw std::runtime_error("invalid JSON number: missing exponent digit");
            }
            while (std::isdigit(static_cast<unsigned char>(peek()))) pos_++;
        }
        Json v; v.type = Json::Type::Number;
        const char* first = text_.data() + start;
        const char* last = text_.data() + pos_;
        const auto parsed = std::from_chars(first, last, v.n, std::chars_format::general);
        if (parsed.ec != std::errc() || parsed.ptr != last || !std::isfinite(v.n)) {
            throw std::runtime_error("invalid or non-finite JSON number conversion");
        }
        return v;
    }
    Json parse_array() {
        enter_container("array");
        Json v; v.type = Json::Type::Array;
        expect('['); skip_ws();
        if (peek() == ']') { get(); leave_container(); return v; }
        while (true) {
            v.a.push_back(parse_value());
            skip_ws();
            char c = get();
            if (c == ']') break;
            if (c != ',') throw std::runtime_error("expected comma in array");
        }
        leave_container();
        return v;
    }
    Json parse_object() {
        enter_container("object");
        Json v; v.type = Json::Type::Object;
        expect('{'); skip_ws();
        if (peek() == '}') { get(); leave_container(); return v; }
        while (true) {
            skip_ws();
            if (peek() != '"') throw std::runtime_error("expected object key");
            std::string key = parse_string();
            skip_ws(); expect(':');
            Json value = parse_value();
            auto inserted = v.o.emplace(key, std::move(value));
            if (!inserted.second) {
                throw std::runtime_error("duplicate JSON object key rejected: " + key);
            }
            skip_ws();
            char c = get();
            if (c == '}') break;
            if (c != ',') throw std::runtime_error("expected comma in object");
        }
        leave_container();
        return v;
    }
};

}  // namespace

Json parse_json_text(const std::string& text) {
    return JsonParser(text).parse();
}

}  // namespace anonsync
