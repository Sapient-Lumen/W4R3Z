#include "iotox/security/recovery.hpp"
#include "iotox/security/authority.hpp"
#include "iotox/security/sodium.hpp"
#include "test_harness.hpp"

#include <cstdlib>
#include <filesystem>
#include <string>

namespace {

std::filesystem::path wordlist_path() {
    const char *path = std::getenv("IOTOX_TEST_RECALL_WORDLIST");
    IOTOX_CHECK_MSG(path != nullptr, "IOTOX_TEST_RECALL_WORDLIST is not set");
    return path;
}

std::filesystem::path mock_argon2_path() {
    const char *path = std::getenv("IOTOX_TEST_MOCK_ARGON2");
    IOTOX_CHECK_MSG(path != nullptr, "IOTOX_TEST_MOCK_ARGON2 is not set");
    return path;
}

}  // namespace

IOTOX_TEST("recall word list and canonical phrase contract") {
    auto wordlist = iotox::security::RecallWordList::load(wordlist_path());
    IOTOX_CHECK_MSG(wordlist.ok(), wordlist.status().message());
    IOTOX_CHECK(wordlist.value().size() == iotox::security::RecallContract::wordlist_entries);
    IOTOX_CHECK(wordlist.value().contains("abacus"));
    IOTOX_CHECK(wordlist.value().contains("drop-down"));
    IOTOX_CHECK(wordlist.value().contains("zoom"));

    auto phrase = iotox::security::RecallPhrase::parse(
        "  ABACUS\tabdomen  abdominal\nabide abiding ability ablaze able  ",
        wordlist.value());
    IOTOX_CHECK_MSG(phrase.ok(), phrase.status().message());
    IOTOX_CHECK(phrase.value().canonical() == iotox::security::kRecoveryKnownAnswerPhrase);
}

IOTOX_TEST("recall phrase rejects weak structure and foreign words") {
    auto wordlist = iotox::security::RecallWordList::load(wordlist_path());
    IOTOX_CHECK_MSG(wordlist.ok(), wordlist.status().message());

    auto too_short = iotox::security::RecallPhrase::parse(
        "abacus abdomen abdominal abide abiding ability ablaze", wordlist.value());
    IOTOX_CHECK(!too_short.ok());

    auto foreign = iotox::security::RecallPhrase::parse(
        "abacus abdomen abdominal abide abiding ability ablaze notinthelist", wordlist.value());
    IOTOX_CHECK(!foreign.ok());

    const std::string unicode =
        "abacus abdomen abdominal abide abiding ability ablaze abl\xC3\xA9";
    auto non_ascii = iotox::security::RecallPhrase::parse(unicode, wordlist.value());
    IOTOX_CHECK(!non_ascii.ok());

    auto valid_hyphenated = iotox::security::RecallPhrase::parse(
        "drop-down abdomen abdominal abide abiding ability ablaze able", wordlist.value());
    IOTOX_CHECK_MSG(valid_hyphenated.ok(), valid_hyphenated.status().message());

    auto leading_hyphen = iotox::security::RecallPhrase::parse(
        "-abacus abdomen abdominal abide abiding ability ablaze able", wordlist.value());
    IOTOX_CHECK(!leading_hyphen.ok());

    auto trailing_hyphen = iotox::security::RecallPhrase::parse(
        "abacus- abdomen abdominal abide abiding ability ablaze able", wordlist.value());
    IOTOX_CHECK(!trailing_hyphen.ok());

    auto repeated_hyphen = iotox::security::RecallPhrase::parse(
        "aba--cus abdomen abdominal abide abiding ability ablaze able", wordlist.value());
    IOTOX_CHECK(!repeated_hyphen.ok());
}

IOTOX_TEST("dynamic Argon2 boundary receives the frozen recall-root-v1 contract") {
    auto wordlist = iotox::security::RecallWordList::load(wordlist_path());
    IOTOX_CHECK_MSG(wordlist.ok(), wordlist.status().message());
    auto phrase = iotox::security::RecallPhrase::parse(
        iotox::security::kRecoveryKnownAnswerPhrase, wordlist.value());
    IOTOX_CHECK_MSG(phrase.ok(), phrase.status().message());

    auto library = iotox::security::DynamicArgon2::load(mock_argon2_path());
    IOTOX_CHECK_MSG(library.ok(), library.status().message());
    auto root = library.value().derive(phrase.value());
    IOTOX_CHECK_MSG(root.ok(), root.status().message());
    IOTOX_CHECK(
        iotox::security::hex_encode(root.value().bytes()) ==
        "a0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebf");
}

IOTOX_TEST("embedded recall word list is the complete pinned standalone contract") {
    auto embedded = iotox::security::RecallWordList::embedded();
    IOTOX_CHECK_MSG(embedded.ok(), embedded.status().message());
    IOTOX_CHECK(embedded.value().size() ==
                iotox::security::RecallContract::wordlist_entries);
    IOTOX_CHECK(embedded.value().contains("abacus"));
    IOTOX_CHECK(embedded.value().contains("drop-down"));
    IOTOX_CHECK(embedded.value().contains("zoom"));

    auto phrase = iotox::security::RecallPhrase::parse(
        iotox::security::kRecoveryKnownAnswerPhrase, embedded.value());
    IOTOX_CHECK_MSG(phrase.ok(), phrase.status().message());
    IOTOX_CHECK(phrase.value().canonical() ==
                iotox::security::kRecoveryKnownAnswerPhrase);
}



IOTOX_TEST("RecallRoot-v1 generator emits eight unbiased-list words") {
    auto wordlist = iotox::security::RecallWordList::embedded();
    IOTOX_CHECK_MSG(wordlist.ok(), wordlist.status().message());

    for (std::size_t attempt = 0U; attempt < 16U; ++attempt) {
        auto generated = iotox::security::RecallPhrase::generate(wordlist.value());
        IOTOX_CHECK_MSG(generated.ok(), generated.status().message());

        auto reparsed = iotox::security::RecallPhrase::parse(
            generated.value().canonical(), wordlist.value());
        IOTOX_CHECK_MSG(reparsed.ok(), reparsed.status().message());
        IOTOX_CHECK(reparsed.value().canonical() == generated.value().canonical());

        std::size_t words = 1U;
        for (const char value : generated.value().canonical()) {
            if (value == ' ') {
                ++words;
            }
        }
        IOTOX_CHECK(words == iotox::security::RecallContract::phrase_words);
    }
}

IOTOX_TEST("RecallRoot-v1 deterministically reconstructs the stable owner principal") {
    auto wordlist = iotox::security::RecallWordList::embedded();
    IOTOX_CHECK_MSG(wordlist.ok(), wordlist.status().message());
    auto phrase = iotox::security::RecallPhrase::parse(
        iotox::security::kRecoveryKnownAnswerPhrase, wordlist.value());
    IOTOX_CHECK_MSG(phrase.ok(), phrase.status().message());

    auto argon2 = iotox::security::DynamicArgon2::load(mock_argon2_path());
    IOTOX_CHECK_MSG(argon2.ok(), argon2.status().message());
    auto root = argon2.value().derive(phrase.value());
    IOTOX_CHECK_MSG(root.ok(), root.status().message());

    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto owner_seed = iotox::security::derive_owner_signing_seed(
        root.value(), sodium.value());
    IOTOX_CHECK_MSG(owner_seed.ok(), owner_seed.status().message());
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed.value());
    iotox::security::secure_wipe(owner_seed.value());
    IOTOX_CHECK_MSG(owner.ok(), owner.status().message());
    IOTOX_CHECK(iotox::security::hex(owner.value().public_key()) ==
                "2B3C75E532CA1BDC734E19F3DB43855D4B3C3B38470C7CA3492C5727ABE1AD35");
}
