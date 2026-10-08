#include "anonsync_core_internal.hpp"

namespace anonsync {

// rev0595 translation unit: operation contracts and policy profile binding.
std::string contract_key(const std::string& kind, const std::string& file, const std::string& operation_id) {
    return kind + "\n" + file + "\n" + operation_id;
}

std::vector<std::string> string_array(const Json& arr) {
    std::vector<std::string> out;
    if (!arr.is_array()) return out;
    for (const auto& item : arr.a) if (item.is_string()) out.push_back(item.s);
    return out;
}

bool same_string_set(std::vector<std::string> a, std::vector<std::string> b) {
    std::sort(a.begin(), a.end());
    std::sort(b.begin(), b.end());
    return a == b;
}

bool is_lowercase_sha256_hex(const std::string& value) {
    if (value.size() != 64) return false;
    for (char c : value) {
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
    }
    return true;
}

OperationContractTable load_operation_contract_table(const std::string& path, const std::string& text) {
    Json doc = parse_json_text(text);
    OperationContractTable table;
    table.revision_id = doc.at("revision_id").str();
    table.operation_contract_root_sha256 = doc.at("operation_contract_root_sha256").str();
    table.table_digest_sha256 = sha256_hex(text);
    if (!is_lowercase_sha256_hex(table.operation_contract_root_sha256)) {
        throw std::runtime_error("operation contract table has a noncanonical operation_contract_root_sha256");
    }
    const Json& rows = doc.at("rows");
    if (!rows.is_array()) throw std::runtime_error("operation contract table missing rows array: " + path);
    for (const auto& row : rows.a) {
        OperationContract c;
        c.kind = row.at("kind").str();
        c.file = row.at("file").str();
        c.operation_id = row.at("operation_id").str();
        c.contract_digest_sha256 = row.at("contract_digest_sha256").str();
        c.required_scope = row.at("required_scope").str();
        c.required_roles = string_array(row.at("required_roles"));
        c.expected_tenant_id = row.at("expected_tenant_id").str("tenant-alpha");
        c.method = row.at("method").str();
        c.path_template = row.at("path_template").str();
        c.channel = row.at("channel").str();
        c.action = row.at("action").str();
        if (c.kind.empty() || c.file.empty() || c.operation_id.empty() || c.contract_digest_sha256.empty()) {
            throw std::runtime_error("operation contract row has an empty identity/digest field");
        }
        if (!is_lowercase_sha256_hex(c.contract_digest_sha256)) {
            throw std::runtime_error("operation contract row has a noncanonical contract_digest_sha256");
        }
        std::string key = contract_key(c.kind, c.file, c.operation_id);
        if (!table.rows.emplace(key, std::move(c)).second) {
            throw std::runtime_error("duplicate operation contract row for " + key);
        }
    }
    return table;
}

bool validate_operation_contract_binding(const OperationContractTable& table, const Profile& profile, const Json& tc, const Json& claims, std::string& reason) {
    const std::string kind = tc.at("kind").str();
    const std::string file = tc.at("file").str();
    const std::string operation_id = tc.at("operation_id").str();
    auto it = table.rows.find(contract_key(kind, file, operation_id));
    if (it == table.rows.end()) { reason = "operation contract table has no row for case operation"; return false; }
    const OperationContract& c = it->second;
    if (tc.at("required_scope").str() != c.required_scope) { reason = "case required_scope does not match the C++ operation contract table"; return false; }
    if (!same_string_set(string_array(tc.at("required_roles")), c.required_roles)) { reason = "case required_roles do not match the C++ operation contract table"; return false; }
    if (claims.at("operation_id").str() != c.operation_id) { reason = "JWT operation_id claim does not match the selected operation contract"; return false; }
    if (claims.at("contract_digest_sha256").str() != c.contract_digest_sha256) { reason = "JWT contract_digest_sha256 claim does not match the selected operation contract"; return false; }
    if (claims.at("tenant_id").str() != c.expected_tenant_id) { reason = "JWT tenant_id claim does not match the operation contract tenant boundary"; return false; }
    if (claims.at("cnf").at("kid").str() != profile.active_kid) { reason = "JWT cnf.kid is not bound to the active proof key"; return false; }
    return true;
}

}  // namespace anonsync
