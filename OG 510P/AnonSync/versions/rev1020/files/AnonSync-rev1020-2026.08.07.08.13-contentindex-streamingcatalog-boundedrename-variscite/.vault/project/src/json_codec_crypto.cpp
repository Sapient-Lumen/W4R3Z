#include "anonsync_core_internal.hpp"
#include "sync_bounded_regular_file.hpp"

#include <climits>

namespace anonsync {

// rev0595 translation unit: json codec and OpenSSL-backed crypto.

std::string read_file(const std::string& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("could not open " + path);
    std::ostringstream ss;
    ss << in.rdbuf();
    if (!in.eof() && in.fail()) throw std::runtime_error("could not read " + path);
    return ss.str();
}

std::string read_file_bounded(const std::string& path,
                              size_t maximum_bytes,
                              const std::string& label) {
    return read_sync_bounded_regular_file_no_symlink_or_throw(
        path, static_cast<std::uint64_t>(maximum_bytes), label);
}

void write_file(const std::string& path, const std::string& text) {
    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("could not write " + path);
    out << text;
}

Json load_json(const std::string& path) { return parse_json_text(read_file(path)); }

std::string json_escape(const std::string& value) {
    static constexpr char hex[] = "0123456789abcdef";
    std::string out;
    out.reserve(value.size());
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
                    out.push_back(hex[(c >> 4U) & 0x0fU]);
                    out.push_back(hex[c & 0x0fU]);
                } else {
                    out.push_back(static_cast<char>(c));
                }
        }
    }
    return out;
}


std::string canonical_json(const Json& value) {
    switch (value.type) {
        case Json::Type::Null:
            return "null";
        case Json::Type::Bool:
            return value.b ? "true" : "false";
        case Json::Type::String:
            return "\"" + json_escape(value.s) + "\"";
        case Json::Type::Number: {
            std::ostringstream out;
            out.imbue(std::locale::classic());
            out << std::setprecision(17) << value.n;
            return out.str();
        }
        case Json::Type::Array: {
            std::string out = "[";
            for (size_t i = 0; i < value.a.size(); ++i) {
                if (i) out += ",";
                out += canonical_json(value.a[i]);
            }
            out += "]";
            return out;
        }
        case Json::Type::Object: {
            std::string out = "{";
            bool first = true;
            for (const auto& kv : value.o) {
                if (!first) out += ",";
                first = false;
                out += "\"" + json_escape(kv.first) + "\":" + canonical_json(kv.second);
            }
            out += "}";
            return out;
        }
    }
    throw std::runtime_error("unknown JSON type while canonicalizing");
}


std::string b64url_encode(const unsigned char* data, size_t len) {
    static const char* alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
    std::string out;
    out.reserve(((len + 2) / 3) * 4);
    for (size_t i = 0; i < len; i += 3) {
        const unsigned int b0 = data[i];
        const unsigned int b1 = (i + 1 < len) ? data[i + 1] : 0;
        const unsigned int b2 = (i + 2 < len) ? data[i + 2] : 0;
        const unsigned int triple = (b0 << 16) | (b1 << 8) | b2;
        out.push_back(alphabet[(triple >> 18) & 0x3f]);
        out.push_back(alphabet[(triple >> 12) & 0x3f]);
        if (i + 1 < len) out.push_back(alphabet[(triple >> 6) & 0x3f]);
        if (i + 2 < len) out.push_back(alphabet[triple & 0x3f]);
    }
    return out;
}

std::string b64url_encode(const std::vector<unsigned char>& bytes) {
    return b64url_encode(bytes.data(), bytes.size());
}

std::vector<unsigned char> b64url_decode(const std::string& input) {
    static const std::array<int8_t, 256> table = [] {
        std::array<int8_t, 256> t{};
        t.fill(-1);
        for (int i = 0; i < 26; ++i) { t[static_cast<unsigned char>('A' + i)] = i; t[static_cast<unsigned char>('a' + i)] = 26 + i; }
        for (int i = 0; i < 10; ++i) t[static_cast<unsigned char>('0' + i)] = 52 + i;
        t[static_cast<unsigned char>('-')] = 62; t[static_cast<unsigned char>('_')] = 63;
        return t;
    }();
    if (input.find('=') != std::string::npos || input.find('+') != std::string::npos || input.find('/') != std::string::npos) {
        throw std::runtime_error("base64url input uses forbidden padding or non-url alphabet characters");
    }
    if (input.size() % 4 == 1) {
        throw std::runtime_error("base64url canonical length is impossible without padding");
    }
    if (!input.empty()) {
        int last = table[static_cast<unsigned char>(input.back())];
        if (last == -1) throw std::runtime_error("invalid base64url character");
        if (input.size() % 4 == 2 && (last & 0x0F) != 0) {
            throw std::runtime_error("base64url canonical residual bits rejected");
        }
        if (input.size() % 4 == 3 && (last & 0x03) != 0) {
            throw std::runtime_error("base64url canonical residual bits rejected");
        }
    }
    std::vector<unsigned char> out;
    std::uint32_t val = 0;
    int valb = -8;
    for (unsigned char c : input) {
        int d = table[c];
        if (d == -1) throw std::runtime_error("invalid base64url character");
        val = (val << 6) + d;
        valb += 6;
        if (valb >= 0) {
            out.push_back(static_cast<unsigned char>((val >> valb) & 0xFF));
            valb -= 8;
        }
    }
    return out;
}

std::string hmac_sha256_hex(const std::string& key, const std::string& data) {
    if (key.size() > static_cast<size_t>(INT_MAX)) {
        throw std::runtime_error("HMAC-SHA256 key exceeds OpenSSL length range");
    }
    unsigned char mac[EVP_MAX_MD_SIZE];
    unsigned int mac_len = 0;
    if (HMAC(EVP_sha256(), key.data(), static_cast<int>(key.size()),
             reinterpret_cast<const unsigned char*>(data.data()), data.size(),
             mac, &mac_len) == nullptr) {
        throw std::runtime_error("HMAC-SHA256 failed");
    }
    static constexpr char hex[] = "0123456789abcdef";
    std::string out(static_cast<size_t>(mac_len) * 2U, '\0');
    for (unsigned int i = 0; i < mac_len; ++i) {
        out[static_cast<size_t>(i) * 2U] = hex[(mac[i] >> 4U) & 0x0fU];
        out[static_cast<size_t>(i) * 2U + 1U] = hex[mac[i] & 0x0fU];
    }
    return out;
}

std::string length_prefixed_security_tuple(
    const std::string& domain,
    const std::vector<std::pair<std::string, std::string>>& fields) {
    // rev0632: byte-length framing prevents delimiter injection and cross-field substitution.
    // Format: fixed domain separator followed by decimal-byte-length ':' byte-string components.
    std::string out = "anonsync-length-prefixed-tuple-v1";
    auto append_component = [&](const std::string& value) {
        std::array<char, 32> decimal{};
        const auto result = std::to_chars(
            decimal.data(), decimal.data() + decimal.size(), value.size());
        if (result.ec != std::errc{}) {
            throw std::runtime_error(
                "security tuple component length formatting failed");
        }
        out.append(decimal.data(),
                   static_cast<size_t>(result.ptr - decimal.data()));
        out.push_back(':');
        out.append(value);
    };
    append_component(domain);
    for (const auto& field : fields) {
        append_component(field.first);
        append_component(field.second);
    }
    return out;
}

bool contains_disallowed_security_control(const std::string& value) {
    for (unsigned char c : value) {
        if (c < 0x20 || c == 0x7f) return true;
    }
    return false;
}

std::string join_bytes(const std::vector<unsigned char>& bytes) {
    if (bytes.empty()) return {};
    return std::string(reinterpret_cast<const char*>(bytes.data()), bytes.size());
}

void OpenSSLDeleter::operator()(EVP_PKEY* p) const { EVP_PKEY_free(p); }
void OpenSSLDeleter::operator()(EVP_MD_CTX* p) const { EVP_MD_CTX_free(p); }


PKeyPtr pem_private_key_to_pkey(const std::string& pem_text) {
    BIO* raw = BIO_new_mem_buf(pem_text.data(), static_cast<int>(pem_text.size()));
    if (!raw) throw std::runtime_error("could not allocate BIO for private key PEM");
    std::unique_ptr<BIO, decltype(&BIO_free)> bio(raw, BIO_free);
    EVP_PKEY* key = PEM_read_bio_PrivateKey(bio.get(), nullptr, nullptr, nullptr);
    if (!key) throw std::runtime_error("could not read private key PEM");
    return PKeyPtr(key);
}

std::string sign_rs256(EVP_PKEY* key, const std::string& signing_input) {
    if (!key) throw std::runtime_error("RS256 signing requires a private key");
    MdCtxPtr ctx(EVP_MD_CTX_new());
    if (!ctx) throw std::runtime_error("could not allocate RS256 signing context");
    if (EVP_DigestSignInit(ctx.get(), nullptr, EVP_sha256(), nullptr, key) != 1) throw std::runtime_error("EVP_DigestSignInit failed");
    if (EVP_DigestSignUpdate(ctx.get(), signing_input.data(), signing_input.size()) != 1) throw std::runtime_error("EVP_DigestSignUpdate failed");
    size_t sig_len = 0;
    if (EVP_DigestSignFinal(ctx.get(), nullptr, &sig_len) != 1) throw std::runtime_error("EVP_DigestSignFinal length failed");
    std::vector<unsigned char> sig(sig_len);
    if (EVP_DigestSignFinal(ctx.get(), sig.data(), &sig_len) != 1) throw std::runtime_error("EVP_DigestSignFinal failed");
    sig.resize(sig_len);
    return b64url_encode(sig);
}

PKeyPtr jwk_to_pkey(const std::string& n_b64, const std::string& e_b64) {
    if (n_b64.empty() || e_b64.empty() || n_b64.size() > 2048 || e_b64.size() > 32) {
        throw std::runtime_error("RSA JWK modulus/exponent size is unsupported");
    }
    std::vector<unsigned char> n_bytes = b64url_decode(n_b64);
    std::vector<unsigned char> e_bytes = b64url_decode(e_b64);
    if (n_bytes.empty() || e_bytes.empty() || n_bytes.front() == 0 || e_bytes.front() == 0) {
        throw std::runtime_error("RSA JWK n/e must use canonical nonempty Base64urlUInt encoding");
    }
    BIGNUM* n = BN_bin2bn(n_bytes.data(), static_cast<int>(n_bytes.size()), nullptr);
    BIGNUM* e = BN_bin2bn(e_bytes.data(), static_cast<int>(e_bytes.size()), nullptr);
    if (!n || !e) { BN_free(n); BN_free(e); throw std::runtime_error("could not allocate RSA BIGNUMs"); }

    EVP_PKEY_CTX* raw_ctx = EVP_PKEY_CTX_new_from_name(nullptr, "RSA", nullptr);
    if (!raw_ctx) { BN_free(n); BN_free(e); throw std::runtime_error("could not allocate RSA fromdata context"); }
    std::unique_ptr<EVP_PKEY_CTX, decltype(&EVP_PKEY_CTX_free)> ctx(raw_ctx, EVP_PKEY_CTX_free);
    if (EVP_PKEY_fromdata_init(ctx.get()) != 1) { BN_free(n); BN_free(e); throw std::runtime_error("EVP_PKEY_fromdata_init failed"); }

    OSSL_PARAM_BLD* raw_bld = OSSL_PARAM_BLD_new();
    if (!raw_bld) { BN_free(n); BN_free(e); throw std::runtime_error("could not allocate OSSL_PARAM_BLD"); }
    std::unique_ptr<OSSL_PARAM_BLD, decltype(&OSSL_PARAM_BLD_free)> bld(raw_bld, OSSL_PARAM_BLD_free);
    if (OSSL_PARAM_BLD_push_BN(bld.get(), OSSL_PKEY_PARAM_RSA_N, n) != 1 ||
        OSSL_PARAM_BLD_push_BN(bld.get(), OSSL_PKEY_PARAM_RSA_E, e) != 1) {
        BN_free(n); BN_free(e);
        throw std::runtime_error("could not push RSA n/e params");
    }
    OSSL_PARAM* raw_params = OSSL_PARAM_BLD_to_param(bld.get());
    if (!raw_params) { BN_free(n); BN_free(e); throw std::runtime_error("could not materialize RSA params"); }
    std::unique_ptr<OSSL_PARAM, decltype(&OSSL_PARAM_free)> params(raw_params, OSSL_PARAM_free);

    EVP_PKEY* raw_key = nullptr;
    int ok = EVP_PKEY_fromdata(ctx.get(), &raw_key, EVP_PKEY_PUBLIC_KEY, params.get());
    BN_free(n);
    BN_free(e);
    if (ok != 1 || raw_key == nullptr) {
        throw std::runtime_error("EVP_PKEY_fromdata failed for RSA public key");
    }
    PKeyPtr key(raw_key);
    if (EVP_PKEY_get_bits(key.get()) < 2048 || EVP_PKEY_get_security_bits(key.get()) < 112) {
        throw std::runtime_error("RSA public key must provide at least 2048-bit/112-bit security strength");
    }
    return key;
}

bool verify_rs256(EVP_PKEY* pkey, const std::string& signing_input, const std::string& signature_b64url, std::string& reason) {
    std::vector<unsigned char> sig;
    try { sig = b64url_decode(signature_b64url); }
    catch (const std::exception& e) { reason = std::string("signature base64url decode failed: ") + e.what(); return false; }
    MdCtxPtr ctx(EVP_MD_CTX_new());
    if (!ctx) { reason = "could not allocate digest context"; return false; }
    if (EVP_DigestVerifyInit(ctx.get(), nullptr, EVP_sha256(), nullptr, pkey) != 1) { reason = "EVP_DigestVerifyInit failed"; return false; }
    if (EVP_DigestVerifyUpdate(ctx.get(), signing_input.data(), signing_input.size()) != 1) { reason = "EVP_DigestVerifyUpdate failed"; return false; }
    int ok = EVP_DigestVerifyFinal(ctx.get(), sig.data(), sig.size());
    if (ok == 1) { reason = "RS256 signature verified by OpenSSL"; return true; }
    reason = "RS256 signature verification failed";
    return false;
}

std::vector<std::string> split_words(const std::string& text) {
    std::istringstream in(text);
    std::vector<std::string> words;
    std::string w;
    while (in >> w) words.push_back(w);
    return words;
}


std::string strict_utc_from_epoch(long long epoch) {
    if (epoch < 0) throw std::runtime_error("cannot format negative epoch as UTC");
    std::time_t t = static_cast<std::time_t>(epoch);
    std::tm tm{};
#if defined(_WIN32)
    if (gmtime_s(&tm, &t) != 0) throw std::runtime_error("gmtime_s failed");
#else
    if (gmtime_r(&t, &tm) == nullptr) throw std::runtime_error("gmtime_r failed");
#endif
    char buf[32];
    if (std::strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &tm) == 0) throw std::runtime_error("strftime failed");
    return std::string(buf);
}

bool array_contains_string(const Json& arr, const std::string& value) {
    if (!arr.is_array()) return false;
    for (const auto& item : arr.a) if (item.is_string() && item.s == value) return true;
    return false;
}

}  // namespace anonsync
