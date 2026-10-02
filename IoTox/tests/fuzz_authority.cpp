#include "iotox/security/authority.hpp"
#include "iotox/security/authority_session.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <span>

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t *data, std::size_t size) {
    const std::span<const std::uint8_t> input(data, size);

    const auto prepare = iotox::security::decode_authority_prepare_request(input);
    if (prepare) {
        const auto encoded =
            iotox::security::encode_authority_prepare_request(prepare.value());
        if (!encoded || encoded.value().size() != input.size() ||
            !std::equal(encoded.value().begin(), encoded.value().end(), input.begin())) {
            __builtin_trap();
        }
    }

    const auto record = iotox::security::decode_authority_record(input);
    if (record) {
        const auto body =
            iotox::security::encode_authority_record_body(record.value());
        if (!body || input.size() < body.value().size() ||
            !std::equal(body.value().begin(), body.value().end(), input.begin())) {
            __builtin_trap();
        }
    }

    const auto challenge =
        iotox::security::decode_authority_challenge(input);
    if (challenge) {
        const auto encoded =
            iotox::security::encode_authority_challenge(challenge.value());
        if (!encoded || encoded.value().size() != input.size() ||
            !std::equal(encoded.value().begin(), encoded.value().end(), input.begin())) {
            __builtin_trap();
        }
    }

    const auto proof = iotox::security::decode_authority_proof(input);
    if (proof) {
        const auto body =
            iotox::security::encode_authority_proof_body(proof.value());
        if (!body || input.size() != iotox::security::kAuthorityProofBytes ||
            !std::equal(body.value().begin(), body.value().end(), input.begin()) ||
            !std::equal(proof.value().signature.begin(),
                        proof.value().signature.end(),
                        input.begin() + static_cast<std::ptrdiff_t>(body.value().size()))) {
            __builtin_trap();
        }
    }
    return 0;
}
