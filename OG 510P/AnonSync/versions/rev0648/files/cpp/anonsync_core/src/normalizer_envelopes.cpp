#include "anonsync_core_internal.hpp"

namespace anonsync {

// rev0595 translation unit: request/event normalization envelopes
std::string ascii_lower(std::string value) {
    for (char& c : value) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    return value;
}

std::string ascii_upper(std::string value) {
    for (char& c : value) c = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
    return value;
}

std::map<std::string, std::string> string_object_lower_keys(const Json& obj) {
    std::map<std::string, std::string> out;
    if (!obj.is_object()) throw std::runtime_error("normalized security metadata must be a JSON object");
    for (const auto& kv : obj.o) {
        if (!kv.second.is_string()) {
            throw std::runtime_error("normalized security metadata values must be strings");
        }
        const std::string lower_key = ascii_lower(kv.first);
        if (contains_disallowed_security_control(kv.first) || contains_disallowed_security_control(kv.second.s)) {
            throw std::runtime_error("normalized security metadata contains a disallowed ASCII control character");
        }
        if (!out.emplace(lower_key, kv.second.s).second) {
            throw std::runtime_error("duplicate case-insensitive normalized security metadata key rejected: " + lower_key);
        }
    }
    return out;
}

std::string map_value(const std::map<std::string, std::string>& values, const std::string& key, const std::string& fallback) {
    auto it = values.find(ascii_lower(key));
    return it == values.end() ? fallback : it->second;
}

bool starts_with(const std::string& text, const std::string& prefix) {
    return text.size() >= prefix.size() && text.compare(0, prefix.size(), prefix) == 0;
}

std::vector<std::string> split_path(const std::string& raw_path) {
    std::string path = raw_path;
    size_t q = path.find('?');
    if (q != std::string::npos) path = path.substr(0, q);
    std::vector<std::string> parts;
    std::string cur;
    for (char c : path) {
        if (c == '/') {
            if (!cur.empty()) { parts.push_back(cur); cur.clear(); }
        } else {
            cur.push_back(c);
        }
    }
    if (!cur.empty()) parts.push_back(cur);
    return parts;
}

bool path_template_matches(const std::string& tmpl, const std::string& path) {
    if (tmpl.empty()) return false;
    if (path.find("//") != std::string::npos) return false;
    if (path.find('\\') != std::string::npos) return false;
    std::vector<std::string> want = split_path(tmpl);
    std::vector<std::string> got = split_path(path);
    if (want.size() != got.size()) return false;
    for (size_t i = 0; i < want.size(); ++i) {
        const std::string& w = want[i];
        const std::string& g = got[i];
        const std::string lower_g = ascii_lower(g);
        if (g.empty() || g == "." || g == "..") return false;
        if (lower_g.find("%2f") != std::string::npos || lower_g.find("%2e") != std::string::npos || lower_g.find("%5c") != std::string::npos) {
            return false;  // rev0594: percent-encoded slash, dot, and backslash cannot bypass segment policy.
        }
        bool templated = w.size() >= 2 && w.front() == '{' && w.back() == '}';
        if (!templated && w != g) return false;
    }
    return true;
}

const OperationContract* find_http_contract(const OperationContractTable& table, const std::string& method, const std::string& path, std::string& reason) {
    const OperationContract* found = nullptr;
    for (const auto& kv : table.rows) {
        const OperationContract& c = kv.second;
        if (c.kind != "openapi") continue;
        if (ascii_upper(c.method) != ascii_upper(method)) continue;
        if (!path_template_matches(c.path_template, path)) continue;
        if (found != nullptr) { reason = "HTTP request matched more than one operation contract"; return nullptr; }
        found = &c;
    }
    if (found == nullptr) reason = "HTTP request did not match any C++ route contract";
    return found;
}

const OperationContract* find_event_contract(const OperationContractTable& table, const std::string& channel, const std::string& action, const std::string& file_hint, std::string& reason) {
    const OperationContract* found = nullptr;
    for (const auto& kv : table.rows) {
        const OperationContract& c = kv.second;
        if (c.kind != "asyncapi") continue;
        if (!file_hint.empty() && c.file != file_hint) continue;
        if (c.channel != channel) continue;
        if (!c.action.empty() && !action.empty() && c.action != action) continue;
        if (found != nullptr) { reason = "event envelope matched more than one operation contract; add x-anonsync-contract-file namespace"; return nullptr; }
        found = &c;
    }
    if (found == nullptr) reason = "event envelope did not match any C++ channel/action contract";
    return found;
}

Json json_string_value(const std::string& value) { Json v; v.type = Json::Type::String; v.s = value; return v; }
Json json_bool_value(bool value) { Json v; v.type = Json::Type::Bool; v.b = value; return v; }
Json json_array_strings_value(const std::vector<std::string>& values) {
    Json v; v.type = Json::Type::Array;
    for (const auto& s : values) v.a.push_back(json_string_value(s));
    return v;
}
Json json_null_value() { return Json{}; }

Json make_normalized_legacy_case(const Json& raw, const OperationContract& contract, const std::string& token, const std::string& policy_envelope_key, const std::string& ledger_mode, bool cloud_event_id_present, bool cloud_event_source_present, const std::string& cloud_event_source, const std::string& cloud_event_id, const std::string& effect_idempotency_key) {
    Json tc; tc.type = Json::Type::Object;
    auto put = [&](const std::string& key, Json value) { tc.o[key] = std::move(value); };
    put("case_id", json_string_value(raw.at("case_id").str()));
    put("kind", json_string_value(contract.kind));
    put("file", json_string_value(contract.file));
    put("operation_id", json_string_value(contract.operation_id));
    put("required_scope", json_string_value(contract.required_scope));
    put("required_roles", json_array_strings_value(contract.required_roles));
    put("expected_tenant_id", json_string_value(contract.expected_tenant_id));
    put("expected_action", json_string_value(raw.at("expected_action").str()));
    put("token", json_string_value(token));
    put("policy_envelope_key", json_string_value(policy_envelope_key.empty() ? "normal" : policy_envelope_key));
    put("preseed_replay_jti", json_bool_value(raw.at("preseed_replay_jti").boolean(false)));
    put("use_stale_jwks", json_bool_value(raw.at("use_stale_jwks").boolean(false)));
    put("ledger_mode", json_string_value(ledger_mode.empty() ? "normal" : ledger_mode));
    put("cloud_event_id_present", json_bool_value(cloud_event_id_present));
    put("cloud_event_source_present", json_bool_value(cloud_event_source_present));
    put("cloud_event_source", json_string_value(cloud_event_source));
    put("cloud_event_id", json_string_value(cloud_event_id));
    put("effect_idempotency_key", json_string_value(effect_idempotency_key));
    put("effect_state", json_string_value("prepared"));
    if (raw.at("failure_injection").is_null()) put("failure_injection", json_null_value());
    else put("failure_injection", json_string_value(raw.at("failure_injection").str()));
    if (raw.at("ingress_sender_replay").is_object()) {
        put("ingress_sender_replay", raw.at("ingress_sender_replay"));
    }
    return tc;
}

DecisionResult make_preblocked_decision(const std::string& kind, const std::string& expected, const std::string& reason) {
    DecisionResult result;
    result.action = kind == "asyncapi" ? "quarantine" : "deny";
    result.reason = reason;
    result.passed = result.action == expected;
    return result;
}


std::string bearer_token_from_headers(const std::map<std::string, std::string>& headers, std::string& reason) {
    std::string authorization = map_value(headers, "authorization");
    if (authorization.empty()) { reason = "authorization header is missing from normalized C++ context"; return ""; }
    const std::string prefix = "Bearer ";
    if (!starts_with(authorization, prefix) || authorization.size() == prefix.size()) {
        reason = "authorization header is not a Bearer token";
        return "";
    }
    return authorization.substr(prefix.size());
}

std::string proof_binding_material_for_envelope(const std::string& kind, const OperationContract& contract, const std::string& proof_kid, const std::string& tenant, const std::string& token, const Json& request_or_event) {
    std::vector<std::pair<std::string, std::string>> fields = {
        {"kind", kind},
        {"proof_kid", proof_kid},
        {"tenant", tenant},
        {"contract_file", contract.file},
        {"operation_id", contract.operation_id},
        {"contract_digest_sha256", contract.contract_digest_sha256},
        {"token_sha256", sha256_hex(token)},
    };
    if (kind == "openapi") {
        fields.emplace_back("method", ascii_upper(request_or_event.at("method").str()));
        fields.emplace_back("path", request_or_event.at("path").str());
        fields.emplace_back("body_sha256", sha256_hex(canonical_json(request_or_event.at("body"))));
    } else if (kind == "asyncapi") {
        fields.emplace_back("channel", request_or_event.at("channel").str());
        fields.emplace_back("action", request_or_event.at("action").str());
        fields.emplace_back("cloud_event_source", request_or_event.at("cloud_event").at("source").str());
        fields.emplace_back("cloud_event_id", request_or_event.at("cloud_event").at("id").str());
        fields.emplace_back("payload_sha256", sha256_hex(canonical_json(request_or_event.at("payload"))));
    } else {
        throw std::runtime_error("proof binding material requested for unsupported normalized kind");
    }
    return length_prefixed_security_tuple("anonsync-proof-binding-v2", fields);
}

std::string expected_proof_binding_digest(const Profile& profile, const std::string& kind, const OperationContract& contract, const std::string& proof_kid, const std::string& tenant, const std::string& token, const Json& request_or_event) {
    if (!profile.proof_binding_required) return "";
    if (profile.proof_binding_material_version != "anonsync-proof-binding-v2-lp-hmac-sha256") {
        throw std::runtime_error("unsupported object/event proof binding material version");
    }
    if (profile.proof_binding_hmac_sha256_secret.empty()) {
        throw std::runtime_error("object/event proof binding is required but no HMAC secret is configured");
    }
    return hmac_sha256_hex(profile.proof_binding_hmac_sha256_secret, proof_binding_material_for_envelope(kind, contract, proof_kid, tenant, token, request_or_event));
}

std::string effect_idempotency_material_for_envelope(const std::string& kind, const OperationContract& contract, const std::string& tenant, const Json& request_or_event) {
    std::vector<std::pair<std::string, std::string>> fields = {
        {"kind", kind},
        {"tenant", tenant},
        {"contract_file", contract.file},
        {"operation_id", contract.operation_id},
        {"contract_digest_sha256", contract.contract_digest_sha256},
    };
    if (kind == "openapi") {
        fields.emplace_back("method", ascii_upper(request_or_event.at("method").str()));
        fields.emplace_back("path", request_or_event.at("path").str());
        fields.emplace_back("body_sha256", sha256_hex(canonical_json(request_or_event.at("body"))));
    } else if (kind == "asyncapi") {
        fields.emplace_back("channel", request_or_event.at("channel").str());
        fields.emplace_back("action", request_or_event.at("action").str());
        fields.emplace_back("cloud_event_source", request_or_event.at("cloud_event").at("source").str());
        fields.emplace_back("cloud_event_id", request_or_event.at("cloud_event").at("id").str());
        fields.emplace_back("payload_sha256", sha256_hex(canonical_json(request_or_event.at("payload"))));
    } else {
        throw std::runtime_error("effect idempotency material requested for unsupported normalized kind");
    }
    return length_prefixed_security_tuple("anonsync-effect-idempotency-v2", fields);
}

std::string effect_idempotency_key_for_envelope(const std::string& kind, const OperationContract& contract, const std::string& tenant, const Json& request_or_event) {
    return sha256_hex(effect_idempotency_material_for_envelope(kind, contract, tenant, request_or_event));
}

NormalizedCaseResult normalize_case_from_envelope(const OperationContractTable& table, const Profile& profile, const Json& raw) {
    NormalizedCaseResult normalized;
    const std::string kind = raw.at("kind").str();
    const std::string expected = raw.at("expected_action").str();
    std::string reason;
    const OperationContract* contract = nullptr;
    std::map<std::string, std::string> metadata;
    std::string token;
    std::string ledger_mode = "normal";
    std::string policy_envelope_key = "normal";
    bool cloud_event_id_present = true;
    bool cloud_event_source_present = true;
    std::string cloud_event_source;
    std::string cloud_event_id;

    if (kind == "openapi") {
        const Json& request = raw.at("http_request");
        try {
            metadata = string_object_lower_keys(request.at("headers"));
        } catch (const std::exception& e) {
            normalized.has_preblocked_decision = true;
            normalized.preblock_category = "authorization";
            normalized.preblocked = make_preblocked_decision(kind, expected, e.what());
            return normalized;
        }
        const std::string method = request.at("method").str();
        const std::string path = request.at("path").str();
        if (contains_disallowed_security_control(method) || contains_disallowed_security_control(path)) {
            normalized.has_preblocked_decision = true;
            normalized.preblock_category = "route";
            normalized.preblocked = make_preblocked_decision(kind, expected, "HTTP method/path contains a disallowed ASCII control character");
            return normalized;
        }
        contract = find_http_contract(table, method, path, reason);
        if (contract == nullptr) {
            normalized.has_preblocked_decision = true;
            normalized.preblock_category = "route";
            normalized.preblocked = make_preblocked_decision(kind, expected, reason);
            return normalized;
        }
        normalized.route_matched = true;
        policy_envelope_key = map_value(metadata, "x-anonsync-policy-envelope", "normal");
        ledger_mode = map_value(metadata, "x-anonsync-ledger-mode", "normal");
    } else if (kind == "asyncapi") {
        const Json& event = raw.at("event_envelope");
        try {
            metadata = string_object_lower_keys(event.at("attributes"));
        } catch (const std::exception& e) {
            normalized.has_preblocked_decision = true;
            normalized.preblock_category = "authorization";
            normalized.preblocked = make_preblocked_decision(kind, expected, e.what());
            return normalized;
        }
        const std::string channel = event.at("channel").str();
        const std::string action = event.at("action").str();
        cloud_event_id = event.at("cloud_event").at("id").str();
        cloud_event_source = event.at("cloud_event").at("source").str();
        if (contains_disallowed_security_control(channel) || contains_disallowed_security_control(action)) {
            normalized.has_preblocked_decision = true;
            normalized.preblock_category = "route";
            normalized.preblocked = make_preblocked_decision(kind, expected, "event channel/action contains a disallowed ASCII control character");
            return normalized;
        }
        if (contains_disallowed_security_control(cloud_event_source) || contains_disallowed_security_control(cloud_event_id)) {
            normalized.has_preblocked_decision = true;
            normalized.preblock_category = "proof";
            normalized.preblocked = make_preblocked_decision(kind, expected, "CloudEvents source/id contains a disallowed ASCII control character");
            return normalized;
        }
        contract = find_event_contract(table, channel, action, map_value(metadata, "x-anonsync-contract-file"), reason);
        if (contract == nullptr) {
            normalized.has_preblocked_decision = true;
            normalized.preblock_category = "route";
            normalized.preblocked = make_preblocked_decision(kind, expected, reason);
            return normalized;
        }
        normalized.route_matched = true;
        policy_envelope_key = map_value(metadata, "x-anonsync-policy-envelope", "normal");
        ledger_mode = map_value(metadata, "x-anonsync-ledger-mode", "normal");
        cloud_event_id_present = !cloud_event_id.empty();
        cloud_event_source_present = !cloud_event_source.empty();
    } else {
        normalized.has_preblocked_decision = true;
        normalized.preblock_category = "route";
        normalized.preblocked = make_preblocked_decision(kind, expected, "normalized case kind is neither openapi nor asyncapi");
        return normalized;
    }

    token = bearer_token_from_headers(metadata, reason);
    if (token.empty()) {
        normalized.has_preblocked_decision = true;
        normalized.preblock_category = "authorization";
        normalized.preblocked = make_preblocked_decision(kind, expected, reason);
        return normalized;
    }
    std::string proof_kid = map_value(metadata, "x-anonsync-proof-kid");
    const std::string expected_proof_kid = profile.proof_binding_active_kid.empty() ? profile.active_kid : profile.proof_binding_active_kid;
    if (proof_kid.empty() || proof_kid != expected_proof_kid) {
        normalized.has_preblocked_decision = true;
        normalized.preblock_category = "proof";
        normalized.preblocked = make_preblocked_decision(kind, expected, "normalized context lacks the active object/event proof key binding");
        return normalized;
    }
    std::string context_tenant = map_value(metadata, "x-anonsync-tenant");
    if (context_tenant != contract->expected_tenant_id) {
        normalized.has_preblocked_decision = true;
        normalized.preblock_category = "tenant_context";
        normalized.preblocked = make_preblocked_decision(kind, expected, "normalized context tenant does not match the selected operation contract tenant boundary");
        return normalized;
    }
    if (profile.proof_binding_required) {
        const std::string supplied_binding = map_value(metadata, "x-anonsync-proof-binding-sha256");
        if (!is_lowercase_sha256_hex(supplied_binding)) {
            normalized.has_preblocked_decision = true;
            normalized.preblock_category = "proof";
            normalized.preblocked = make_preblocked_decision(kind, expected, "normalized context lacks the required object/event proof binding digest");
            return normalized;
        }
        const Json& request_or_event = kind == "openapi" ? raw.at("http_request") : raw.at("event_envelope");
        const std::string expected_binding = expected_proof_binding_digest(profile, kind, *contract, proof_kid, context_tenant, token, request_or_event);
        if (supplied_binding != expected_binding) {
            normalized.has_preblocked_decision = true;
            normalized.preblock_category = "proof";
            normalized.preblocked = make_preblocked_decision(kind, expected, "object/event proof binding digest did not match the selected contract, token, tenant, and normalized envelope");
            return normalized;
        }
    }

    const Json& request_or_event = kind == "openapi" ? raw.at("http_request") : raw.at("event_envelope");
    const std::string effect_idempotency_key = effect_idempotency_key_for_envelope(kind, *contract, context_tenant, request_or_event);
    normalized.tc = make_normalized_legacy_case(raw, *contract, token, policy_envelope_key, ledger_mode, cloud_event_id_present, cloud_event_source_present, cloud_event_source, cloud_event_id, effect_idempotency_key);
    return normalized;
}

}  // namespace anonsync
