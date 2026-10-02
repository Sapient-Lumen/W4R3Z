#include "iotox/local/control_socket.hpp"
#include "iotox/security/authority.hpp"
#include "iotox/security/sodium.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <iostream>
#include <mutex>
#include <optional>
#include <span>
#include <spawn.h>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <sys/wait.h>
#include <unistd.h>
#include <utility>
#include <vector>

extern char **environ;

namespace {

using iotox::local::ControlKind;
using iotox::local::ControlOperation;
using iotox::local::ControlPacket;
using iotox::security::AuthorityAction;
using iotox::security::AuthorityRecord;
using iotox::security::PrincipalRole;
using iotox::security::SigningPublicKey;

constexpr std::uint32_t kFriendNumber = 7U;

struct CommandResult {
    int exit_code{0};
    std::string output;
};

void require(bool condition, std::string_view message) {
    if (!condition) {
        throw std::runtime_error(std::string(message));
    }
}

std::vector<char *> make_argv(std::vector<std::string> &arguments) {
    std::vector<char *> argv;
    argv.reserve(arguments.size() + 1U);
    for (std::string &argument : arguments) {
        argv.push_back(argument.data());
    }
    argv.push_back(nullptr);
    return argv;
}

CommandResult run_capture_with_input(
    const std::filesystem::path &program,
    const std::vector<std::string> &extra_arguments,
    std::span<const std::uint8_t> input) {
    int output_descriptors[2]{};
    int input_descriptors[2]{};
    if (::pipe(output_descriptors) != 0) {
        throw std::runtime_error(
            "output pipe failed: " + std::string(std::strerror(errno)));
    }
    if (::pipe(input_descriptors) != 0) {
        const int saved_errno = errno;
        static_cast<void>(::close(output_descriptors[0]));
        static_cast<void>(::close(output_descriptors[1]));
        throw std::runtime_error(
            "input pipe failed: " + std::string(std::strerror(saved_errno)));
    }

    // Feed the complete, deliberately small ceremony phrase before spawning.
    // Writing after spawn races commands that reject their arguments before
    // reading stdin: a fast child can close the pipe and deliver SIGPIPE to the
    // test process. Limiting the preload to PIPE_BUF guarantees that an empty
    // pipe can accept it atomically without a reader or a blocking partial
    // write.
    const long pipe_buffer = ::fpathconf(input_descriptors[1], _PC_PIPE_BUF);
    if (pipe_buffer < 0 ||
        input.size() > static_cast<std::size_t>(pipe_buffer)) {
        const int saved_errno = pipe_buffer < 0 ? errno : EOVERFLOW;
        for (const int descriptor : output_descriptors) {
            static_cast<void>(::close(descriptor));
        }
        for (const int descriptor : input_descriptors) {
            static_cast<void>(::close(descriptor));
        }
        throw std::runtime_error(
            "stdin test input exceeds the atomic pipe preload limit: " +
            std::string(std::strerror(saved_errno)));
    }
    std::size_t written = 0U;
    while (written < input.size()) {
        const ssize_t count = ::write(
            input_descriptors[1], input.data() + written, input.size() - written);
        if (count > 0) {
            written += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) {
            continue;
        }
        const int saved_errno = errno;
        for (const int descriptor : output_descriptors) {
            static_cast<void>(::close(descriptor));
        }
        for (const int descriptor : input_descriptors) {
            static_cast<void>(::close(descriptor));
        }
        throw std::runtime_error(
            "stdin pipe preload failed: " +
            std::string(std::strerror(saved_errno)));
    }

    std::vector<std::string> arguments;
    arguments.reserve(extra_arguments.size() + 1U);
    arguments.push_back(program.string());
    arguments.insert(arguments.end(), extra_arguments.begin(), extra_arguments.end());
    std::vector<char *> argv = make_argv(arguments);

    posix_spawn_file_actions_t actions;
    int spawn_error = ::posix_spawn_file_actions_init(&actions);
    const bool actions_initialized = spawn_error == 0;
    const auto add_action = [&spawn_error](int result) {
        if (spawn_error == 0 && result != 0) {
            spawn_error = result;
        }
    };
    if (spawn_error == 0) {
        add_action(::posix_spawn_file_actions_addclose(
            &actions, output_descriptors[0]));
        add_action(::posix_spawn_file_actions_addclose(
            &actions, input_descriptors[1]));
        add_action(::posix_spawn_file_actions_adddup2(
            &actions, output_descriptors[1], STDOUT_FILENO));
        add_action(::posix_spawn_file_actions_adddup2(
            &actions, output_descriptors[1], STDERR_FILENO));
        add_action(::posix_spawn_file_actions_adddup2(
            &actions, input_descriptors[0], STDIN_FILENO));
        add_action(::posix_spawn_file_actions_addclose(
            &actions, output_descriptors[1]));
        add_action(::posix_spawn_file_actions_addclose(
            &actions, input_descriptors[0]));
    }

    pid_t child = -1;
    if (spawn_error == 0) {
        spawn_error = ::posix_spawn(
            &child, program.c_str(), &actions, nullptr, argv.data(), environ);
    }
    if (actions_initialized) {
        static_cast<void>(::posix_spawn_file_actions_destroy(&actions));
    }
    if (spawn_error != 0) {
        for (const int descriptor : output_descriptors) {
            static_cast<void>(::close(descriptor));
        }
        for (const int descriptor : input_descriptors) {
            static_cast<void>(::close(descriptor));
        }
        throw std::runtime_error(
            "posix_spawn failed: " + std::string(std::strerror(spawn_error)));
    }

    static_cast<void>(::close(output_descriptors[1]));
    static_cast<void>(::close(input_descriptors[0]));
    static_cast<void>(::close(input_descriptors[1]));

    std::string output;
    std::array<char, 4096U> buffer{};
    for (;;) {
        const ssize_t count = ::read(
            output_descriptors[0], buffer.data(), buffer.size());
        if (count > 0) {
            output.append(buffer.data(), static_cast<std::size_t>(count));
            continue;
        }
        if (count < 0 && errno == EINTR) {
            continue;
        }
        break;
    }
    static_cast<void>(::close(output_descriptors[0]));

    int status = 0;
    if (::waitpid(child, &status, 0) != child) {
        throw std::runtime_error("waitpid failed");
    }
    if (WIFEXITED(status)) {
        return {WEXITSTATUS(status), std::move(output)};
    }
    return {WIFSIGNALED(status) ? 128 + WTERMSIG(status) : 128,
            std::move(output)};
}

CommandResult run_control_with_phrase(
    const std::filesystem::path &iotox,
    const std::filesystem::path &runtime,
    const std::vector<std::string> &command,
    std::string_view phrase) {
    std::vector<std::string> arguments{
        "--runtime", runtime.string(), "--timeout-ms", "5000"};
    arguments.insert(arguments.end(), command.begin(), command.end());
    return run_capture_with_input(
        iotox, arguments,
        std::span<const std::uint8_t>{
            reinterpret_cast<const std::uint8_t *>(phrase.data()), phrase.size()});
}

std::string extract_field(std::string_view text, std::string_view field) {
    const std::string prefix = std::string(field) + "=";
    const std::size_t begin = text.find(prefix);
    if (begin == std::string_view::npos) {
        return {};
    }
    const std::size_t value_begin = begin + prefix.size();
    const std::size_t end = text.find('\n', value_begin);
    return std::string(text.substr(value_begin, end - value_begin));
}

std::uint32_t read_u32(std::span<const std::uint8_t> bytes) {
    std::uint32_t value = 0U;
    for (std::size_t index = 0U; index < 4U; ++index) {
        value = static_cast<std::uint32_t>((value << 8U) | bytes[index]);
    }
    return value;
}

std::uint64_t read_u64(std::span<const std::uint8_t> bytes) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | bytes[index];
    }
    return value;
}

SigningPublicKey read_public_key(
    std::span<const std::uint8_t> payload, std::size_t offset) {
    SigningPublicKey key{};
    std::copy_n(payload.begin() + static_cast<std::ptrdiff_t>(offset),
                key.size(), key.begin());
    return key;
}

std::vector<std::uint8_t> authority_signature_message(
    std::span<const std::uint8_t, iotox::security::kAuthorityRecordBodyBytes> body) {
    constexpr std::string_view prefix = "IOTOXS1";
    constexpr std::string_view domain_v1 =
        "iotox-authority-record-signature-v1";
    constexpr std::string_view domain_v2 =
        "iotox-authority-record-signature-v2";
    constexpr std::string_view domain_v3 =
        "iotox-authority-record-signature-v3";
    const std::string_view domain =
        body[4U] == 3U ? domain_v3 : (body[4U] == 2U ? domain_v2 : domain_v1);
    std::vector<std::uint8_t> message;
    message.reserve(prefix.size() + 2U + domain.size() + body.size());
    message.insert(message.end(), prefix.begin(), prefix.end());
    message.push_back(static_cast<std::uint8_t>((domain.size() >> 8U) & 0xFFU));
    message.push_back(static_cast<std::uint8_t>(domain.size() & 0xFFU));
    message.insert(message.end(), domain.begin(), domain.end());
    message.insert(message.end(), body.begin(), body.end());
    return message;
}

bool same_unsigned_record(const AuthorityRecord &left, const AuthorityRecord &right) {
    return left.format == right.format && left.action == right.action &&
           left.role == right.role &&
           left.sequence == right.sequence &&
           left.ownership_epoch == right.ownership_epoch &&
           left.not_before_unix_ms == right.not_before_unix_ms &&
           left.not_after_unix_ms == right.not_after_unix_ms &&
           left.capabilities == right.capabilities && left.device == right.device &&
           left.issuer == right.issuer && left.subject == right.subject &&
           left.previous_digest == right.previous_digest;
}

struct CeremonyState {
    explicit CeremonyState(const iotox::security::Sodium &sodium_value)
        : sodium(&sodium_value) {
        device.fill(0xD1U);
        self_subject.fill(0xB2U);
        previous_digest.fill(0xA5U);
    }

    const iotox::security::Sodium *sodium;
    SigningPublicKey device{};
    SigningPublicKey self_subject{};
    iotox::security::Digest previous_digest{};
    std::mutex mutex;
    std::optional<AuthorityRecord> prepared;
    std::vector<AuthorityRecord> received;
    std::vector<AuthorityRecord> local_received;
    std::size_t local_append_attempts{0U};
    bool poison_next_local_prepare{true};
    std::string failure;
};

ControlPacket ceremony_response(
    CeremonyState &state, const ControlPacket &request) {
    std::scoped_lock lock(state.mutex);
    ControlPacket response;
    response.kind = ControlKind::response;
    response.operation = request.operation;
    response.request_id = request.request_id;

    const auto fail = [&state, &response](std::string message) {
        if (state.failure.empty()) {
            state.failure = message;
        }
        response.status = iotox::ErrorCode::protocol_error;
        response.payload = iotox::local::text_payload(std::move(message) + "\n");
        return response;
    };
    const auto prepare = [&state, &response, &fail](AuthorityRecord record) {
        auto body = iotox::security::encode_authority_record_body(record);
        if (!body) {
            return fail("fixture could not encode authority body");
        }
        state.prepared = record;
        response.payload.assign(body.value().begin(), body.value().end());
        return response;
    };

    AuthorityRecord record;
    record.device = state.device;
    record.previous_digest = state.previous_digest;

    switch (request.operation) {
        case ControlOperation::authority_prepare: {
            auto requested = iotox::security::decode_authority_prepare_request(
                request.payload);
            const bool migrate_v2 =
                requested &&
                requested.value().action == AuthorityAction::migrate_v2;
            const bool migrate_v3 =
                requested &&
                requested.value().action == AuthorityAction::migrate_v3;
            if (!requested || (!migrate_v2 && !migrate_v3) ||
                requested.value().role != PrincipalRole::owner ||
                requested.value().capabilities !=
                    (migrate_v3 ? iotox::security::kAuthorityV2Capabilities
                                : iotox::security::kAuthorityV1Capabilities) ||
                requested.value().issuer != requested.value().subject) {
                return fail(
                    "malformed local authority migration prepare request");
            }
            record.format = migrate_v3
                                ? iotox::security::AuthorityLedgerFormat::v3
                                : iotox::security::AuthorityLedgerFormat::v2;
            record.sequence = migrate_v3 ? 5U : 4U;
            record.ownership_epoch = 1U;
            record.issuer = requested.value().issuer;
            if (state.poison_next_local_prepare) {
                state.poison_next_local_prepare = false;
                // A compromised daemon substitutes a terminal grant for the
                // exact owner-self migration requested by the RecallRoot CLI.
                // The CLI must reject this body before transmitting a
                // signature or append request.
                record.action = AuthorityAction::grant;
                record.role = PrincipalRole::operator_role;
                record.capabilities = static_cast<std::uint64_t>(
                    iotox::security::Capability::interactive_terminal);
                record.subject = state.self_subject;
                auto poisoned = iotox::security::encode_authority_record_body(
                    record);
                if (!poisoned) {
                    return fail("fixture could not encode substituted authority body");
                }
                response.payload.assign(
                    poisoned.value().begin(), poisoned.value().end());
                return response;
            }
            record.action = migrate_v3 ? AuthorityAction::migrate_v3
                                       : AuthorityAction::migrate_v2;
            record.role = PrincipalRole::owner;
            record.capabilities = requested.value().capabilities;
            record.subject = requested.value().subject;
            return prepare(record);
        }

        case ControlOperation::authority_append: {
            ++state.local_append_attempts;
            if (request.payload.size() !=
                    iotox::security::kAuthorityRecordBytes ||
                !state.prepared) {
                return fail("malformed or unprepared local signed authority mutation");
            }
            auto decoded = iotox::security::decode_authority_record(
                request.payload);
            if (!decoded ||
                !same_unsigned_record(decoded.value(), *state.prepared)) {
                return fail("local signed mutation changed the prepared authority body");
            }
            iotox::security::AuthorityRecordBody body{};
            std::copy_n(request.payload.begin(), body.size(), body.begin());
            const std::vector<std::uint8_t> message =
                authority_signature_message(body);
            const iotox::Status verified = state.sodium->verify_detached(
                decoded.value().signature, message, decoded.value().issuer);
            if (!verified.ok()) {
                return fail("local signed mutation did not verify against its issuer");
            }
            state.local_received.push_back(decoded.value());
            state.prepared.reset();
            response.payload =
                iotox::local::text_payload("authority-migration-appended\n");
            return response;
        }

        case ControlOperation::authority_remote_delegation_prepare:
            if (request.payload.size() != 48U ||
                read_u32(request.payload) != kFriendNumber) {
                return fail("malformed self-delegation prepare request");
            }
            record.action = AuthorityAction::grant;
            record.role = static_cast<PrincipalRole>(request.payload[36U]);
            record.sequence = 2U;
            record.ownership_epoch = 1U;
            record.capabilities = read_u64(
                std::span<const std::uint8_t>{request.payload}.subspan(40U, 8U));
            record.issuer = read_public_key(request.payload, 4U);
            record.subject = state.self_subject;
            return prepare(record);

        case ControlOperation::authority_remote_revocation_prepare:
            if (request.payload.size() != 68U ||
                read_u32(request.payload) != kFriendNumber) {
                return fail("malformed remote revocation prepare request");
            }
            record.action = AuthorityAction::revoke;
            record.role = PrincipalRole::none;
            record.sequence = 3U;
            record.ownership_epoch = 1U;
            record.issuer = read_public_key(request.payload, 4U);
            record.subject = read_public_key(request.payload, 36U);
            return prepare(record);

        case ControlOperation::authority_remote_successor_prepare:
            if (request.payload.size() != 76U ||
                read_u32(request.payload) != kFriendNumber) {
                return fail("malformed successor nomination prepare request");
            }
            record.format = iotox::security::AuthorityLedgerFormat::v2;
            record.action = AuthorityAction::grant;
            record.role = PrincipalRole::owner;
            record.sequence = 5U;
            record.ownership_epoch = 1U;
            record.capabilities = read_u64(
                std::span<const std::uint8_t>{request.payload}.subspan(68U, 8U));
            record.issuer = read_public_key(request.payload, 4U);
            record.subject = read_public_key(request.payload, 36U);
            return prepare(record);

        case ControlOperation::authority_remote_epoch_transition_prepare:
            if (request.payload.size() != 44U ||
                read_u32(request.payload) != kFriendNumber) {
                return fail("malformed ownership transition prepare request");
            }
            record.format = iotox::security::AuthorityLedgerFormat::v2;
            record.action = AuthorityAction::epoch_transition;
            record.role = PrincipalRole::owner;
            record.sequence = 1U;
            record.ownership_epoch = 2U;
            record.capabilities = read_u64(
                std::span<const std::uint8_t>{request.payload}.subspan(36U, 8U));
            record.issuer = read_public_key(request.payload, 4U);
            record.subject = record.issuer;
            return prepare(record);

        case ControlOperation::authority_remote_migration_prepare:
            if (request.payload.size() != 36U ||
                read_u32(request.payload) != kFriendNumber) {
                return fail("malformed authority v2 migration prepare request");
            }
            record.format = iotox::security::AuthorityLedgerFormat::v2;
            record.action = AuthorityAction::migrate_v2;
            record.role = PrincipalRole::owner;
            record.sequence = 4U;
            record.ownership_epoch = 1U;
            record.capabilities = iotox::security::kAuthorityV1Capabilities;
            record.issuer = read_public_key(request.payload, 4U);
            record.subject = record.issuer;
            return prepare(record);

        case ControlOperation::authority_remote_v3_migration_prepare:
            if (request.payload.size() != 44U ||
                read_u32(request.payload) != kFriendNumber) {
                return fail("malformed authority v3 migration prepare request");
            }
            record.format = iotox::security::AuthorityLedgerFormat::v3;
            record.action = AuthorityAction::migrate_v3;
            record.role = PrincipalRole::owner;
            record.sequence = 2U;
            record.ownership_epoch = 2U;
            record.capabilities =
                read_u64(std::span<const std::uint8_t>{request.payload}.subspan(
                    36U, 8U));
            record.issuer = read_public_key(request.payload, 4U);
            record.subject = record.issuer;
            return prepare(record);

        case ControlOperation::authority_remote_delegation_send: {
            if (request.payload.size() !=
                    4U + iotox::security::kAuthorityRecordBytes ||
                read_u32(request.payload) != kFriendNumber || !state.prepared) {
                return fail("malformed or unprepared signed authority mutation");
            }
            auto decoded = iotox::security::decode_authority_record(
                std::span<const std::uint8_t>{request.payload}.subspan(4U));
            if (!decoded || !same_unsigned_record(decoded.value(), *state.prepared)) {
                return fail("signed mutation changed the prepared authority body");
            }
            iotox::security::AuthorityRecordBody body{};
            std::copy_n(request.payload.begin() + 4,
                        body.size(), body.begin());
            std::vector<std::uint8_t> message = authority_signature_message(body);
            const iotox::Status verified = state.sodium->verify_detached(
                decoded.value().signature, message, decoded.value().issuer);
            if (!verified.ok()) {
                return fail("signed mutation did not verify against its issuer");
            }
            state.received.push_back(decoded.value());
            state.prepared.reset();
            response.payload =
                iotox::local::text_payload("remote-delegation-queued\n");
            return response;
        }

        default:
            return fail("unexpected control operation in authority ceremony");
    }
}

}  // namespace

int main(int argc, char **argv) {
    if (argc != 2) {
        std::cerr << "usage: test_cli_authority_process IOTOX\n";
        return 2;
    }

    const std::filesystem::path iotox = argv[1];
    const std::filesystem::path directory =
        std::filesystem::temp_directory_path() /
        ("iotox-cli-authority-test-" +
         std::to_string(static_cast<long long>(::getpid())));
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);

    try {
        require(std::filesystem::create_directories(directory),
                "unable to create CLI authority process-test directory");
        std::filesystem::permissions(
            directory, std::filesystem::perms::owner_all,
            std::filesystem::perm_options::replace);

        auto sodium = iotox::security::Sodium::load();
        require(sodium.ok(), sodium.status().message());
        CeremonyState state(sodium.value());
        iotox::local::ControlServer::Config config;
        config.socket_path = directory / "control.sock";
        iotox::local::ControlServer server(
            config, [&state](const ControlPacket &request, const auto &) {
                return ceremony_response(state, request);
            });
        const iotox::Status started = server.start();
        require(started.ok(), started.message());

        constexpr std::string_view current_phrase =
            "abacus abdomen abdominal abide abiding ability ablaze able\n";
        constexpr std::string_view successor_phrase =
            "absentee absently absinthe absolute absolve abstain abstract absurd\n";

        const CommandResult substituted = run_control_with_phrase(
            iotox, directory,
            {"authority-migrate-v2-recall-stdin"},
            current_phrase);
        require(substituted.exit_code == 5 &&
                    substituted.output.find(
                        "authority-prepare response changed the requested") !=
                        std::string::npos &&
                    substituted.output.find(current_phrase) == std::string::npos,
                "CLI signed or accepted a substituted local authority body: " +
                    substituted.output);
        {
            std::scoped_lock lock(state.mutex);
            require(state.local_append_attempts == 0U &&
                        state.local_received.empty() && !state.prepared,
                    "CLI transmitted a signature for the substituted local authority body");
        }

        const CommandResult local_migrated = run_control_with_phrase(
            iotox, directory,
            {"authority-migrate-v2-recall-stdin"},
            current_phrase);
        const std::string current_owner =
            extract_field(local_migrated.output, "owner-public-key");
        require(local_migrated.exit_code == 0 && current_owner.size() == 64U &&
                    local_migrated.output.find("authority-migration-appended") !=
                        std::string::npos &&
                    local_migrated.output.find(current_phrase) ==
                        std::string::npos,
                "CLI local authority v2 migration ceremony failed or leaked its phrase: " +
                    local_migrated.output);
        {
            std::scoped_lock lock(state.mutex);
            require(state.local_append_attempts == 1U &&
                        state.local_received.size() == 1U &&
                        state.local_received.front().format ==
                            iotox::security::AuthorityLedgerFormat::v2 &&
                        state.local_received.front().action ==
                            AuthorityAction::migrate_v2 &&
                        state.local_received.front().role ==
                            PrincipalRole::owner &&
                        state.local_received.front().capabilities ==
                            iotox::security::kAuthorityV1Capabilities,
                    "CLI did not sign the exact local authority v2 migration body");
        }

        const CommandResult local_v3_migrated = run_control_with_phrase(
            iotox, directory, {"authority-migrate-v3-recall-stdin", "all-v2"},
            current_phrase);
        require(
            local_v3_migrated.exit_code == 0 &&
                extract_field(local_v3_migrated.output, "owner-public-key") ==
                    current_owner &&
                local_v3_migrated.output.find("authority-migration-appended") !=
                    std::string::npos &&
                local_v3_migrated.output.find(current_phrase) ==
                    std::string::npos,
            "CLI local authority v3 migration ceremony failed or leaked its "
            "phrase: " +
                local_v3_migrated.output);
        {
            std::scoped_lock lock(state.mutex);
            require(
                state.local_append_attempts == 2U &&
                    state.local_received.size() == 2U &&
                    state.local_received.back().format ==
                        iotox::security::AuthorityLedgerFormat::v3 &&
                    state.local_received.back().action ==
                        AuthorityAction::migrate_v3 &&
                    state.local_received.back().capabilities ==
                        iotox::security::kAuthorityV2Capabilities,
                "CLI did not sign the exact local authority v3 migration body");
        }

        const CommandResult rejected_owner = run_control_with_phrase(
            iotox, directory,
            {"authority-delegate-self-recall-stdin", "7", "owner", "all"},
            current_phrase);
        require(rejected_owner.exit_code == 2 &&
                    rejected_owner.output.find("requires a non-owner role") !=
                        std::string::npos,
                "CLI did not reject owner creation through self-delegation");

        const CommandResult delegated = run_control_with_phrase(
            iotox, directory,
            {"authority-delegate-self-recall-stdin", "7", "automation",
             "read.telemetry"},
            current_phrase);
        const std::string delegated_owner =
            extract_field(delegated.output, "owner-public-key");
        require(delegated.exit_code == 0 && delegated_owner == current_owner &&
                    delegated.output.find("remote-delegation-queued") !=
                        std::string::npos &&
                    delegated.output.find(current_phrase) == std::string::npos,
                "CLI remote self-delegation ceremony failed or leaked its phrase: " +
                    delegated.output);

        SigningPublicKey revoked_subject{};
        revoked_subject.fill(0xC3U);
        const CommandResult revoked = run_control_with_phrase(
            iotox, directory,
            {"authority-revoke-remote-recall-stdin", "7",
             iotox::security::hex(revoked_subject)},
            current_phrase);
        require(revoked.exit_code == 0 &&
                    extract_field(revoked.output, "owner-public-key") ==
                        current_owner,
                "CLI remote revocation ceremony failed");

        const CommandResult successor_public = run_control_with_phrase(
            iotox, directory, {"recall-owner-public-key-stdin"},
            successor_phrase);
        const std::string successor =
            extract_field(successor_public.output, "owner-public-key");
        require(successor_public.exit_code == 0 && successor.size() == 64U &&
                    successor != current_owner,
                "CLI did not derive a distinct successor owner");

        const CommandResult migrated = run_control_with_phrase(
            iotox, directory,
            {"authority-migrate-v2-remote-recall-stdin", "7"},
            current_phrase);
        require(migrated.exit_code == 0 &&
                    extract_field(migrated.output, "owner-public-key") ==
                        current_owner &&
                    migrated.output.find("remote-delegation-queued") !=
                        std::string::npos,
                "CLI remote authority v2 migration ceremony failed");

        const CommandResult nominated = run_control_with_phrase(
            iotox, directory,
            {"authority-nominate-successor-remote-recall-stdin", "7",
             successor, "all-v2"},
            current_phrase);
        require(nominated.exit_code == 0 &&
                    extract_field(nominated.output, "owner-public-key") ==
                        current_owner &&
                    extract_field(nominated.output, "successor-public-key") ==
                        successor,
                "CLI remote successor nomination ceremony failed");

        const CommandResult transitioned = run_control_with_phrase(
            iotox, directory,
            {"authority-transition-remote-recall-stdin", "7", "all-v2"},
            successor_phrase);
        require(transitioned.exit_code == 0 &&
                    extract_field(transitioned.output, "owner-public-key") ==
                        successor,
                "CLI successor-signed ownership transition ceremony failed");

        const CommandResult migrated_v3 = run_control_with_phrase(
            iotox, directory,
            {"authority-migrate-v3-remote-recall-stdin", "7", "all-v2"},
            successor_phrase);
        require(migrated_v3.exit_code == 0 &&
                    extract_field(migrated_v3.output, "owner-public-key") ==
                        successor &&
                    migrated_v3.output.find("remote-delegation-queued") !=
                        std::string::npos,
                "CLI remote authority v3 migration ceremony failed");

        {
            std::scoped_lock lock(state.mutex);
            require(state.failure.empty(), state.failure);
            require(!state.prepared.has_value(),
                    "CLI left a prepared authority mutation unsigned");
            require(state.received.size() == 6U,
                    "CLI did not send all six signed remote mutations");
            require(
                state.received[0U].action == AuthorityAction::grant &&
                    state.received[0U].role == PrincipalRole::automation &&
                    state.received[0U].capabilities ==
                        static_cast<std::uint64_t>(
                            iotox::security::Capability::read_telemetry) &&
                    state.received[1U].action == AuthorityAction::revoke &&
                    state.received[1U].subject == revoked_subject &&
                    state.received[2U].format ==
                        iotox::security::AuthorityLedgerFormat::v2 &&
                    state.received[2U].action == AuthorityAction::migrate_v2 &&
                    state.received[2U].capabilities ==
                        iotox::security::kAuthorityV1Capabilities &&
                    state.received[3U].format ==
                        iotox::security::AuthorityLedgerFormat::v2 &&
                    state.received[3U].action == AuthorityAction::grant &&
                    state.received[3U].role == PrincipalRole::owner &&
                    state.received[3U].capabilities ==
                        iotox::security::kAuthorityV2Capabilities &&
                    state.received[4U].action ==
                        AuthorityAction::epoch_transition &&
                    state.received[4U].format ==
                        iotox::security::AuthorityLedgerFormat::v2 &&
                    state.received[4U].capabilities ==
                        iotox::security::kAuthorityV2Capabilities &&
                    state.received[4U].ownership_epoch == 2U &&
                    state.received[4U].sequence == 1U &&
                    state.received[5U].format ==
                        iotox::security::AuthorityLedgerFormat::v3 &&
                    state.received[5U].action == AuthorityAction::migrate_v3 &&
                    state.received[5U].capabilities ==
                        iotox::security::kAuthorityV2Capabilities,
                "CLI sent an unexpected authority mutation sequence");
        }

        server.stop();
        std::filesystem::remove_all(directory, ignored);
        std::cout << "PASS real CLI signs remote authority and ownership ceremonies\n";
        return 0;
    } catch (const std::exception &exception) {
        std::filesystem::remove_all(directory, ignored);
        std::cerr << "FAIL CLI authority process contract: " << exception.what()
                  << '\n';
        return 1;
    }
}
