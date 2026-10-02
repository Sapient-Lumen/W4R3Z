#include "artifact_hasher.hpp"

#include <fstream>
#include <memory>
#include <stdexcept>
#include <utility>

#if defined(TOXSYNC_HAVE_OPENSSL)
#include <openssl/evp.h>
#endif

namespace toxsync::detail {

ArtifactSha256::ArtifactSha256() {
#if defined(TOXSYNC_HAVE_OPENSSL)
    auto* context = EVP_MD_CTX_new();
    if (context == nullptr) throw std::runtime_error("cannot allocate OpenSSL SHA-256 context");
    context_ = context;
    if (EVP_DigestInit_ex(context, EVP_sha256(), nullptr) != 1) {
        EVP_MD_CTX_free(context);
        context_ = nullptr;
        throw std::runtime_error("cannot initialize OpenSSL SHA-256 context");
    }
#endif
}

ArtifactSha256::~ArtifactSha256() {
#if defined(TOXSYNC_HAVE_OPENSSL)
    EVP_MD_CTX_free(static_cast<EVP_MD_CTX*>(context_));
#endif
}

ArtifactSha256::ArtifactSha256(ArtifactSha256&& other) noexcept
#if defined(TOXSYNC_HAVE_OPENSSL)
    : context_(std::exchange(other.context_, nullptr)),
#else
    : portable_(std::move(other.portable_)),
#endif
      digest_(other.digest_), finished_(other.finished_) {}

ArtifactSha256& ArtifactSha256::operator=(ArtifactSha256&& other) noexcept {
    if (this == &other) return *this;
#if defined(TOXSYNC_HAVE_OPENSSL)
    EVP_MD_CTX_free(static_cast<EVP_MD_CTX*>(context_));
    context_ = std::exchange(other.context_, nullptr);
#else
    portable_ = std::move(other.portable_);
#endif
    digest_ = other.digest_;
    finished_ = other.finished_;
    return *this;
}

void ArtifactSha256::update(std::span<const std::byte> bytes) {
    if (finished_ || bytes.empty()) return;
#if defined(TOXSYNC_HAVE_OPENSSL)
    if (context_ == nullptr || EVP_DigestUpdate(static_cast<EVP_MD_CTX*>(context_), bytes.data(), bytes.size()) != 1) {
        throw std::runtime_error("OpenSSL SHA-256 update failed");
    }
#else
    portable_.update(bytes);
#endif
}

Digest256 ArtifactSha256::finish() {
    if (finished_) return digest_;
#if defined(TOXSYNC_HAVE_OPENSSL)
    unsigned int length{};
    if (context_ == nullptr ||
        EVP_DigestFinal_ex(static_cast<EVP_MD_CTX*>(context_),
                           reinterpret_cast<unsigned char*>(digest_.bytes.data()), &length) != 1 ||
        length != digest_.bytes.size()) {
        throw std::runtime_error("OpenSSL SHA-256 finalization failed");
    }
#else
    digest_ = portable_.finish();
#endif
    finished_ = true;
    return digest_;
}

} // namespace toxsync::detail

namespace toxsync {

std::string_view sha256_backend_name() noexcept {
#if defined(TOXSYNC_HAVE_OPENSSL)
    return "openssl-evp";
#else
    return "builtin-cpp";
#endif
}

Digest256 sha256(std::span<const std::byte> bytes) {
    detail::ArtifactSha256 hasher;
    hasher.update(bytes);
    return hasher.finish();
}

Digest256 sha256_file(const std::string& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("cannot open file for SHA-256: " + path);
    detail::ArtifactSha256 hasher;
    constexpr std::size_t kBufferBytes = 1024U * 1024U;
    auto buffer = std::make_unique_for_overwrite<std::byte[]>(kBufferBytes);
    while (input) {
        input.read(reinterpret_cast<char*>(buffer.get()), static_cast<std::streamsize>(kBufferBytes));
        const auto count = input.gcount();
        if (count > 0) hasher.update(std::span<const std::byte>(buffer.get(), static_cast<std::size_t>(count)));
    }
    if (!input.eof()) throw std::runtime_error("failed while hashing file: " + path);
    return hasher.finish();
}

} // namespace toxsync
