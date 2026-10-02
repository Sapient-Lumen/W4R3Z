#include "iotox/cli_registry.hpp"

#include <algorithm>
#include <array>
#include <sstream>

namespace iotox {
namespace {

using Kind = CliCommandKind;

constexpr auto kCommands = std::to_array<CliCommandDescriptor>({
    {"action", Kind::control, {}},
    {"action-hex", Kind::control, {}},
    {"action-stdin", Kind::control, {}},
    {"address", Kind::control, {}},
    {"auth-challenge", Kind::compatibility, "authority-challenge"},
    {"auth-prove-device", Kind::compatibility, "authority-prove-device"},
    {"auth-prove-recall-stdin", Kind::compatibility,
     "authority-prove-recall-stdin"},
    {"auth-session", Kind::compatibility, "authority-session"},
    {"auth-sessions", Kind::compatibility, "authority-sessions"},
    {"authority", Kind::control, {}},
    {"authority-append-hex", Kind::control, {}},
    {"authority-bootstrap-recall-stdin", Kind::control, {}},
    {"authority-challenge", Kind::control, {}},
    {"authority-delegate-self-recall-stdin", Kind::control, {}},
    {"authority-delegation", Kind::control, {}},
    {"authority-delegation-retry", Kind::control, {}},
    {"authority-grant-recall-stdin", Kind::control, {}},
    {"authority-migrate-v2-recall-stdin", Kind::control, {}},
    {"authority-migrate-v2-remote-recall-stdin", Kind::control, {}},
    {"authority-migrate-v3-recall-stdin", Kind::control, {}},
    {"authority-migrate-v3-remote-recall-stdin", Kind::control, {}},
    {"authority-nominate-successor-remote-recall-stdin", Kind::control, {}},
    {"authority-prove-device", Kind::control, {}},
    {"authority-prove-recall-stdin", Kind::control, {}},
    {"authority-revoke-recall-stdin", Kind::control, {}},
    {"authority-revoke-remote-recall-stdin", Kind::control, {}},
    {"authority-session", Kind::control, {}},
    {"authority-sessions", Kind::control, {}},
    {"authority-transition-recall-stdin", Kind::control, {}},
    {"authority-transition-remote-recall-stdin", Kind::control, {}},
    {"bootstrap-seeds", Kind::informational, {}},
    {"command", Kind::control, {}},
    {"command-cancel", Kind::control, {}},
    {"command-record", Kind::control, {}},
    {"command-store", Kind::control, {}},
    {"completion", Kind::informational, {}},
    {"config-lint", Kind::agent, {}},
    {"confirm", Kind::control, {}},
    {"device-describe", Kind::compatibility, "command"},
    {"diagnostics-export", Kind::control, {}},
    {"diagnostics-inspect", Kind::control, {}},
    {"doctor", Kind::informational, {}},
    {"events", Kind::control, {}},
    {"evidence", Kind::control, {}},
    {"explain", Kind::informational, {}},
    {"file-cancel", Kind::compatibility, "file-control"},
    {"file-control", Kind::control, {}},
    {"file-receive", Kind::control, {}},
    {"file-send", Kind::control, {}},
    {"files", Kind::control, {}},
    {"friend-events", Kind::control, {}},
    {"friend-events-watch", Kind::control, {}},
    {"hello", Kind::control, {}},
    {"help", Kind::informational, {}},
    {"host-capabilities", Kind::terminal_admin, {}},
    {"identity", Kind::control, {}},
    {"init", Kind::agent, {}},
    {"message", Kind::control, {}},
    {"message-hex", Kind::control, {}},
    {"message-probe", Kind::control, {}},
    {"message-stdin", Kind::control, {}},
    {"overview", Kind::control, {}},
    {"packet-probe", Kind::control, {}},
    {"packet-probe-burst", Kind::control, {}},
    {"pair-card", Kind::control, {}},
    {"peer-alias-remove", Kind::control, {}},
    {"peer-alias-rename", Kind::control, {}},
    {"peer-alias-set", Kind::control, {}},
    {"peer-aliases", Kind::control, {}},
    {"peer-description", Kind::control, {}},
    {"peer-file-events", Kind::control, {}},
    {"peer-file-events-watch", Kind::control, {}},
    {"peer-invitation-accept", Kind::control, {}},
    {"peer-invitation-create", Kind::control, {}},
    {"peer-invitation-import", Kind::control, {}},
    {"peer-invitation-inspect", Kind::control, {}},
    {"peer-message-events", Kind::control, {}},
    {"peer-message-events-watch", Kind::control, {}},
    {"peer-messages", Kind::control, {}},
    {"peer-protocol", Kind::control, {}},
    {"peer-protocol-watch", Kind::control, {}},
    {"peer-session", Kind::control, {}},
    {"peer-watch", Kind::control, {}},
    {"peers", Kind::control, {}},
    {"person", Kind::control, {}},
    {"ping", Kind::control, {}},
    {"principals", Kind::control, {}},
    {"profile", Kind::control, {}},
    {"profile-name", Kind::control, {}},
    {"profile-name-hex", Kind::control, {}},
    {"profile-name-stdin", Kind::control, {}},
    {"profile-status", Kind::control, {}},
    {"profile-status-message", Kind::control, {}},
    {"profile-status-message-hex", Kind::control, {}},
    {"profile-status-message-stdin", Kind::control, {}},
    {"protocol-sessions", Kind::compatibility, "sessions"},
    {"readiness", Kind::control, {}},
    {"recall-generate", Kind::control, {}},
    {"recall-owner-public-key-stdin", Kind::control, {}},
    {"request-accept", Kind::control, {}},
    {"request-reject", Kind::control, {}},
    {"requests", Kind::control, {}},
    {"route-health", Kind::control, {}},
    {"route-health-watch", Kind::control, {}},
    {"route-qualification-check", Kind::control, {}},
    {"route-set-create", Kind::control, {}},
    {"route-set-create-v2", Kind::control, {}},
    {"route-target-health", Kind::control, {}},
    {"routes", Kind::control, {}},
    {"routes-watch", Kind::control, {}},
    {"run", Kind::agent, {}},
    {"run-check", Kind::agent, {}},
    {"service", Kind::control, {}},
    {"session", Kind::control, {}},
    {"sessions", Kind::control, {}},
    {"ship-check", Kind::control, {}},
    {"status", Kind::control, {}},
    {"stop", Kind::control, {}},
    {"support-bundle", Kind::control, {}},
    {"sync", Kind::control, {}},
    {"sync-activate", Kind::control, {}},
    {"sync-auto-publish", Kind::control, {}},
    {"sync-automation", Kind::control, {}},
    {"sync-automation-remove", Kind::control, {}},
    {"sync-cancel", Kind::control, {}},
    {"sync-checkpoint", Kind::control, {}},
    {"sync-conflict-explain", Kind::control, {}},
    {"sync-conflicts", Kind::control, {}},
    {"sync-conflicts-summary", Kind::control, {}},
    {"sync-create", Kind::control, {}},
    {"sync-dataset-readiness", Kind::control, {}},
    {"sync-diff", Kind::control, {}},
    {"sync-doctor", Kind::control, {}},
    {"sync-doctor-configured", Kind::agent, {}},
    {"sync-follow", Kind::control, {}},
    {"sync-freeze", Kind::control, {}},
    {"sync-freeze-status", Kind::control, {}},
    {"sync-gc", Kind::control, {}},
    {"sync-health", Kind::control, {}},
    {"sync-history", Kind::control, {}},
    {"sync-interest", Kind::control, {}},
    {"sync-interest-clear", Kind::control, {}},
    {"sync-namespace-install", Kind::control, {}},
    {"sync-namespace-lint", Kind::control, {}},
    {"sync-namespace-remove", Kind::control, {}},
    {"sync-namespace-template", Kind::control, {}},
    {"sync-namespace-template-tree", Kind::control, {}},
    {"sync-namespace-update", Kind::control, {}},
    {"sync-namespaces", Kind::control, {}},
    {"sync-pin", Kind::control, {}},
    {"sync-publish", Kind::control, {}},
    {"sync-pull", Kind::control, {}},
    {"sync-pull-multi", Kind::control, {}},
    {"sync-pull-multi-route", Kind::control, {}},
    {"sync-recovery-verify", Kind::control, {}},
    {"sync-repair", Kind::control, {}},
    {"sync-replica-import", Kind::control, {}},
    {"sync-restore", Kind::control, {}},
    {"sync-restore-forward", Kind::control, {}},
    {"sync-restore-plan", Kind::control, {}},
    {"sync-retention", Kind::control, {}},
    {"sync-share", Kind::control, {}},
    {"sync-source-add", Kind::control, {}},
    {"sync-status", Kind::control, {}},
    {"sync-unfreeze", Kind::control, {}},
    {"sync-unpin", Kind::control, {}},
    {"sync-watch", Kind::control, {}},
    {"sync-writer-cutoff", Kind::control, {}},
    {"terminal", Kind::terminal, {}},
    {"terminal-close", Kind::terminal, {}},
    {"terminal-profile-bind", Kind::terminal_admin, {}},
    {"terminal-profile-check", Kind::terminal_admin, {}},
    {"terminal-profile-install", Kind::terminal_admin, {}},
    {"terminal-profile-lint", Kind::terminal_admin, {}},
    {"terminal-profile-list", Kind::terminal_admin, {}},
    {"terminal-profile-remove", Kind::terminal_admin, {}},
    {"terminal-profile-shell-template", Kind::terminal_admin, {}},
    {"terminal-profile-show", Kind::terminal_admin, {}},
    {"terminal-profile-template", Kind::terminal_admin, {}},
    {"terminal-profile-toolbox-template", Kind::terminal_admin, {}},
    {"terminal-profile-unbind", Kind::terminal_admin, {}},
    {"terminal-resume", Kind::terminal, {}},
    {"terminal-sessions", Kind::terminal, {}},
    {"terminal-shell-discover", Kind::terminal_admin, {}},
    {"transport-hello", Kind::compatibility, "hello"},
    {"transport-peer-accept", Kind::control, {}},
    {"transport-peer-add", Kind::compatibility, "transport-peer-accept"},
    {"transport-peer-reject", Kind::compatibility, "request-reject"},
    {"transport-peer-remove", Kind::control, {}},
    {"transport-peer-request", Kind::control, {}},
    {"transport-send", Kind::control, {}},
    {"typing", Kind::control, {}},
    {"update-apply", Kind::control, {}},
    {"update-bundle-create", Kind::control, {}},
    {"update-confirm", Kind::control, {}},
    {"update-gc", Kind::control, {}},
    {"update-policy-lint", Kind::control, {}},
    {"update-policy-rotate", Kind::control, {}},
    {"update-policy-template", Kind::control, {}},
    {"update-signer-keygen", Kind::control, {}},
    {"update-signer-show", Kind::control, {}},
    {"update-stage", Kind::control, {}},
    {"update-status", Kind::control, {}},
    {"version", Kind::informational, {}},
    {"watch", Kind::control, {}},
    {"witness-authority-enrollment", Kind::witness, {}},
    {"witness-command-effects-enrollment", Kind::witness, {}},
    {"witness-domain-generate", Kind::witness, {}},
    {"witness-incarnation-enrollment", Kind::witness, {}},
    {"witness-route-enrollment", Kind::witness, {}},
    {"witness-service-checkpoint", Kind::witness, {}},
    {"witness-service-checkpoint-custody", Kind::witness, {}},
    {"witness-service-checkpoint-verify", Kind::witness, {}},
    {"witness-service-enroll", Kind::witness, {}},
    {"witness-service-keygen", Kind::witness, {}},
    {"witness-service-serve", Kind::witness, {}},
    {"witness-sync-guarded-enrollment", Kind::witness, {}},
    {"witness-sync-policy-commit", Kind::witness, {}},
    {"witness-sync-policy-enrollment", Kind::witness, {}},
    {"witness-terminal-policy-commit", Kind::witness, {}},
    {"witness-terminal-policy-enrollment", Kind::witness, {}},
    {"witness-update-enrollment", Kind::witness, {}},
});

static_assert(std::ranges::is_sorted(
    kCommands, {}, &CliCommandDescriptor::name));

std::string_view kind_name(CliCommandKind kind) noexcept {
    switch (kind) {
        case Kind::agent: return "agent";
        case Kind::control: return "control";
        case Kind::terminal: return "terminal";
        case Kind::terminal_admin: return "terminal-admin";
        case Kind::witness: return "witness";
        case Kind::informational: return "information";
        case Kind::compatibility: return "compatibility";
    }
    return "unknown";
}

void write_words(std::ostream &output) {
    output << "--help --version";
    for (const auto &command : kCommands) output << ' ' << command.name;
}

}  // namespace

std::span<const CliCommandDescriptor> cli_command_registry() noexcept {
    return kCommands;
}

const CliCommandDescriptor *find_cli_command(std::string_view name) noexcept {
    const auto found = std::ranges::lower_bound(
        kCommands, name, {}, &CliCommandDescriptor::name);
    return found != kCommands.end() && found->name == name
        ? &*found
        : nullptr;
}

bool is_cli_command_kind(
    std::string_view name, CliCommandKind kind) noexcept {
    const auto *command = find_cli_command(name);
    return command != nullptr && command->kind == kind;
}

void write_cli_command_index(std::ostream &output) {
    output << "\nCOMMAND INDEX (generated from the parser registry):\n";
    for (const auto &command : kCommands) {
        output << "  " << command.name << "  [" << kind_name(command.kind)
               << ']';
        if (!command.canonical_name.empty()) {
            output << " alias-for=" << command.canonical_name;
        }
        output << '\n';
    }
}

Result<std::string> generate_cli_completion(std::string_view shell) {
    std::ostringstream output;
    if (shell == "bash") {
        output << "# generated by iotox completion bash\n"
               << "_iotox_complete() {\n"
               << "  local current=\"${COMP_WORDS[COMP_CWORD]}\"\n"
               << "  local words='";
        write_words(output);
        output << "'\n"
               << "  COMPREPLY=( $(compgen -W \"$words\" -- \"$current\") )\n"
               << "}\n"
               << "complete -F _iotox_complete iotox\n";
    } else if (shell == "zsh") {
        output << "#compdef iotox\n"
               << "# generated by iotox completion zsh\n"
               << "_iotox() {\n"
               << "  local -a words\n"
               << "  words=(";
        write_words(output);
        output << ")\n"
               << "  _describe 'iotox command' words\n"
               << "}\n"
               << "compdef _iotox iotox\n";
    } else if (shell == "fish") {
        output << "# generated by iotox completion fish\n"
               << "complete -c iotox -f -a '--help --version'\n";
        for (const auto &command : kCommands) {
            output << "complete -c iotox -f -a '" << command.name
                   << "' -d 'IoTox " << kind_name(command.kind);
            if (!command.canonical_name.empty()) {
                output << " alias for " << command.canonical_name;
            }
            output << "'\n";
        }
    } else {
        return Status{ErrorCode::invalid_argument,
                      "completion shell must be bash, zsh, or fish"};
    }
    return output.str();
}

}  // namespace iotox
