#include "iotox/security/recovery.hpp"

#include "embedded_wordlist.hpp"
#include "iotox/security/random.hpp"

#include <algorithm>
#include <array>
#include <cstdlib>
#include <cstring>
#include <dlfcn.h>
#include <fstream>
#include <limits>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace iotox::security {
namespace {

void secure_erase(void *memory, std::size_t size) noexcept {
    auto *bytes = static_cast<volatile std::uint8_t *>(memory);
    while (size > 0U) {
        *bytes = 0U;
        ++bytes;
        --size;
    }
}

class StringWipeGuard {
  public:
    explicit StringWipeGuard(std::string &value) noexcept : value_(value) {}
    ~StringWipeGuard() {
        if (armed_) {
            secure_erase(value_.data(), value_.size());
        }
    }

    StringWipeGuard(const StringWipeGuard &) = delete;
    StringWipeGuard &operator=(const StringWipeGuard &) = delete;

    void release() noexcept { armed_ = false; }

  private:
    std::string &value_;
    bool armed_{true};
};

bool is_ascii_whitespace(unsigned char value) noexcept {
    return value == ' ' || value == '\t' || value == '\n' || value == '\r' ||
           value == '\f' || value == '\v';
}

Result<std::string> canonicalize(std::string_view input) {
    std::string canonical;
    StringWipeGuard wipe_on_error(canonical);
    canonical.reserve(input.size());

    std::size_t word_count = 0U;
    bool in_word = false;
    bool last_was_hyphen = false;

    for (const char raw_character : input) {
        const unsigned char raw = static_cast<unsigned char>(raw_character);
        if (raw >= 0x80U) {
            return Status{ErrorCode::invalid_argument,
                          "recall phrase v1 accepts ASCII words only"};
        }

        if (is_ascii_whitespace(raw)) {
            if (in_word) {
                if (last_was_hyphen) {
                    return Status{ErrorCode::invalid_argument,
                                  "recall phrase words may not end with '-'"};
                }
                in_word = false;
                ++word_count;
            }
            continue;
        }

        unsigned char value = raw;
        if (value >= 'A' && value <= 'Z') {
            value = static_cast<unsigned char>(value - 'A' + 'a');
        }
        if (!((value >= 'a' && value <= 'z') || value == '-')) {
            return Status{ErrorCode::invalid_argument,
                          "recall phrase v1 words may contain only ASCII letters and internal '-'"};
        }

        if (!in_word) {
            if (value == '-') {
                return Status{ErrorCode::invalid_argument,
                              "recall phrase words may not begin with '-'"};
            }
            if (!canonical.empty()) {
                canonical.push_back(' ');
            }
            in_word = true;
            last_was_hyphen = false;
        }

        if (value == '-' && last_was_hyphen) {
            return Status{ErrorCode::invalid_argument,
                          "recall phrase words may not contain consecutive '-'"};
        }
        canonical.push_back(static_cast<char>(value));
        last_was_hyphen = value == '-';
    }

    if (in_word) {
        if (last_was_hyphen) {
            return Status{ErrorCode::invalid_argument,
                          "recall phrase words may not end with '-'"};
        }
        ++word_count;
    }

    if (word_count != RecallContract::phrase_words) {
        return Status{ErrorCode::invalid_argument,
                      "recall phrase v1 requires exactly " +
                          std::to_string(RecallContract::phrase_words) + " words"};
    }
    wipe_on_error.release();
    return canonical;
}

std::vector<std::string_view> split_words(std::string_view canonical) {
    std::vector<std::string_view> words;
    std::size_t begin = 0U;
    while (begin < canonical.size()) {
        const std::size_t end = canonical.find(' ', begin);
        if (end == std::string_view::npos) {
            words.push_back(canonical.substr(begin));
            break;
        }
        words.push_back(canonical.substr(begin, end - begin));
        begin = end + 1U;
    }
    return words;
}

std::string expected_dice_code(std::size_t index) {
    std::string code(5U, '1');
    for (std::size_t position = code.size(); position > 0U; --position) {
        code[position - 1U] = static_cast<char>('1' + (index % 6U));
        index /= 6U;
    }
    return code;
}

template <typename FunctionPointer>
Result<FunctionPointer> load_symbol(void *handle, const char *name) {
    ::dlerror();
    void *raw = ::dlsym(handle, name);
    const char *error = ::dlerror();
    if (error != nullptr || raw == nullptr) {
        return Status{ErrorCode::library_error,
                      "Argon2 symbol '" + std::string(name) + "' is unavailable: " +
                          (error == nullptr ? std::string("unknown dlsym failure") :
                                              std::string(error))};
    }

    static_assert(sizeof(FunctionPointer) == sizeof(raw));
    FunctionPointer function{};
    std::memcpy(&function, &raw, sizeof(function));
    return function;
}

template <typename FunctionPointer>
Status assign_symbol(void *handle, const char *name, FunctionPointer &destination) {
    auto symbol = load_symbol<FunctionPointer>(handle, name);
    if (!symbol) {
        return symbol.status();
    }
    destination = symbol.value();
    return Status::success();
}

std::vector<std::string> library_candidates(const std::filesystem::path &explicit_path) {
    if (!explicit_path.empty()) {
        return {explicit_path.string()};
    }
    if (const char *environment = std::getenv("IOTOX_ARGON2_LIBRARY");
        environment != nullptr && environment[0] != '\0') {
        return {environment};
    }
    return {"libargon2.so.1", "libargon2.so", "libargon2.dylib"};
}

}  // namespace

Result<RecallWordList> RecallWordList::parse_stream(
    std::istream &input, std::string_view source) {
    RecallWordList result;
    result.ordered_words_.reserve(RecallContract::wordlist_entries);
    result.words_.reserve(RecallContract::wordlist_entries);

    std::string line;
    std::size_t index = 0U;
    while (std::getline(input, line)) {
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        if (index >= RecallContract::wordlist_entries) {
            return Status{ErrorCode::protocol_error,
                          "recall word list contains more than 7776 entries"};
        }

        const std::size_t tab = line.find('\t');
        if (tab == std::string::npos || line.find('\t', tab + 1U) != std::string::npos) {
            return Status{ErrorCode::protocol_error,
                          "invalid recall word list line " + std::to_string(index + 1U)};
        }

        const std::string code = line.substr(0U, tab);
        std::string word = line.substr(tab + 1U);
        if (code != expected_dice_code(index)) {
            return Status{ErrorCode::protocol_error,
                          "unexpected dice code on recall word list line " +
                              std::to_string(index + 1U)};
        }
        if (word.empty()) {
            return Status{ErrorCode::protocol_error,
                          "empty word on recall word list line " +
                              std::to_string(index + 1U)};
        }
        for (std::size_t position = 0U; position < word.size(); ++position) {
            const unsigned char value = static_cast<unsigned char>(word[position]);
            if (!((value >= 'a' && value <= 'z') ||
                  (value == '-' && position > 0U && position + 1U < word.size()))) {
                return Status{ErrorCode::protocol_error,
                              "invalid word syntax on recall word list line " +
                                  std::to_string(index + 1U)};
            }
        }
        if (!result.words_.insert(word).second) {
            return Status{ErrorCode::protocol_error,
                          "duplicate recall word on line " + std::to_string(index + 1U)};
        }
        result.ordered_words_.push_back(std::move(word));
        ++index;
    }

    if (!input.eof()) {
        return Status{ErrorCode::io_error,
                      "error while reading recall word list: " + std::string(source)};
    }
    if (index != RecallContract::wordlist_entries) {
        return Status{ErrorCode::protocol_error,
                      "recall word list must contain exactly 7776 entries; found " +
                          std::to_string(index)};
    }
    return result;
}

Result<RecallWordList> RecallWordList::load(const std::filesystem::path &path) {
    std::ifstream input(path);
    if (!input) {
        return Status{ErrorCode::not_found,
                      "unable to open recall word list: " + path.string()};
    }
    return parse_stream(input, path.string());
}

Result<RecallWordList> RecallWordList::embedded() {
    std::istringstream input{std::string(embedded_recall_wordlist_text())};
    return parse_stream(input, "embedded EFF long word list");
}

bool RecallWordList::contains(std::string_view word) const {
    return words_.find(std::string(word)) != words_.end();
}

Result<std::string_view> RecallWordList::word_at(std::size_t index) const {
    if (index >= ordered_words_.size()) {
        return Status{ErrorCode::invalid_argument,
                      "recall word-list index is outside the pinned list"};
    }
    return std::string_view(ordered_words_[index]);
}

RecallPhrase::~RecallPhrase() {
    secure_erase(canonical_.data(), canonical_.size());
}

RecallPhrase::RecallPhrase(RecallPhrase &&other) noexcept
    : canonical_(std::move(other.canonical_)) {
    secure_erase(other.canonical_.data(), other.canonical_.size());
    other.canonical_.clear();
}

RecallPhrase &RecallPhrase::operator=(RecallPhrase &&other) noexcept {
    if (this != &other) {
        secure_erase(canonical_.data(), canonical_.size());
        canonical_ = std::move(other.canonical_);
        secure_erase(other.canonical_.data(), other.canonical_.size());
        other.canonical_.clear();
    }
    return *this;
}

Result<RecallPhrase> RecallPhrase::parse(
    std::string_view input, const RecallWordList &wordlist) {
    auto canonical = canonicalize(input);
    if (!canonical) {
        return canonical.status();
    }

    for (const std::string_view word : split_words(canonical.value())) {
        if (!wordlist.contains(word)) {
            secure_erase(canonical.value().data(), canonical.value().size());
            return Status{ErrorCode::invalid_argument,
                          "recall phrase contains a word outside the pinned v1 list"};
        }
    }
    return RecallPhrase(std::move(canonical.value()));
}

Result<RecallPhrase> RecallPhrase::generate(const RecallWordList &wordlist) {
    if (wordlist.size() != RecallContract::wordlist_entries) {
        return Status{ErrorCode::invalid_argument,
                      "RecallRoot-v1 generation requires the complete 7776-word list"};
    }

    // Sampling uint16 values modulo 7776 without rejection would slightly favor
    // the first 3328 words. Accept only the largest complete multiple of 7776.
    constexpr std::uint32_t sample_space = 1U << 16U;
    constexpr std::uint32_t acceptance_limit =
        sample_space - (sample_space % RecallContract::wordlist_entries);
    static_assert(acceptance_limit == 62'208U);

    std::string canonical;
    StringWipeGuard wipe_on_error(canonical);
    canonical.reserve(RecallContract::phrase_words * 12U);

    for (std::size_t position = 0U; position < RecallContract::phrase_words; ++position) {
        bool selected = false;
        for (std::size_t attempt = 0U; attempt < 1'024U; ++attempt) {
            std::array<std::uint8_t, 2U> sample{};
            const Status random_status = fill_random(sample);
            if (!random_status.ok()) {
                secure_erase(sample.data(), sample.size());
                return random_status;
            }
            const std::uint32_t value =
                (static_cast<std::uint32_t>(sample[0]) << 8U) | sample[1];
            secure_erase(sample.data(), sample.size());
            if (value >= acceptance_limit) {
                continue;
            }

            const std::size_t index =
                static_cast<std::size_t>(value % RecallContract::wordlist_entries);
            auto word = wordlist.word_at(index);
            if (!word) {
                return word.status();
            }
            if (!canonical.empty()) {
                canonical.push_back(' ');
            }
            canonical.append(word.value());
            selected = true;
            break;
        }
        if (!selected) {
            return Status{ErrorCode::internal_error,
                          "operating-system random source repeatedly missed the unbiased "
                          "RecallRoot-v1 sampling range"};
        }
    }

    wipe_on_error.release();
    return RecallPhrase(std::move(canonical));
}

RecoveryRoot::~RecoveryRoot() {
    secure_erase(bytes_.data(), bytes_.size());
}

RecoveryRoot::RecoveryRoot(RecoveryRoot &&other) noexcept : bytes_(other.bytes_) {
    secure_erase(other.bytes_.data(), other.bytes_.size());
}

RecoveryRoot &RecoveryRoot::operator=(RecoveryRoot &&other) noexcept {
    if (this != &other) {
        secure_erase(bytes_.data(), bytes_.size());
        bytes_ = other.bytes_;
        secure_erase(other.bytes_.data(), other.bytes_.size());
    }
    return *this;
}

DynamicArgon2::~DynamicArgon2() {
    if (handle_ != nullptr) {
        ::dlclose(handle_);
    }
}

DynamicArgon2::DynamicArgon2(DynamicArgon2 &&other) noexcept
    : handle_(std::exchange(other.handle_, nullptr)),
      api_(other.api_),
      loaded_path_(std::move(other.loaded_path_)) {
    other.api_ = {};
}

DynamicArgon2 &DynamicArgon2::operator=(DynamicArgon2 &&other) noexcept {
    if (this != &other) {
        if (handle_ != nullptr) {
            ::dlclose(handle_);
        }
        handle_ = std::exchange(other.handle_, nullptr);
        api_ = other.api_;
        loaded_path_ = std::move(other.loaded_path_);
        other.api_ = {};
    }
    return *this;
}

Result<DynamicArgon2> DynamicArgon2::load(const std::filesystem::path &explicit_path) {
#if defined(IOTOX_LINKED_ARGON2)
    if (explicit_path.empty()) {
        DynamicArgon2 library;
        library.api_.id_context = &::argon2id_ctx;
        library.api_.error_message = &::argon2_error_message;
        library.loaded_path_ = "linked-static-argon2";
        return library;
    }
#endif

    std::ostringstream failures;
    for (const std::string &candidate : library_candidates(explicit_path)) {
        ::dlerror();
        void *handle = ::dlopen(candidate.c_str(), RTLD_NOW | RTLD_LOCAL);
        if (handle == nullptr) {
            const char *message = ::dlerror();
            failures << candidate << ": "
                     << (message == nullptr ? "unknown dlopen failure" : message) << '\n';
            continue;
        }

        argon2_abi::Api api{};
        Status status = assign_symbol(handle, "argon2id_ctx", api.id_context);
        if (status.ok()) {
            status = assign_symbol(handle, "argon2_error_message", api.error_message);
        }
        if (!status.ok()) {
            failures << candidate << ": " << status.message() << '\n';
            ::dlclose(handle);
            continue;
        }

        DynamicArgon2 library;
        library.handle_ = handle;
        library.api_ = api;
        library.loaded_path_ = candidate;
        return library;
    }

    return Status{ErrorCode::unavailable,
                  "unable to load a compatible Argon2 shared library:\n" + failures.str()};
}

Result<RecoveryRoot> DynamicArgon2::derive(const RecallPhrase &phrase) const {
    if (api_.id_context == nullptr || api_.error_message == nullptr) {
        return Status{ErrorCode::internal_error, "Argon2 provider is not loaded"};
    }
    if (phrase.canonical().size() > std::numeric_limits<std::uint32_t>::max()) {
        return Status{ErrorCode::invalid_argument, "recall phrase is too large"};
    }

    std::vector<std::uint8_t> password(phrase.canonical().begin(), phrase.canonical().end());
    std::array<std::uint8_t, RecallContract::salt.size()> salt = RecallContract::salt;
    std::array<std::uint8_t, RecallContract::output_bytes> output{};

    argon2_abi::Context context{
        output.data(),
        static_cast<std::uint32_t>(output.size()),
        password.data(),
        static_cast<std::uint32_t>(password.size()),
        salt.data(),
        static_cast<std::uint32_t>(salt.size()),
        nullptr,
        0U,
        nullptr,
        0U,
        RecallContract::iterations,
        RecallContract::memory_kib,
        RecallContract::parallelism,
        RecallContract::parallelism,
        RecallContract::argon2_version,
        nullptr,
        nullptr,
        argon2_abi::kFlagClearPassword,
    };

    const int result = api_.id_context(&context);
    secure_erase(password.data(), password.size());
    secure_erase(salt.data(), salt.size());
    if (result != argon2_abi::kOk) {
        secure_erase(output.data(), output.size());
        const char *message = api_.error_message(result);
        return Status{ErrorCode::library_error,
                      "Argon2id derivation failed: " +
                          std::string(message == nullptr ? "unknown Argon2 error" : message)};
    }

    RecoveryRoot root(output);
    secure_erase(output.data(), output.size());
    return root;
}

std::string hex_encode(std::span<const std::uint8_t> bytes) {
    static constexpr char alphabet[] = "0123456789abcdef";
    std::string output;
    output.resize(bytes.size() * 2U);
    for (std::size_t index = 0U; index < bytes.size(); ++index) {
        output[index * 2U] = alphabet[(bytes[index] >> 4U) & 0x0FU];
        output[index * 2U + 1U] = alphabet[bytes[index] & 0x0FU];
    }
    return output;
}

}  // namespace iotox::security
