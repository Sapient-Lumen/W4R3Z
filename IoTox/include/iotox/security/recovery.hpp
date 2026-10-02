#pragma once

#include "iotox/security/argon2_abi.hpp"
#include "iotox/status.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <istream>
#include <span>
#include <string>
#include <string_view>
#include <unordered_set>
#include <vector>

namespace iotox::security {

struct RecallContract {
    static constexpr std::string_view id = "iotox-recall-root-v1";
    static constexpr std::string_view algorithm = "Argon2id";
    static constexpr std::uint32_t argon2_version = argon2_abi::kVersion13;
    static constexpr std::uint32_t memory_kib = 65'536U;
    static constexpr std::uint32_t iterations = 3U;
    static constexpr std::uint32_t parallelism = 4U;
    static constexpr std::size_t output_bytes = 32U;
    static constexpr std::size_t phrase_words = 8U;
    static constexpr std::size_t wordlist_entries = 7'776U;
    static constexpr double generated_entropy_bits = 103.39850002884624;
    static constexpr std::string_view wordlist_sha256 =
        "addd35536511597a02fa0a9ff1e5284677b8883b83e986e43f15a3db996b903e";
    static constexpr std::array<std::uint8_t, 16> salt = {
        'I', 'o', 'T', 'o', 'x', 'R', 'e', 'c', 'a', 'l', 'l', 'R', 'o', 'o', 't', '1'};
};

class RecallWordList {
  public:
    [[nodiscard]] static Result<RecallWordList> load(const std::filesystem::path &path);
    [[nodiscard]] static Result<RecallWordList> embedded();

    [[nodiscard]] bool contains(std::string_view word) const;
    [[nodiscard]] Result<std::string_view> word_at(std::size_t index) const;
    [[nodiscard]] std::size_t size() const noexcept { return ordered_words_.size(); }

  private:
    [[nodiscard]] static Result<RecallWordList> parse_stream(
        std::istream &input, std::string_view source);
    std::vector<std::string> ordered_words_;
    std::unordered_set<std::string> words_;
};

class RecallPhrase {
  public:
    ~RecallPhrase();

    RecallPhrase(const RecallPhrase &) = delete;
    RecallPhrase &operator=(const RecallPhrase &) = delete;
    RecallPhrase(RecallPhrase &&other) noexcept;
    RecallPhrase &operator=(RecallPhrase &&other) noexcept;

    [[nodiscard]] static Result<RecallPhrase> parse(
        std::string_view input, const RecallWordList &wordlist);
    [[nodiscard]] static Result<RecallPhrase> generate(const RecallWordList &wordlist);

    [[nodiscard]] std::string_view canonical() const noexcept { return canonical_; }

  private:
    explicit RecallPhrase(std::string canonical) : canonical_(std::move(canonical)) {}

    std::string canonical_;
};

class RecoveryRoot {
  public:
    ~RecoveryRoot();

    RecoveryRoot(const RecoveryRoot &) = delete;
    RecoveryRoot &operator=(const RecoveryRoot &) = delete;
    RecoveryRoot(RecoveryRoot &&other) noexcept;
    RecoveryRoot &operator=(RecoveryRoot &&other) noexcept;

    [[nodiscard]] std::span<const std::uint8_t, RecallContract::output_bytes> bytes() const noexcept {
        return bytes_;
    }

  private:
    friend class DynamicArgon2;
    explicit RecoveryRoot(std::array<std::uint8_t, RecallContract::output_bytes> bytes)
        : bytes_(bytes) {}

    std::array<std::uint8_t, RecallContract::output_bytes> bytes_{};
};

class DynamicArgon2 {
  public:
    DynamicArgon2() = default;
    ~DynamicArgon2();

    DynamicArgon2(const DynamicArgon2 &) = delete;
    DynamicArgon2 &operator=(const DynamicArgon2 &) = delete;
    DynamicArgon2(DynamicArgon2 &&other) noexcept;
    DynamicArgon2 &operator=(DynamicArgon2 &&other) noexcept;

    [[nodiscard]] static Result<DynamicArgon2> load(
        const std::filesystem::path &explicit_path = {});

    [[nodiscard]] Result<RecoveryRoot> derive(const RecallPhrase &phrase) const;
    [[nodiscard]] const std::string &loaded_path() const noexcept { return loaded_path_; }

  private:
    void *handle_{nullptr};
    argon2_abi::Api api_{};
    std::string loaded_path_;
};

[[nodiscard]] std::string hex_encode(std::span<const std::uint8_t> bytes);

inline constexpr std::string_view kRecoveryKnownAnswerPhrase =
    "abacus abdomen abdominal abide abiding ability ablaze able";
inline constexpr std::string_view kRecoveryKnownAnswerHex =
    "87184eb373901af775366823ef670f4291806d062292ff2b2bff956337df2804";

}  // namespace iotox::security
