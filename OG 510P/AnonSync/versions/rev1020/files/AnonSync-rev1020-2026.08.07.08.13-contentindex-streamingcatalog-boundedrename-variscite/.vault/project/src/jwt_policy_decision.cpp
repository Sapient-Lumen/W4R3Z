#include "anonsync_core_internal.hpp"

namespace anonsync {

// rev0599 translation unit: JWT, DSSE policy, and decision evaluation with ReplayLedger::stage backend boundary.
// rev0595 compatibility needle: JWT, DSSE policy, and decision evaluation
std::pair<std::string, std::string> split_token_part(const std::string& token, size_t& p1, size_t& p2) {
    p1 = token.find('.');
    p2 = token.find('.', p1 == std::string::npos ? 0 : p1 + 1);
    if (p1 == std::string::npos || p2 == std::string::npos || token.find('.', p2 + 1) != std::string::npos) {
        throw std::runtime_error("JWT compact serialization is malformed");
    }
    return {token.substr(0, p1), token.substr(p1 + 1, p2 - p1 - 1)};
}

std::string decode_jti_untrusted(const std::string& token) {
    try {
        size_t p1 = 0, p2 = 0;
        auto parts = split_token_part(token, p1, p2);
        Json payload = parse_json_text(join_bytes(b64url_decode(parts.second)));
        return payload.at("jti").str();
    } catch (...) {
        return "";
    }
}

bool verify_token(const Profile& profile, const Json& tc, std::unordered_set<std::string>& seen_jti, const IReplayLedgerBackend* ledger, Json& claims, std::string& reason) {
    const std::string token = tc.at("token").str();
    if (tc.at("use_stale_jwks").boolean(false)) {
        if (profile.stale_jwks_expires_epoch <= profile.now_epoch) { reason = "JWKS trust profile is stale at gateway evaluation time"; return false; }
    } else if (profile.fresh_jwks_expires_epoch <= profile.now_epoch) {
        reason = "fresh JWKS profile is unexpectedly stale"; return false;
    }
    bool preseed_replay_jti = tc.at("preseed_replay_jti").boolean(false);
    if (preseed_replay_jti) {
        std::string jti = decode_jti_untrusted(token);
        if (!jti.empty()) seen_jti.insert(jti);
    }
    size_t p1 = 0, p2 = 0;
    std::pair<std::string, std::string> header_payload;
    try { header_payload = split_token_part(token, p1, p2); }
    catch (const std::exception& e) { reason = e.what(); return false; }
    const std::string header_b64 = header_payload.first;
    const std::string payload_b64 = header_payload.second;
    const std::string signature = token.substr(p2 + 1);
    Json header;
    try {
        header = parse_json_text(join_bytes(b64url_decode(header_b64)));
        claims = parse_json_text(join_bytes(b64url_decode(payload_b64)));
    } catch (const std::exception& e) { reason = std::string("JWT header or payload decode failed: ") + e.what(); return false; }

    if (header.at("typ").str() != profile.required_typ) { reason = "JWT typ is not the gateway-required access-token profile"; return false; }
    if (header.at("alg").str() != "RS256") { reason = "JWT alg is not allowed by the asymmetric trust profile"; return false; }
    if (header.at("kid").str() != profile.active_kid) { reason = "JWT kid did not select the active public JWK"; return false; }
    std::string sig_reason;
    if (!verify_rs256(profile.public_key.get(), header_b64 + "." + payload_b64, signature, sig_reason)) { reason = sig_reason; return false; }

    for (const char* claim_c : {"iss", "sub", "aud", "exp", "nbf", "iat", "jti", "tenant_id", "scope", "operation_id", "contract_digest_sha256", "cnf"}) {
        const std::string claim(claim_c);
        const Json& v = claims.at(claim);
        if (v.is_null() || (v.is_string() && v.s.empty())) { reason = "JWT required claim " + claim + " is absent"; return false; }
    }
    if (claims.at("iss").str() != profile.issuer) { reason = "JWT issuer claim does not match trust profile"; return false; }
    const Json& aud = claims.at("aud");
    bool aud_ok = aud.is_string() ? aud.s == profile.audience : array_contains_string(aud, profile.audience);
    if (!aud_ok) { reason = "JWT audience claim does not include gateway audience"; return false; }
    if (claims.at("exp").integer() <= profile.now_epoch) { reason = "JWT is expired"; return false; }
    if (claims.at("nbf").integer() > profile.now_epoch) { reason = "JWT is not yet valid"; return false; }
    if (claims.at("iat").integer() > profile.now_epoch) { reason = "JWT issued-at is in the future"; return false; }

    std::string required_scope = tc.at("required_scope").str();
    if (!required_scope.empty()) {
        std::vector<std::string> scopes = split_words(claims.at("scope").str());
        if (std::find(scopes.begin(), scopes.end(), required_scope) == scopes.end()) { reason = "JWT scope does not contain the operation-required scope"; return false; }
    }
    const Json& required_roles = tc.at("required_roles");
    if (required_roles.is_array()) {
        for (const auto& role : required_roles.a) {
            if (role.is_string() && !array_contains_string(claims.at("roles"), role.s)) { reason = "JWT roles do not contain the operation-required roles"; return false; }
        }
    }
    std::string jti = claims.at("jti").str();
    if (preseed_replay_jti && seen_jti.find(jti) != seen_jti.end()) { reason = "JWT jti has already been consumed inside the process replay horizon"; return false; }
    if (ledger != nullptr && ledger->contains_jti(jti)) { reason = "durable replay ledger already contains JWT jti"; return false; }
    if (seen_jti.find(jti) != seen_jti.end()) { reason = "JWT jti has already been consumed inside the process replay horizon"; return false; }
    reason = sig_reason + "; claims, scope, roles, and jti replay horizon validated";
    return true;
}

std::string pae(const std::string& payload_type, const std::string& payload_bytes) {
    return "DSSEv1 " + std::to_string(payload_type.size()) + " " + payload_type + " " + std::to_string(payload_bytes.size()) + " " + payload_bytes;
}

bool verify_policy_envelope(const Profile& profile, const PolicyProfile& policy, const std::string& key, std::map<std::string, std::pair<bool, std::string>>& cache, std::string& reason) {
    auto cached = cache.find(key);
    if (cached != cache.end()) { reason = cached->second.second; return cached->second.first; }
    auto remember = [&](bool ok, const std::string& why) {
        cache[key] = {ok, why}; reason = why; return ok;
    };
    auto it = policy.envelopes.find(key);
    if (it == policy.envelopes.end()) return remember(false, "policy bundle envelope key is absent from controls");
    const Json& envelope = it->second;
    if (envelope.at("payloadType").str() != policy.payload_type) return remember(false, "policy bundle DSSE payloadType is not the gateway-required type");
    const Json& signatures = envelope.at("signatures");
    if (!signatures.is_array() || signatures.a.size() != 1) return remember(false, "policy bundle DSSE envelope does not contain exactly one signature");
    const Json& sig = signatures.at(0);
    if (sig.at("keyid").str() != profile.active_kid) return remember(false, "policy bundle signing key rejected: key is not active");
    std::string payload_bytes;
    try { payload_bytes = join_bytes(b64url_decode(envelope.at("payload").str())); }
    catch (const std::exception& e) { return remember(false, std::string("policy bundle payload decode failed: ") + e.what()); }
    std::string sig_reason;
    if (!verify_rs256(profile.public_key.get(), pae(policy.payload_type, payload_bytes), sig.at("sig").str(), sig_reason)) {
        return remember(false, "policy bundle DSSE signature failed: " + sig_reason);
    }
    Json payload;
    try { payload = parse_json_text(payload_bytes); }
    catch (const std::exception& e) { return remember(false, std::string("policy bundle payload JSON failed: ") + e.what()); }
    const Json& pred = payload.at("predicate");
    if (pred.at("revision_id").str() != policy.expected_revision) return remember(false, "policy bundle revision id mismatch");
    if (pred.at("bundle_version").str() != policy.expected_bundle_version) return remember(false, "policy bundle version mismatch or rollback");
    if (pred.at("bundle_sequence").integer() < policy.minimum_sequence) return remember(false, "policy bundle sequence is below the minimum accepted anti-rollback floor");
    if (pred.at("operation_contract_root_sha256").str() != policy.operation_contract_root_sha256) return remember(false, "policy bundle operation-contract root is stale or mismatched");
    const Json& subject = payload.at("subject").at(0).at("digest").at("sha256");
    if (subject.str() != policy.operation_contract_root_sha256) return remember(false, "policy bundle subject digest does not match operation-contract root");
    return remember(true, "policy bundle DSSE signature, anti-rollback sequence, and operation-contract root validated; " + sig_reason);
}

DecisionResult evaluate_case(const Profile& profile, const PolicyProfile& policy, const OperationContractTable* contracts, IReplayLedgerBackend* ledger, const Json& tc, std::unordered_set<std::string>& seen_jti, std::map<std::string, std::pair<bool, std::string>>& policy_cache) {
    const std::string kind = tc.at("kind").str();
    const std::string expected = tc.at("expected_action").str();
    DecisionResult out;
    out.action = kind == "asyncapi" ? "accept" : "allow";
    Json claims;
    std::string reason;
    if (!verify_token(profile, tc, seen_jti, ledger, claims, reason)) {
        out.action = kind == "asyncapi" ? "quarantine" : "deny";
        out.reason = reason;
        out.durable_replay_ledger_rejection = reason.find("durable replay ledger") != std::string::npos;
    } else if (!verify_policy_envelope(profile, policy, tc.at("policy_envelope_key").str("normal"), policy_cache, reason)) {
        out.action = kind == "asyncapi" ? "quarantine" : "deny";
        out.reason = reason;
    } else if (contracts != nullptr && !validate_operation_contract_binding(*contracts, profile, tc, claims, reason)) {
        out.action = kind == "asyncapi" ? "quarantine" : "deny";
        out.reason = reason;
    } else if (kind == "asyncapi" && !tc.at("cloud_event_id_present").boolean(true)) {
        out.action = "quarantine";
        out.reason = "CloudEvents id is absent, so event identity cannot bind replay ledger entry";
        out.event_identity_rejection = true;
    } else if (kind == "asyncapi" && !tc.at("cloud_event_source_present").boolean(true)) {
        out.action = "quarantine";
        out.reason = "CloudEvents source is absent, so source+id identity cannot bind replay ledger entry";
        out.event_identity_rejection = true;
    } else if (tc.at("ledger_mode").str("normal") == "partial_write") {
        out.action = kind == "asyncapi" ? "quarantine" : "deny";
        out.reason = "ledger append stopped at prepared state and failed closed";
    } else if (tc.at("ledger_mode").str("normal") == "split_brain") {
        out.action = kind == "asyncapi" ? "quarantine" : "deny";
        out.reason = "ledger append detected split-brain chain head and failed closed";
    } else {
        std::string ledger_reason;
        if (ledger != nullptr && ledger->is_enabled() && !ledger->stage(tc, claims, out.action, ledger_reason)) {
            out.action = kind == "asyncapi" ? "quarantine" : "deny";
            out.reason = ledger_reason;
            out.durable_replay_ledger_rejection = ledger_reason.find("durable replay ledger") != std::string::npos || ledger_reason.find("sqlite-wal replay ledger") != std::string::npos;
            out.effect_idempotency_rejection = ledger_reason.find("effect idempotency") != std::string::npos || ledger_reason.find("effect_idempotency_key") != std::string::npos;
        } else {
            seen_jti.insert(claims.at("jti").str());
            out.ledger_appended = ledger != nullptr && ledger->is_enabled();
            out.reason = "C++ OpenSSL gateway kernel allowed/accepted after JWT, DSSE, replay, contract, event identity, and durable ledger checks";
            if (!ledger_reason.empty()) out.reason += "; " + ledger_reason;
        }
    }
    out.passed = out.action == expected;
    return out;
}

}  // namespace anonsync
