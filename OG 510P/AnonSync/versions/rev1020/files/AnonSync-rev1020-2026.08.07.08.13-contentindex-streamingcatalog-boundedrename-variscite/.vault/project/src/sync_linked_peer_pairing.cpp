#include "sync_linked_peer_pairing.hpp"

#if !defined(_WIN32)

#include "anonsync_json_parser.hpp"
#include "sha256_digest.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_bounded_regular_file.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_replica_deployment_binding.hpp"
#include "sync_replica_operational_database.hpp"
#include "sync_replica_tls_membership_anchor_sqlite_owner.hpp"
#include "sync_replica_tls_membership_anchored_owner.hpp"
#include "sync_replica_tls_membership_sqlite_owner.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <filesystem>
#include <iomanip>
#include <limits>
#include <memory>
#include <optional>
#include <set>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <openssl/asn1.h>
#include <openssl/bn.h>
#include <openssl/err.h>
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <openssl/rand.h>
#include <openssl/x509.h>
#include <openssl/x509v3.h>

namespace anonsync {
namespace {

namespace fs = std::filesystem;
using BioOwner = std::unique_ptr<BIO, decltype(&BIO_free)>;
using PkeyOwner = std::unique_ptr<EVP_PKEY, decltype(&EVP_PKEY_free)>;
using PkeyContextOwner =
    std::unique_ptr<EVP_PKEY_CTX, decltype(&EVP_PKEY_CTX_free)>;
using MdContextOwner =
    std::unique_ptr<EVP_MD_CTX, decltype(&EVP_MD_CTX_free)>;
using CertificateOwner = std::unique_ptr<X509, decltype(&X509_free)>;
using BignumOwner = std::unique_ptr<BIGNUM, decltype(&BN_free)>;
using Asn1IntegerOwner =
    std::unique_ptr<ASN1_INTEGER, decltype(&ASN1_INTEGER_free)>;
using BasicConstraintsOwner =
    std::unique_ptr<BASIC_CONSTRAINTS, decltype(&BASIC_CONSTRAINTS_free)>;
using Asn1BitStringOwner =
    std::unique_ptr<ASN1_BIT_STRING, decltype(&ASN1_BIT_STRING_free)>;
using ExtendedKeyUsageOwner =
    std::unique_ptr<EXTENDED_KEY_USAGE, decltype(&EXTENDED_KEY_USAGE_free)>;
using ExtensionOwner =
    std::unique_ptr<X509_EXTENSION, decltype(&X509_EXTENSION_free)>;

constexpr std::string_view kCardSignatureDomain =
    "anonsync:linked-peer-card:v1";
constexpr std::size_t kEd25519SignatureBytes = 64U;
constexpr std::uint64_t kMaximumExactJsonInteger = 9007199254740991ULL;
constexpr long kIdentityCertificateLifetimeSeconds =
    20L * 365L * 24L * 60L * 60L;

[[nodiscard]] std::string child_label(
    std::string_view label,
    std::string_view child) {
    return std::string(label) + " " + std::string(child);
}

[[nodiscard]] std::string openssl_errors() {
    std::string output;
    for (unsigned long code = ERR_get_error(); code != 0UL;
         code = ERR_get_error()) {
        char text[256]{};
        ERR_error_string_n(code, text, sizeof(text));
        if (!output.empty()) output += "; ";
        output += text;
    }
    return output.empty() ? "no OpenSSL detail" : output;
}

[[noreturn]] void throw_openssl(std::string_view message) {
    throw std::runtime_error(
        std::string(message) + ": " + openssl_errors());
}

[[nodiscard]] std::string json_quote(std::string_view value) {
    std::ostringstream output;
    output << '"';
    for (const unsigned char byte : value) {
        switch (byte) {
            case '"': output << "\\\""; break;
            case '\\': output << "\\\\"; break;
            case '\b': output << "\\b"; break;
            case '\f': output << "\\f"; break;
            case '\n': output << "\\n"; break;
            case '\r': output << "\\r"; break;
            case '\t': output << "\\t"; break;
            default:
                if (byte < 0x20U) {
                    output << "\\u00" << std::hex << std::setw(2)
                           << std::setfill('0')
                           << static_cast<unsigned int>(byte)
                           << std::dec << std::setfill(' ');
                } else {
                    output << static_cast<char>(byte);
                }
        }
    }
    output << '"';
    return output.str();
}

[[nodiscard]] std::span<const unsigned char> byte_span(
    const std::string& value) noexcept {
    return {
        reinterpret_cast<const unsigned char*>(value.data()), value.size()};
}

[[nodiscard]] fs::path normalized_absolute_file_or_throw(
    const fs::path& path,
    std::string_view label) {
    if (path.empty() || !path.is_absolute() ||
        path.lexically_normal() != path || path.filename().empty()) {
        throw std::invalid_argument(
            std::string(label) +
            " must be a lexically normalized absolute file path");
    }
    return path;
}

[[nodiscard]] bool path_entry_exists_or_throw(
    const fs::path& path,
    std::string_view label) {
    std::error_code error;
    const fs::file_status status = fs::symlink_status(path, error);
    if (!error) return status.type() != fs::file_type::not_found;
    if (error == std::errc::no_such_file_or_directory) return false;
    throw std::runtime_error(
        std::string(label) + " could not inspect " +
        path.generic_string() + ": " + error.message());
}

[[nodiscard]] std::string bio_bytes_or_throw(
    BIO* bio,
    std::string_view label) {
    if (bio == nullptr) {
        throw std::invalid_argument(
            std::string(label) + " BIO is null");
    }
    BUF_MEM* memory = nullptr;
    BIO_get_mem_ptr(bio, &memory);
    if (memory == nullptr || memory->data == nullptr || memory->length == 0U) {
        throw std::runtime_error(
            std::string(label) + " produced no bytes");
    }
    return std::string(memory->data, memory->length);
}

[[nodiscard]] std::string encode_private_key_or_throw(
    EVP_PKEY* key,
    std::string_view label) {
    BioOwner output(BIO_new(BIO_s_mem()), BIO_free);
    if (!output) throw_openssl(child_label(label, "memory BIO"));
    ERR_clear_error();
    if (PEM_write_bio_PrivateKey(
            output.get(), key, nullptr, nullptr, 0, nullptr, nullptr) != 1) {
        throw_openssl(child_label(label, "PEM encoding"));
    }
    return bio_bytes_or_throw(output.get(), label);
}

[[nodiscard]] std::string encode_certificate_or_throw(
    X509* certificate,
    std::string_view label) {
    BioOwner output(BIO_new(BIO_s_mem()), BIO_free);
    if (!output) throw_openssl(child_label(label, "memory BIO"));
    ERR_clear_error();
    if (PEM_write_bio_X509(output.get(), certificate) != 1) {
        throw_openssl(child_label(label, "PEM encoding"));
    }
    return bio_bytes_or_throw(output.get(), label);
}

void require_trailing_ascii_whitespace_or_throw(
    BIO* input,
    std::string_view label) {
    std::array<char, 256U> buffer{};
    for (;;) {
        const int read = BIO_read(
            input, buffer.data(), static_cast<int>(buffer.size()));
        if (read < 0) throw_openssl(child_label(label, "trailing read"));
        if (read == 0) break;
        for (int index = 0; index < read; ++index) {
            const unsigned char byte =
                static_cast<unsigned char>(buffer[static_cast<std::size_t>(index)]);
            if (byte != ' ' && byte != '\t' && byte != '\r' && byte != '\n') {
                throw std::invalid_argument(
                    std::string(label) +
                    " contains trailing non-whitespace PEM bytes");
            }
        }
    }
}

[[nodiscard]] PkeyOwner parse_private_key_or_throw(
    const std::string& exact,
    std::string_view label) {
    if (exact.empty() || exact.size() > kSyncLinkedPeerIdentityFileMaximumBytes) {
        throw std::invalid_argument(
            std::string(label) + " private key size is invalid");
    }
    BioOwner input(
        BIO_new_mem_buf(exact.data(), static_cast<int>(exact.size())),
        BIO_free);
    if (!input) throw_openssl(child_label(label, "input BIO"));
    ERR_clear_error();
    PkeyOwner key(
        PEM_read_bio_PrivateKey(input.get(), nullptr, nullptr, nullptr),
        EVP_PKEY_free);
    if (!key) throw_openssl(child_label(label, "PEM parse"));
    require_trailing_ascii_whitespace_or_throw(input.get(), label);
    if (EVP_PKEY_base_id(key.get()) != EVP_PKEY_ED25519) {
        throw std::invalid_argument(
            std::string(label) + " private key is not Ed25519");
    }
    const std::string canonical = encode_private_key_or_throw(key.get(), label);
    if (canonical != exact) {
        throw std::invalid_argument(
            std::string(label) + " private key is not canonical AnonSync PEM");
    }
    return key;
}

[[nodiscard]] bool certificate_extension_is_critical(
    X509* certificate,
    int nid) {
    const int index = X509_get_ext_by_NID(certificate, nid, -1);
    if (index < 0) return false;
    X509_EXTENSION* extension = X509_get_ext(certificate, index);
    return extension != nullptr && X509_EXTENSION_get_critical(extension) == 1;
}

void validate_certificate_profile_or_throw(
    X509* certificate,
    std::string_view label) {
    if (certificate == nullptr) {
        throw std::invalid_argument(
            std::string(label) + " certificate is null");
    }
    if (X509_get_version(certificate) != 2L) {
        throw std::invalid_argument(
            std::string(label) + " certificate is not X.509 v3");
    }
    PkeyOwner public_key(X509_get_pubkey(certificate), EVP_PKEY_free);
    if (!public_key) throw_openssl(child_label(label, "public key"));
    if (EVP_PKEY_base_id(public_key.get()) != EVP_PKEY_ED25519) {
        throw std::invalid_argument(
            std::string(label) + " certificate key is not Ed25519");
    }
    if (X509_NAME_cmp(
            X509_get_subject_name(certificate),
            X509_get_issuer_name(certificate)) != 0) {
        throw std::invalid_argument(
            std::string(label) + " certificate is not self-issued");
    }
    ERR_clear_error();
    if (X509_verify(certificate, public_key.get()) != 1) {
        throw_openssl(child_label(label, "self-signature verification"));
    }
    if (X509_cmp_current_time(X509_get0_notBefore(certificate)) > 0 ||
        X509_cmp_current_time(X509_get0_notAfter(certificate)) < 0) {
        throw std::invalid_argument(
            std::string(label) + " certificate is not currently valid");
    }

    BasicConstraintsOwner constraints(
        static_cast<BASIC_CONSTRAINTS*>(
            X509_get_ext_d2i(
                certificate, NID_basic_constraints, nullptr, nullptr)),
        BASIC_CONSTRAINTS_free);
    if (!constraints || constraints->ca == 0 ||
        constraints->pathlen == nullptr ||
        ASN1_INTEGER_get(constraints->pathlen) != 0L ||
        !certificate_extension_is_critical(
            certificate, NID_basic_constraints)) {
        throw std::invalid_argument(
            std::string(label) +
            " certificate lacks critical CA:TRUE,pathlen:0 constraints");
    }

    Asn1BitStringOwner key_usage(
        static_cast<ASN1_BIT_STRING*>(
            X509_get_ext_d2i(certificate, NID_key_usage, nullptr, nullptr)),
        ASN1_BIT_STRING_free);
    if (!key_usage || ASN1_BIT_STRING_get_bit(key_usage.get(), 0) != 1 ||
        ASN1_BIT_STRING_get_bit(key_usage.get(), 5) != 1 ||
        !certificate_extension_is_critical(certificate, NID_key_usage)) {
        throw std::invalid_argument(
            std::string(label) +
            " certificate lacks critical digitalSignature/keyCertSign usage");
    }

    ExtendedKeyUsageOwner extended_usage(
        static_cast<EXTENDED_KEY_USAGE*>(
            X509_get_ext_d2i(
                certificate, NID_ext_key_usage, nullptr, nullptr)),
        EXTENDED_KEY_USAGE_free);
    bool client = false;
    bool server = false;
    if (extended_usage) {
        const int count = sk_ASN1_OBJECT_num(extended_usage.get());
        for (int index = 0; index < count; ++index) {
            const int nid = OBJ_obj2nid(
                sk_ASN1_OBJECT_value(extended_usage.get(), index));
            client = client || nid == NID_client_auth;
            server = server || nid == NID_server_auth;
        }
    }
    if (!client || !server ||
        !certificate_extension_is_critical(
            certificate, NID_ext_key_usage)) {
        throw std::invalid_argument(
            std::string(label) +
            " certificate lacks critical clientAuth/serverAuth usage");
    }
}

[[nodiscard]] CertificateOwner parse_certificate_or_throw(
    const std::string& exact,
    std::string_view label) {
    if (exact.empty() || exact.size() > kSyncLinkedPeerIdentityFileMaximumBytes) {
        throw std::invalid_argument(
            std::string(label) + " certificate size is invalid");
    }
    BioOwner input(
        BIO_new_mem_buf(exact.data(), static_cast<int>(exact.size())),
        BIO_free);
    if (!input) throw_openssl(child_label(label, "input BIO"));
    ERR_clear_error();
    CertificateOwner certificate(
        PEM_read_bio_X509(input.get(), nullptr, nullptr, nullptr), X509_free);
    if (!certificate) throw_openssl(child_label(label, "PEM parse"));
    require_trailing_ascii_whitespace_or_throw(input.get(), label);
    validate_certificate_profile_or_throw(certificate.get(), label);
    const std::string canonical =
        encode_certificate_or_throw(certificate.get(), label);
    if (canonical != exact) {
        throw std::invalid_argument(
            std::string(label) +
            " certificate is not canonical AnonSync PEM");
    }
    return certificate;
}

[[nodiscard]] std::string certificate_spki_sha256_or_throw(
    X509* certificate,
    std::string_view label) {
    X509_PUBKEY* public_key = X509_get_X509_PUBKEY(certificate);
    if (public_key == nullptr) {
        throw std::invalid_argument(
            std::string(label) + " certificate has no SubjectPublicKeyInfo");
    }
    const int encoded_bytes = i2d_X509_PUBKEY(public_key, nullptr);
    if (encoded_bytes <= 0) {
        throw_openssl(child_label(label, "SPKI size"));
    }
    std::string encoded(static_cast<std::size_t>(encoded_bytes), '\0');
    unsigned char* output =
        reinterpret_cast<unsigned char*>(encoded.data());
    if (i2d_X509_PUBKEY(public_key, &output) != encoded_bytes) {
        throw_openssl(child_label(label, "SPKI encoding"));
    }
    return sha256_hex(encoded);
}

[[nodiscard]] PkeyOwner generate_ed25519_key_or_throw(
    std::string_view label) {
    ERR_clear_error();
    PkeyContextOwner context(
        EVP_PKEY_CTX_new_id(EVP_PKEY_ED25519, nullptr), EVP_PKEY_CTX_free);
    if (!context) throw_openssl(child_label(label, "key context"));
    if (EVP_PKEY_keygen_init(context.get()) != 1) {
        throw_openssl(child_label(label, "keygen init"));
    }
    EVP_PKEY* raw = nullptr;
    if (EVP_PKEY_keygen(context.get(), &raw) != 1 || raw == nullptr) {
        throw_openssl(child_label(label, "key generation"));
    }
    return PkeyOwner(raw, EVP_PKEY_free);
}

void add_certificate_extension_or_throw(
    X509* certificate,
    X509V3_CTX* context,
    int nid,
    const char* value,
    std::string_view label) {
    ERR_clear_error();
    ExtensionOwner extension(
        X509V3_EXT_conf_nid(nullptr, context, nid, value),
        X509_EXTENSION_free);
    if (!extension) throw_openssl(child_label(label, "extension creation"));
    if (X509_add_ext(certificate, extension.get(), -1) != 1) {
        throw_openssl(child_label(label, "extension append"));
    }
}

[[nodiscard]] CertificateOwner generate_certificate_or_throw(
    EVP_PKEY* key,
    const SyncReplicaDeploymentManifest& deployment,
    std::string_view label) {
    CertificateOwner certificate(X509_new(), X509_free);
    if (!certificate) throw_openssl(child_label(label, "allocation"));
    if (X509_set_version(certificate.get(), 2L) != 1) {
        throw_openssl(child_label(label, "version"));
    }

    std::array<unsigned char, 16U> serial_bytes{};
    ERR_clear_error();
    if (RAND_bytes(
            serial_bytes.data(), static_cast<int>(serial_bytes.size())) != 1) {
        throw_openssl(child_label(label, "serial generation"));
    }
    serial_bytes.front() &= 0x7fU;
    if (std::all_of(
            serial_bytes.begin(), serial_bytes.end(),
            [](unsigned char byte) { return byte == 0U; })) {
        serial_bytes.back() = 1U;
    }
    BignumOwner serial_bn(
        BN_bin2bn(
            serial_bytes.data(), static_cast<int>(serial_bytes.size()),
            nullptr),
        BN_free);
    Asn1IntegerOwner serial(ASN1_INTEGER_new(), ASN1_INTEGER_free);
    if (!serial_bn || !serial ||
        BN_to_ASN1_INTEGER(serial_bn.get(), serial.get()) == nullptr ||
        X509_set_serialNumber(certificate.get(), serial.get()) != 1) {
        throw_openssl(child_label(label, "serial encoding"));
    }

    if (X509_gmtime_adj(X509_getm_notBefore(certificate.get()), -300L) ==
            nullptr ||
        X509_gmtime_adj(
            X509_getm_notAfter(certificate.get()),
            kIdentityCertificateLifetimeSeconds) == nullptr) {
        throw_openssl(child_label(label, "validity"));
    }
    if (X509_set_pubkey(certificate.get(), key) != 1) {
        throw_openssl(child_label(label, "public key"));
    }

    X509_NAME* subject = X509_get_subject_name(certificate.get());
    if (subject == nullptr ||
        X509_NAME_add_entry_by_txt(
            subject, "CN", MBSTRING_ASC,
            reinterpret_cast<const unsigned char*>("AnonSync linked peer"),
            -1, -1, 0) != 1 ||
        X509_NAME_add_entry_by_txt(
            subject, "OU", MBSTRING_ASC,
            reinterpret_cast<const unsigned char*>(
                deployment.local_actor.device_id.c_str()),
            -1, -1, 0) != 1 ||
        X509_set_issuer_name(certificate.get(), subject) != 1) {
        throw_openssl(child_label(label, "subject"));
    }

    X509V3_CTX extension_context;
    X509V3_set_ctx_nodb(&extension_context);
    X509V3_set_ctx(
        &extension_context, certificate.get(), certificate.get(), nullptr,
        nullptr, 0);
    add_certificate_extension_or_throw(
        certificate.get(), &extension_context, NID_basic_constraints,
        "critical,CA:TRUE,pathlen:0", label);
    add_certificate_extension_or_throw(
        certificate.get(), &extension_context, NID_key_usage,
        "critical,digitalSignature,keyCertSign", label);
    add_certificate_extension_or_throw(
        certificate.get(), &extension_context, NID_ext_key_usage,
        "critical,clientAuth,serverAuth", label);
    add_certificate_extension_or_throw(
        certificate.get(), &extension_context, NID_subject_key_identifier,
        "hash", label);
    add_certificate_extension_or_throw(
        certificate.get(), &extension_context, NID_authority_key_identifier,
        "keyid:always", label);

    ERR_clear_error();
    if (X509_sign(certificate.get(), key, nullptr) <= 0) {
        throw_openssl(child_label(label, "self-signature"));
    }
    validate_certificate_profile_or_throw(certificate.get(), label);
    return certificate;
}

[[nodiscard]] std::string encode_unsigned_card(
    const SyncLinkedPeerCard& card) {
    std::ostringstream output;
    output << "{\"schema\":" << json_quote(card.schema)
           << ",\"folder_id\":" << json_quote(card.folder_id)
           << ",\"device_id\":" << json_quote(card.actor.device_id)
           << ",\"epoch\":" << card.actor.epoch
           << ",\"spki_sha256\":" << json_quote(card.spki_sha256)
           << ",\"certificate_pem\":"
           << json_quote(card.certificate_pem) << "}";
    return output.str();
}

[[nodiscard]] std::string signature_message(
    const SyncLinkedPeerCard& card) {
    const std::string unsigned_card = encode_unsigned_card(card);
    std::string message;
    message.reserve(
        kCardSignatureDomain.size() + 1U + unsigned_card.size());
    message.append(kCardSignatureDomain);
    message.push_back('\0');
    message.append(unsigned_card);
    return message;
}

[[nodiscard]] std::string hex_encode(
    std::span<const unsigned char> bytes) {
    constexpr std::string_view hex = "0123456789abcdef";
    std::string output;
    output.reserve(bytes.size() * 2U);
    for (const unsigned char byte : bytes) {
        output.push_back(hex[byte >> 4U]);
        output.push_back(hex[byte & 0x0fU]);
    }
    return output;
}

[[nodiscard]] std::vector<unsigned char> hex_decode_or_throw(
    std::string_view encoded,
    std::size_t expected_bytes,
    std::string_view label) {
    if (encoded.size() != expected_bytes * 2U) {
        throw std::invalid_argument(
            std::string(label) + " has the wrong hexadecimal length");
    }
    auto nibble = [&](char character) -> unsigned char {
        if (character >= '0' && character <= '9') {
            return static_cast<unsigned char>(character - '0');
        }
        if (character >= 'a' && character <= 'f') {
            return static_cast<unsigned char>(10 + character - 'a');
        }
        throw std::invalid_argument(
            std::string(label) + " is not lowercase hexadecimal");
    };
    std::vector<unsigned char> output(expected_bytes);
    for (std::size_t index = 0U; index < expected_bytes; ++index) {
        output[index] = static_cast<unsigned char>(
            (nibble(encoded[index * 2U]) << 4U) |
            nibble(encoded[index * 2U + 1U]));
    }
    return output;
}

[[nodiscard]] std::string sign_card_or_throw(
    const SyncLinkedPeerCard& card,
    EVP_PKEY* key,
    std::string_view label) {
    const std::string message = signature_message(card);
    MdContextOwner context(EVP_MD_CTX_new(), EVP_MD_CTX_free);
    if (!context) throw_openssl(child_label(label, "signature context"));
    ERR_clear_error();
    if (EVP_DigestSignInit(
            context.get(), nullptr, nullptr, nullptr, key) != 1) {
        throw_openssl(child_label(label, "signature init"));
    }
    std::array<unsigned char, kEd25519SignatureBytes> signature{};
    std::size_t size = signature.size();
    if (EVP_DigestSign(
            context.get(), signature.data(), &size,
            reinterpret_cast<const unsigned char*>(message.data()),
            message.size()) != 1 ||
        size != signature.size()) {
        throw_openssl(child_label(label, "signature"));
    }
    return hex_encode(signature);
}

void verify_card_signature_or_throw(
    const SyncLinkedPeerCard& card,
    X509* certificate,
    std::string_view label) {
    const std::vector<unsigned char> signature = hex_decode_or_throw(
        card.signature_ed25519, kEd25519SignatureBytes,
        child_label(label, "signature"));
    PkeyOwner key(X509_get_pubkey(certificate), EVP_PKEY_free);
    if (!key) throw_openssl(child_label(label, "public key"));
    const std::string message = signature_message(card);
    MdContextOwner context(EVP_MD_CTX_new(), EVP_MD_CTX_free);
    if (!context) throw_openssl(child_label(label, "verify context"));
    ERR_clear_error();
    if (EVP_DigestVerifyInit(
            context.get(), nullptr, nullptr, nullptr, key.get()) != 1) {
        throw_openssl(child_label(label, "verify init"));
    }
    const int verified = EVP_DigestVerify(
        context.get(), signature.data(), signature.size(),
        reinterpret_cast<const unsigned char*>(message.data()),
        message.size());
    if (verified != 1) {
        if (verified < 0) throw_openssl(child_label(label, "verification"));
        throw std::invalid_argument(
            std::string(label) + " signature does not verify");
    }
}

[[nodiscard]] std::string encode_card(const SyncLinkedPeerCard& card) {
    const std::string unsigned_card = encode_unsigned_card(card);
    std::string exact = unsigned_card;
    exact.pop_back();
    exact += ",\"signature_ed25519\":";
    exact += json_quote(card.signature_ed25519);
    exact += "}\n";
    return exact;
}

[[nodiscard]] const Json& require_object_field(
    const Json& object,
    std::string_view key,
    std::string_view label) {
    if (!object.is_object()) {
        throw std::invalid_argument(
            std::string(label) + " root is not an object");
    }
    const auto found = object.o.find(std::string(key));
    if (found == object.o.end()) {
        throw std::invalid_argument(
            std::string(label) + " is missing field " + std::string(key));
    }
    return found->second;
}

[[nodiscard]] std::string require_string_field(
    const Json& object,
    std::string_view key,
    std::string_view label) {
    const Json& value = require_object_field(object, key, label);
    if (!value.is_string() || value.s.empty()) {
        throw std::invalid_argument(
            std::string(label) + " field " + std::string(key) +
            " must be a nonempty string");
    }
    return value.s;
}

[[nodiscard]] std::uint64_t require_u64_field(
    const Json& object,
    std::string_view key,
    std::string_view label) {
    const Json& value = require_object_field(object, key, label);
    if (!value.is_number()) {
        throw std::invalid_argument(
            std::string(label) + " field " + std::string(key) +
            " must be an integer");
    }
    const long long signed_value = value.integer(-1);
    if (signed_value <= 0) {
        throw std::invalid_argument(
            std::string(label) + " field " + std::string(key) +
            " must be positive");
    }
    return static_cast<std::uint64_t>(signed_value);
}

void require_exact_card_keys_or_throw(
    const Json& root,
    std::string_view label) {
    static const std::set<std::string> expected{
        "schema", "folder_id", "device_id", "epoch", "spki_sha256",
        "certificate_pem", "signature_ed25519"};
    if (!root.is_object() || root.o.size() != expected.size()) {
        throw std::invalid_argument(
            std::string(label) + " has missing or unknown fields");
    }
    for (const auto& [key, ignored] : root.o) {
        (void)ignored;
        if (!expected.contains(key)) {
            throw std::invalid_argument(
                std::string(label) + " contains unknown field " + key);
        }
    }
}

[[nodiscard]] SyncLinkedPeerCard decode_card_or_throw(
    const std::string& exact,
    std::string_view label) {
    if (exact.empty() || exact.size() > kSyncLinkedPeerCardMaximumBytes) {
        throw std::invalid_argument(
            std::string(label) + " size is invalid");
    }
    Json root;
    try {
        root = parse_json_text(exact);
    } catch (const std::exception& error) {
        throw std::invalid_argument(
            std::string(label) + " JSON is invalid: " + error.what());
    }
    require_exact_card_keys_or_throw(root, label);
    SyncLinkedPeerCard card{
        .schema = require_string_field(root, "schema", label),
        .folder_id = require_string_field(root, "folder_id", label),
        .actor = {
            .device_id = require_string_field(root, "device_id", label),
            .epoch = require_u64_field(root, "epoch", label),
        },
        .spki_sha256 = require_string_field(root, "spki_sha256", label),
        .certificate_pem =
            require_string_field(root, "certificate_pem", label),
        .signature_ed25519 =
            require_string_field(root, "signature_ed25519", label),
    };
    if (card.schema != kSyncLinkedPeerCardSchema) {
        throw std::invalid_argument(
            std::string(label) + " schema is unsupported");
    }
    if (!sync_id_is_valid(card.folder_id) ||
        !sync_id_is_valid(card.actor.device_id)) {
        throw std::invalid_argument(
            std::string(label) + " folder/device identity is invalid");
    }
    if (!is_lowercase_sha256_hex(card.spki_sha256)) {
        throw std::invalid_argument(
            std::string(label) + " SPKI is not lowercase SHA-256");
    }
    CertificateOwner certificate = parse_certificate_or_throw(
        card.certificate_pem, child_label(label, "certificate"));
    if (certificate_spki_sha256_or_throw(certificate.get(), label) !=
        card.spki_sha256) {
        throw std::invalid_argument(
            std::string(label) + " SPKI does not match its certificate");
    }
    verify_card_signature_or_throw(card, certificate.get(), label);
    if (encode_card(card) != exact) {
        throw std::invalid_argument(
            std::string(label) + " is not canonical linked-peer-card JSON");
    }
    return card;
}

void validate_identity_layout_or_throw(
    const SyncLinkedPeerIdentityLayout& layout,
    std::string_view label) {
    if (!sync_id_is_valid(layout.instance)) {
        throw std::invalid_argument(
            std::string(label) + " layout instance is invalid");
    }
    if (layout.identity_directory.empty() ||
        !layout.identity_directory.is_absolute() ||
        layout.identity_directory.lexically_normal() !=
            layout.identity_directory ||
        layout.identity_directory.filename() != layout.instance) {
        throw std::invalid_argument(
            std::string(label) + " identity directory is invalid");
    }
    const std::array<std::pair<const fs::path*, std::string_view>, 4U> files{{
        {&layout.private_key_path, "local.key"},
        {&layout.certificate_path, "local.pem"},
        {&layout.pairing_card_path, "pairing-card.json"},
        {&layout.peer_trust_path, "peer-trust.pem"},
    }};
    for (const auto& [path, basename] : files) {
        if (path->parent_path() != layout.identity_directory ||
            path->filename() != basename) {
            throw std::invalid_argument(
                std::string(label) + " layout file path is invalid");
        }
    }
}

[[nodiscard]] SyncReplicaSqliteDeploymentBinding
binding_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const fs::path& path,
    SyncReplicaSqliteDeploymentRole role,
    std::string_view label) {
    return {
        .deployment = sync_replica_deployment_identity_or_throw(
            deployment, child_label(label, "deployment identity")),
        .role = role,
        .database_path = path,
    };
}

[[nodiscard]] SyncReplicaOperationalDatabase
open_bound_database_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const fs::path& path,
    SyncReplicaSqliteDeploymentRole role,
    std::string_view label) {
    SyncReplicaOperationalDatabase database =
        SyncReplicaOperationalDatabase::open_or_throw(
            path,
            SyncReplicaOperationalDatabaseOpenDisposition::ExistingOperational,
            std::string(label));
    attest_sync_replica_sqlite_deployment_binding_or_throw(
        database.handle(), binding_or_throw(deployment, path, role, label),
        child_label(label, "deployment binding"));
    return database;
}

}  // namespace

const char* sync_linked_peer_identity_file_disposition_name(
    SyncLinkedPeerIdentityFileDisposition disposition) noexcept {
    switch (disposition) {
        case SyncLinkedPeerIdentityFileDisposition::Created:
            return "created";
        case SyncLinkedPeerIdentityFileDisposition::ReusedExact:
            return "reused_exact";
    }
    return "unknown";
}

SyncLinkedPeerIdentityCreationResult
create_or_resume_sync_linked_peer_identity_or_throw(
    const SyncLinkedPeerIdentityLayout& layout,
    const SyncReplicaDeploymentManifest& deployment,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync linked-peer identity creation label is empty");
    }
    validate_sync_replica_deployment_manifest_or_throw(deployment, label);
    validate_identity_layout_or_throw(layout, label);

    // The durable identity is published as one strict prefix:
    //
    //   private key -> matching certificate -> signed public card
    //
    // A later artifact without every predecessor cannot be a crash cutpoint
    // produced by this owner. Reject such a suffix before generating or
    // publishing replacement material, especially before creating a new key
    // beside an orphaned certificate.
    const bool key_exists = path_entry_exists_or_throw(
        layout.private_key_path, child_label(label, "private key"));
    const bool certificate_exists = path_entry_exists_or_throw(
        layout.certificate_path, child_label(label, "certificate"));
    const bool card_exists = path_entry_exists_or_throw(
        layout.pairing_card_path, child_label(label, "pairing card"));
    if (certificate_exists && !key_exists) {
        throw std::runtime_error(
            label + " identity has a certificate without its private key");
    }
    if (card_exists && (!key_exists || !certificate_exists)) {
        throw std::runtime_error(
            label +
            " identity has a pairing card without its complete key and "
            "certificate prefix");
    }

    SyncLinkedPeerIdentityFileDisposition key_disposition =
        SyncLinkedPeerIdentityFileDisposition::Created;
    PkeyOwner key(nullptr, EVP_PKEY_free);
    std::string key_pem;
    if (key_exists) {
        key_pem = read_sync_bounded_private_regular_file_no_symlink_or_throw(
            layout.private_key_path, kSyncLinkedPeerIdentityFileMaximumBytes,
            child_label(label, "private key"));
        key = parse_private_key_or_throw(
            key_pem, child_label(label, "private key"));
        key_disposition =
            SyncLinkedPeerIdentityFileDisposition::ReusedExact;
    } else {
        key = generate_ed25519_key_or_throw(child_label(label, "private key"));
        key_pem = encode_private_key_or_throw(
            key.get(), child_label(label, "private key"));
        write_sync_file_atomically_create_new_no_symlink_or_throw(
            layout.private_key_path, byte_span(key_pem),
            child_label(label, "private-key publication"));
    }

    SyncLinkedPeerIdentityFileDisposition certificate_disposition =
        SyncLinkedPeerIdentityFileDisposition::Created;
    CertificateOwner certificate(nullptr, X509_free);
    std::string certificate_pem;
    if (certificate_exists) {
        certificate_pem =
            read_sync_bounded_private_regular_file_no_symlink_or_throw(
                layout.certificate_path,
                kSyncLinkedPeerIdentityFileMaximumBytes,
                child_label(label, "certificate"));
        certificate = parse_certificate_or_throw(
            certificate_pem, child_label(label, "certificate"));
        ERR_clear_error();
        if (X509_check_private_key(certificate.get(), key.get()) != 1) {
            throw_openssl(
                child_label(label, "certificate/private-key match"));
        }
        certificate_disposition =
            SyncLinkedPeerIdentityFileDisposition::ReusedExact;
    } else {
        certificate = generate_certificate_or_throw(
            key.get(), deployment, child_label(label, "certificate"));
        certificate_pem = encode_certificate_or_throw(
            certificate.get(), child_label(label, "certificate"));
        write_sync_file_atomically_create_new_no_symlink_or_throw(
            layout.certificate_path, byte_span(certificate_pem),
            child_label(label, "certificate publication"));
    }

    SyncLinkedPeerCard card{
        .schema = std::string(kSyncLinkedPeerCardSchema),
        .folder_id = deployment.folder_id,
        .actor = deployment.local_actor,
        .spki_sha256 = certificate_spki_sha256_or_throw(
            certificate.get(), child_label(label, "certificate")),
        .certificate_pem = certificate_pem,
        .signature_ed25519 = {},
    };
    card.signature_ed25519 = sign_card_or_throw(
        card, key.get(), child_label(label, "pairing card"));
    const std::string exact_card = encode_card(card);
    if (exact_card.size() > kSyncLinkedPeerCardMaximumBytes) {
        throw std::length_error(
            label + " pairing card exceeds its byte limit");
    }

    SyncLinkedPeerIdentityFileDisposition card_disposition =
        SyncLinkedPeerIdentityFileDisposition::Created;
    if (card_exists) {
        const std::string existing =
            read_sync_bounded_private_regular_file_no_symlink_or_throw(
                layout.pairing_card_path, kSyncLinkedPeerCardMaximumBytes,
                child_label(label, "pairing card"));
        const SyncLinkedPeerCard decoded = decode_card_or_throw(
            existing, child_label(label, "pairing card"));
        if (decoded != card || existing != exact_card) {
            throw std::runtime_error(
                label + " pairing card conflicts with local identity");
        }
        card_disposition =
            SyncLinkedPeerIdentityFileDisposition::ReusedExact;
    } else {
        write_sync_json_file_atomically_create_new_no_symlink_or_throw(
            layout.pairing_card_path, exact_card,
            child_label(label, "pairing-card publication"));
    }

    return {
        .layout = layout,
        .card = std::move(card),
        .private_key_disposition = key_disposition,
        .certificate_disposition = certificate_disposition,
        .pairing_card_disposition = card_disposition,
    };
}

SyncLinkedPeerCard read_sync_linked_peer_card_file_or_throw(
    const fs::path& absolute_card_path,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument("sync linked-peer card label is empty");
    }
    const fs::path path = normalized_absolute_file_or_throw(
        absolute_card_path, label);
    const std::string exact =
        read_sync_bounded_regular_file_no_symlink_or_throw(
            path, kSyncLinkedPeerCardMaximumBytes, label);
    return decode_card_or_throw(exact, label);
}

std::string sync_linked_peer_card_sha256_or_throw(
    const SyncLinkedPeerCard& card,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync linked-peer card fingerprint label is empty");
    }
    const std::string exact = encode_card(card);
    (void)decode_card_or_throw(exact, label);
    return sha256_hex(exact);
}

std::string sync_linked_peer_card_verification_code_or_throw(
    const SyncLinkedPeerCard& card,
    std::string_view label_view) {
    const std::string digest = sync_linked_peer_card_sha256_or_throw(
        card, label_view);
    constexpr std::size_t kVerificationHexDigits = 32U;
    constexpr std::size_t kGroupHexDigits = 4U;
    std::string code;
    code.reserve(
        kVerificationHexDigits +
        (kVerificationHexDigits / kGroupHexDigits - 1U));
    for (std::size_t index = 0U; index < kVerificationHexDigits; ++index) {
        if (index != 0U && index % kGroupHexDigits == 0U) {
            code.push_back('-');
        }
        code.push_back(digest[index]);
    }
    return code;
}

SyncLinkedPeerAdmissionResult admit_sync_linked_peer_card_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const SyncLinkedPeerCard& peer_card,
    const fs::path& absolute_peer_trust_path,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync linked-peer admission label is empty");
    }
    validate_sync_replica_deployment_manifest_or_throw(deployment, label);
    if (!deployment.membership_db.has_value() ||
        !deployment.anchor_db.has_value()) {
        throw std::invalid_argument(
            label + " deployment lacks membership and anchor stores");
    }

    // Re-encode/decode is the public-card validation boundary for in-memory
    // callers too. It proves the signature, certificate profile, exact SPKI,
    // and canonical schema instead of trusting a freely assembled struct.
    const SyncLinkedPeerCard card = decode_card_or_throw(
        encode_card(peer_card), child_label(label, "peer card"));
    if (card.folder_id != deployment.folder_id) {
        throw std::invalid_argument(
            label + " peer card is for a different folder");
    }
    if (card.actor.device_id == deployment.local_actor.device_id) {
        throw std::invalid_argument(
            label + " refuses a card for the local device ID");
    }

    const fs::path trust_path = normalized_absolute_file_or_throw(
        absolute_peer_trust_path, child_label(label, "peer trust path"));
    bool trust_created = false;
    const auto reconciled =
        reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            trust_path, byte_span(card.certificate_pem),
            child_label(label, "peer trust reconciliation"));
    switch (reconciled) {
        case SyncImmutableFileReconciliationOutcome::Absent:
            write_sync_file_atomically_create_new_no_symlink_or_throw(
                trust_path, byte_span(card.certificate_pem),
                child_label(label, "peer trust publication"));
            trust_created = true;
            break;
        case SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced:
            break;
        case SyncImmutableFileReconciliationOutcome::ConflictingEntry:
            throw std::runtime_error(
                label + " peer trust path contains conflicting material");
    }

    SyncReplicaOperationalDatabase membership_database =
        open_bound_database_or_throw(
            deployment, *deployment.membership_db,
            SyncReplicaSqliteDeploymentRole::TlsMembership,
            child_label(label, "membership database"));
    SyncReplicaOperationalDatabase anchor_database =
        open_bound_database_or_throw(
            deployment, *deployment.anchor_db,
            SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor,
            child_label(label, "membership anchor database"));
    SyncReplicaTlsMembershipSqliteOwner membership_owner(
        membership_database.handle(), deployment.folder_id,
        deployment.local_actor, child_label(label, "membership owner"));
    SyncReplicaTlsMembershipAnchorSqliteOwner anchor_owner(
        anchor_database.handle(), deployment.folder_id,
        deployment.local_actor, child_label(label, "anchor owner"));
    SyncReplicaTlsMembershipAnchoredOwner coordinator(
        membership_owner, anchor_owner,
        child_label(label, "anchored membership owner"));
    const SyncReplicaTlsMembershipAnchorCoverageResult coverage =
        coordinator.reconcile_or_throw();
    const SyncReplicaTlsMembershipSqliteSnapshot snapshot =
        membership_owner.snapshot_or_throw(coverage.durable_anchor);

    std::vector<SyncReplicaTlsMembershipEntry> entries;
    entries.reserve(
        static_cast<std::size_t>(snapshot.current_entry_count) + 1U);
    bool exact_member = false;
    if (snapshot.current_authority.has_value()) {
        for (const SyncReplicaTlsMembershipEntry& entry :
             snapshot.current_authority->snapshot().entries()) {
            if (entry.actor == card.actor &&
                entry.spki_sha256 == card.spki_sha256) {
                exact_member = true;
            } else if (entry.actor == card.actor) {
                throw std::runtime_error(
                    label +
                    " peer actor already has a different SPKI; explicit "
                    "identity rotation is required");
            } else if (entry.spki_sha256 == card.spki_sha256) {
                throw std::runtime_error(
                    label +
                    " peer SPKI is already bound to a different actor");
            }
            entries.push_back(entry);
        }
    }

    if (exact_member) {
        return {
            .peer_trust_created = trust_created,
            .membership_changed = false,
            .membership_state_generation = snapshot.state_generation,
            .membership_policy_epoch = snapshot.current_policy_epoch,
            .membership_entry_count = snapshot.current_entry_count,
            .membership_chain_digest = snapshot.current_chain_digest,
        };
    }
    if (snapshot.current_policy_epoch >= kMaximumExactJsonInteger ||
        snapshot.current_policy_epoch ==
            std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(
            label + " membership policy epoch cannot advance");
    }
    entries.push_back({
        .spki_sha256 = card.spki_sha256,
        .actor = card.actor,
    });
    const std::uint64_t next_policy_epoch =
        snapshot.current_policy_epoch + 1U;
    SyncReplicaTlsAnchoredMembershipAuthority published =
        coordinator.publish_or_throw(
            snapshot.anchor(), next_policy_epoch, std::move(entries));
    return {
        .peer_trust_created = trust_created,
        .membership_changed = true,
        .membership_state_generation = published.state_generation(),
        .membership_policy_epoch = published.snapshot().policy_epoch(),
        .membership_entry_count = published.snapshot().entry_count(),
        .membership_chain_digest = published.chain_digest(),
    };
}

}  // namespace anonsync

#endif
