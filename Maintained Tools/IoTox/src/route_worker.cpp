#include "iotox/route_worker.hpp"

#include "iotox/security/random.hpp"
#include "iotox/sync_content_wire.hpp"
#include "iotox/sync_wire.hpp"

#include <algorithm>
#include <chrono>
#include <limits>
#include <map>
#include <mutex>
#include <sys/stat.h>
#include <thread>
#include <unistd.h>

namespace iotox::routes {

ToxTransport::Config apply_worker_network_override(
    ToxTransport::Config transport_config,
    const WorkerNetworkOverride &network_override) {
    transport_config.network = network_override.network;
    transport_config.socks5_proxy = network_override.socks5_proxy;
    if (!network_override.bootstrap_nodes.empty()) {
        transport_config.bootstrap_nodes = network_override.bootstrap_nodes;
    }
    if (!network_override.tcp_relays.empty()) {
        transport_config.tcp_relays = network_override.tcp_relays;
    }
    return transport_config;
}

namespace {

std::uint64_t unix_time_ms() {
    return static_cast<std::uint64_t>(
        std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count());
}

Status validate_private_directory(const std::filesystem::path &path) {
    struct stat state {};
    if (::lstat(path.c_str(), &state) != 0) {
        return Status{ErrorCode::io_error,
                      "route worker state root is unavailable"};
    }
    if (!S_ISDIR(state.st_mode) || S_ISLNK(state.st_mode) ||
        state.st_uid != ::geteuid() || (state.st_mode & 0777U) != 0700U) {
        return Status{
            ErrorCode::io_error,
            "route worker state root must be an owner-owned mode-0700 directory"};
    }
    return Status::success();
}

Status validate_private_state(const std::filesystem::path &path) {
    struct stat state {};
    if (::lstat(path.c_str(), &state) != 0) {
        return Status{ErrorCode::io_error,
                      "configured route worker savedata is unavailable"};
    }
    if (!S_ISREG(state.st_mode) || S_ISLNK(state.st_mode) ||
        state.st_uid != ::geteuid() || state.st_nlink != 1U ||
        (state.st_mode & 0777U) != 0600U || state.st_size <= 0) {
        return Status{
            ErrorCode::io_error,
            "route worker savedata must be a nonempty owner-owned mode-0600 single-link regular file"};
    }
    return Status::success();
}

bool retryable(ErrorCode code) {
    return code == ErrorCode::unavailable || code == ErrorCode::timeout ||
           code == ErrorCode::resource_exhausted;
}

bool sync_frame_type(protocol::MessageType type) noexcept {
    return type == protocol::MessageType::sync_object_request ||
           type == protocol::MessageType::sync_object_result ||
           type == protocol::MessageType::sync_range_request ||
           type == protocol::MessageType::sync_range_result ||
           type == protocol::MessageType::sync_content_object_request ||
           type == protocol::MessageType::sync_content_object_result ||
           type == protocol::MessageType::sync_content_availability_request ||
           type == protocol::MessageType::sync_content_availability_result;
}

Status validate_sync_frame(const protocol::Frame &frame) {
    if (frame.type == protocol::MessageType::sync_object_request) {
        return sync::validate_sync_object_request_frame(frame);
    }
    if (frame.type == protocol::MessageType::sync_object_result) {
        return sync::validate_sync_object_result_frame(frame);
    }
    if (frame.type == protocol::MessageType::sync_range_request) {
        return sync::validate_sync_range_request_frame(frame);
    }
    if (frame.type == protocol::MessageType::sync_range_result) {
        return sync::validate_sync_range_result_frame(frame);
    }
    if (frame.type == protocol::MessageType::sync_content_object_request) {
        return sync::validate_sync_content_object_request_frame(frame);
    }
    if (frame.type == protocol::MessageType::sync_content_object_result) {
        return sync::validate_sync_content_object_result_frame(frame);
    }
    if (frame.type ==
        protocol::MessageType::sync_content_availability_request) {
        return sync::validate_sync_content_availability_request_frame(frame);
    }
    if (frame.type ==
        protocol::MessageType::sync_content_availability_result) {
        return sync::validate_sync_content_availability_result_frame(frame);
    }
    return Status{ErrorCode::unsupported,
                  "auxiliary route permits only sync object/range/content request/result frames"};
}

bool range_sync_frame_type(protocol::MessageType type) noexcept {
    return type == protocol::MessageType::sync_range_request ||
           type == protocol::MessageType::sync_range_result;
}

bool content_sync_frame_type(protocol::MessageType type) noexcept {
    return type == protocol::MessageType::sync_content_object_request ||
           type == protocol::MessageType::sync_content_object_result ||
           type == protocol::MessageType::sync_content_availability_request ||
           type == protocol::MessageType::sync_content_availability_result;
}

void saturating_increment(std::uint64_t &value) noexcept {
    if (value != std::numeric_limits<std::uint64_t>::max()) ++value;
}

// A successful toxcore enqueue is not an end-to-end acknowledgement. During
// asymmetric reconnect, the peer can still classify that packet against its
// preceding offline application epoch. Retry only the two frozen handshake
// records, at a bounded cadence, until their transcript is confirmed.
constexpr auto kApplicationHandshakeRetryInterval =
    std::chrono::seconds(1);

}  // namespace

class WorkerSupervisor::Impl {
  public:
    explicit Impl(Config config) : config_(std::move(config)) {}
    ~Impl() { stop(); }

    Status set_sync_content_frames_enabled(bool enabled) {
        if (start_called_.load()) {
            return Status{
                ErrorCode::invalid_argument,
                "route worker content construction gate is immutable after start"};
        }
        if (enabled && !config_.sync_frames_enabled) {
            return Status{
                ErrorCode::invalid_argument,
                "route worker content frames require base sync frames"};
        }
        config_.sync_content_frames_enabled = enabled;
        return Status::success();
    }

    Status start() {
        bool expected = false;
        if (!start_called_.compare_exchange_strong(expected, true)) {
            return Status{ErrorCode::invalid_argument,
                          "route worker supervisor start may only be called once"};
        }
        const Status root = validate_private_directory(config_.state_root);
        if (!root.ok()) return root;
        if (config_.make_binding_frame &&
            config_.make_private_binding_frame) {
            return Status{
                ErrorCode::invalid_argument,
                "route worker v1 and private-v2 binding factories are mutually exclusive"};
        }
        if ((config_.make_binding_frame ||
             config_.make_private_binding_frame) &&
            config_.sodium == nullptr) {
            return Status{ErrorCode::invalid_argument,
                          "route-binding worker exchange requires the sodium verifier"};
        }
        if (config_.session_incarnation == 0U) {
            return Status{
                ErrorCode::invalid_argument,
                "route workers require a nonzero application-protocol incarnation"};
        }
        const Status network_overrides = validate_network_overrides();
        if (!network_overrides.ok()) return network_overrides;
        if (config_.maximum_transfer_terminal_events == 0U ||
            config_.maximum_transfer_terminal_events > 65536U) {
            return Status{ErrorCode::invalid_argument,
                          "route worker terminal-event bound is invalid"};
        }
        if (config_.sync_frames_enabled &&
            (config_.maximum_sync_frame_events == 0U ||
             config_.maximum_sync_frame_events > 65536U)) {
            return Status{ErrorCode::invalid_argument,
                          "route worker sync-frame event bound is invalid"};
        }
        if (config_.sync_content_frames_enabled &&
            !config_.sync_frames_enabled) {
            return Status{
                ErrorCode::invalid_argument,
                "route worker content frames require base sync frames"};
        }
        constexpr auto kMaximumQualificationDelay =
            std::chrono::seconds(60);
        if (config_.qualification_other_worker_delay.count() < 0) {
            return Status{
                ErrorCode::invalid_argument,
                "route worker readiness qualification delay cannot be negative"};
        }
        if ((config_.qualification_first_worker.has_value()) !=
            (config_.qualification_other_worker_delay.count() > 0)) {
            return Status{
                ErrorCode::invalid_argument,
                "route worker readiness qualification requires both an exact first worker and a positive delay"};
        }
        if (config_.qualification_other_worker_delay >
            kMaximumQualificationDelay) {
            return Status{ErrorCode::invalid_argument,
                          "route worker readiness qualification delay exceeds 60 seconds"};
        }
        if (config_.qualification_first_worker) {
            const auto selected = std::find_if(
                config_.route_set.members.begin(),
                config_.route_set.members.end(),
                [this](const MemberPolicy &member) {
                    return member.tox_public_key ==
                               *config_.qualification_first_worker &&
                           member.tox_public_key !=
                               config_.route_set.coordinator_tox_public_key;
                });
            if (selected == config_.route_set.members.end()) {
                return Status{
                    ErrorCode::invalid_argument,
                    "route worker readiness qualification key is not an auxiliary route-set member"};
            }
        }
        // Validate every exact savedata path and fully derived network policy
        // before starting any toxcore owner. A malformed later override must
        // not leave an earlier worker live during construction rollback.
        for (const MemberPolicy &member : config_.route_set.members) {
            if (member.tox_public_key ==
                config_.route_set.coordinator_tox_public_key) {
                continue;
            }
            const Status state = validate_private_state(
                WorkerSupervisor::state_path_for(
                    config_.state_root, member.tox_public_key));
            if (!state.ok()) return state;
            auto transport_config = transport_config_for(member);
            if (!transport_config) return transport_config.status();
        }
        // Agent's event thread may ask for a snapshot as soon as its primary
        // transport starts. Publish the auxiliary population as one locked
        // construction transition instead of exposing vector growth or a
        // partially initialized worker set.
        std::scoped_lock snapshot_lock(snapshot_mutex_);
        // Every admitted receive owns one future terminal-event slot. Reserve
        // the actual backing storage before any transport can create an
        // admitted effect, so terminal accounting cannot fail on allocation.
        terminal_events_.reserve(config_.maximum_transfer_terminal_events);
        if (config_.sync_frames_enabled) {
            sync_frame_events_.reserve(config_.maximum_sync_frame_events);
        }
        for (const MemberPolicy &member : config_.route_set.members) {
            // A coordinator key that is also a member is already owned by the
            // parent Agent and must never be instantiated twice.
            if (member.tox_public_key ==
                config_.route_set.coordinator_tox_public_key) {
                continue;
            }
            const auto state_path = WorkerSupervisor::state_path_for(
                config_.state_root, member.tox_public_key);
            const Status state = validate_private_state(state_path);
            if (!state.ok()) {
                stop_workers();
                return state;
            }
            auto worker_id = security::random_u64_nonzero();
            if (!worker_id) {
                stop_workers();
                return worker_id.status();
            }
            auto configured_transport = transport_config_for(member);
            if (!configured_transport) {
                stop_workers();
                return configured_transport.status();
            }
            auto worker = std::make_shared<Worker>(
                member, worker_id.value(),
                std::move(configured_transport).value(),
                config_.maximum_finite_file_bytes);
            const Status incarnation =
                worker->sessions.set_local_incarnation(
                    config_.session_incarnation);
            if (!incarnation.ok()) {
                stop_workers();
                return incarnation;
            }
            if (binding_enabled()) {
                std::uint64_t feature_mask =
                    protocol::kImplementedFeatureMask |
                    protocol::feature_bit(
                        protocol::Feature::application_epoch_restart_v1) |
                    protocol::feature_bit(
                        protocol::Feature::route_binding_v1);
                if (config_.make_private_binding_frame) {
                    feature_mask |= protocol::feature_bit(
                        protocol::Feature::private_route_binding_v2);
                }
                if (config_.sync_frames_enabled) {
                    feature_mask |= protocol::feature_bit(
                        protocol::Feature::state_sync_v1);
                    feature_mask |= protocol::feature_bit(
                        protocol::Feature::state_sync_ranges_v1);
                }
                if (config_.sync_content_frames_enabled) {
                    feature_mask |= protocol::feature_bit(
                        protocol::Feature::state_sync_content_v2);
                }
                const Status features =
                    worker->sessions.set_supported_features(feature_mask);
                if (!features.ok()) {
                    stop_workers();
                    return features;
                }
            }
            const Status started = worker->transport.start();
            if (!started.ok()) {
                stop_workers();
                return Status{started.code(),
                              "route worker transport failed before supervision: " +
                                  started.message()};
            }
            const std::string address = worker->transport.address_hex();
            if (address.size() != toxcore::abi::kAddressSize * 2U) {
                worker->transport.stop();
                stop_workers();
                return Status{ErrorCode::protocol_error,
                              "route worker returned an invalid Tox address"};
            }
            const Status local_key = worker->sessions.set_local_public_key(
                address.substr(0U, toxcore::abi::kPublicKeySize * 2U));
            if (!local_key.ok()) {
                worker->transport.stop();
                stop_workers();
                return local_key;
            }
            auto peers = worker->transport.list_friends();
            if (!peers || peers.value().size() != 1U) {
                worker->transport.stop();
                stop_workers();
                return Status{
                    ErrorCode::protocol_error,
                    "route worker savedata must contain exactly one configured peer"};
            }
            worker->peer_key = public_key_hex(peers.value().front().public_key);
            worker->friend_number = peers.value().front().friend_number;
            worker->unique_peer = true;
            const Status offline = worker->sessions.ensure_offline_peer(
                worker->friend_number, worker->peer_key, unix_time_ms());
            if (!offline.ok()) {
                worker->transport.stop();
                stop_workers();
                return offline;
            }
            workers_.push_back(std::move(worker));
        }
        if (workers_.empty()) {
            return Status{ErrorCode::invalid_argument,
                          "route set contains no auxiliary worker identity"};
        }
        qualification_release_at_.reset();
        carrier_stop_requested_.store(false);
        stop_requested_.store(false);
        running_.store(true);
        event_thread_ = std::thread([this] { event_main(); });
        carrier_thread_ = std::thread([this] { carrier_main(); });
        return Status::success();
    }

    void stop() {
        if (!start_called_.load()) return;
        // Quiesce synchronous carrier commands while the event consumer is
        // still alive. A carrier command can be waiting for toxcore's owner
        // thread to publish a required event; stopping the event consumer
        // first would recreate the owner/event liveness cycle in reverse.
        carrier_stop_requested_.store(true);
        if (carrier_thread_.joinable() &&
            carrier_thread_.get_id() != std::this_thread::get_id()) {
            carrier_thread_.join();
        }
        stop_requested_.store(true);
        if (event_thread_.joinable() &&
            event_thread_.get_id() != std::this_thread::get_id()) {
            event_thread_.join();
        }
        std::scoped_lock lock(snapshot_mutex_);
        for (auto &worker : workers_) {
            worker->transfers.stop();
            worker->transport.stop();
        }
        running_.store(false);
    }

    bool running() const noexcept { return running_.load(); }

    std::vector<WorkerSessionSnapshot> snapshot() const {
        std::scoped_lock lock(snapshot_mutex_);
        std::vector<WorkerSessionSnapshot> output;
        output.reserve(workers_.size());
        for (const auto &worker : workers_) {
            WorkerSessionSnapshot current;
            current.policy = worker->policy;
            current.network = worker->network;
            current.worker_id = worker->worker_id;
            current.transport_running = worker->transport.running();
            current.qualification_held = qualification_holds(
                *worker, std::chrono::steady_clock::now());
            current.unique_peer = worker->unique_peer;
            current.friend_number = worker->friend_number;
            current.last_failure = worker->last_failure;
            auto session = worker->sessions.get(worker->friend_number);
            if (session) {
                current.application_ready =
                    protocol::is_application_ready(session.value());
                current.hello_sent = session.value().hello_sent;
                current.hello_received = session.value().hello_received;
                current.confirmation_sent =
                    session.value().confirmation_sent;
                current.confirmation_received =
                    session.value().confirmation_received;
                current.hello_send_attempts =
                    session.value().hello_send_attempts;
                current.confirmation_send_attempts =
                    session.value().confirmation_send_attempts;
                current.online_epoch = session.value().online_epoch;
                current.range_transfer_negotiated =
                    (session.value().negotiated.shared_features &
                     protocol::feature_bit(
                         protocol::Feature::state_sync_ranges_v1)) != 0U;
                current.content_transfer_negotiated =
                    (session.value().negotiated.shared_features &
                     protocol::feature_bit(
                         protocol::Feature::state_sync_content_v2)) != 0U;
            }
            current.local_binding_sent = worker->local_binding_sent;
            current.remote_binding_authenticated =
                worker->remote_binding_authenticated;
            current.local_binding_message_id =
                worker->local_binding_message_id;
            current.remote_binding_message_id =
                worker->remote_binding_message_id;
            current.remote_route_generation =
                worker->remote_route_generation;
            current.remote_stable_principal =
                worker->remote_stable_principal;
            current.remote_coordinator_route_key =
                worker->remote_coordinator_route_key;
            current.primary_authority_online_epoch =
                worker->primary_authority_online_epoch;
            current.sync_frame_events_queued = static_cast<std::size_t>(
                std::count_if(
                    sync_frame_events_.begin(), sync_frame_events_.end(),
                    [&worker](const WorkerSyncFrameEvent &event) {
                        return event.route_key == worker->policy.tox_public_key &&
                               event.worker_id == worker->worker_id;
                    }));
            current.sync_frames_received = worker->sync_frames_received;
            current.sync_frames_rejected = worker->sync_frames_rejected;
            output.push_back(current);
        }
        return output;
    }

    Status replace_remote_trust(std::vector<RemoteRouteTrust> trust) {
        std::scoped_lock lock(snapshot_mutex_);
        if (trust == remote_trust_) return Status::success();
        const Status replaced = bindings_.replace_trust(trust);
        if (!replaced.ok()) return replaced;
        remote_trust_ = std::move(trust);
        // Re-evaluate retained reciprocal frames against the replacement.
        // Exact unchanged trust replays idempotently; revoked or advanced
        // trust cannot leave a stale authenticated flag behind.
        for (auto &worker : workers_) {
            for (const FileTransferRecord &transfer : worker->transfers.list()) {
                static_cast<void>(worker->transfers.cancel(
                    transfer.friend_number, transfer.file_number));
            }
            terminate_all(*worker, WorkerTransferOutcome::cancelled,
                          ErrorCode::unavailable);
            purge_sync_frames(*worker);
            worker->remote_binding_authenticated = false;
            worker->remote_binding_rejected = false;
            worker->remote_binding_message_id = 0U;
            worker->remote_route_generation = 0U;
            worker->remote_stable_principal.fill(0U);
            worker->remote_coordinator_route_key.fill(0U);
            worker->primary_authority_online_epoch = 0U;
        }
        return Status::success();
    }

    Status replace_private_route_contexts(
        std::vector<PrivateRoutePrimaryContext> contexts) {
        std::scoped_lock lock(snapshot_mutex_);
        if (!config_.make_private_binding_frame) {
            if (contexts.empty()) return Status::success();
            return Status{
                ErrorCode::unsupported,
                "private route contexts require the v2 worker factory"};
        }
        if (contexts.size() > 64U) {
            return Status{ErrorCode::resource_exhausted,
                          "private route context bound is exhausted"};
        }
        std::sort(
            contexts.begin(), contexts.end(),
            [](const auto &left, const auto &right) {
                return left.session.friend_number <
                    right.session.friend_number;
            });
        for (std::size_t index = 0U; index < contexts.size(); ++index) {
            auto transcript =
                security::authority_session_transcript_digest(
                    contexts[index].session, *config_.sodium);
            if (!protocol::is_application_ready(contexts[index].session) ||
                !contexts[index].authority.connected ||
                !contexts[index].authority.feature_negotiated ||
                !contexts[index].authority.remote_authorized ||
                contexts[index].authority.transport_public_key !=
                    contexts[index].session.public_key ||
                !security::constant_time_equal(
                    contexts[index].authority.remote_principal,
                    contexts[index].inventory.route_set.
                        stable_device_principal) ||
                public_key_hex(contexts[index].inventory.route_set.
                    coordinator_tox_public_key) !=
                    contexts[index].session.public_key ||
                (contexts[index].session.negotiated.shared_features &
                 protocol::feature_bit(
                     protocol::Feature::private_route_binding_v2)) == 0U ||
                !transcript ||
                transcript.value() != contexts[index].authority.
                    session_transcript_digest ||
                contexts[index].inventory.primary_friend_number !=
                    contexts[index].session.friend_number ||
                contexts[index].inventory.primary_online_epoch !=
                    contexts[index].session.online_epoch ||
                contexts[index].authority.friend_number !=
                    contexts[index].session.friend_number ||
                contexts[index].authority.online_epoch !=
                    contexts[index].session.online_epoch) {
                return Status{ErrorCode::invalid_argument,
                              "private route context lacks its exact live primary edge"};
            }
            for (std::size_t later = index + 1U;
                 later < contexts.size(); ++later) {
                if (contexts[index].session.friend_number ==
                    contexts[later].session.friend_number) {
                    return Status{ErrorCode::invalid_argument,
                                  "private route primary context is duplicated"};
                }
            }
        }
        for (const auto &worker : workers_) {
            const std::size_t matches = static_cast<std::size_t>(
                std::count_if(
                    contexts.begin(), contexts.end(),
                    [&worker](const auto &context) {
                        return std::any_of(
                            context.inventory.route_set.members.begin(),
                            context.inventory.route_set.members.end(),
                            [&worker](const MemberPolicy &member) {
                                return public_key_hex(
                                           member.tox_public_key) ==
                                    worker->peer_key;
                            });
                    }));
            if (matches > 1U) {
                return Status{
                    ErrorCode::protocol_error,
                    "private route member is ambiguous across primary inventories"};
            }
        }
        if (private_contexts_equal(private_contexts_, contexts)) {
            return Status::success();
        }
        private_contexts_ = std::move(contexts);
        // A primary inventory change invalidates the local proof and every
        // queued effect.  Preserve an already-received remote proof just long
        // enough to evaluate it against the replacement context: the peer can
        // legitimately finish its auxiliary exchange before this side has
        // admitted the corresponding inventory on the primary edge.  Dropping
        // that early proof here would leave both peers waiting forever because
        // a successfully sent proof is intentionally not retransmitted.
        for (auto &worker : workers_) {
            auto retained_remote = std::move(worker->remote_binding_frame);
            const Failure retained_failure = worker->last_failure;
            for (const FileTransferRecord &transfer : worker->transfers.list()) {
                static_cast<void>(worker->transfers.cancel(
                    transfer.friend_number, transfer.file_number));
            }
            terminate_all(*worker, WorkerTransferOutcome::cancelled,
                          ErrorCode::unavailable);
            clear_binding_state(*worker);
            const auto session = worker->sessions.get(worker->friend_number);
            if (retained_remote && private_context_for(*worker) != nullptr &&
                session &&
                protocol::is_application_ready(session.value())) {
                worker->remote_binding_frame.emplace(
                    std::move(*retained_remote));
                verify_remote_binding(*worker, session.value());
                if (worker->remote_binding_rejected) {
                    // A proof from the prior inventory is expected to fail
                    // after a genuine route-set change.  It was never admitted
                    // under the replacement context, so discard it and allow
                    // the peer's new proof to arrive instead of pinning the
                    // worker in a rejected state.
                    worker->remote_binding_frame.reset();
                    worker->remote_binding_rejected = false;
                    worker->remote_binding_message_id = 0U;
                    worker->remote_route_generation = 0U;
                    worker->remote_stable_principal.fill(0U);
                    worker->remote_coordinator_route_key.fill(0U);
                    worker->primary_authority_online_epoch = 0U;
                    worker->last_failure = retained_failure;
                }
            }
        }
        return Status::success();
    }

    std::vector<WorkerTransferSnapshot> transfers() const {
        std::scoped_lock lock(snapshot_mutex_);
        std::vector<WorkerTransferSnapshot> output;
        for (const auto &worker : workers_) {
            for (FileTransferRecord transfer : worker->transfers.list()) {
                output.push_back(WorkerTransferSnapshot{
                    worker->policy.tox_public_key, worker->worker_id,
                    std::move(transfer)});
            }
        }
        return output;
    }

    Result<FileTransferRecord> receive_to_path(
        const ToxPublicKey &route_key, std::uint64_t worker_id,
        std::uint32_t file_number,
        const std::filesystem::path &destination,
        std::optional<std::uint64_t> resume_offset = std::nullopt) {
        std::scoped_lock lock(snapshot_mutex_);
        Worker *worker = exact_bulk_worker(route_key, worker_id);
        if (worker == nullptr) {
            return Status{ErrorCode::unavailable,
                          "file receive requires an exact authenticated bulk worker"};
        }
        if (reserved_terminal_events() >=
            config_.maximum_transfer_terminal_events) {
            return Status{ErrorCode::resource_exhausted,
                          "route worker terminal-event capacity is exhausted"};
        }
        if (worker->admitted_receives.contains(file_number)) {
            return Status{ErrorCode::protocol_error,
                          "route worker file number already owns an attempt"};
        }
        auto offers = worker->transfers.list();
        const auto offered = std::find_if(
            offers.begin(), offers.end(),
            [worker, file_number](const FileTransferRecord &record) {
                return record.direction == FileTransferDirection::incoming &&
                       record.friend_number == worker->friend_number &&
                       record.file_number == file_number;
            });
        if (offered == offers.end()) {
            return Status{ErrorCode::not_found,
                          "no incoming worker offer matches the requested file"};
        }
        FileTransferRecord provisional = *offered;
        provisional.local_path = destination;
        auto [binding, inserted] = worker->admitted_receives.emplace(
            file_number, std::move(provisional));
        if (!inserted) {
            return Status{ErrorCode::protocol_error,
                          "route worker file number already owns an attempt"};
        }
        auto accepted = resume_offset
            ? worker->transfers.receive_to_path_from_offset(
                  worker->friend_number, file_number, destination,
                  *resume_offset)
            : worker->transfers.receive_to_path(
                  worker->friend_number, file_number, destination);
        if (!accepted) {
            worker->admitted_receives.erase(binding);
            return accepted.status();
        }
        if (accepted.value().direction != FileTransferDirection::incoming ||
            accepted.value().friend_number != worker->friend_number ||
            accepted.value().file_number != file_number ||
            accepted.value().file_size != binding->second.file_size ||
            accepted.value().local_path != destination) {
            static_cast<void>(worker->transfers.cancel(
                worker->friend_number, file_number));
            worker->admitted_receives.erase(binding);
            return Status{ErrorCode::protocol_error,
                          "route worker accepted record changed the reserved offer"};
        }
        binding->second.state = accepted.value().state;
        binding->second.position = accepted.value().position;
        binding->second.local_paused = accepted.value().local_paused;
        binding->second.peer_paused = accepted.value().peer_paused;
        return std::move(accepted).value();
    }

    Result<FileTransferRecord> send_path_with_file_id(
        const ToxPublicKey &route_key, std::uint64_t worker_id,
        const std::filesystem::path &source, const FileId &file_id) {
        std::scoped_lock lock(snapshot_mutex_);
        Worker *worker = exact_bulk_worker(route_key, worker_id);
        if (worker == nullptr) {
            return Status{ErrorCode::unavailable,
                          "file send requires an exact authenticated bulk worker"};
        }
        if (reserved_terminal_events() >=
            config_.maximum_transfer_terminal_events) {
            return Status{ErrorCode::resource_exhausted,
                          "route worker terminal-event capacity is exhausted"};
        }
        if (worker->admitted_sends.size() >=
            worker->policy.maximum_active_work) {
            return Status{ErrorCode::resource_exhausted,
                          "route worker outgoing-attempt capacity is exhausted"};
        }
        const auto duplicate = std::find_if(
            worker->admitted_sends.begin(), worker->admitted_sends.end(),
            [&file_id](const FileTransferRecord &record) {
                return record.has_file_id && record.file_id == file_id;
            });
        if (duplicate != worker->admitted_sends.end()) {
            return Status{ErrorCode::protocol_error,
                          "route worker file ID already owns an outgoing attempt"};
        }
        auto offered = worker->transfers.send_path_with_file_id(
            worker->friend_number, source, file_id);
        if (!offered) return offered.status();
        if (offered.value().direction != FileTransferDirection::outgoing ||
            offered.value().friend_number != worker->friend_number ||
            !offered.value().has_file_id ||
            offered.value().file_id != file_id ||
            offered.value().local_path != source) {
            static_cast<void>(worker->transfers.cancel(
                worker->friend_number, offered.value().file_number));
            return Status{ErrorCode::protocol_error,
                          "route worker outgoing offer changed its reserved identity"};
        }
        worker->admitted_sends.push_back(offered.value());
        if (offered.value().state == FileTransferState::completed) {
            emit_terminal(*worker, std::move(worker->admitted_sends.back()),
                          WorkerTransferOutcome::completed, ErrorCode::ok);
            worker->admitted_sends.pop_back();
        }
        return std::move(offered).value();
    }

    Result<FileTransferRecord> send_path_ranges_with_file_id(
        const ToxPublicKey &route_key, std::uint64_t worker_id,
        const std::filesystem::path &source,
        std::span<const FileByteRange> ranges, const FileId &file_id) {
        std::scoped_lock lock(snapshot_mutex_);
        Worker *worker = exact_bulk_worker(route_key, worker_id);
        if (worker == nullptr) {
            return Status{ErrorCode::unavailable,
                          "range send requires an exact authenticated bulk worker"};
        }
        auto session = worker->sessions.get(worker->friend_number);
        if (!session ||
            (session.value().negotiated.shared_features &
             protocol::feature_bit(
                 protocol::Feature::state_sync_ranges_v1)) == 0U) {
            return Status{ErrorCode::unsupported,
                          "authenticated bulk worker did not negotiate range sync"};
        }
        if (reserved_terminal_events() >=
            config_.maximum_transfer_terminal_events) {
            return Status{ErrorCode::resource_exhausted,
                          "route worker terminal-event capacity is exhausted"};
        }
        if (worker->admitted_sends.size() >=
            worker->policy.maximum_active_work) {
            return Status{ErrorCode::resource_exhausted,
                          "route worker outgoing-attempt capacity is exhausted"};
        }
        const auto duplicate = std::find_if(
            worker->admitted_sends.begin(), worker->admitted_sends.end(),
            [&file_id](const FileTransferRecord &record) {
                return record.has_file_id && record.file_id == file_id;
            });
        if (duplicate != worker->admitted_sends.end()) {
            return Status{ErrorCode::protocol_error,
                          "route worker file ID already owns an outgoing attempt"};
        }
        auto offered = worker->transfers.send_path_ranges_with_file_id(
            worker->friend_number, source, ranges, file_id);
        if (!offered) return offered.status();
        if (offered.value().direction != FileTransferDirection::outgoing ||
            offered.value().friend_number != worker->friend_number ||
            !offered.value().has_file_id ||
            offered.value().file_id != file_id ||
            offered.value().local_path != source) {
            static_cast<void>(worker->transfers.cancel(
                worker->friend_number, offered.value().file_number));
            return Status{ErrorCode::protocol_error,
                          "route worker range offer changed its reserved identity"};
        }
        worker->admitted_sends.push_back(offered.value());
        if (offered.value().state == FileTransferState::completed) {
            emit_terminal(*worker, std::move(worker->admitted_sends.back()),
                          WorkerTransferOutcome::completed, ErrorCode::ok);
            worker->admitted_sends.pop_back();
        }
        return std::move(offered).value();
    }

    Status cancel_transfer(const ToxPublicKey &route_key,
                           std::uint64_t worker_id,
                           std::uint32_t file_number) {
        std::scoped_lock lock(snapshot_mutex_);
        Worker *worker = exact_bulk_worker(route_key, worker_id);
        if (worker == nullptr) {
            return Status{ErrorCode::unavailable,
                          "file cancellation requires an exact authenticated bulk worker"};
        }
        const Status cancelled = worker->transfers.cancel(
            worker->friend_number, file_number);
        const auto binding = worker->admitted_receives.find(file_number);
        if (cancelled.ok() && binding != worker->admitted_receives.end()) {
            emit_terminal(*worker, std::move(binding->second),
                          WorkerTransferOutcome::cancelled,
                          ErrorCode::unavailable);
            worker->admitted_receives.erase(binding);
        } else if (cancelled.ok()) {
            const auto outgoing = std::find_if(
                worker->admitted_sends.begin(), worker->admitted_sends.end(),
                [worker, file_number](const FileTransferRecord &record) {
                    return record.friend_number == worker->friend_number &&
                           record.file_number == file_number;
                });
            if (outgoing != worker->admitted_sends.end()) {
                emit_terminal(*worker, std::move(*outgoing),
                              WorkerTransferOutcome::cancelled,
                              ErrorCode::unavailable);
                worker->admitted_sends.erase(outgoing);
            }
        }
        return cancelled;
    }

    Status retire_incoming_transfer(const ToxPublicKey &route_key,
                                    std::uint64_t worker_id,
                                    std::uint32_t file_number) {
        std::scoped_lock lock(snapshot_mutex_);
        const auto found = std::find_if(
            workers_.begin(), workers_.end(),
            [&route_key, worker_id](const auto &worker) {
                return worker->policy.tox_public_key == route_key &&
                       worker->worker_id == worker_id;
            });
        // An already-destroyed worker cannot retain or recreate the local
        // destination, so local retirement is idempotently complete.
        if (found == workers_.end()) return Status::success();
        Worker &worker = **found;
        const Status retired = worker.transfers.retire_incoming(
            worker.friend_number, file_number);
        if (retired.ok()) worker.admitted_receives.erase(file_number);
        return retired;
    }

    Result<std::vector<WorkerTransferTerminalEvent>>
    take_transfer_terminal_events(std::size_t maximum_events) {
        if (maximum_events == 0U ||
            maximum_events > config_.maximum_transfer_terminal_events) {
            return Status{ErrorCode::invalid_argument,
                          "route worker terminal-event drain bound is invalid"};
        }
        std::scoped_lock lock(snapshot_mutex_);
        const std::size_t count =
            std::min(maximum_events, terminal_events_.size());
        std::vector<WorkerTransferTerminalEvent> output;
        output.reserve(count);
        for (std::size_t index = 0U; index < count; ++index) {
            output.push_back(std::move(terminal_events_[index]));
        }
        terminal_events_.erase(
            terminal_events_.begin(),
            terminal_events_.begin() + static_cast<std::ptrdiff_t>(count));
        return output;
    }

    Status send_sync_frame(const ToxPublicKey &route_key,
                           std::uint64_t worker_id,
                           const protocol::Frame &frame) {
        if (!config_.sync_frames_enabled) {
            return Status{ErrorCode::unsupported,
                          "auxiliary sync frames are disabled"};
        }
        const Status valid = validate_sync_frame(frame);
        if (!valid.ok()) return valid;
        auto packet = protocol::encode(frame);
        if (!packet) return packet.status();
        std::shared_ptr<Worker> worker;
        {
            std::scoped_lock lock(snapshot_mutex_);
            const auto found = std::find_if(
                workers_.begin(), workers_.end(),
                [&route_key, worker_id](const auto &candidate) {
                    return candidate->policy.tox_public_key == route_key &&
                           candidate->worker_id == worker_id;
                });
            if (found == workers_.end() || !bulk_authenticated(**found)) {
                return Status{
                    ErrorCode::unavailable,
                    "sync frame requires an exact authenticated bulk worker"};
            }
            auto session = (*found)->sessions.get((*found)->friend_number);
            if (!session ||
                (session.value().negotiated.shared_features &
                 protocol::feature_bit(
                     protocol::Feature::state_sync_v1)) == 0U) {
                return Status{
                    ErrorCode::unsupported,
                    "authenticated bulk worker did not negotiate state sync"};
            }
            if (range_sync_frame_type(frame.type) &&
                (session.value().negotiated.shared_features &
                 protocol::feature_bit(
                     protocol::Feature::state_sync_ranges_v1)) == 0U) {
                return Status{
                    ErrorCode::unsupported,
                    "authenticated bulk worker did not negotiate range sync"};
            }
            if (content_sync_frame_type(frame.type) &&
                (!config_.sync_content_frames_enabled ||
                 (session.value().negotiated.shared_features &
                  protocol::feature_bit(
                      protocol::Feature::state_sync_content_v2)) == 0U)) {
                return Status{
                    ErrorCode::unsupported,
                    "authenticated bulk worker did not negotiate content sync"};
            }
            worker = *found;
        }

        // Keep the supervisor state lock out of the synchronous toxcore
        // owner-command wait. A concurrent qualification replacement retains
        // this incarnation through the shared pointer and stops its transport,
        // so the send either belongs to the exact validated worker or fails.
        return worker->transport.send_lossless(
            worker->friend_number, packet.value(),
            TransportTrafficClass::bulk);
    }

    Result<std::vector<WorkerSyncFrameEvent>>
    take_sync_frame_events(std::size_t maximum_events) {
        if (!config_.sync_frames_enabled) {
            return Status{ErrorCode::unsupported,
                          "auxiliary sync frames are disabled"};
        }
        if (maximum_events == 0U ||
            maximum_events > config_.maximum_sync_frame_events) {
            return Status{ErrorCode::invalid_argument,
                          "route worker sync-frame drain bound is invalid"};
        }
        std::scoped_lock lock(snapshot_mutex_);
        const std::size_t count =
            std::min(maximum_events, sync_frame_events_.size());
        std::vector<WorkerSyncFrameEvent> output;
        output.reserve(count);
        for (std::size_t index = 0U; index < count; ++index) {
            output.push_back(std::move(sync_frame_events_[index]));
        }
        sync_frame_events_.erase(
            sync_frame_events_.begin(),
            sync_frame_events_.begin() + static_cast<std::ptrdiff_t>(count));
        return output;
    }

    Status stop_worker_for_qualification(
        const ToxPublicKey &route_key, std::uint64_t worker_id) {
        std::scoped_lock lock(snapshot_mutex_);
        const auto found = std::find_if(
            workers_.begin(), workers_.end(),
            [&route_key, worker_id](const auto &worker) {
                return worker->policy.tox_public_key == route_key &&
                       worker->worker_id == worker_id;
            });
        if (found == workers_.end() ||
            (*found)->policy.role != Role::bulk ||
            !(*found)->transport.running()) {
            return Status{
                ErrorCode::unavailable,
                "qualification stop requires an exact running bulk worker"};
        }
        Worker &worker = **found;
        const Status retired = bindings_.retire_worker(
            worker.policy.tox_public_key, worker.worker_id);
        if (!retired.ok() && retired.code() != ErrorCode::not_found) {
            return Status{
                retired.code(),
                "qualification stop could not retire the old route binding: " +
                    retired.message()};
        }
        terminate_all(worker, WorkerTransferOutcome::cancelled,
                      ErrorCode::unavailable);
        worker.transfers.stop();
        worker.transport.stop();
        static_cast<void>(worker.sessions.peer_offline(
            worker.friend_number, unix_time_ms()));
        clear_binding_state(worker);
        worker.last_failure = Failure::transport;
        return Status::success();
    }

    Result<std::uint64_t> restart_worker_for_qualification(
        const ToxPublicKey &route_key, std::uint64_t worker_id) {
        std::scoped_lock lock(snapshot_mutex_);
        const auto found = std::find_if(
            workers_.begin(), workers_.end(),
            [&route_key, worker_id](const auto &worker) {
                return worker->policy.tox_public_key == route_key &&
                       worker->worker_id == worker_id;
            });
        if (found == workers_.end() ||
            (*found)->policy.role != Role::bulk ||
            (*found)->transport.running()) {
            return Status{
                ErrorCode::unavailable,
                "qualification restart requires an exact stopped bulk worker"};
        }
        auto next_id = security::random_u64_nonzero();
        if (!next_id) return next_id.status();

        const MemberPolicy policy = (*found)->policy;
        auto configured_transport = transport_config_for(policy);
        if (!configured_transport) return configured_transport.status();
        auto replacement = std::make_shared<Worker>(
            policy, next_id.value(),
            std::move(configured_transport).value(),
            config_.maximum_finite_file_bytes);
        const Status incarnation =
            replacement->sessions.set_local_incarnation(
                config_.session_incarnation);
        if (!incarnation.ok()) return incarnation;
        if (binding_enabled()) {
            std::uint64_t feature_mask =
                protocol::kImplementedFeatureMask |
                protocol::feature_bit(
                    protocol::Feature::application_epoch_restart_v1) |
                protocol::feature_bit(protocol::Feature::route_binding_v1);
            if (config_.make_private_binding_frame) {
                feature_mask |= protocol::feature_bit(
                    protocol::Feature::private_route_binding_v2);
            }
            if (config_.sync_frames_enabled) {
                feature_mask |=
                    protocol::feature_bit(protocol::Feature::state_sync_v1);
                feature_mask |= protocol::feature_bit(
                    protocol::Feature::state_sync_ranges_v1);
            }
            if (config_.sync_content_frames_enabled) {
                feature_mask |= protocol::feature_bit(
                    protocol::Feature::state_sync_content_v2);
            }
            const Status features =
                replacement->sessions.set_supported_features(feature_mask);
            if (!features.ok()) return features;
        }
        const Status started = replacement->transport.start();
        if (!started.ok()) {
            return Status{
                started.code(),
                "route worker transport failed during qualification restart: " +
                    started.message()};
        }
        const std::string address = replacement->transport.address_hex();
        if (address.size() != toxcore::abi::kAddressSize * 2U) {
            replacement->transport.stop();
            return Status{ErrorCode::protocol_error,
                          "restarted route worker returned an invalid Tox address"};
        }
        const Status local_key = replacement->sessions.set_local_public_key(
            address.substr(0U, toxcore::abi::kPublicKeySize * 2U));
        if (!local_key.ok()) {
            replacement->transport.stop();
            return local_key;
        }
        auto peers = replacement->transport.list_friends();
        if (!peers || peers.value().size() != 1U) {
            replacement->transport.stop();
            return Status{
                ErrorCode::protocol_error,
                "restarted route worker savedata must retain exactly one configured peer"};
        }
        replacement->peer_key =
            public_key_hex(peers.value().front().public_key);
        replacement->friend_number = peers.value().front().friend_number;
        replacement->unique_peer = true;
        const Status offline = replacement->sessions.ensure_offline_peer(
            replacement->friend_number, replacement->peer_key,
            unix_time_ms());
        if (!offline.ok()) {
            replacement->transport.stop();
            return offline;
        }
        *found = std::move(replacement);
        return next_id.value();
    }

  private:
    struct Worker {
        Worker(MemberPolicy member_policy, std::uint64_t id,
               ToxTransport::Config transport_config,
               std::uint64_t maximum_finite_file_bytes)
            : policy(std::move(member_policy)), worker_id(id),
              network(transport_config.network),
              transport(std::move(transport_config)),
              transfers(transport, transfer_config(
                  policy.maximum_active_work, maximum_finite_file_bytes)),
              sessions(maximum_finite_file_bytes) {
            // Outgoing file numbers are allocated by toxcore. Reserve this
            // bounded ledger before the transport starts so recording an
            // admitted send cannot allocate after the external offer effect.
            admitted_sends.reserve(policy.maximum_active_work);
        }

        static FileTransferManager::Config transfer_config(
            std::uint16_t maximum_active_work,
            std::uint64_t maximum_finite_file_bytes) {
            FileTransferManager::Config config;
            config.max_active_sends = maximum_active_work;
            config.max_active_receives = maximum_active_work;
            config.max_pending_offers =
                std::max<std::size_t>(maximum_active_work, 1U);
            config.max_file_bytes = maximum_finite_file_bytes;
            return config;
        }

        MemberPolicy policy;
        std::uint64_t worker_id{0U};
        NetworkStack network{};
        ToxTransport transport;
        FileTransferManager transfers;
        protocol::PeerSessionRegistry sessions;
        std::string peer_key;
        std::uint32_t friend_number{0U};
        bool unique_peer{false};
        Failure last_failure{Failure::none};
        std::optional<protocol::Frame> local_binding_frame;
        std::optional<protocol::Frame> remote_binding_frame;
        bool local_binding_sent{false};
        bool remote_binding_authenticated{false};
        bool remote_binding_rejected{false};
        std::uint64_t local_binding_message_id{0U};
        std::uint64_t remote_binding_message_id{0U};
        std::uint64_t remote_route_generation{0U};
        security::SigningPublicKey remote_stable_principal{};
        ToxPublicKey remote_coordinator_route_key{};
        std::uint64_t primary_authority_online_epoch{0U};
        std::map<std::uint32_t, FileTransferRecord> admitted_receives;
        std::vector<FileTransferRecord> admitted_sends;
        std::uint64_t sync_frames_received{0U};
        std::uint64_t sync_frames_rejected{0U};
        std::chrono::steady_clock::time_point next_hello_attempt{};
        std::chrono::steady_clock::time_point next_confirmation_attempt{};
    };

    [[nodiscard]] bool binding_enabled() const noexcept {
        return static_cast<bool>(config_.make_binding_frame) ||
               static_cast<bool>(config_.make_private_binding_frame);
    }

    [[nodiscard]] Status validate_network_overrides() const {
        if (config_.network_overrides.size() > 15U) {
            return Status{ErrorCode::resource_exhausted,
                          "route worker network override bound is exhausted"};
        }
        for (std::size_t index = 0U;
             index < config_.network_overrides.size(); ++index) {
            const WorkerNetworkOverride &override =
                config_.network_overrides[index];
            if (!override.network.implemented()) {
                return Status{
                    ErrorCode::unsupported,
                    "route worker network override selects an unsupported context"};
            }
            constexpr std::size_t kMaximumEndpointsPerWorker = 16U;
            if (override.bootstrap_nodes.size() >
                    kMaximumEndpointsPerWorker ||
                override.tcp_relays.size() >
                    kMaximumEndpointsPerWorker) {
                return Status{
                    ErrorCode::resource_exhausted,
                    "route worker endpoint override bound is exhausted"};
            }
            const auto endpoints_unique = [](const auto &endpoints) {
                for (std::size_t endpoint_index = 0U;
                     endpoint_index < endpoints.size(); ++endpoint_index) {
                    if (std::find(
                            endpoints.begin() + static_cast<std::ptrdiff_t>(
                                endpoint_index + 1U),
                            endpoints.end(), endpoints[endpoint_index]) !=
                        endpoints.end()) {
                        return false;
                    }
                }
                return true;
            };
            if (!endpoints_unique(override.bootstrap_nodes) ||
                !endpoints_unique(override.tcp_relays)) {
                return Status{
                    ErrorCode::invalid_argument,
                    "route worker endpoint override contains a duplicate record"};
            }
            const auto member = std::find_if(
                config_.route_set.members.begin(),
                config_.route_set.members.end(),
                [&override](const MemberPolicy &candidate) {
                    return candidate.tox_public_key ==
                        override.tox_public_key;
                });
            if (member == config_.route_set.members.end() ||
                override.tox_public_key ==
                    config_.route_set.coordinator_tox_public_key) {
                return Status{
                    ErrorCode::invalid_argument,
                    "route worker network override key is not an auxiliary member"};
            }
            for (std::size_t later = index + 1U;
                 later < config_.network_overrides.size(); ++later) {
                if (override.tox_public_key ==
                    config_.network_overrides[later].tox_public_key) {
                    return Status{
                        ErrorCode::invalid_argument,
                        "route worker network override key is duplicated"};
                }
            }
        }
        return Status::success();
    }

    [[nodiscard]] Result<ToxTransport::Config> transport_config_for(
        const MemberPolicy &member) const {
        ToxTransport::Config transport_config =
            config_.transport_template;
        transport_config.state_path = WorkerSupervisor::state_path_for(
            config_.state_root, member.tox_public_key);
        transport_config.expected_public_key = member.tox_public_key;
        const auto override = std::find_if(
            config_.network_overrides.begin(),
            config_.network_overrides.end(),
            [&member](const WorkerNetworkOverride &candidate) {
                return candidate.tox_public_key == member.tox_public_key;
            });
        if (override != config_.network_overrides.end()) {
            transport_config = apply_worker_network_override(
                std::move(transport_config), *override);
        }
        auto constructed_class = network_class_from_stack(
            transport_config.network);
        if (!constructed_class) return constructed_class.status();
        if (member.network_class != NetworkClass::unspecified &&
            member.network_class != constructed_class.value()) {
            return Status{
                ErrorCode::protocol_error,
                "constructed route worker network violates signed member policy"};
        }
        if (is_strict_socks_tox_route(
                transport_config.network.tox_route) &&
            member.connection_class == ConnectionClass::udp) {
            return Status{
                ErrorCode::invalid_argument,
                "strict routed Tox refuses a route-set member requiring UDP"};
        }
        if (is_strict_socks_tox_route(
                transport_config.network.tox_route) ||
            member.connection_class == ConnectionClass::tcp) {
            transport_config.native_udp_enabled = false;
        } else if (member.connection_class == ConnectionClass::udp) {
            transport_config.native_udp_enabled = true;
        }
        const Status route =
            ToxTransport::validate_route_config(transport_config);
        if (!route.ok()) {
            return Status{
                route.code(),
                "route worker network override is invalid: " +
                    route.message()};
        }
        return transport_config;
    }

    [[nodiscard]] static bool private_context_equal(
        const PrivateRoutePrimaryContext &left,
        const PrivateRoutePrimaryContext &right) {
        return left.inventory == right.inventory &&
               left.session.friend_number == right.session.friend_number &&
               left.session.online_epoch == right.session.online_epoch &&
               left.session.public_key == right.session.public_key &&
               left.session.local_public_key == right.session.local_public_key &&
               left.authority.friend_number == right.authority.friend_number &&
               left.authority.online_epoch == right.authority.online_epoch &&
               left.authority.transport_public_key ==
                   right.authority.transport_public_key &&
               left.authority.remote_principal ==
                   right.authority.remote_principal &&
               left.authority.session_transcript_digest ==
                   right.authority.session_transcript_digest &&
               left.authority.connected == right.authority.connected &&
               left.authority.remote_authorized ==
                   right.authority.remote_authorized;
    }

    [[nodiscard]] static bool private_contexts_equal(
        const std::vector<PrivateRoutePrimaryContext> &left,
        const std::vector<PrivateRoutePrimaryContext> &right) {
        if (left.size() != right.size()) return false;
        for (std::size_t index = 0U; index < left.size(); ++index) {
            if (!private_context_equal(left[index], right[index])) {
                return false;
            }
        }
        return true;
    }

    [[nodiscard]] const PrivateRoutePrimaryContext *private_context_for(
        const Worker &worker) const {
        const auto found = std::find_if(
            private_contexts_.begin(), private_contexts_.end(),
            [&worker](const PrivateRoutePrimaryContext &context) {
                return std::any_of(
                    context.inventory.route_set.members.begin(),
                    context.inventory.route_set.members.end(),
                    [&worker](const MemberPolicy &member) {
                        return public_key_hex(member.tox_public_key) ==
                            worker.peer_key;
                    });
            });
        return found == private_contexts_.end() ? nullptr : &*found;
    }

    bool qualification_holds(
        const Worker &worker,
        std::chrono::steady_clock::time_point now) const noexcept {
        if (!config_.qualification_first_worker ||
            worker.policy.tox_public_key ==
                *config_.qualification_first_worker) {
            return false;
        }
        return !qualification_release_at_ ||
               now < *qualification_release_at_;
    }

    void maybe_begin_qualification_release(
        const Worker &worker,
        std::chrono::steady_clock::time_point now) noexcept {
        if (!config_.qualification_first_worker ||
            qualification_release_at_ ||
            worker.policy.tox_public_key !=
                *config_.qualification_first_worker) {
            return;
        }
        const auto session = worker.sessions.get(worker.friend_number);
        if (!session || !protocol::is_application_ready(session.value())) {
            return;
        }
        if (binding_enabled() &&
            (!worker.local_binding_sent ||
             !worker.remote_binding_authenticated)) {
            return;
        }
        qualification_release_at_ =
            now + config_.qualification_other_worker_delay;
    }

    void purge_sync_frames(const Worker &worker) {
        std::erase_if(
            sync_frame_events_, [&worker](const WorkerSyncFrameEvent &event) {
                return event.route_key == worker.policy.tox_public_key &&
                       event.worker_id == worker.worker_id;
            });
    }

    void clear_binding_state(Worker &worker) {
        worker.local_binding_frame.reset();
        worker.remote_binding_frame.reset();
        worker.local_binding_sent = false;
        worker.remote_binding_authenticated = false;
        worker.remote_binding_rejected = false;
        worker.local_binding_message_id = 0U;
        worker.remote_binding_message_id = 0U;
        worker.remote_route_generation = 0U;
        worker.remote_stable_principal.fill(0U);
        worker.remote_coordinator_route_key.fill(0U);
        worker.primary_authority_online_epoch = 0U;
        purge_sync_frames(worker);
    }

    std::size_t reserved_terminal_events() const {
        std::size_t reserved = terminal_events_.size();
        for (const auto &worker : workers_) {
            reserved += worker->admitted_receives.size();
            reserved += worker->admitted_sends.size();
        }
        return reserved;
    }

    void emit_terminal(Worker &worker, FileTransferRecord transfer,
                       WorkerTransferOutcome outcome, ErrorCode failure) {
        transfer.state = outcome == WorkerTransferOutcome::completed
                             ? FileTransferState::completed
                         : outcome == WorkerTransferOutcome::cancelled
                             ? FileTransferState::cancelled
                             : FileTransferState::failed;
        if (outcome == WorkerTransferOutcome::completed) {
            transfer.position = transfer.file_size;
        }
        transfer.detail.clear();
        terminal_events_.push_back(WorkerTransferTerminalEvent{
            worker.policy.tox_public_key, worker.worker_id,
            std::move(transfer), outcome, failure});
    }

    void terminate_all(Worker &worker, WorkerTransferOutcome outcome,
                       ErrorCode failure) {
        for (auto &[file_number, transfer] : worker.admitted_receives) {
            static_cast<void>(file_number);
            emit_terminal(worker, std::move(transfer), outcome, failure);
        }
        worker.admitted_receives.clear();
        for (FileTransferRecord &transfer : worker.admitted_sends) {
            emit_terminal(worker, std::move(transfer), outcome, failure);
        }
        worker.admitted_sends.clear();
    }

    Worker *exact_bulk_worker(const ToxPublicKey &route_key,
                              std::uint64_t worker_id) {
        const auto found = std::find_if(
            workers_.begin(), workers_.end(),
            [&route_key, worker_id](const auto &worker) {
                return worker->policy.tox_public_key == route_key &&
                       worker->worker_id == worker_id;
            });
        if (found == workers_.end() || !bulk_authenticated(**found)) {
            return nullptr;
        }
        return found->get();
    }

    static bool bulk_authenticated(const Worker &worker) {
        if (worker.policy.role != Role::bulk ||
            !worker.local_binding_sent ||
            !worker.remote_binding_authenticated) {
            return false;
        }
        auto session = worker.sessions.get(worker.friend_number);
        return session && protocol::is_application_ready(session.value());
    }

    static bool file_event(TransportEventKind kind) noexcept {
        return kind == TransportEventKind::file_offer ||
               kind == TransportEventKind::file_control ||
               kind == TransportEventKind::file_chunk_request ||
               kind == TransportEventKind::file_chunk;
    }

    void reconcile_transfer_event(Worker &worker,
                                  const TransportEvent &event,
                                  const Status &handled) {
        if (event.kind == TransportEventKind::friend_connection &&
            event.connection_status ==
                static_cast<int>(toxcore::abi::kConnectionNone)) {
            terminate_all(worker, WorkerTransferOutcome::cancelled,
                          ErrorCode::unavailable);
            purge_sync_frames(worker);
            return;
        }
        if (event.kind == TransportEventKind::friend_removed) {
            terminate_all(worker, WorkerTransferOutcome::cancelled,
                          ErrorCode::unavailable);
            worker.sessions.erase(worker.friend_number);
            clear_binding_state(worker);
            return;
        }
        const auto binding = worker.admitted_receives.find(event.file_number);
        const auto outgoing = std::find_if(
            worker.admitted_sends.begin(), worker.admitted_sends.end(),
            [&event](const FileTransferRecord &record) {
                return record.friend_number == event.friend_number &&
                       record.file_number == event.file_number;
            });
        if (binding == worker.admitted_receives.end() &&
            outgoing == worker.admitted_sends.end()) return;
        if (event.kind == TransportEventKind::file_chunk &&
            !event.data.empty() && handled.ok() &&
            binding != worker.admitted_receives.end()) {
            binding->second.position =
                event.file_position + event.data.size();
        }
        if (event.kind == TransportEventKind::file_control &&
            event.file_control == TransferControl::cancel) {
            if (binding != worker.admitted_receives.end()) {
                emit_terminal(worker, std::move(binding->second),
                              WorkerTransferOutcome::cancelled,
                              ErrorCode::unavailable);
                worker.admitted_receives.erase(binding);
            }
            if (outgoing != worker.admitted_sends.end()) {
                emit_terminal(worker, std::move(*outgoing),
                              WorkerTransferOutcome::cancelled,
                              ErrorCode::unavailable);
                worker.admitted_sends.erase(outgoing);
            }
        } else if (event.kind == TransportEventKind::file_chunk &&
                   event.data.empty() && handled.ok() &&
                   binding != worker.admitted_receives.end()) {
            emit_terminal(worker, std::move(binding->second),
                          WorkerTransferOutcome::completed, ErrorCode::ok);
            worker.admitted_receives.erase(binding);
        } else if (event.kind == TransportEventKind::file_chunk_request &&
                   event.requested_length == 0U && handled.ok() &&
                   outgoing != worker.admitted_sends.end()) {
            emit_terminal(worker, std::move(*outgoing),
                          WorkerTransferOutcome::completed, ErrorCode::ok);
            worker.admitted_sends.erase(outgoing);
        } else if (file_event(event.kind) && !handled.ok()) {
            if (binding != worker.admitted_receives.end()) {
                emit_terminal(worker, std::move(binding->second),
                              WorkerTransferOutcome::failed, handled.code());
                worker.admitted_receives.erase(binding);
            }
            if (outgoing != worker.admitted_sends.end()) {
                emit_terminal(worker, std::move(*outgoing),
                              WorkerTransferOutcome::failed, handled.code());
                worker.admitted_sends.erase(outgoing);
            }
        }
    }

    void stop_workers() {
        for (auto &worker : workers_) {
            worker->transfers.stop();
            worker->transport.stop();
        }
        workers_.clear();
    }

    Status send_hello(Worker &worker) {
        worker.next_hello_attempt = std::chrono::steady_clock::now() +
                                    kApplicationHandshakeRetryInterval;
        auto current = worker.sessions.get(worker.friend_number);
        if (!current) return current.status();
        std::uint64_t message_id = current.value().local_hello_message_id;
        if (message_id == 0U) {
            auto generated = security::random_u64_nonzero();
            if (!generated) return generated.status();
            message_id = generated.value();
        }
        auto frame = worker.sessions.make_hello_frame(
            worker.friend_number, message_id);
        if (!frame) return frame.status();
        auto packet = protocol::encode(frame.value());
        if (!packet) return packet.status();
        const Status sent = worker.transport.send_lossless(
            worker.friend_number, packet.value());
        if (!sent.ok()) {
            static_cast<void>(worker.sessions.mark_hello_send_failed(
                worker.friend_number, sent.code(), sent.message(), unix_time_ms()));
            return sent;
        }
        return worker.sessions.mark_hello_sent(
            worker.friend_number, message_id, unix_time_ms());
    }

    Status send_confirmation(Worker &worker) {
        worker.next_confirmation_attempt =
            std::chrono::steady_clock::now() +
            kApplicationHandshakeRetryInterval;
        auto current = worker.sessions.get(worker.friend_number);
        if (!current) return current.status();
        std::uint64_t message_id =
            current.value().local_confirmation_message_id;
        if (message_id == 0U) {
            auto generated = security::random_u64_nonzero();
            if (!generated) return generated.status();
            message_id = generated.value();
        }
        auto frame = worker.sessions.make_confirmation_frame(
            worker.friend_number, message_id);
        if (!frame) return frame.status();
        auto packet = protocol::encode(frame.value());
        if (!packet) return packet.status();
        const Status sent = worker.transport.send_lossless(
            worker.friend_number, packet.value());
        if (!sent.ok()) {
            static_cast<void>(worker.sessions.mark_confirmation_send_failed(
                worker.friend_number, sent.code(), sent.message(), unix_time_ms()));
            return sent;
        }
        return worker.sessions.mark_confirmation_sent(
            worker.friend_number, message_id, unix_time_ms());
    }

    Status send_binding(Worker &worker,
                        const protocol::PeerSessionSnapshot &session) {
        if (!binding_enabled()) {
            return Status{ErrorCode::unsupported,
                          "route-binding frame factory is not configured"};
        }
        if (!worker.local_binding_frame) {
            auto message_id = security::random_u64_nonzero();
            if (!message_id) return message_id.status();
            Result<protocol::Frame> frame = Status{
                ErrorCode::unavailable,
                "private route inventory is not admitted on a primary edge"};
            if (config_.make_private_binding_frame) {
                const auto *context = private_context_for(worker);
                if (context == nullptr) return frame.status();
                frame = config_.make_private_binding_frame(
                    worker.policy, *context, session, message_id.value());
            } else {
                frame = config_.make_binding_frame(
                    worker.policy, session, message_id.value());
            }
            if (!frame) return frame.status();
            worker.local_binding_frame.emplace(std::move(frame).value());
            worker.local_binding_message_id = message_id.value();
        }
        auto packet = protocol::encode(*worker.local_binding_frame);
        if (!packet) return packet.status();
        const Status sent = worker.transport.send_lossless(
            worker.friend_number, packet.value());
        if (sent.ok()) worker.local_binding_sent = true;
        return sent;
    }

    void verify_remote_binding(Worker &worker,
                               const protocol::PeerSessionSnapshot &session) {
        if (!worker.remote_binding_frame ||
            worker.remote_binding_authenticated ||
            worker.remote_binding_rejected ||
            !protocol::is_application_ready(session)) {
            return;
        }
        if (config_.make_private_binding_frame) {
            const auto *context = private_context_for(worker);
            if (context == nullptr) return;
            const Status verified = verify_private_route_member_binding_frame(
                *worker.remote_binding_frame, context->inventory,
                context->session, session, context->authority,
                *config_.sodium);
            if (!verified.ok()) {
                worker.remote_binding_rejected = true;
                worker.last_failure = Failure::authentication;
                return;
            }
            worker.remote_binding_authenticated = true;
            worker.remote_binding_message_id =
                worker.remote_binding_frame->message_id;
            worker.remote_route_generation =
                context->inventory.route_set.generation;
            worker.remote_stable_principal =
                context->inventory.route_set.stable_device_principal;
            worker.remote_coordinator_route_key =
                context->inventory.route_set.coordinator_tox_public_key;
            worker.primary_authority_online_epoch =
                context->session.online_epoch;
            worker.last_failure = Failure::none;
            return;
        }
        if (bindings_.snapshot().trusted_primary_routes == 0U) return;
        auto admitted = bindings_.receive(
            worker.policy.tox_public_key, worker.worker_id,
            *worker.remote_binding_frame, session, *config_.sodium);
        if (!admitted) {
            worker.remote_binding_rejected = true;
            worker.last_failure = Failure::authentication;
            return;
        }
        worker.remote_binding_authenticated = true;
        worker.remote_binding_message_id =
            worker.remote_binding_frame->message_id;
        worker.remote_route_generation =
            admitted.value().verified.route_set.generation;
        worker.remote_stable_principal =
            admitted.value().trust.stable_device_principal;
        worker.remote_coordinator_route_key =
            admitted.value().trust.coordinator_tox_public_key;
        worker.primary_authority_online_epoch =
            admitted.value().trust.primary_online_epoch;
        worker.last_failure = Failure::none;
    }

    void advance(Worker &worker) {
        auto session = worker.sessions.get(worker.friend_number);
        if (!session || !session.value().connected) return;
        if (protocol::is_application_ready(session.value())) {
            if (binding_enabled() && !worker.local_binding_sent) {
                const Status sent = send_binding(worker, session.value());
                if (!sent.ok() && !retryable(sent.code())) {
                    worker.last_failure = Failure::transport;
                }
            }
            verify_remote_binding(worker, session.value());
            return;
        }
        switch (session.value().state) {
            case protocol::PeerSessionState::incompatible_version:
            case protocol::PeerSessionState::incompatible_features:
            case protocol::PeerSessionState::malformed_frame:
            case protocol::PeerSessionState::malformed_hello:
            case protocol::PeerSessionState::conflicting_hello:
            case protocol::PeerSessionState::malformed_confirmation:
            case protocol::PeerSessionState::conflicting_confirmation:
                return;
            case protocol::PeerSessionState::offline:
            case protocol::PeerSessionState::awaiting_hello:
            case protocol::PeerSessionState::awaiting_confirmation:
            case protocol::PeerSessionState::confirmed:
            case protocol::PeerSessionState::hello_send_failed:
            case protocol::PeerSessionState::confirmation_send_failed:
                break;
        }
        const auto now = std::chrono::steady_clock::now();
        Status status = Status::success();
        if (!session.value().hello_sent ||
            now >= worker.next_hello_attempt) {
            status = send_hello(worker);
            if (!status.ok()) {
                if (!retryable(status.code())) worker.last_failure = Failure::transport;
                return;
            }
            session = worker.sessions.get(worker.friend_number);
            if (!session) return;
        }
        if (session.value().hello_sent && session.value().hello_received &&
            session.value().negotiated.compatible &&
            (!session.value().confirmation_sent ||
             now >= worker.next_confirmation_attempt)) {
            status = send_confirmation(worker);
            if (!status.ok() && !retryable(status.code())) {
                worker.last_failure = Failure::transport;
            }
        }
    }

    void handle_connection(Worker &worker, const TransportEvent &event) {
        if (event.friend_number != worker.friend_number) {
            worker.last_failure = Failure::policy;
            return;
        }
        const std::uint64_t now = unix_time_ms();
        if (event.connection_status ==
            static_cast<int>(toxcore::abi::kConnectionNone)) {
            static_cast<void>(worker.sessions.peer_offline(
                worker.friend_number, now));
            clear_binding_state(worker);
            return;
        }
        if ((worker.policy.connection_class == ConnectionClass::tcp &&
             event.connection_status !=
                 static_cast<int>(toxcore::abi::kConnectionTcp)) ||
            (worker.policy.connection_class == ConnectionClass::udp &&
             event.connection_status !=
                 static_cast<int>(toxcore::abi::kConnectionUdp))) {
            worker.last_failure = Failure::policy;
            return;
        }
        auto before = worker.sessions.get(worker.friend_number);
        if (!before) {
            worker.last_failure = Failure::internal;
            return;
        }
        protocol::SessionNonce nonce = before.value().local.session_nonce;
        if (!before.value().connected) {
            auto generated = security::random_nonce_128();
            if (!generated) {
                worker.last_failure = Failure::internal;
                return;
            }
            nonce = generated.value();
        }
        auto online = worker.sessions.peer_online(
            worker.friend_number, worker.peer_key, event.connection_status,
            nonce, now);
        if (!online) {
            worker.last_failure = Failure::authentication;
            return;
        }
        advance(worker);
    }

    void handle_lossless(Worker &worker, const TransportEvent &event) {
        if (event.friend_number != worker.friend_number || event.data.empty() ||
            event.data.front() != protocol::kToxLosslessPacketId) return;
        auto frame = protocol::decode(event.data);
        if (!frame) {
            static_cast<void>(worker.sessions.mark_malformed_frame(
                worker.friend_number, "malformed auxiliary route frame",
                unix_time_ms()));
            worker.last_failure = Failure::authentication;
            return;
        }
        Status accepted{ErrorCode::unsupported,
                        "auxiliary route application type is not enabled"};
        bool application_restarted = false;
        if (frame.value().type == protocol::MessageType::hello) {
            const auto before =
                worker.sessions.get(worker.friend_number);
            accepted = worker.sessions.receive_hello(
                worker.friend_number, worker.peer_key, frame.value(),
                unix_time_ms());
            const auto after =
                worker.sessions.get(worker.friend_number);
            application_restarted = accepted.ok() && before && after &&
                after.value().online_epoch >
                    before.value().online_epoch;
        } else if (frame.value().type == protocol::MessageType::capabilities) {
            accepted = worker.sessions.receive_confirmation(
                worker.friend_number, worker.peer_key, frame.value(),
                unix_time_ms());
        } else if ((config_.make_private_binding_frame &&
                    frame.value().type == protocol::MessageType::
                        private_route_member_binding) ||
                   (!config_.make_private_binding_frame &&
                    frame.value().type ==
                        protocol::MessageType::route_binding)) {
            auto encoded = protocol::encode(frame.value());
            if (!encoded) {
                worker.last_failure = Failure::authentication;
                return;
            }
            if (worker.remote_binding_frame) {
                auto retained = protocol::encode(*worker.remote_binding_frame);
                if (!retained || retained.value() != encoded.value()) {
                    worker.last_failure = Failure::authentication;
                    return;
                }
            } else {
                worker.remote_binding_frame.emplace(frame.value());
            }
            auto session = worker.sessions.get(worker.friend_number);
            if (session) verify_remote_binding(worker, session.value());
            return;
        } else if (config_.sync_frames_enabled &&
                   sync_frame_type(frame.value().type)) {
            auto session = worker.sessions.get(worker.friend_number);
            if (!session || !bulk_authenticated(worker) ||
                (session.value().negotiated.shared_features &
                 protocol::feature_bit(protocol::Feature::state_sync_v1)) == 0U) {
                return;
            }
            if (range_sync_frame_type(frame.value().type) &&
                (session.value().negotiated.shared_features &
                 protocol::feature_bit(
                     protocol::Feature::state_sync_ranges_v1)) == 0U) {
                saturating_increment(worker.sync_frames_rejected);
                return;
            }
            if (content_sync_frame_type(frame.value().type) &&
                (!config_.sync_content_frames_enabled ||
                 (session.value().negotiated.shared_features &
                  protocol::feature_bit(
                      protocol::Feature::state_sync_content_v2)) == 0U)) {
                saturating_increment(worker.sync_frames_rejected);
                return;
            }
            const Status valid = validate_sync_frame(frame.value());
            if (!valid.ok()) {
                saturating_increment(worker.sync_frames_rejected);
                worker.last_failure = Failure::policy;
                return;
            }
            if (sync_frame_events_.size() >=
                config_.maximum_sync_frame_events) {
                saturating_increment(worker.sync_frames_rejected);
                return;
            }
            sync_frame_events_.push_back(WorkerSyncFrameEvent{
                worker.policy.tox_public_key,
                worker.worker_id,
                worker.friend_number,
                session.value().online_epoch,
                worker.remote_route_generation,
                worker.remote_stable_principal,
                worker.remote_coordinator_route_key,
                worker.primary_authority_online_epoch,
                std::move(frame).value()});
            saturating_increment(worker.sync_frames_received);
            return;
        } else {
            return;
        }
        if (!accepted.ok()) {
            worker.last_failure = Failure::authentication;
            return;
        }
        if (application_restarted) {
            terminate_all(worker, WorkerTransferOutcome::cancelled,
                          ErrorCode::unavailable);
            clear_binding_state(worker);
            const Status resent = send_hello(worker);
            if (!resent.ok()) {
                worker.last_failure = retryable(resent.code())
                    ? Failure::transport
                    : Failure::authentication;
                return;
            }
        }
        advance(worker);
    }

    void event_main() noexcept {
        try {
            while (!stop_requested_.load()) {
                bool observed = false;
                {
                    std::scoped_lock lock(snapshot_mutex_);
                    for (auto &worker : workers_) {
                        const auto now = std::chrono::steady_clock::now();
                        if (qualification_holds(*worker, now)) {
                            continue;
                        }
                        if (auto event = worker->transport.poll_event(
                                std::chrono::milliseconds(0))) {
                            observed = true;
                            if (bulk_authenticated(*worker) ||
                                event->kind ==
                                    TransportEventKind::friend_connection ||
                                event->kind == TransportEventKind::friend_removed) {
                                const Status handled =
                                    worker->transfers.handle_event(*event);
                                reconcile_transfer_event(
                                    *worker, *event, handled);
                            } else if (file_event(event->kind) &&
                                       event->kind ==
                                           TransportEventKind::file_offer) {
                                static_cast<void>(worker->transport.control_file(
                                    event->friend_number, event->file_number,
                                    TransferControl::cancel));
                            }
                            if (event->kind ==
                                TransportEventKind::friend_connection) {
                                handle_connection(*worker, *event);
                            } else if (event->kind ==
                                       TransportEventKind::lossless_packet) {
                                handle_lossless(*worker, *event);
                            }
                        }
                        advance(*worker);
                        maybe_begin_qualification_release(
                            *worker, std::chrono::steady_clock::now());
                    }
                }
                if (!observed) {
                    std::this_thread::sleep_for(std::chrono::milliseconds(10));
                }
            }
        } catch (...) {
            std::scoped_lock lock(snapshot_mutex_);
            for (auto &worker : workers_) {
                worker->last_failure = Failure::internal;
            }
            carrier_stop_requested_.store(true);
            stop_requested_.store(true);
            running_.store(false);
        }
    }

    void carrier_main() noexcept {
        try {
            while (!carrier_stop_requested_.load() &&
                   !stop_requested_.load()) {
                std::vector<std::shared_ptr<Worker>> workers;
                {
                    std::scoped_lock lock(snapshot_mutex_);
                    workers.reserve(workers_.size());
                    for (const auto &worker : workers_) {
                        if (worker) workers.push_back(worker);
                    }
                }
                for (const auto &worker : workers) {
                    if (carrier_stop_requested_.load() ||
                        stop_requested_.load()) {
                        break;
                    }
                    if (!worker->transport.running()) continue;

                    // File-carrier pause/resume is a synchronous toxcore
                    // owner operation. Keep it off the only thread that can
                    // drain this worker's required transport events, and do
                    // not retain the supervisor snapshot mutex while the
                    // owner command is in flight. This is the auxiliary-route
                    // counterpart of ADR 0157's primary Agent split.
                    const Status carrier =
                        worker->transfers.service_carrier();
                    if (!carrier.ok() && !retryable(carrier.code())) {
                        std::scoped_lock lock(snapshot_mutex_);
                        const bool still_owned = std::any_of(
                            workers_.begin(), workers_.end(),
                            [&worker](const auto &candidate) {
                                return candidate.get() == worker.get();
                            });
                        if (still_owned) {
                            worker->last_failure = Failure::transport;
                        }
                    }
                }
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        } catch (...) {
            std::scoped_lock lock(snapshot_mutex_);
            for (auto &worker : workers_) {
                worker->last_failure = Failure::internal;
            }
            carrier_stop_requested_.store(true);
            stop_requested_.store(true);
            running_.store(false);
        }
    }

    Config config_;
    std::vector<std::shared_ptr<Worker>> workers_;
    mutable std::mutex snapshot_mutex_;
    std::atomic<bool> start_called_{false};
    std::atomic<bool> carrier_stop_requested_{false};
    std::atomic<bool> stop_requested_{false};
    std::atomic<bool> running_{false};
    std::thread event_thread_;
    std::thread carrier_thread_;
    RouteBindingRegistry bindings_;
    std::optional<std::chrono::steady_clock::time_point>
        qualification_release_at_;
    std::vector<RemoteRouteTrust> remote_trust_;
    std::vector<PrivateRoutePrimaryContext> private_contexts_;
    std::vector<WorkerTransferTerminalEvent> terminal_events_;
    std::vector<WorkerSyncFrameEvent> sync_frame_events_;
};

WorkerSupervisor::WorkerSupervisor(Config config)
    : impl_(std::make_unique<Impl>(std::move(config))) {}
WorkerSupervisor::~WorkerSupervisor() = default;
Status WorkerSupervisor::set_sync_content_frames_enabled(bool enabled) {
    return impl_->set_sync_content_frames_enabled(enabled);
}
Status WorkerSupervisor::start() { return impl_->start(); }
void WorkerSupervisor::stop() { impl_->stop(); }
bool WorkerSupervisor::running() const noexcept { return impl_->running(); }
std::vector<WorkerSessionSnapshot> WorkerSupervisor::snapshot() const {
    return impl_->snapshot();
}
Status WorkerSupervisor::replace_remote_trust(
    std::vector<RemoteRouteTrust> trust) {
    return impl_->replace_remote_trust(std::move(trust));
}
Status WorkerSupervisor::replace_private_route_contexts(
    std::vector<PrivateRoutePrimaryContext> contexts) {
    return impl_->replace_private_route_contexts(std::move(contexts));
}
std::vector<WorkerTransferSnapshot> WorkerSupervisor::transfers() const {
    return impl_->transfers();
}
Result<FileTransferRecord> WorkerSupervisor::receive_to_path(
    const ToxPublicKey &route_key, std::uint64_t worker_id,
    std::uint32_t file_number, const std::filesystem::path &destination) {
    return impl_->receive_to_path(
        route_key, worker_id, file_number, destination);
}
Result<FileTransferRecord> WorkerSupervisor::receive_to_path_from_offset(
    const ToxPublicKey &route_key, std::uint64_t worker_id,
    std::uint32_t file_number, const std::filesystem::path &destination,
    std::uint64_t resume_offset) {
    return impl_->receive_to_path(
        route_key, worker_id, file_number, destination, resume_offset);
}
Result<FileTransferRecord> WorkerSupervisor::send_path_with_file_id(
    const ToxPublicKey &route_key, std::uint64_t worker_id,
    const std::filesystem::path &source, const FileId &file_id) {
    return impl_->send_path_with_file_id(route_key, worker_id, source, file_id);
}
Result<FileTransferRecord> WorkerSupervisor::send_path_ranges_with_file_id(
    const ToxPublicKey &route_key, std::uint64_t worker_id,
    const std::filesystem::path &source,
    std::span<const FileByteRange> ranges, const FileId &file_id) {
    return impl_->send_path_ranges_with_file_id(
        route_key, worker_id, source, ranges, file_id);
}
Status WorkerSupervisor::cancel_transfer(
    const ToxPublicKey &route_key, std::uint64_t worker_id,
    std::uint32_t file_number) {
    return impl_->cancel_transfer(route_key, worker_id, file_number);
}
Status WorkerSupervisor::retire_incoming_transfer(
    const ToxPublicKey &route_key, std::uint64_t worker_id,
    std::uint32_t file_number) {
    return impl_->retire_incoming_transfer(
        route_key, worker_id, file_number);
}
Result<std::vector<WorkerTransferTerminalEvent>>
WorkerSupervisor::take_transfer_terminal_events(std::size_t maximum_events) {
    return impl_->take_transfer_terminal_events(maximum_events);
}
Status WorkerSupervisor::send_sync_frame(
    const ToxPublicKey &route_key, std::uint64_t worker_id,
    const protocol::Frame &frame) {
    return impl_->send_sync_frame(route_key, worker_id, frame);
}
Result<std::vector<WorkerSyncFrameEvent>>
WorkerSupervisor::take_sync_frame_events(std::size_t maximum_events) {
    return impl_->take_sync_frame_events(maximum_events);
}
Status WorkerSupervisor::stop_worker_for_qualification(
    const ToxPublicKey &route_key, std::uint64_t worker_id) {
    return impl_->stop_worker_for_qualification(route_key, worker_id);
}
Result<std::uint64_t> WorkerSupervisor::restart_worker_for_qualification(
    const ToxPublicKey &route_key, std::uint64_t worker_id) {
    return impl_->restart_worker_for_qualification(route_key, worker_id);
}

std::filesystem::path WorkerSupervisor::state_path_for(
    const std::filesystem::path &root, const ToxPublicKey &key) {
    return root / (public_key_hex(key) + ".toxsave");
}

}  // namespace iotox::routes
