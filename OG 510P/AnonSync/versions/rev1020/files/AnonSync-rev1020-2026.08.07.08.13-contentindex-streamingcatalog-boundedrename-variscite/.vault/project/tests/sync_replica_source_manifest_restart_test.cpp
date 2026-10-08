#include "self_exec_test_process.hpp"
#include "sync_replica_delivery_test_channel.hpp"
#include "sync_replica_reconciliation_service.hpp"
#include "sync_replica_source_manifest_checkpoint.hpp"
#include "sync_replica_sqlite_owner.hpp"
#include "sync_sqlite_support.hpp"

#if !defined(_WIN32)

#include <sqlite3.h>
#include <signal.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <unistd.h>

#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <optional>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {

namespace fs = std::filesystem;
std::uint64_t checks = 0U;

void require(bool condition, std::string_view message) {
    ++checks;
    if (!condition) throw std::runtime_error(std::string(message));
}

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
        path_ = fs::temp_directory_path() /
            ("anonsync-source-manifest-restart-" +
             std::to_string(static_cast<unsigned long long>(::getpid())) +
             "-" + std::to_string(tick));
        fs::create_directory(path_);
        if (::chmod(path_.c_str(), 0700) != 0) {
            throw std::runtime_error("could not make restart test root private");
        }
    }
    ~TemporaryDirectory() {
        std::error_code ignored;
        fs::remove_all(path_, ignored);
    }
    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;

    fs::path private_directory(std::string_view name) const {
        const fs::path path = path_ / std::string(name);
        fs::create_directory(path);
        if (::chmod(path.c_str(), 0700) != 0) {
            throw std::runtime_error("could not make fixture directory private");
        }
        return path;
    }
    fs::path database(std::string_view name) const {
        return path_ / (std::string(name) + ".sqlite3");
    }
    const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
};

anonsync::SyncSqliteDb open_database(const fs::path& path) {
    anonsync::SyncSqliteDb owner;
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int result = sqlite3_open_v2(
        path.string().c_str(), owner.db.out(), flags, nullptr);
    if (result != SQLITE_OK) {
        throw std::runtime_error(anonsync::sqlite_error_message(
            owner.db, "source manifest restart database open"));
    }
    anonsync::sqlite_set_busy_timeout_or_throw(
        owner.db, 5000, "source manifest restart busy timeout");
    anonsync::sqlite_exec_or_throw(
        owner.db,
        "PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;"
        "PRAGMA wal_autocheckpoint=1;",
        "source manifest restart durability profile");
    return owner;
}

anonsync::SyncReplicaSqliteOwnerLimits owner_limits() {
    anonsync::SyncReplicaSqliteOwnerLimits value;
    value.model.max_operations = 32U;
    value.model.max_context_entries = 64U;
    value.model.max_predecessor_ids = 64U;
    value.model.max_canonical_operation_bytes = 256U * 1024U;
    value.model.max_retained_canonical_bytes = 8U * 1024U * 1024U;
    value.model.max_retained_context_entries = 4096U;
    value.model.max_retained_predecessor_ids = 4096U;
    value.max_outbox_intents = 64U;
    value.max_outbox_destination_bytes = 64U * 1024U;
    return value;
}

anonsync::SyncReplicaFilePayloadStoreLimits payload_limits() {
    anonsync::SyncReplicaFilePayloadStoreLimits value;
    value.max_entries = 32U;
    value.max_payload_bytes = 16U * 1024U * 1024U;
    value.max_indexed_bytes = 64U * 1024U * 1024U;
    value.max_transient_entries = 64U;
    value.max_transient_bytes = 32U * 1024U * 1024U;
    return value;
}

anonsync::SyncReplicaReconciliationProtocolLimits wire_limits() {
    anonsync::SyncReplicaReconciliationProtocolLimits value;
    value.model = owner_limits().model;
    value.max_operations_per_page = 1U;
    value.max_canonical_operation_bytes_per_page = 2U * 1024U * 1024U;
    value.max_payloads_per_page = 2U;
    value.max_single_payload_bytes = 8U * 1024U * 1024U;
    value.max_payload_bytes_per_page = 8U * 1024U * 1024U;
    value.max_payload_extent_bytes = 16U * 1024U * 1024U;
    value.max_request_frame_bytes = 64U * 1024U;
    value.max_response_frame_bytes = 16U * 1024U * 1024U;
    return value;
}

std::string read_file(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("could not open checkpoint bytes");
    return std::string(
        std::istreambuf_iterator<char>(input),
        std::istreambuf_iterator<char>());
}

void replace_payload_inode_with_exact_bytes(
    const fs::path& payload_root,
    std::string_view content_sha256,
    std::string_view bytes) {
    const fs::path replacement = payload_root / ".replacement-payload";
    {
        std::ofstream output(replacement, std::ios::binary | std::ios::trunc);
        if (!output) {
            throw std::runtime_error("could not create replacement payload");
        }
        output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
        if (!output) {
            throw std::runtime_error("could not write replacement payload");
        }
    }
    if (::chmod(replacement.c_str(), 0600) != 0) {
        throw std::runtime_error("could not make replacement payload private");
    }
    fs::rename(replacement, payload_root / std::string(content_sha256));
}

void write_file(const fs::path& path, std::string_view bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("could not create restart fixture file");
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    if (!output) throw std::runtime_error("could not write restart fixture file");
}

class FileSizePublicationFault final {
public:
    FileSizePublicationFault() {
        if (::getrlimit(RLIMIT_FSIZE, &saved_limit_) != 0) {
            throw std::runtime_error(
                "could not observe the source-checkpoint file-size limit");
        }
        struct sigaction ignored{};
        ignored.sa_handler = SIG_IGN;
        if (::sigemptyset(&ignored.sa_mask) != 0 ||
            ::sigaction(SIGXFSZ, &ignored, &saved_action_) != 0) {
            throw std::runtime_error(
                "could not install the source-checkpoint SIGXFSZ guard");
        }
        struct rlimit limited = saved_limit_;
        limited.rlim_cur = 0U;
        if (::setrlimit(RLIMIT_FSIZE, &limited) != 0) {
            (void)::sigaction(SIGXFSZ, &saved_action_, nullptr);
            throw std::runtime_error(
                "could not arm the source-checkpoint publication fault");
        }
        armed_ = true;
    }

    ~FileSizePublicationFault() {
        if (!armed_) return;
        (void)::setrlimit(RLIMIT_FSIZE, &saved_limit_);
        (void)::sigaction(SIGXFSZ, &saved_action_, nullptr);
    }

    FileSizePublicationFault(const FileSizePublicationFault&) = delete;
    FileSizePublicationFault& operator=(const FileSizePublicationFault&) = delete;

    void restore_or_throw() {
        if (!armed_) return;
        const bool limit_restored =
            ::setrlimit(RLIMIT_FSIZE, &saved_limit_) == 0;
        const bool action_restored =
            ::sigaction(SIGXFSZ, &saved_action_, nullptr) == 0;
        if (!limit_restored || !action_restored) {
            throw std::runtime_error(
                "could not restore the source-checkpoint publication fault");
        }
        armed_ = false;
    }

private:
    struct rlimit saved_limit_{};
    struct sigaction saved_action_{};
    bool armed_ = false;
};

constexpr std::string_view kSelfExecHelper =
    "--source-manifest-restart-helper-v1";
constexpr std::uint64_t kSelfExecPulse = 1ULL * 1024ULL * 1024ULL;
constexpr std::uint64_t kSelfExecPayload = 10ULL * 1024ULL * 1024ULL;
constexpr std::string_view kSelfExecFolder =
    "folder-source-manifest-self-exec-restart";
constexpr std::string_view kSelfExecSession =
    "source-manifest-self-exec-restart-session";

anonsync::SyncReplicaActor self_exec_source_actor() {
    return {"device-source-manifest-self-exec-source", 23001U};
}

anonsync::SyncReplicaActor self_exec_receiver_actor() {
    return {"device-source-manifest-self-exec-receiver", 23002U};
}

void run_self_exec_helper_or_throw(int argc, char** argv) {
    anonsync::test::verify_self_exec_child_boundary_or_throw();
    if (argc != 6 || std::string_view(argv[1]) != kSelfExecHelper) {
        throw std::runtime_error("source manifest self-exec helper argv is invalid");
    }
    const std::string_view phase(argv[2]);
    const fs::path source_database(argv[3]);
    const fs::path source_payload_root(argv[4]);
    const fs::path request_path(argv[5]);

    anonsync::SyncSqliteDb source_db = open_database(source_database);
    anonsync::SyncReplicaSqliteOwner source_owner(
        source_db.db, std::string(kSelfExecFolder), self_exec_source_actor(),
        owner_limits(), "source manifest self-exec source owner");
    anonsync::SyncReplicaFilePayloadStore source_store(
        std::string(kSelfExecFolder), source_payload_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        payload_limits(), "source manifest self-exec source store");
    anonsync::SyncReplicaReconciliationService source_service(
        source_owner, source_store, wire_limits(),
        "source manifest self-exec source service",
        anonsync::sync_replica_default_selective_sync_policy(),
        anonsync::kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
        anonsync::kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply,
        anonsync::kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply,
        kSelfExecPulse);
    const auto source_channel =
        anonsync::testing::SyncReplicaDeliveryTestChannelFactory::make_or_throw(
            self_exec_receiver_actor(), kSelfExecSession);
    const std::string request_frame = read_file(request_path);

    if (phase == "prepare") {
        auto session = source_service.make_serve_session_or_throw(source_channel);
        const auto response = source_service.serve_request_or_throw(
            source_channel, request_frame, session);
        const auto status = source_service.source_manifest_projection_status();
        require(
            response.response.disposition ==
                    anonsync::SyncReplicaReconciliationResponseDisposition::
                        SourcePayloadPreparing &&
                session.content_defined_manifest_hashed_bytes() ==
                    kSelfExecPulse &&
                status.pending && status.next_offset_bytes == kSelfExecPulse,
            "self-exec prepare did not publish the first exact byte frontier");
        return;
    }
    if (phase == "resume") {
        const auto discovered =
            source_service.discover_source_manifest_projection_or_throw();
        require(
            discovered.pending &&
                discovered.next_offset_bytes == kSelfExecPulse,
            "fresh process did not discover the durable source obligation");
        std::uint64_t hashed_bytes = 0U;
        std::uint64_t pulses = 0U;
        for (;;) {
            const auto step =
                source_service.continue_source_manifest_projection_or_throw();
            ++pulses;
            hashed_bytes += step.hashed_bytes;
            require(
                step.hashed_bytes != 0U &&
                    step.hashed_bytes <= kSelfExecPulse,
                "self-exec resume crossed its bounded byte frontier");
            if (pulses == 1U) {
                require(
                    step.before.pending &&
                        step.before.next_offset_bytes == kSelfExecPulse &&
                        step.after.pending &&
                        step.after.next_offset_bytes == 2U * kSelfExecPulse,
                    "fresh process did not resume at the durable interior frontier");
            }
            if (step.disposition ==
                anonsync::
                    SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                        Completed) {
                require(!step.after.pending,
                        "self-exec completion retained pending source work");
                break;
            }
            require(
                step.disposition ==
                        anonsync::
                            SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                                Progress &&
                    step.after.pending,
                "self-exec resume did not make bounded progress");
        }
        require(
            hashed_bytes == kSelfExecPayload - kSelfExecPulse &&
                pulses == (kSelfExecPayload - kSelfExecPulse) / kSelfExecPulse,
            "fresh process did not hash exactly the remaining source bytes");
        return;
    }
    if (phase == "serve") {
        auto session = source_service.make_serve_session_or_throw(source_channel);
        const auto response = source_service.serve_request_or_throw(
            source_channel, request_frame, session);
        require(
            response.response.disposition ==
                    anonsync::SyncReplicaReconciliationResponseDisposition::Page &&
                !response.response.payloads.empty(),
            "fresh process did not serve the completed durable manifest");
        require(
            session.content_defined_manifest_hashed_bytes() == 0U &&
                session.content_defined_manifest_scans() == 0U &&
                session.content_defined_manifest_reuses() == 1U,
            "fresh process rehashed a completed durable manifest");
        return;
    }
    throw std::runtime_error("source manifest self-exec helper phase is invalid");
}

void test_true_process_restart() {
    TemporaryDirectory temporary;
    const fs::path source_database = temporary.database("self-exec-source");
    const fs::path receiver_database = temporary.database("self-exec-receiver");
    const fs::path source_payload_root =
        temporary.private_directory("self-exec-source-payloads");
    const fs::path receiver_payload_root =
        temporary.private_directory("self-exec-receiver-payloads");
    const fs::path request_path = temporary.path() / "request.frame";
    const fs::path checkpoint_path = source_payload_root /
        std::string(anonsync::kSyncReplicaSourceManifestCheckpointBasename);
    std::string operation_id;

    {
        anonsync::SyncSqliteDb source_db = open_database(source_database);
        anonsync::SyncSqliteDb receiver_db = open_database(receiver_database);
        anonsync::SyncReplicaSqliteOwner source_owner(
            source_db.db, std::string(kSelfExecFolder), self_exec_source_actor(),
            owner_limits(), "self-exec fixture source owner");
        anonsync::SyncReplicaSqliteOwner receiver_owner(
            receiver_db.db, std::string(kSelfExecFolder),
            self_exec_receiver_actor(), owner_limits(),
            "self-exec fixture receiver owner");
        anonsync::SyncReplicaFilePayloadStore source_store(
            std::string(kSelfExecFolder), source_payload_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            payload_limits(), "self-exec fixture source store");
        anonsync::SyncReplicaFilePayloadStore receiver_store(
            std::string(kSelfExecFolder), receiver_payload_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            payload_limits(), "self-exec fixture receiver store");
        const std::string payload(
            static_cast<std::size_t>(kSelfExecPayload), '\x2a');
        const auto put = source_store.put_payload_or_throw(payload);
        const auto operation = source_owner.publish_local_file_or_throw(
            "media/self-exec-ten-mebibytes.bin", put.size_bytes,
            put.content_sha256);
        operation_id = operation.operation_id;
        anonsync::SyncReplicaReconciliationService receiver_service(
            receiver_owner, receiver_store, wire_limits(),
            "self-exec fixture receiver service");
        const auto receiver_channel =
            anonsync::testing::SyncReplicaDeliveryTestChannelFactory::make_or_throw(
                self_exec_source_actor(), kSelfExecSession);
        const auto request =
            receiver_service.make_request_or_throw(receiver_channel);
        write_file(request_path, request.request_frame);
    }

    const fs::path executable =
        anonsync::test::current_self_executable_or_throw();
    const auto run_phase = [&](std::string phase, std::string_view label) {
        auto child = anonsync::test::spawn_self_exec_test_process_or_throw(
            executable,
            {std::string(kSelfExecHelper), std::move(phase),
             source_database.string(), source_payload_root.string(),
             request_path.string()});
        child.wait_for_exact_exit(0, std::chrono::seconds(30), label);
    };

    run_phase("prepare", "source-manifest self-exec prepare");
    const auto active =
        anonsync::parse_sync_replica_source_manifest_checkpoint_or_throw(
            read_file(checkpoint_path), payload_limits().max_payload_bytes,
            anonsync::kSyncReplicaSourceManifestCheckpointMaximumChunks,
            "self-exec active checkpoint");
    require(
        active.disposition ==
                anonsync::SyncReplicaSourceManifestCheckpointDisposition::
                    ActiveProjection &&
            active.operation_id == operation_id &&
            active.next_offset_bytes == kSelfExecPulse,
        "self-exec prepare did not leave the exact active checkpoint");

    run_phase("resume", "source-manifest self-exec resume");
    const std::string complete_bytes = read_file(checkpoint_path);
    const auto complete =
        anonsync::parse_sync_replica_source_manifest_checkpoint_or_throw(
            complete_bytes, payload_limits().max_payload_bytes,
            anonsync::kSyncReplicaSourceManifestCheckpointMaximumChunks,
            "self-exec complete checkpoint");
    require(
        complete.disposition ==
                anonsync::SyncReplicaSourceManifestCheckpointDisposition::
                    CompleteManifest &&
            complete.operation_id == operation_id &&
            complete.next_offset_bytes == kSelfExecPayload &&
            complete.generation == active.generation + 1U,
        "self-exec resume did not publish one completion after bounded local pulses");

    run_phase("serve", "source-manifest self-exec completed reuse");
    require(
        read_file(checkpoint_path) == complete_bytes,
        "completed-manifest reuse rewrote the durable acceleration record");
}

void test_completed_publication_retries_from_peer_free_discovery() {
    constexpr std::uint64_t kPulse = 5ULL * 1024ULL * 1024ULL;
    constexpr std::uint64_t kPayload = 2ULL * kPulse;
    const std::string folder =
        "folder-source-manifest-complete-publication-retry";
    const anonsync::SyncReplicaActor source_actor{
        "device-source-manifest-publication-source", 24001U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-source-manifest-publication-receiver", 24002U};
    constexpr std::string_view kSession =
        "source-manifest-complete-publication-retry-session";

    TemporaryDirectory temporary;
    anonsync::SyncSqliteDb source_db =
        open_database(temporary.database("publication-source"));
    anonsync::SyncSqliteDb receiver_db =
        open_database(temporary.database("publication-receiver"));
    const fs::path source_payload_root =
        temporary.private_directory("publication-source-payloads");
    const fs::path receiver_payload_root =
        temporary.private_directory("publication-receiver-payloads");
    anonsync::SyncReplicaSqliteOwner source_owner(
        source_db.db, folder, source_actor, owner_limits(),
        "source manifest publication source owner");
    anonsync::SyncReplicaSqliteOwner receiver_owner(
        receiver_db.db, folder, receiver_actor, owner_limits(),
        "source manifest publication receiver owner");
    anonsync::SyncReplicaFilePayloadStore source_store(
        folder, source_payload_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        payload_limits(), "source manifest publication source store");
    anonsync::SyncReplicaFilePayloadStore receiver_store(
        folder, receiver_payload_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        payload_limits(), "source manifest publication receiver store");
    const std::string payload(static_cast<std::size_t>(kPayload), '\x6d');
    const auto put = source_store.put_payload_or_throw(payload);
    const auto operation = source_owner.publish_local_file_or_throw(
        "media/publication-retry.bin", put.size_bytes, put.content_sha256);

    anonsync::SyncReplicaReconciliationService receiver_service(
        receiver_owner, receiver_store, wire_limits(),
        "source manifest publication receiver service");
    anonsync::SyncReplicaReconciliationService source_service(
        source_owner, source_store, wire_limits(),
        "source manifest publication source service",
        anonsync::sync_replica_default_selective_sync_policy(),
        anonsync::kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
        anonsync::kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply,
        anonsync::kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply,
        kPulse);
    const auto receiver_channel =
        anonsync::testing::SyncReplicaDeliveryTestChannelFactory::make_or_throw(
            source_actor, kSession);
    const auto source_channel =
        anonsync::testing::SyncReplicaDeliveryTestChannelFactory::make_or_throw(
            receiver_actor, kSession);
    const auto request = receiver_service.make_request_or_throw(receiver_channel);
    auto session = source_service.make_serve_session_or_throw(source_channel);
    const auto first = source_service.serve_request_or_throw(
        source_channel, request.request_frame, session);
    require(
        first.response.disposition ==
                anonsync::SyncReplicaReconciliationResponseDisposition::
                    SourcePayloadPreparing &&
            session.content_defined_manifest_hashed_bytes() == kPulse,
        "publication-retry fixture did not stop at its first exact pulse");

    const fs::path checkpoint_path = source_payload_root /
        std::string(anonsync::kSyncReplicaSourceManifestCheckpointBasename);
    const std::string active_bytes = read_file(checkpoint_path);
    const auto active =
        anonsync::parse_sync_replica_source_manifest_checkpoint_or_throw(
            active_bytes, payload_limits().max_payload_bytes,
            anonsync::kSyncReplicaSourceManifestCheckpointMaximumChunks,
            "publication-retry active checkpoint");
    require(
        active.operation_id == operation.operation_id &&
            active.disposition ==
                anonsync::SyncReplicaSourceManifestCheckpointDisposition::
                    ActiveProjection &&
            active.next_offset_bytes == kPulse,
        "publication-retry fixture did not retain its active frontier");

    {
        FileSizePublicationFault publication_fault;
        const auto completed =
            source_service.continue_source_manifest_projection_or_throw();
        publication_fault.restore_or_throw();
        require(
            completed.disposition ==
                    anonsync::
                        SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                            Completed &&
                completed.hashed_bytes == kPulse &&
                !completed.after.pending,
            "typed completion-publication failure changed hash completion");
    }
    require(
        read_file(checkpoint_path) == active_bytes,
        "failed completion publication replaced the last durable frontier");

    const auto discovered =
        source_service.discover_source_manifest_projection_or_throw();
    require(
        !discovered.pending,
        "peer-free publication retry recreated completed hash work");
    const std::string complete_bytes = read_file(checkpoint_path);
    const auto complete =
        anonsync::parse_sync_replica_source_manifest_checkpoint_or_throw(
            complete_bytes, payload_limits().max_payload_bytes,
            anonsync::kSyncReplicaSourceManifestCheckpointMaximumChunks,
            "publication-retry complete checkpoint");
    require(
        complete.disposition ==
                anonsync::SyncReplicaSourceManifestCheckpointDisposition::
                    CompleteManifest &&
            complete.operation_id == operation.operation_id &&
            complete.next_offset_bytes == kPayload &&
            complete.generation == active.generation + 1U,
        "peer-free discovery did not publish the retained complete checkpoint");

    anonsync::SyncReplicaReconciliationService fresh_source_service(
        source_owner, source_store, wire_limits(),
        "fresh source manifest publication source service",
        anonsync::sync_replica_default_selective_sync_policy(),
        anonsync::kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
        anonsync::kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply,
        anonsync::kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply,
        kPulse);
    auto fresh_session =
        fresh_source_service.make_serve_session_or_throw(source_channel);
    const auto served = fresh_source_service.serve_request_or_throw(
        source_channel, request.request_frame, fresh_session);
    require(
        served.response.disposition ==
                anonsync::SyncReplicaReconciliationResponseDisposition::Page &&
            !served.response.payloads.empty() &&
            fresh_session.content_defined_manifest_hashed_bytes() == 0U &&
            fresh_session.content_defined_manifest_scans() == 0U &&
            fresh_session.content_defined_manifest_reuses() == 1U,
        "fresh service rehashed after peer-free complete-checkpoint retry");
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc > 1 && std::string_view(argv[1]) == kSelfExecHelper) {
            run_self_exec_helper_or_throw(argc, argv);
            return 0;
        }
        constexpr std::uint64_t kPulse = 1ULL * 1024ULL * 1024ULL;
        constexpr std::uint64_t kPayload = 10ULL * 1024ULL * 1024ULL;
        TemporaryDirectory temporary;
        const std::string folder = "folder-source-manifest-restart";
        const anonsync::SyncReplicaActor source_actor{
            "device-source-manifest-restart-source", 21001U};
        const anonsync::SyncReplicaActor receiver_actor{
            "device-source-manifest-restart-receiver", 21002U};
        anonsync::SyncSqliteDb source_db =
            open_database(temporary.database("source"));
        anonsync::SyncSqliteDb receiver_db =
            open_database(temporary.database("receiver"));
        const fs::path source_payload_root =
            temporary.private_directory("source-payloads");
        const fs::path receiver_payload_root =
            temporary.private_directory("receiver-payloads");
        anonsync::SyncReplicaSqliteOwner source_owner(
            source_db.db, folder, source_actor, owner_limits(),
            "source manifest restart source owner");
        anonsync::SyncReplicaSqliteOwner receiver_owner(
            receiver_db.db, folder, receiver_actor, owner_limits(),
            "source manifest restart receiver owner");
        anonsync::SyncReplicaFilePayloadStore source_store(
            folder, source_payload_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            payload_limits(), "source manifest restart source store");
        anonsync::SyncReplicaFilePayloadStore receiver_store(
            folder, receiver_payload_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            payload_limits(), "source manifest restart receiver store");
        const std::string payload(static_cast<std::size_t>(kPayload), '\0');
        const auto put = source_store.put_payload_or_throw(payload);
        const auto operation = source_owner.publish_local_file_or_throw(
            "media/ten-mebibytes.bin", put.size_bytes, put.content_sha256);
        anonsync::SyncReplicaReconciliationService receiver_service(
            receiver_owner, receiver_store, wire_limits(),
            "source manifest restart receiver service");
        const auto receiver_channel =
            anonsync::testing::SyncReplicaDeliveryTestChannelFactory::make_or_throw(
                source_actor, "source-manifest-restart-session");
        const auto source_channel =
            anonsync::testing::SyncReplicaDeliveryTestChannelFactory::make_or_throw(
                receiver_actor, "source-manifest-restart-session");
        const auto request = receiver_service.make_request_or_throw(
            receiver_channel);
        const fs::path checkpoint_path = source_payload_root /
            std::string(anonsync::kSyncReplicaSourceManifestCheckpointBasename);

        {
            anonsync::SyncReplicaReconciliationService first(
                source_owner, source_store, wire_limits(),
                "first source manifest service",
                anonsync::sync_replica_default_selective_sync_policy(),
                anonsync::kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
                anonsync::kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply,
                anonsync::kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply,
                kPulse);
            auto session = first.make_serve_session_or_throw(source_channel);
            const auto response = first.serve_request_or_throw(
                source_channel, request.request_frame, session);
            const auto status = first.source_manifest_projection_status();
            require(
                response.response.disposition ==
                    anonsync::SyncReplicaReconciliationResponseDisposition::
                        SourcePayloadPreparing,
                "first bounded pulse unexpectedly completed the 10 MiB manifest");
            require(
                session.content_defined_manifest_hashed_bytes() == kPulse &&
                    status.pending && status.next_offset_bytes == kPulse &&
                    status.completed_chunk_count == 0U,
                "first bounded pulse did not retain an interior first-chunk frontier");
        }

        require(fs::exists(checkpoint_path),
                "active source-manifest checkpoint was not published");
        const auto active =
            anonsync::parse_sync_replica_source_manifest_checkpoint_or_throw(
                read_file(checkpoint_path), payload_limits().max_payload_bytes,
                anonsync::kSyncReplicaSourceManifestCheckpointMaximumChunks,
                "active restart checkpoint");
        require(
            active.disposition ==
                    anonsync::SyncReplicaSourceManifestCheckpointDisposition::
                        ActiveProjection &&
                active.operation_id == operation.operation_id &&
                active.next_offset_bytes == kPulse &&
                active.whole_hash.total_bytes == kPulse &&
                active.completed_chunk_bytes == 0U &&
                active.chunker.pending_chunk_bytes == kPulse &&
                active.current_chunk_hash.total_bytes == kPulse &&
                active.chunker.completed_chunk_count == 0U &&
                !active.chunker.finished,
            "active checkpoint did not bind the exact operation and interior byte frontier");

        {
            anonsync::SyncReplicaReconciliationService second(
                source_owner, source_store, wire_limits(),
                "second source manifest service",
                anonsync::sync_replica_default_selective_sync_policy(),
                anonsync::kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
                anonsync::kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply,
                anonsync::kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply,
                kPulse);
            std::uint64_t source_local_hashed_bytes = 0U;
            std::uint64_t source_local_pulses = 0U;
            for (;;) {
                const auto step =
                    second.continue_source_manifest_projection_or_throw();
                ++source_local_pulses;
                source_local_hashed_bytes += step.hashed_bytes;
                require(
                    step.hashed_bytes != 0U && step.hashed_bytes <= kPulse,
                    "source-local restart pulse exceeded its exact byte frontier");
                if (source_local_pulses == 1U) {
                    require(
                        step.before.pending &&
                            step.before.next_offset_bytes == kPulse &&
                            step.after.pending &&
                            step.after.next_offset_bytes == 2U * kPulse,
                        "fresh peer-free service did not resume at the durable interior frontier");
                }
                if (step.disposition ==
                    anonsync::SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                        Completed) {
                    require(
                        !step.after.pending,
                        "completed source-local restart retained pending work");
                    break;
                }
                require(
                    step.disposition ==
                            anonsync::SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                                Progress &&
                        step.after.pending,
                    "source-local restart did not make bounded progress");
            }
            require(
                source_local_hashed_bytes == kPayload - kPulse &&
                    source_local_pulses ==
                        (kPayload - kPulse) / kPulse,
                "peer-free scheduler did not hash exactly the remaining source bytes");
        }

        const auto complete =
            anonsync::parse_sync_replica_source_manifest_checkpoint_or_throw(
                read_file(checkpoint_path), payload_limits().max_payload_bytes,
                anonsync::kSyncReplicaSourceManifestCheckpointMaximumChunks,
                "complete restart checkpoint");
        require(
            complete.disposition ==
                    anonsync::SyncReplicaSourceManifestCheckpointDisposition::
                        CompleteManifest &&
                complete.completed_chunk_bytes == kPayload &&
                complete.operation_id == operation.operation_id &&
                complete.generation == active.generation + 1U,
            "completed manifest was not retained with one coalesced durable publication");
        require(
            read_file(checkpoint_path).size() < 384U * 1024U,
            "completed checkpoint exceeded its bounded memory/file frontier");

        {
            anonsync::SyncReplicaReconciliationService third(
                source_owner, source_store, wire_limits(),
                "third source manifest service",
                anonsync::sync_replica_default_selective_sync_policy(),
                anonsync::kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
                anonsync::kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply,
                anonsync::kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply,
                kPulse);
            auto session = third.make_serve_session_or_throw(source_channel);
            const auto response = third.serve_request_or_throw(
                source_channel, request.request_frame, session);
            require(
                response.response.disposition ==
                        anonsync::SyncReplicaReconciliationResponseDisposition::Page &&
                    !response.response.payloads.empty(),
                "fresh service did not serve from the durable completed manifest");
            require(
                session.content_defined_manifest_hashed_bytes() == 0U &&
                    session.content_defined_manifest_scans() == 0U &&
                    session.content_defined_manifest_reuses() == 1U,
                "fresh completed-manifest reuse performed source hashing");
        }

        const auto snapshot = source_store.snapshot_or_throw();
        require(
            snapshot.entry_count() == 1U &&
                snapshot.payload_size_or_none(operation.content_sha256) ==
                    std::optional<std::uint64_t>(kPayload),
            "checkpoint metadata contaminated the physical payload inventory");

        // An exact digest-named payload may be replaced by a different private
        // inode carrying the same bytes. The old checkpoint then loses its
        // acceleration authority. Prove that a lower fresh arbitrary-byte
        // frontier is published immediately rather than being suppressed until
        // it catches the stale higher frontier.
        {
            constexpr std::uint64_t kDriftInitialPulse =
                8ULL * 1024ULL * 1024ULL;
            constexpr std::uint64_t kSmallPulse = 1ULL * 1024ULL * 1024ULL;
            TemporaryDirectory drift_temporary;
            const std::string drift_folder =
                "folder-source-manifest-inode-drift";
            const anonsync::SyncReplicaActor drift_source_actor{
                "device-source-manifest-drift-source", 22001U};
            const anonsync::SyncReplicaActor drift_receiver_actor{
                "device-source-manifest-drift-receiver", 22002U};
            anonsync::SyncSqliteDb drift_source_db =
                open_database(drift_temporary.database("source"));
            anonsync::SyncSqliteDb drift_receiver_db =
                open_database(drift_temporary.database("receiver"));
            const fs::path drift_source_payload_root =
                drift_temporary.private_directory("source-payloads");
            const fs::path drift_receiver_payload_root =
                drift_temporary.private_directory("receiver-payloads");
            anonsync::SyncReplicaSqliteOwner drift_source_owner(
                drift_source_db.db, drift_folder, drift_source_actor,
                owner_limits(), "source manifest drift source owner");
            anonsync::SyncReplicaSqliteOwner drift_receiver_owner(
                drift_receiver_db.db, drift_folder, drift_receiver_actor,
                owner_limits(), "source manifest drift receiver owner");
            anonsync::SyncReplicaFilePayloadStore drift_source_store(
                drift_folder, drift_source_payload_root,
                anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                    CreateIfMissing,
                payload_limits(), "source manifest drift source store");
            anonsync::SyncReplicaFilePayloadStore drift_receiver_store(
                drift_folder, drift_receiver_payload_root,
                anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                    CreateIfMissing,
                payload_limits(), "source manifest drift receiver store");
            const std::string drift_payload(
                static_cast<std::size_t>(kPayload), '\x5a');
            const auto drift_put =
                drift_source_store.put_payload_or_throw(drift_payload);
            const auto drift_operation =
                drift_source_owner.publish_local_file_or_throw(
                    "media/inode-drift.bin", drift_put.size_bytes,
                    drift_put.content_sha256);
            anonsync::SyncReplicaReconciliationService drift_receiver_service(
                drift_receiver_owner, drift_receiver_store, wire_limits(),
                "source manifest drift receiver service");
            const auto drift_receiver_channel =
                anonsync::testing::SyncReplicaDeliveryTestChannelFactory::
                    make_or_throw(
                        drift_source_actor,
                        "source-manifest-drift-session");
            const auto drift_source_channel =
                anonsync::testing::SyncReplicaDeliveryTestChannelFactory::
                    make_or_throw(
                        drift_receiver_actor,
                        "source-manifest-drift-session");
            const auto drift_request =
                drift_receiver_service.make_request_or_throw(
                    drift_receiver_channel);
            const fs::path drift_checkpoint_path =
                drift_source_payload_root /
                std::string(
                    anonsync::kSyncReplicaSourceManifestCheckpointBasename);

            {
                anonsync::SyncReplicaReconciliationService first_drift(
                    drift_source_owner, drift_source_store, wire_limits(),
                    "first source manifest drift service",
                    anonsync::sync_replica_default_selective_sync_policy(),
                    anonsync::
                        kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
                    anonsync::
                        kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply,
                    anonsync::
                        kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply,
                    kDriftInitialPulse);
                auto session = first_drift.make_serve_session_or_throw(
                    drift_source_channel);
                const auto response = first_drift.serve_request_or_throw(
                    drift_source_channel, drift_request.request_frame,
                    session);
                require(
                    response.response.disposition ==
                        anonsync::SyncReplicaReconciliationResponseDisposition::
                            SourcePayloadPreparing,
                    "drift fixture unexpectedly completed its first projection");
            }
            const auto stale =
                anonsync::parse_sync_replica_source_manifest_checkpoint_or_throw(
                    read_file(drift_checkpoint_path),
                    payload_limits().max_payload_bytes,
                    anonsync::
                        kSyncReplicaSourceManifestCheckpointMaximumChunks,
                    "stale inode checkpoint");
            require(
                stale.operation_id == drift_operation.operation_id &&
                    stale.next_offset_bytes == kDriftInitialPulse &&
                    stale.next_offset_bytes > kSmallPulse,
                "drift fixture did not establish a higher durable byte frontier");

            replace_payload_inode_with_exact_bytes(
                drift_source_payload_root, drift_put.content_sha256,
                drift_payload);

            {
                anonsync::SyncReplicaReconciliationService second_drift(
                    drift_source_owner, drift_source_store, wire_limits(),
                    "second source manifest drift service",
                    anonsync::sync_replica_default_selective_sync_policy(),
                    anonsync::
                        kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
                    anonsync::
                        kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply,
                    anonsync::
                        kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply,
                    kSmallPulse);
                auto session = second_drift.make_serve_session_or_throw(
                    drift_source_channel);
                const auto response = second_drift.serve_request_or_throw(
                    drift_source_channel, drift_request.request_frame,
                    session);
                require(
                    response.response.disposition ==
                            anonsync::SyncReplicaReconciliationResponseDisposition::
                                SourcePayloadPreparing &&
                        session.content_defined_manifest_hashed_bytes() ==
                            kSmallPulse,
                    "inode drift did not restart at the configured fresh pulse");
            }
            const auto refreshed =
                anonsync::parse_sync_replica_source_manifest_checkpoint_or_throw(
                    read_file(drift_checkpoint_path),
                    payload_limits().max_payload_bytes,
                    anonsync::
                        kSyncReplicaSourceManifestCheckpointMaximumChunks,
                    "refreshed inode checkpoint");
            require(
                refreshed.generation == stale.generation + 1U &&
                    refreshed.operation_id == drift_operation.operation_id &&
                    refreshed.payload_metadata != stale.payload_metadata &&
                    refreshed.disposition ==
                        anonsync::SyncReplicaSourceManifestCheckpointDisposition::
                            ActiveProjection &&
                    refreshed.next_offset_bytes == kSmallPulse &&
                    refreshed.next_offset_bytes < stale.next_offset_bytes &&
                    refreshed.completed_chunk_bytes == 0U &&
                    refreshed.whole_hash.total_bytes == kSmallPulse &&
                    refreshed.current_chunk_hash.total_bytes == kSmallPulse &&
                    refreshed.chunker.pending_chunk_bytes == kSmallPulse &&
                    !refreshed.chunker.finished,
                "stale durable frontier suppressed the lower exact-inode byte checkpoint");
        }

        test_true_process_restart();
        test_completed_publication_retries_from_peer_free_discovery();

        std::cout << "sync replica source manifest restart tests passed: "
                  << checks << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica source manifest restart test failure after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}

#else

int main() { return 0; }

#endif
