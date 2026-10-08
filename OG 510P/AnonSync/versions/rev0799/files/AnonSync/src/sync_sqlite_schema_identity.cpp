#include "sync_sqlite_schema_identity.hpp"

#include <cctype>
#include <cstddef>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace anonsync {
namespace {

enum class SchemaTokenKind : char {
    word = 'w',
    number = 'n',
    quoted = 'q',
    blob = 'b',
    symbol = 's',
    comment = 'c'
};

struct SchemaToken final {
    SchemaTokenKind kind;
    std::string text;
};

bool ascii_word_start(unsigned char c) {
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
           c == '_' || c == '$' || c >= 0x80;
}

bool ascii_word_continue(unsigned char c) {
    return ascii_word_start(c) || (c >= '0' && c <= '9');
}

char lower_ascii(char c) {
    const unsigned char uc = static_cast<unsigned char>(c);
    if (uc >= 'A' && uc <= 'Z') {
        return static_cast<char>(uc - 'A' + 'a');
    }
    return c;
}

std::string parse_quoted_token(std::string_view sql,
                               std::size_t& index,
                               char opening,
                               char closing) {
    const std::size_t start = index;
    ++index;
    while (index < sql.size()) {
        if (sql[index] != closing) {
            ++index;
            continue;
        }
        ++index;
        if (index < sql.size() && sql[index] == closing) {
            ++index;
            continue;
        }
        return std::string(sql.substr(start, index - start));
    }
    throw std::runtime_error(
        std::string("SQLite schema SQL contains an unterminated ") + opening +
        " quoted token");
}

void append_token_identity(std::string& out, const SchemaToken& token) {
    out.push_back(static_cast<char>(token.kind));
    out.append(std::to_string(token.text.size()));
    out.push_back(':');
    out.append(token.text);
    out.push_back(';');
}

}  // namespace

std::string canonicalize_sqlite_schema_sql_or_throw(std::string_view sql) {
    std::vector<SchemaToken> tokens;
    tokens.reserve(sql.size() / 3 + 1);

    for (std::size_t i = 0; i < sql.size();) {
        const unsigned char c = static_cast<unsigned char>(sql[i]);
        if (std::isspace(c) != 0) {
            ++i;
            continue;
        }

        if (sql[i] == '-' && i + 1 < sql.size() && sql[i + 1] == '-') {
            const std::size_t start = i;
            i += 2;
            while (i < sql.size() && sql[i] != '\n' && sql[i] != '\r') ++i;
            tokens.push_back({SchemaTokenKind::comment,
                              std::string(sql.substr(start, i - start))});
            continue;
        }
        if (sql[i] == '/' && i + 1 < sql.size() && sql[i + 1] == '*') {
            const std::size_t start = i;
            i += 2;
            while (i + 1 < sql.size() &&
                   !(sql[i] == '*' && sql[i + 1] == '/')) {
                ++i;
            }
            if (i + 1 >= sql.size()) {
                throw std::runtime_error(
                    "SQLite schema SQL contains an unterminated block comment");
            }
            i += 2;
            tokens.push_back({SchemaTokenKind::comment,
                              std::string(sql.substr(start, i - start))});
            continue;
        }

        // SQLite blob literals require X to be immediately adjacent to the
        // opening quote. Tokenizing before whitespace removal preserves the
        // distinction between X'00' and X '00'.
        if ((sql[i] == 'x' || sql[i] == 'X') && i + 1 < sql.size() &&
            sql[i + 1] == '\'') {
            ++i;
            std::string quoted = parse_quoted_token(sql, i, '\'', '\'');
            std::string blob;
            blob.reserve(1 + quoted.size());
            blob.push_back('x');
            blob.append(quoted);
            tokens.push_back({SchemaTokenKind::blob, std::move(blob)});
            continue;
        }

        if (sql[i] == '\'' || sql[i] == '"' || sql[i] == '`' || sql[i] == '[') {
            const char opening = sql[i];
            const char closing = opening == '[' ? ']' : opening;
            tokens.push_back({SchemaTokenKind::quoted,
                              parse_quoted_token(sql, i, opening, closing)});
            continue;
        }

        if (ascii_word_start(c)) {
            std::string word;
            do {
                word.push_back(lower_ascii(sql[i]));
                ++i;
            } while (i < sql.size() &&
                     ascii_word_continue(static_cast<unsigned char>(sql[i])));
            tokens.push_back({SchemaTokenKind::word, std::move(word)});
            continue;
        }

        if (c >= '0' && c <= '9') {
            const std::size_t start = i;
            bool exponent_may_take_sign = false;
            while (i < sql.size()) {
                const unsigned char nc = static_cast<unsigned char>(sql[i]);
                if ((nc >= '0' && nc <= '9') ||
                    (nc >= 'A' && nc <= 'Z') ||
                    (nc >= 'a' && nc <= 'z') || sql[i] == '.' ||
                    sql[i] == '_') {
                    exponent_may_take_sign = sql[i] == 'e' || sql[i] == 'E';
                    ++i;
                    continue;
                }
                if (exponent_may_take_sign &&
                    (sql[i] == '+' || sql[i] == '-')) {
                    exponent_may_take_sign = false;
                    ++i;
                    continue;
                }
                break;
            }
            std::string number(sql.substr(start, i - start));
            for (char& digit : number) digit = lower_ascii(digit);
            tokens.push_back({SchemaTokenKind::number, std::move(number)});
            continue;
        }

        static constexpr std::string_view kThreeCharacterOperators[] = {"->>"};
        static constexpr std::string_view kTwoCharacterOperators[] = {
            "||", "->", "==", "!=", "<>", "<=", ">=", "<<", ">>"};
        bool matched = false;
        for (std::string_view op : kThreeCharacterOperators) {
            if (sql.substr(i, op.size()) == op) {
                tokens.push_back({SchemaTokenKind::symbol, std::string(op)});
                i += op.size();
                matched = true;
                break;
            }
        }
        if (matched) continue;
        for (std::string_view op : kTwoCharacterOperators) {
            if (sql.substr(i, op.size()) == op) {
                tokens.push_back({SchemaTokenKind::symbol, std::string(op)});
                i += op.size();
                matched = true;
                break;
            }
        }
        if (matched) continue;

        tokens.push_back({SchemaTokenKind::symbol, std::string(1, sql[i])});
        ++i;
    }

    while (!tokens.empty() && tokens.back().kind == SchemaTokenKind::symbol &&
           tokens.back().text == ";") {
        tokens.pop_back();
    }

    std::string identity = "anonsync-sqlite-schema-token-stream-v1|";
    for (const SchemaToken& token : tokens) append_token_identity(identity, token);
    return identity;
}

}  // namespace anonsync
