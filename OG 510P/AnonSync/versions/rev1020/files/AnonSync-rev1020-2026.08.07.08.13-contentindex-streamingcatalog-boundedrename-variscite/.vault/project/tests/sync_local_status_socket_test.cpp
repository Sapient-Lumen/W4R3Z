#include "sync_local_status_socket.hpp"
#include "sync_linux_process_resources.hpp"
#include "anonsync_json_parser.hpp"
#include "sync_replica_historical_version_inventory_json.hpp"
#include "sync_replica_peer_service_status.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cstdlib>
#include <cerrno>
#include <exception>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <type_traits>
#include <utility>
#include <vector>

#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;

static_assert(!std::is_copy_constructible_v<
              anonsync::SyncLocalStatusSocketServer>);
static_assert(!std::is_move_constructible_v<
              anonsync::SyncLocalStatusSocketServer>);

std::size_t checks = 0U;

void require(bool condition, std::string_view message) {
    ++checks;
    if (!condition) throw std::runtime_error(std::string(message));
}

void require_valid_json(
    const std::string& document,
    std::string_view message) {
    ++checks;
    try {
        (void)anonsync::parse_json_text(document);
    } catch (const std::exception& error) {
        throw std::runtime_error(
            std::string(message) + ": " + error.what());
    }
}

template <typename Function>
void require_throws(Function&& function, std::string_view message) {
    ++checks;
    try {
        std::forward<Function>(function)();
    } catch (const std::exception&) {
        return;
    }
    throw std::runtime_error(std::string(message));
}

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
        std::string pattern = "/tmp/anonsync-status-socket-test-XXXXXX";
        std::vector<char> writable(pattern.begin(), pattern.end());
        writable.push_back('\0');
        char* selected = ::mkdtemp(writable.data());
        if (selected == nullptr) {
            throw std::runtime_error("mkdtemp failed");
        }
        path_ = selected;
        if (::chmod(path_.c_str(), 0700U) != 0) {
            throw std::runtime_error("temporary directory chmod failed");
        }
    }

    ~TemporaryDirectory() noexcept {
        std::error_code error;
        fs::remove_all(path_, error);
    }

    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
};

void bind_stale_socket_or_throw(const fs::path& path) {
    const int descriptor = ::socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (descriptor < 0) throw std::runtime_error("stale socket() failed");
    sockaddr_un address{};
    address.sun_family = AF_UNIX;
    const std::string native = path.string();
    if (native.size() >= sizeof(address.sun_path)) {
        (void)::close(descriptor);
        throw std::runtime_error("stale socket path too long");
    }
    std::copy(native.begin(), native.end(), address.sun_path);
    address.sun_path[native.size()] = '\0';
    if (::bind(
            descriptor, reinterpret_cast<const sockaddr*>(&address),
            sizeof(address)) != 0) {
        const int error = errno;
        (void)::close(descriptor);
        throw std::runtime_error(
            "stale socket bind failed: " + std::to_string(error));
    }
    if (::chmod(path.c_str(), 0600U) != 0) {
        (void)::close(descriptor);
        throw std::runtime_error("stale socket chmod failed");
    }
    (void)::close(descriptor);
}

std::string raw_local_request_or_throw(
    const fs::path& path,
    std::string_view request) {
    const int descriptor = ::socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (descriptor < 0) {
        throw std::runtime_error("raw local request socket() failed");
    }
    const auto fail_after_close = [&](std::string message) -> void {
        const int ignored = ::close(descriptor);
        (void)ignored;
        throw std::runtime_error(std::move(message));
    };

    sockaddr_un address{};
    address.sun_family = AF_UNIX;
    const std::string native = path.string();
    if (native.size() >= sizeof(address.sun_path)) {
        fail_after_close("raw local request socket path is too long");
    }
    std::copy(native.begin(), native.end(), address.sun_path);
    address.sun_path[native.size()] = '\0';
    if (::connect(
            descriptor, reinterpret_cast<const sockaddr*>(&address),
            sizeof(address)) != 0) {
        fail_after_close(
            "raw local request connect failed: " +
            std::to_string(errno));
    }

    std::size_t written = 0U;
    while (written < request.size()) {
        const ssize_t count = ::write(
            descriptor, request.data() + written, request.size() - written);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) {
            fail_after_close(
                "raw local request write failed: " +
                std::to_string(errno));
        }
        written += static_cast<std::size_t>(count);
    }
    if (::shutdown(descriptor, SHUT_WR) != 0) {
        fail_after_close(
            "raw local request shutdown failed: " +
            std::to_string(errno));
    }

    std::string response;
    char buffer[4096];
    for (;;) {
        const ssize_t count = ::read(descriptor, buffer, sizeof(buffer));
        if (count < 0 && errno == EINTR) continue;
        if (count < 0) {
            fail_after_close(
                "raw local request read failed: " +
                std::to_string(errno));
        }
        if (count == 0) break;
        response.append(buffer, static_cast<std::size_t>(count));
        if (response.size() > 64U * 1024U) {
            fail_after_close("raw local response exceeded test bound");
        }
    }
    if (::close(descriptor) != 0) {
        throw std::runtime_error("raw local request close failed");
    }
    return response;
}

template <typename Client>
void with_raw_server_unlinked_before_response_or_throw(
    const fs::path& path,
    std::string_view expected_request,
    std::string_view response,
    Client&& client) {
    std::atomic<bool> ready{false};
    std::atomic<bool> failed{false};
    std::exception_ptr server_failure;
    std::jthread server([&] {
        int listener = -1;
        int connection = -1;
        const auto close_descriptors = [&]() noexcept {
            if (connection >= 0) {
                (void)::close(connection);
                connection = -1;
            }
            if (listener >= 0) {
                (void)::close(listener);
                listener = -1;
            }
        };
        try {
            listener = ::socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
            if (listener < 0) {
                throw std::runtime_error(
                    "unlinked-response server socket failed");
            }
            sockaddr_un address{};
            address.sun_family = AF_UNIX;
            const std::string native = path.string();
            if (native.size() >= sizeof(address.sun_path)) {
                throw std::runtime_error(
                    "unlinked-response server path is too long");
            }
            std::copy(native.begin(), native.end(), address.sun_path);
            address.sun_path[native.size()] = '\0';
            if (::bind(
                    listener, reinterpret_cast<const sockaddr*>(&address),
                    sizeof(address)) != 0) {
                throw std::runtime_error(
                    "unlinked-response server bind failed: " +
                    std::to_string(errno));
            }
            if (::chmod(path.c_str(), 0600U) != 0) {
                throw std::runtime_error(
                    "unlinked-response server chmod failed: " +
                    std::to_string(errno));
            }
            if (::listen(listener, 1) != 0) {
                throw std::runtime_error(
                    "unlinked-response server listen failed: " +
                    std::to_string(errno));
            }
            ready.store(true, std::memory_order_release);

            do {
                connection = ::accept4(listener, nullptr, nullptr, SOCK_CLOEXEC);
            } while (connection < 0 && errno == EINTR);
            if (connection < 0) {
                throw std::runtime_error(
                    "unlinked-response server accept failed: " +
                    std::to_string(errno));
            }

            std::string observed_request;
            observed_request.reserve(expected_request.size());
            while (observed_request.find('\n') == std::string::npos) {
                std::array<char, 256U> buffer{};
                const ssize_t count = ::read(
                    connection, buffer.data(), buffer.size());
                if (count < 0 && errno == EINTR) continue;
                if (count <= 0) {
                    throw std::runtime_error(
                        "unlinked-response server request read failed");
                }
                observed_request.append(
                    buffer.data(), static_cast<std::size_t>(count));
                if (observed_request.size() > 4096U) {
                    throw std::runtime_error(
                        "unlinked-response server request exceeded test bound");
                }
            }
            if (observed_request != expected_request) {
                throw std::runtime_error(
                    "unlinked-response server received an unexpected request");
            }
            if (::unlink(path.c_str()) != 0) {
                throw std::runtime_error(
                    "unlinked-response server unlink failed: " +
                    std::to_string(errno));
            }

            std::size_t written = 0U;
            while (written < response.size()) {
                const ssize_t count = ::send(
                    connection, response.data() + written,
                    response.size() - written, MSG_NOSIGNAL);
                if (count < 0 && errno == EINTR) continue;
                if (count <= 0) {
                    throw std::runtime_error(
                        "unlinked-response server response write failed");
                }
                written += static_cast<std::size_t>(count);
            }
            close_descriptors();
        } catch (...) {
            close_descriptors();
            (void)::unlink(path.c_str());
            server_failure = std::current_exception();
            failed.store(true, std::memory_order_release);
        }
    });

    const auto ready_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(2);
    while (!ready.load(std::memory_order_acquire) &&
           !failed.load(std::memory_order_acquire)) {
        if (std::chrono::steady_clock::now() >= ready_deadline) {
            throw std::runtime_error(
                "unlinked-response server readiness deadline expired");
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    if (failed.load(std::memory_order_acquire)) {
        server.join();
        std::rethrow_exception(server_failure);
    }

    std::exception_ptr client_failure;
    try {
        std::forward<Client>(client)();
    } catch (...) {
        client_failure = std::current_exception();
    }
    server.join();
    if (server_failure) std::rethrow_exception(server_failure);
    if (client_failure) std::rethrow_exception(client_failure);
}

void require_socket_mode(const fs::path& path, mode_t mode) {
    struct stat status {};
    require(::lstat(path.c_str(), &status) == 0, "socket path must exist");
    require(S_ISSOCK(status.st_mode), "status path must be a socket");
    require((status.st_mode & 07777U) == mode, "status socket mode mismatch");
    require(status.st_uid == ::geteuid(), "status socket owner mismatch");
}

[[nodiscard]] std::string synthetic_operation_id(std::uint64_t value) {
    std::ostringstream output;
    output << std::hex << std::setw(64) << std::setfill('0') << value;
    return output.str();
}

void test_historical_inventory_status_byte_frontier() {
    anonsync::SyncReplicaHistoricalVersionInventory inventory;
    inventory.query.inspection_mode = anonsync::
        SyncReplicaHistoricalVersionInspectionMode::ExactPayloadAvailability;
    inventory.query.maximum_entries = anonsync::
        kSyncReplicaHistoricalVersionMaximumEntries;
    inventory.source_replica_state_generation = 17U;
    inventory.source_operation_set_digest = std::string(64U, 'a');
    inventory.source_evidence_set_digest = std::string(64U, 'f');
    inventory.source_historical_version_pin_set_digest =
        std::string(64U, '1');
    inventory.historical_version_pin_count = 1U;
    inventory.source_visible_state_digest = std::string(64U, 'b');
    inventory.source_payload_snapshot_digest = std::string(64U, '0');
    inventory.payload_scan_hashed_entry_count = 3U;
    inventory.payload_scan_hashed_bytes = 30U;
    inventory.payload_scan_reused_entry_count = 4U;
    inventory.payload_scan_reused_bytes = 40U;
    inventory.payload_present_count = 7U;
    inventory.restore_ready_count = 5U;
    inventory.retained_payload_reachability =
        anonsync::SyncReplicaHistoricalVersionPayloadReachability{
            .payload_entry_count = 7U,
            .payload_indexed_bytes = 70U,
            .current_visible = {3U, 2U, 2U, 20U, 0U},
            .superseded_active = {5U, 4U, 3U, 30U, 1U},
            .inactive_evidence = {2U, 2U, 1U, 10U, 1U},
            .explicit_pins = {1U, 1U, 1U, 10U, 0U},
            .retained_union = {10U, 6U, 5U, 50U, 1U},
            .unreferenced_payload_count = 2U,
            .unreferenced_payload_bytes = 20U,
        };
    inventory.historical_file_operation_count = anonsync::
        kSyncReplicaHistoricalVersionMaximumEntries;
    inventory.historical_file_operation_count_after_cursor = anonsync::
        kSyncReplicaHistoricalVersionMaximumEntries;
    inventory.entries.reserve(static_cast<std::size_t>(anonsync::
        kSyncReplicaHistoricalVersionMaximumEntries));

    const std::string long_path =
        std::string("history/") + std::string(4088U, 'x');
    require(
        long_path.size() == anonsync::
            kSyncReplicaHistoricalVersionMaximumCanonicalPathBytes,
        "history byte-frontier fixture path must reach the public bound");
    for (std::uint64_t index = 1U;
         index <= anonsync::kSyncReplicaHistoricalVersionMaximumEntries;
         ++index) {
        inventory.entries.push_back(
            anonsync::SyncReplicaHistoricalVersionEntry{
                .operation_id = synthetic_operation_id(index),
                .canonical_path = long_path,
                .size_bytes = index,
                .content_sha256 = std::string(64U, 'c'),
                .actor = {.device_id = std::string(64U, 'd'), .epoch = 3U},
                .counter = index,
                .visible_head_count = 1U,
                .current_primary_operation_id = std::string(64U, 'e'),
                .current_primary_kind = anonsync::SyncReplicaValueKind::File,
                .payload_present = std::nullopt,
                .restore_ready = std::nullopt,
            });
    }

    const std::string unbounded = anonsync::
        render_sync_replica_historical_version_inventory_json(inventory);
    require(
        unbounded.size() > anonsync::
            kSyncReplicaHistoricalVersionMaximumStatusInventoryBytes &&
            unbounded.find("\"source_cutpoint\":\"v4:exact:") !=
                std::string::npos &&
            unbounded.find("\"retained_payload_reachability\":{\"scope\":\"share_retained_file_operations\"") !=
                std::string::npos,
        "maximum exact history page must compose evidence-bound reachability with the status overflow boundary");

    const std::vector<anonsync::SyncReplicaHistoricalVersionEntry>
        original_entries = inventory.entries;
    anonsync::
        bound_sync_replica_historical_version_inventory_for_status_or_throw(
            inventory);
    require(
        inventory.status_byte_limit == std::optional<std::uint64_t>(
            anonsync::
                kSyncReplicaHistoricalVersionMaximumStatusInventoryBytes) &&
            inventory.status_byte_frontier_reached &&
            !inventory.entry_limit_frontier_reached && inventory.truncated,
        "history status boundary did not report its independent byte frontier");
    require(
        !inventory.entries.empty() &&
            inventory.entries.size() < original_entries.size(),
        "history status byte frontier did not retain one bounded prefix");
    require(
        inventory.next_start_after_operation_id ==
            std::optional<std::string>(inventory.entries.back().operation_id) &&
            inventory.entries == std::vector<
                anonsync::SyncReplicaHistoricalVersionEntry>(
                    original_entries.begin(),
                    original_entries.begin() +
                        static_cast<std::ptrdiff_t>(inventory.entries.size())),
        "history status byte frontier changed order or lost its exact continuation cursor");

    const std::string bounded = anonsync::
        render_sync_replica_historical_version_inventory_json(inventory);
    require(
        bounded.size() <= anonsync::
            kSyncReplicaHistoricalVersionMaximumStatusInventoryBytes &&
            bounded.find("\"status_byte_frontier_reached\":true") !=
                std::string::npos &&
            bounded.find("\"entry_limit_frontier_reached\":false") !=
                std::string::npos &&
            bounded.find("\"source_evidence_set_digest\":\"" +
                         std::string(64U, 'f') + "\"") !=
                std::string::npos &&
            bounded.find("\"retained_payload_reachability\":{\"scope\":\"share_retained_file_operations\"") !=
                std::string::npos,
        "canonical exact-history renderer exceeded, concealed, or dropped its composed reachability frontier");
    require(
        anonsync::kSyncReplicaHistoricalVersionMaximumStatusInventoryBytes <
            anonsync::kSyncLocalStatusSocketMaximumResponseBytes,
        "history inventory must leave independent local-status headroom");

    anonsync::SyncReplicaPeerServiceStepResult step;
    step.disposition = anonsync::SyncReplicaPeerServiceStepDisposition::
        OperatorHistoricalVersionCompleted;
    step.historical_version_generation = 9U;
    step.historical_version_action = anonsync::
        SyncReplicaPeerServiceHistoricalVersionAction::Inspect;
    step.historical_version_inventory = inventory;
    anonsync::SyncReplicaPeerServiceLoopSummary summary;
    anonsync::account_sync_replica_peer_service_step(summary, step);
    require(
        summary.last_step.has_value() &&
            summary.last_step->historical_version_generation == 9U &&
            summary.last_step->historical_version_action ==
                step.historical_version_action &&
            !summary.last_step->historical_version_inventory.has_value(),
        "generic last_step retained a duplicate completed history page");

    anonsync::SyncReplicaPeerServiceHistoricalVersionStatus status;
    status.requested_generation = 9U;
    status.started_generation = 9U;
    status.completed_generation = 9U;
    status.action = anonsync::
        SyncReplicaPeerServiceHistoricalVersionAction::Inspect;
    status.query = inventory.query;
    status.last_inventory = inventory;
    const std::string stable = anonsync::
        render_sync_replica_peer_service_historical_version_status_json(
            status);
    require(
        stable.find(inventory.entries.front().operation_id) !=
                std::string::npos &&
            stable.size() < anonsync::
                kSyncLocalStatusSocketMaximumResponseBytes,
        "stable historical status did not retain the single bounded result");

    anonsync::SyncReplicaRetentionPlan plan;
    plan.query.maximum_entries = 2U;
    plan.source_replica_database_incarnation_sha256 = std::string(64U, '7');
    plan.source_replica_database_recovery_epoch = 3U;
    plan.source_replica_state_generation = 19U;
    plan.source_operation_set_digest = std::string(64U, 'a');
    plan.source_evidence_set_digest = std::string(64U, 'b');
    plan.source_historical_version_pin_set_digest = std::string(64U, 'c');
    plan.historical_version_pin_count = 1U;
    plan.source_visible_state_digest = std::string(64U, 'd');
    plan.source_payload_snapshot_digest = std::string(64U, 'e');
    plan.source_payload_transient_namespace_digest = std::string(64U, '1');
    plan.payload_transient_entry_count = 2U;
    plan.payload_transient_bytes = 14U;
    plan.payload_transient_reserved_bytes = 29U;
    plan.live_capability_process_store_scope_digest =
        std::string(64U, '1');
    plan.live_capability_process_store_scope_incarnation_digest =
        std::string(64U, '2');
    plan.live_capability_set_digest = std::string(64U, '3');
    plan.live_snapshot_count = 1U;
    plan.live_opened_payload_count = 2U;
    plan.live_targeted_access_count = 3U;
    plan.live_mutation_batch_count = 4U;
    plan.distinct_live_opened_payload_root_count = 1U;
    plan.distinct_live_opened_payload_root_bytes = 20U;
    plan.live_capabilities_may_reopen_all_current_payloads = true;
    plan.live_capability_rooted_physical_payload_count = 7U;
    plan.live_capability_rooted_physical_payload_bytes = 70U;
    plan.unreferenced_live_capability_rooted_payload_count = 2U;
    plan.unreferenced_live_capability_rooted_payload_bytes = 20U;
    plan.writer_fenced_observation = true;
    plan.cooperating_new_namespace_activity_excluded_during_observation =
        true;
    plan.writer_fenced_candidate_page_entry_count = 2U;
    plan.returned_unreferenced_candidate_count = 1U;
    plan.returned_candidate_payload_use_busy_count = 1U;
    plan.writer_fenced_candidate_page_digest = std::string(64U, '9');
    plan.unreferenced_candidate_set_digest = std::string(64U, 'f');
    plan.durable_candidate_witness_digest = std::string(64U, 'e');
    plan.exact_deletion_free_mark_digest = std::string(64U, '0');
    plan.retained_payload_reachability =
        inventory.retained_payload_reachability.value();
    plan.current_or_explicit_pin = {1U, 10U};
    plan.unreferenced_by_retained_file_operations = {1U, 20U};
    plan.physical_payload_count_after_cursor = 2U;
    plan.entries = {
        {
            .content_sha256 = synthetic_operation_id(7001U),
            .size_bytes = 10U,
            .current_visible = true,
            .inactive_evidence = true,
            .same_process_store_live_capability = true,
            .disposition = anonsync::
                SyncReplicaRetentionPlanDisposition::CurrentOrExplicitPin,
        },
        {
            .content_sha256 = synthetic_operation_id(7002U),
            .size_bytes = 20U,
            .same_process_store_live_capability = true,
            .payload_use_disposition = anonsync::
                SyncReplicaRetentionPlanPayloadUseDisposition::
                    BusyAtCutpoint,
            .disposition = anonsync::SyncReplicaRetentionPlanDisposition::
                UnreferencedByRetainedFileOperations,
        },
    };

    anonsync::SyncReplicaPeerServiceStepResult plan_step;
    plan_step.disposition = anonsync::SyncReplicaPeerServiceStepDisposition::
        OperatorHistoricalVersionCompleted;
    plan_step.historical_version_generation = 10U;
    plan_step.historical_version_action = anonsync::
        SyncReplicaPeerServiceHistoricalVersionAction::RetentionPlan;
    plan_step.historical_version_retention_plan = plan;
    anonsync::SyncReplicaPeerServiceLoopSummary plan_summary;
    anonsync::account_sync_replica_peer_service_step(
        plan_summary, plan_step);
    require(
        plan_summary.last_step.has_value() &&
            plan_summary.last_step->historical_version_generation == 10U &&
            !plan_summary.last_step->historical_version_retention_plan
                 .has_value(),
        "generic last_step retained a duplicate retention-plan page");

    anonsync::SyncReplicaPeerServiceHistoricalVersionStatus plan_status;
    plan_status.requested_generation = 10U;
    plan_status.started_generation = 10U;
    plan_status.completed_generation = 10U;
    plan_status.action = anonsync::
        SyncReplicaPeerServiceHistoricalVersionAction::RetentionPlan;
    plan_status.retention_plan_query = plan.query;
    plan_status.last_retention_plan = plan;
    const std::string stable_plan = anonsync::
        render_sync_replica_peer_service_historical_version_status_json(
            plan_status);
    require_valid_json(
        stable_plan,
        "stable retention-plan status renderer emitted invalid JSON");
    require(
        stable_plan.find("\"retention_plan_query\"") !=
                std::string::npos &&
            stable_plan.find("\"last_retention_plan\"") !=
                std::string::npos &&
            stable_plan.find(plan.entries.back().content_sha256) !=
                std::string::npos &&
            stable_plan.find("\"reclaimable_authority\":false") !=
                std::string::npos &&
            stable_plan.find("\"writer_fenced_observation\":true") !=
                std::string::npos &&
            stable_plan.find(
                "\"cooperating_new_namespace_activity_excluded_during_observation\":true") !=
                std::string::npos &&
            stable_plan.find("\"durable_mark_persisted\":false") !=
                std::string::npos &&
            stable_plan.find("\"payload_store_transient_namespace_bound\":true") !=
                std::string::npos &&
            stable_plan.find("\"same_process_store_live_payload_capabilities_bound\":true") !=
                std::string::npos &&
            stable_plan.find("\"independently_opened_same_process_store_owner_live_payload_capabilities_bound\":true") !=
                std::string::npos &&
            stable_plan.find("\"independent_store_owner_live_payload_capabilities_bound\":false") !=
                std::string::npos &&
            stable_plan.find("\"cross_process_live_payload_capabilities_bound\":false") !=
                std::string::npos &&
            stable_plan.find("\"already_copied_response_bytes_bound\":false") !=
                std::string::npos &&
            stable_plan.find("\"external_transient_root_model_complete\":false") !=
                std::string::npos &&
            stable_plan.find(
                "\"source_payload_transient_namespace_digest\":\"" +
                plan.source_payload_transient_namespace_digest + "\"") !=
                std::string::npos &&
            stable_plan.find("\"payload_transient_entries\":2") !=
                std::string::npos &&
            stable_plan.find("\"payload_transient_bytes\":14") !=
                std::string::npos &&
            stable_plan.find("\"payload_transient_reserved_bytes\":29") !=
                std::string::npos &&
            stable_plan.find(
                "\"live_payload_capabilities\":{\"process_store_scope_digest\":\"" +
                plan.live_capability_process_store_scope_digest +
                "\",\"process_store_scope_incarnation_digest\":\"" +
                plan.live_capability_process_store_scope_incarnation_digest + "\"") !=
                std::string::npos &&
            stable_plan.find(
                "\"capability_set_digest\":\"" +
                plan.live_capability_set_digest + "\"") !=
                std::string::npos &&
            stable_plan.find("\"snapshot_count\":1") !=
                std::string::npos &&
            stable_plan.find("\"opened_payload_count\":2") !=
                std::string::npos &&
            stable_plan.find("\"targeted_access_count\":3") !=
                std::string::npos &&
            stable_plan.find("\"mutation_batch_count\":4") !=
                std::string::npos &&
            stable_plan.find("\"distinct_opened_payload_root_count\":1") !=
                std::string::npos &&
            stable_plan.find("\"distinct_opened_payload_root_bytes\":20") !=
                std::string::npos &&
            stable_plan.find("\"may_reopen_all_current_payloads\":true") !=
                std::string::npos &&
            stable_plan.find("\"rooted_physical_payload_count\":7") !=
                std::string::npos &&
            stable_plan.find("\"rooted_physical_payload_bytes\":70") !=
                std::string::npos &&
            stable_plan.find("\"unreferenced_rooted_payload_count\":2") !=
                std::string::npos &&
            stable_plan.find("\"unreferenced_rooted_payload_bytes\":20") !=
                std::string::npos &&
            stable_plan.find("\"same_process_store_live_capability\":true") !=
                std::string::npos &&
            stable_plan.find(
                "\"returned_unreferenced_candidate_count\":1") !=
                std::string::npos &&
            stable_plan.find(
                "\"writer_fenced_candidate_page_entry_count\":2") !=
                std::string::npos &&
            stable_plan.find(
                "\"returned_candidate_payload_use_exclusive_available_count\":0") !=
                std::string::npos &&
            stable_plan.find(
                "\"returned_candidate_payload_use_busy_count\":1") !=
                std::string::npos &&
            stable_plan.find(
                "\"writer_fenced_candidate_page_digest\":\"" +
                plan.writer_fenced_candidate_page_digest + "\"") !=
                std::string::npos &&
            stable_plan.find(
                "\"payload_use_disposition\":\"busy_at_cutpoint\"") !=
                std::string::npos &&
            stable_plan.find(
                "\"unreferenced_candidate_set_digest\":\"" +
                plan.unreferenced_candidate_set_digest + "\"") !=
                std::string::npos &&
            stable_plan.find(
                "\"durable_candidate_witness_digest\":\"" +
                plan.durable_candidate_witness_digest + "\"") !=
                std::string::npos &&
            stable_plan.find(
                "\"exact_deletion_free_mark_digest\":\"" +
                plan.exact_deletion_free_mark_digest + "\"") !=
                std::string::npos,
        "stable historical status did not retain the deletion-free mark witness");

    anonsync::SyncReplicaRetentionPlan large_plan = plan;
    large_plan.query.maximum_entries = anonsync::
        kSyncReplicaRetentionPlanMaximumEntries;
    large_plan.current_or_explicit_pin = {
        anonsync::kSyncReplicaRetentionPlanMaximumEntries,
        anonsync::kSyncReplicaRetentionPlanMaximumEntries * 4096U};
    large_plan.retained_history_or_evidence = {};
    large_plan.unreferenced_by_retained_file_operations = {};
    large_plan.returned_unreferenced_candidate_count = 0U;
    large_plan.returned_candidate_payload_use_exclusive_available_count = 0U;
    large_plan.returned_candidate_payload_use_busy_count = 0U;
    large_plan.writer_fenced_candidate_page_digest = std::string(64U, '8');
    large_plan.writer_fenced_candidate_page_entry_count = anonsync::
        kSyncReplicaRetentionPlanMaximumEntries;
    large_plan.physical_payload_count_after_cursor = anonsync::
        kSyncReplicaRetentionPlanMaximumEntries;
    large_plan.entries.clear();
    large_plan.entries.reserve(static_cast<std::size_t>(anonsync::
        kSyncReplicaRetentionPlanMaximumEntries));
    for (std::uint64_t index = 1U;
         index <= anonsync::kSyncReplicaRetentionPlanMaximumEntries;
         ++index) {
        large_plan.entries.push_back({
            .content_sha256 = synthetic_operation_id(10000U + index),
            .size_bytes = 4096U,
            .current_visible = true,
            .superseded_active = true,
            .inactive_evidence = true,
            .explicit_pin = true,
            .disposition = anonsync::
                SyncReplicaRetentionPlanDisposition::CurrentOrExplicitPin,
        });
    }

    const std::vector<anonsync::SyncReplicaRetentionPlanEntry>
        original_plan_entries = large_plan.entries;
    const std::string unbounded_plan = anonsync::
        render_sync_replica_retention_plan_json(large_plan);
    require_valid_json(
        unbounded_plan,
        "unbounded retention-plan renderer emitted invalid JSON");
    require(
        unbounded_plan.size() > anonsync::
            kSyncReplicaRetentionPlanMaximumStatusBytes,
        "maximum retention-plan page did not exercise its status byte frontier");

    anonsync::bound_sync_replica_retention_plan_for_status_or_throw(
        large_plan);
    require(
        large_plan.status_byte_limit == std::optional<std::uint64_t>(
            anonsync::kSyncReplicaRetentionPlanMaximumStatusBytes) &&
            large_plan.status_byte_frontier_reached &&
            !large_plan.entry_limit_frontier_reached &&
            large_plan.truncated,
        "retention-plan status boundary did not report its independent byte frontier");
    require(
        !large_plan.entries.empty() &&
            large_plan.entries.size() < original_plan_entries.size() &&
            large_plan.next_start_after_content_sha256 ==
                std::optional<std::string>(
                    large_plan.entries.back().content_sha256) &&
            large_plan.entries ==
                std::vector<anonsync::SyncReplicaRetentionPlanEntry>(
                    original_plan_entries.begin(),
                    original_plan_entries.begin() +
                        static_cast<std::ptrdiff_t>(
                            large_plan.entries.size())),
        "retention-plan byte frontier changed digest order or lost its exact continuation cursor");

    const std::string bounded_plan = anonsync::
        render_sync_replica_retention_plan_json(large_plan);
    require_valid_json(
        bounded_plan,
        "bounded retention-plan renderer emitted invalid JSON");
    require(
        bounded_plan.size() <= anonsync::
                kSyncReplicaRetentionPlanMaximumStatusBytes &&
            bounded_plan.find("\"status_byte_frontier_reached\":true") !=
                std::string::npos &&
            bounded_plan.find("\"reclaimable_authority\":false") !=
                std::string::npos &&
            bounded_plan.find("\"writer_fenced_observation\":true") !=
                std::string::npos &&
            bounded_plan.find(
                "\"cooperating_new_namespace_activity_excluded_during_observation\":true") !=
                std::string::npos &&
            bounded_plan.find("\"writer_fenced_collection\":false") !=
                std::string::npos &&
            bounded_plan.find("\"durable_mark_persisted\":false") !=
                std::string::npos &&
            bounded_plan.find("\"payload_store_transient_namespace_bound\":true") !=
                std::string::npos &&
            bounded_plan.find("\"durable_receiver_restart_obligations_bound\":true") !=
                std::string::npos &&
            bounded_plan.find("\"same_process_store_live_payload_capabilities_bound\":true") !=
                std::string::npos &&
            bounded_plan.find("\"independently_opened_same_process_store_owner_live_payload_capabilities_bound\":true") !=
                std::string::npos &&
            bounded_plan.find("\"independent_store_owner_live_payload_capabilities_bound\":false") !=
                std::string::npos &&
            bounded_plan.find("\"cross_process_live_payload_capabilities_bound\":false") !=
                std::string::npos &&
            bounded_plan.find("\"already_copied_response_bytes_bound\":false") !=
                std::string::npos &&
            bounded_plan.find("\"active_pass_transient_roots_bound\":false") !=
                std::string::npos &&
            bounded_plan.find("\"opened_sender_transient_roots_bound\":false") !=
                std::string::npos &&
            bounded_plan.find("\"mutation_batch_transient_roots_bound\":false") !=
                std::string::npos &&
            bounded_plan.find("\"external_transient_root_model_complete\":false") !=
                std::string::npos &&
            bounded_plan.find(
                "\"source_payload_transient_namespace_digest\":\"" +
                large_plan.source_payload_transient_namespace_digest + "\"") !=
                std::string::npos &&
            bounded_plan.find(
                "\"unreferenced_candidate_set_digest\":\"" +
                large_plan.unreferenced_candidate_set_digest + "\"") !=
                std::string::npos &&
            bounded_plan.find(
                "\"durable_candidate_witness_digest\":\"" +
                large_plan.durable_candidate_witness_digest + "\"") !=
                std::string::npos &&
            bounded_plan.find(
                "\"writer_fenced_candidate_page_digest\":\"" +
                large_plan.writer_fenced_candidate_page_digest + "\"") !=
                std::string::npos &&
            bounded_plan.find(
                "\"writer_fenced_candidate_page_entry_count\":" +
                std::to_string(anonsync::
                    kSyncReplicaRetentionPlanMaximumEntries)) !=
                std::string::npos &&
            bounded_plan.find(
                "\"exact_deletion_free_mark_digest\":\"" +
                large_plan.exact_deletion_free_mark_digest + "\"") !=
                std::string::npos,
        "bounded retention-plan JSON exceeded or concealed its deletion-free mark frontier");

    plan_status.retention_plan_query = large_plan.query;
    plan_status.last_retention_plan = large_plan;
    const std::string bounded_plan_status = anonsync::
        render_sync_replica_peer_service_historical_version_status_json(
            plan_status);
    require(
        bounded_plan_status.size() < anonsync::
                kSyncLocalStatusSocketMaximumResponseBytes &&
            bounded_plan_status.find(
                large_plan.entries.front().content_sha256) !=
                std::string::npos,
        "bounded retention plan did not leave independent local-status response headroom");
}

}  // namespace

int main() {
    try {
        test_historical_inventory_status_byte_frontier();
        TemporaryDirectory temporary;
        const fs::path socket_path = temporary.path() / "status.sock";
        const std::string process_id = std::to_string(
            static_cast<long long>(::getpid()));
        const std::string initial =
            "{\"schema\":\"test.status.v1\",\"generation\":0,\"pid\":" +
            process_id + "}";
        const std::string updated =
            "{\"schema\":\"test.status.v1\",\"generation\":1,\"pid\":" +
            process_id + "}";
        const std::string quarantine_expected(64U, 'a');
        const std::string quarantine_observed(64U, 'b');
        const std::string quarantine_other(64U, 'c');
        const std::string historical_operation(64U, 'd');
        const std::string historical_other(64U, 'e');
        const std::string historical_current(64U, 'f');
        const anonsync::SyncReplicaHistoricalVersionSourceCutpoint
            historical_source{
                .operation_set_digest = historical_operation,
                .evidence_set_digest = historical_current,
                .historical_version_pin_set_digest =
                    std::string(64U, '1'),
                .payload_snapshot_digest = historical_other,
            };
        const std::string historical_source_token = anonsync::
            encode_sync_replica_historical_version_source_cutpoint_or_throw(
                historical_source, "local status test historical source");

        {
            anonsync::SyncLocalStatusSocketServer server(
                socket_path, initial, "status socket test");
            require(server.path() == socket_path, "server path must be exact");
            require_socket_mode(socket_path, 0600U);
            require(
                anonsync::query_sync_local_status_socket_or_throw(socket_path) ==
                    initial,
                "initial snapshot must be served exactly");
            const auto resources = anonsync::
                parse_sync_linux_process_resources_response_json_or_throw(
                    anonsync::query_sync_local_process_resources_or_throw(
                        socket_path),
                    static_cast<std::uint64_t>(::getpid()),
                    "local status resources response");
            require(
                resources.server_pid ==
                        static_cast<std::uint64_t>(::getpid()) &&
                    resources.process_start_time_clock_ticks > 0U &&
                    resources.memory.rss_kib > 0U &&
                    resources.memory.pss_kib > 0U &&
                    resources.open_file_descriptors > 0U &&
                    resources.threads >= 2U,
                "resources request did not return a complete PID-bound live observation");
            require(
                server.action_snapshot() ==
                    anonsync::SyncLocalStatusSocketActionSnapshot{false, 0U, std::nullopt, std::nullopt},
                "a new status socket must begin without drain or recheck");
            require(!server.wait_for_action_request_or_timeout(
                    anonsync::SyncLocalStatusSocketActionSnapshot{false, 0U, std::nullopt, std::nullopt}, 0U),
                    "a nonblocking action observation must begin false");
            require_throws(
                [&] {
                    (void)server.wait_for_action_request_or_timeout(
                        anonsync::SyncLocalStatusSocketActionSnapshot{false, 1U, std::nullopt, std::nullopt}, 0U);
                },
                "an action wait must reject a future generation baseline");

            server.publish_or_throw(updated);
            server.require_healthy_or_throw();
            require(
                anonsync::query_sync_local_status_socket_or_throw(socket_path) ==
                    updated,
                "published snapshot must replace the prior snapshot");

            const std::string wrong_pid =
                "{\"schema\":\"test.status.v1\",\"generation\":2,\"pid\":" +
                std::to_string(static_cast<long long>(::getpid()) + 1LL) + "}";
            server.publish_or_throw(wrong_pid);
            require_throws(
                [&] {
                    (void)anonsync::query_sync_local_status_socket_or_throw(
                        socket_path);
                },
                "status query must bind a reported pid to the connected peer");
            server.publish_or_throw(updated);

            std::atomic<bool> recheck_wait_started{false};
            std::atomic<bool> recheck_wait_completed{false};
            const auto recheck_wait_started_at =
                std::chrono::steady_clock::now();
            std::jthread recheck_waiter([&] {
                recheck_wait_started.store(true, std::memory_order_release);
                recheck_wait_completed.store(
                    server.wait_for_action_request_or_timeout(
                        anonsync::SyncLocalStatusSocketActionSnapshot{false, 0U, std::nullopt, std::nullopt}, 5000U),
                    std::memory_order_release);
            });
            while (!recheck_wait_started.load(std::memory_order_acquire)) {
                std::this_thread::yield();
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(20));
            const std::string first_recheck =
                anonsync::request_sync_local_status_recheck_or_throw(
                    socket_path);
            recheck_waiter.join();
            const auto recheck_wait_elapsed =
                std::chrono::steady_clock::now() - recheck_wait_started_at;
            require(
                first_recheck ==
                    "{\"schema\":\"anonsync.local-recheck.response.v1\","
                    "\"command\":\"recheck\","
                    "\"terminal_class\":\"accepted\","
                    "\"request_generation\":1,\"server_pid\":" +
                        process_id + "}",
                "first recheck request must return the exact acceptance");
            require(
                recheck_wait_completed.load(std::memory_order_acquire),
                "accepted recheck must wake an in-progress action wait");
            require(
                recheck_wait_elapsed < std::chrono::seconds(1),
                "accepted recheck must not wait for the fallback timeout");
            require(
                server.action_snapshot().recheck_request_generation == 1U,
                "accepted recheck must advance the generation");
            require(
                server.action_snapshot() ==
                    anonsync::SyncLocalStatusSocketActionSnapshot{false, 1U, std::nullopt, std::nullopt},
                "action snapshot must bind accepted recheck without drain");
            require(server.wait_for_action_request_or_timeout(
                    anonsync::SyncLocalStatusSocketActionSnapshot{false, 0U, std::nullopt, std::nullopt}, 0U),
                    "an older generation must observe pending action");
            require(!server.wait_for_action_request_or_timeout(
                        anonsync::SyncLocalStatusSocketActionSnapshot{false, 1U, std::nullopt, std::nullopt}, 0U),
                    "the exact accepted generation must not remain pending");

            const std::string second_recheck =
                anonsync::request_sync_local_status_recheck_or_throw(
                    socket_path);
            require(
                second_recheck ==
                    "{\"schema\":\"anonsync.local-recheck.response.v1\","
                    "\"command\":\"recheck\","
                    "\"terminal_class\":\"accepted\","
                    "\"request_generation\":2,\"server_pid\":" +
                        process_id + "}",
                "a second recheck must advance one exact generation");
            require(
                server.action_snapshot().recheck_request_generation == 2U,
                "the second recheck generation must be observable");

            const auto before_quarantine = server.action_snapshot();
            std::atomic<bool> quarantine_wait_started{false};
            std::atomic<bool> quarantine_wait_completed{false};
            std::jthread quarantine_waiter([&] {
                quarantine_wait_started.store(true, std::memory_order_release);
                quarantine_wait_completed.store(
                    server.wait_for_action_request_or_timeout(
                        before_quarantine, 5000U),
                    std::memory_order_release);
            });
            while (!quarantine_wait_started.load(std::memory_order_acquire)) {
                std::this_thread::yield();
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(20));
            const std::string first_quarantine =
                anonsync::request_sync_local_status_payload_quarantine_or_throw(
                    socket_path, quarantine_expected, quarantine_observed);
            quarantine_waiter.join();
            require(
                first_quarantine ==
                    "{\"schema\":\"anonsync.local-quarantine.response.v1\","
                    "\"command\":\"quarantine\","
                    "\"terminal_class\":\"accepted\","
                    "\"request_generation\":1,"
                    "\"expected_content_sha256\":\"" +
                        quarantine_expected +
                        "\",\"observed_content_sha256\":\"" +
                        quarantine_observed +
                        "\",\"server_pid\":" + process_id + "}",
                "first quarantine request must return exact acceptance");
            require(
                quarantine_wait_completed.load(std::memory_order_acquire),
                "accepted quarantine must wake the combined action wait");
            const auto quarantine_one = server.action_snapshot();
            require(
                quarantine_one.payload_quarantine_request.has_value() &&
                    quarantine_one.payload_quarantine_request
                            ->request_generation == 1U &&
                    quarantine_one.payload_quarantine_request
                            ->expected_content_sha256 == quarantine_expected &&
                    quarantine_one.payload_quarantine_request
                            ->observed_content_sha256 == quarantine_observed &&
                    quarantine_one.payload_quarantine_request->operation ==
                        anonsync::
                            SyncLocalStatusSocketPayloadQuarantineOperation::
                                Preserve,
                "combined action snapshot lost the exact quarantine pair");
            require(
                !server.wait_for_action_request_or_timeout(
                    quarantine_one, 0U),
                "the exact quarantine generation must not remain newly pending");

            const std::string coalesced_quarantine =
                anonsync::request_sync_local_status_payload_quarantine_or_throw(
                    socket_path, quarantine_expected, quarantine_observed);
            require(
                coalesced_quarantine ==
                    "{\"schema\":\"anonsync.local-quarantine.response.v1\","
                    "\"command\":\"quarantine\","
                    "\"terminal_class\":\"accepted\","
                    "\"request_generation\":2,"
                    "\"expected_content_sha256\":\"" +
                        quarantine_expected +
                        "\",\"observed_content_sha256\":\"" +
                        quarantine_observed +
                        "\",\"server_pid\":" + process_id + "}",
                "same-pair quarantine must coalesce through a new generation");
            const std::string conflicting_quarantine =
                anonsync::request_sync_local_status_payload_quarantine_or_throw(
                    socket_path, quarantine_expected, quarantine_other);
            require(
                conflicting_quarantine ==
                    "{\"schema\":\"anonsync.local-quarantine.response.v1\","
                    "\"command\":\"quarantine\","
                    "\"terminal_class\":\"rejected\","
                    "\"reason\":\"different_quarantine_pending\","
                    "\"request_generation\":2,"
                    "\"expected_content_sha256\":\"" +
                        quarantine_expected +
                        "\",\"observed_content_sha256\":\"" +
                        quarantine_other +
                        "\",\"server_pid\":" + process_id + "}",
                "different-pair quarantine must not overwrite pending authority");
            server.complete_payload_quarantine_request_or_throw(1U);
            require(
                server.action_snapshot().payload_quarantine_request
                        .has_value() &&
                    server.action_snapshot().payload_quarantine_request
                            ->request_generation == 2U,
                "completion through an older generation cleared coalesced work");
            server.complete_payload_quarantine_request_or_throw(2U);
            server.complete_payload_quarantine_request_or_throw(2U);
            require(
                !server.action_snapshot().payload_quarantine_request
                     .has_value(),
                "exact completion did not release the pending quarantine slot");
            require_throws(
                [&] {
                    server.complete_payload_quarantine_request_or_throw(3U);
                },
                "quarantine completion must reject a future generation");

            const std::string release_quarantine = anonsync::
                request_sync_local_status_payload_quarantine_release_or_throw(
                    socket_path, quarantine_expected, quarantine_observed);
            require(
                release_quarantine ==
                    "{\"schema\":\"anonsync.local-quarantine-release.response.v1\","
                    "\"command\":\"quarantine-release\","
                    "\"terminal_class\":\"accepted\","
                    "\"request_generation\":3,"
                    "\"expected_content_sha256\":\"" +
                        quarantine_expected +
                        "\",\"observed_content_sha256\":\"" +
                        quarantine_observed +
                        "\",\"server_pid\":" + process_id + "}",
                "exact quarantine release must return exact acceptance");
            const auto release_action = server.action_snapshot();
            require(
                release_action.payload_quarantine_request.has_value() &&
                    release_action.payload_quarantine_request
                            ->request_generation == 3U &&
                    release_action.payload_quarantine_request->operation ==
                        anonsync::
                            SyncLocalStatusSocketPayloadQuarantineOperation::
                                Release,
                "combined action snapshot lost the release operation");
            const std::string preserve_during_release =
                anonsync::request_sync_local_status_payload_quarantine_or_throw(
                    socket_path, quarantine_expected, quarantine_observed);
            require(
                preserve_during_release ==
                    "{\"schema\":\"anonsync.local-quarantine.response.v1\","
                    "\"command\":\"quarantine\","
                    "\"terminal_class\":\"rejected\","
                    "\"reason\":\"different_quarantine_pending\","
                    "\"request_generation\":3,"
                    "\"expected_content_sha256\":\"" +
                        quarantine_expected +
                        "\",\"observed_content_sha256\":\"" +
                        quarantine_observed +
                        "\",\"server_pid\":" + process_id + "}",
                "preserve must not overwrite a pending release action");
            server.complete_payload_quarantine_request_or_throw(3U);
            require(
                !server.action_snapshot().payload_quarantine_request
                     .has_value(),
                "release completion did not free the shared action slot");

            const auto before_versions = server.action_snapshot();
            std::atomic<bool> versions_wait_started{false};
            std::atomic<bool> versions_wait_completed{false};
            std::jthread versions_waiter([&] {
                versions_wait_started.store(true, std::memory_order_release);
                versions_wait_completed.store(
                    server.wait_for_action_request_or_timeout(
                        before_versions, 5000U),
                    std::memory_order_release);
            });
            while (!versions_wait_started.load(std::memory_order_acquire)) {
                std::this_thread::yield();
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(20));
            const std::string first_versions = anonsync::
                request_sync_local_status_historical_versions_or_throw(
                    socket_path);
            versions_waiter.join();
            require(
                first_versions ==
                    "{\"schema\":\"anonsync.local-historical-versions.response.v5\","
                    "\"command\":\"versions\","
                    "\"terminal_class\":\"accepted\","
                    "\"request_generation\":1,\"inspection_mode\":\"exact_payload_availability\",\"maximum_entries\":64,"
                    "\"canonical_path\":null,\"start_after_operation_id\":null,"
                    "\"expected_source_cutpoint\":null,\"server_pid\":" +
                        process_id + "}",
                "historical-version inspection must return exact acceptance");
            require(
                versions_wait_completed.load(std::memory_order_acquire),
                "historical-version inspection must wake the combined wait");
            const auto versions_one = server.action_snapshot();
            require(
                versions_one.historical_version_request.has_value() &&
                    versions_one.historical_version_request
                            ->request_generation == 1U &&
                    versions_one.historical_version_request->operation ==
                        anonsync::
                            SyncLocalStatusSocketHistoricalVersionOperation::
                                Inspect &&
                    versions_one.historical_version_request->query ==
                        anonsync::SyncReplicaHistoricalVersionQuery{} &&
                    versions_one.historical_version_request->restore_request ==
                        anonsync::SyncReplicaHistoricalVersionRestoreRequest{},
                "combined action snapshot lost the inspection request");

            const std::string versions_two = anonsync::
                request_sync_local_status_historical_versions_or_throw(
                    socket_path);
            require(
                versions_two ==
                    "{\"schema\":\"anonsync.local-historical-versions.response.v5\","
                    "\"command\":\"versions\","
                    "\"terminal_class\":\"accepted\","
                    "\"request_generation\":2,\"inspection_mode\":\"exact_payload_availability\",\"maximum_entries\":64,"
                    "\"canonical_path\":null,\"start_after_operation_id\":null,"
                    "\"expected_source_cutpoint\":null,\"server_pid\":" +
                        process_id + "}",
                "same historical inspection must coalesce by generation");
            anonsync::SyncReplicaHistoricalVersionQuery page_query;
            page_query.maximum_entries = 7U;
            page_query.canonical_path = "folder/name with space";
            page_query.start_after_operation_id = historical_other;
            page_query.expected_source_cutpoint = historical_source;
            anonsync::SyncReplicaHistoricalVersionQuery invalid_page =
                page_query;
            invalid_page.maximum_entries = 0U;
            require_throws(
                [&] {
                    (void)anonsync::
                        request_sync_local_status_historical_versions_query_or_throw(
                            socket_path, invalid_page);
                },
                "historical query client accepted a zero entry limit");
            invalid_page = page_query;
            invalid_page.canonical_path = "../escape";
            require_throws(
                [&] {
                    (void)anonsync::
                        request_sync_local_status_historical_versions_query_or_throw(
                            socket_path, invalid_page);
                },
                "historical query client accepted a non-canonical path");
            invalid_page = page_query;
            invalid_page.start_after_operation_id = "not-a-digest";
            require_throws(
                [&] {
                    (void)anonsync::
                        request_sync_local_status_historical_versions_query_or_throw(
                            socket_path, invalid_page);
                },
                "historical query client accepted a malformed cursor");
            invalid_page = page_query;
            invalid_page.expected_source_cutpoint =
                anonsync::SyncReplicaHistoricalVersionSourceCutpoint{
                    .operation_set_digest = "not-a-digest",
                    .evidence_set_digest = historical_current,
                    .historical_version_pin_set_digest =
                        std::string(64U, '1'),
                    .payload_snapshot_digest = historical_other,
                };
            require_throws(
                [&] {
                    (void)anonsync::
                        request_sync_local_status_historical_versions_query_or_throw(
                            socket_path, invalid_page);
                },
                "historical query client accepted a malformed source cutpoint");
            const std::string changed_page_while_inspection = anonsync::
                request_sync_local_status_historical_versions_query_or_throw(
                    socket_path, page_query);
            require(
                changed_page_while_inspection ==
                    "{\"schema\":\"anonsync.local-historical-versions.response.v5\","
                    "\"command\":\"versions\","
                    "\"terminal_class\":\"rejected\","
                    "\"reason\":\"different_historical_version_pending\","
                    "\"request_generation\":2,\"inspection_mode\":\"exact_payload_availability\",\"maximum_entries\":7,"
                    "\"canonical_path\":\"folder/name with space\","
                    "\"start_after_operation_id\":\"" +
                        historical_other +
                        "\",\"expected_source_cutpoint\":\"" +
                        historical_source_token + "\",\"server_pid\":" +
                        process_id + "}",
                "a different history page must not overwrite pending work");
            const std::string legacy_page_while_inspection =
                raw_local_request_or_throw(
                    socket_path,
                    "versions-query 7 "
                    "666f6c6465722f6e616d652077697468207370616365 " +
                        historical_other + "\n");
            require(
                legacy_page_while_inspection ==
                    "{\"schema\":\"anonsync.local-historical-versions.response.v5\","
                    "\"command\":\"versions\","
                    "\"terminal_class\":\"rejected\","
                    "\"reason\":\"different_historical_version_pending\","
                    "\"request_generation\":2,\"inspection_mode\":\"exact_payload_availability\",\"maximum_entries\":7,"
                    "\"canonical_path\":\"folder/name with space\","
                    "\"start_after_operation_id\":\"" +
                        historical_other +
                        "\",\"expected_source_cutpoint\":null,\"server_pid\":" +
                        process_id + "}\n",
                "rev0967 three-field historical query frame was not retained");

            const std::string restore_while_inspection = anonsync::
                request_sync_local_status_historical_version_restore_exact_or_throw(
                    socket_path, historical_operation, historical_current);
            require(
                restore_while_inspection ==
                    "{\"schema\":\"anonsync.local-historical-version-restore.response.v2\","
                    "\"command\":\"restore\","
                    "\"terminal_class\":\"rejected\","
                    "\"reason\":\"different_historical_version_pending\","
                    "\"request_generation\":2,\"operation_id\":\"" +
                        historical_operation +
                        "\",\"expected_current_operation_id\":\"" +
                        historical_current + "\",\"server_pid\":" +
                        process_id + "}",
                "exact restore must not overwrite a pending inspection");
            server.complete_historical_version_request_or_throw(1U);
            require(
                server.action_snapshot().historical_version_request
                        .has_value() &&
                    server.action_snapshot().historical_version_request
                            ->request_generation == 2U,
                "older historical completion cleared coalesced work");
            server.complete_historical_version_request_or_throw(2U);
            require(
                !server.action_snapshot().historical_version_request
                     .has_value(),
                "historical inspection completion did not free its lane");

            const std::string accepted_page = anonsync::
                request_sync_local_status_historical_versions_query_or_throw(
                    socket_path, page_query);
            require(
                accepted_page ==
                    "{\"schema\":\"anonsync.local-historical-versions.response.v5\","
                    "\"command\":\"versions\","
                    "\"terminal_class\":\"accepted\","
                    "\"request_generation\":3,\"inspection_mode\":\"exact_payload_availability\",\"maximum_entries\":7,"
                    "\"canonical_path\":\"folder/name with space\","
                    "\"start_after_operation_id\":\"" +
                        historical_other +
                        "\",\"expected_source_cutpoint\":\"" +
                        historical_source_token + "\",\"server_pid\":" +
                        process_id + "}",
                "path-scoped cursor page must return exact acceptance");
            const auto accepted_page_snapshot = server.action_snapshot();
            require(
                accepted_page_snapshot.historical_version_request.has_value() &&
                    accepted_page_snapshot.historical_version_request
                            ->request_generation == 3U &&
                    accepted_page_snapshot.historical_version_request->query ==
                        page_query,
                "history page query was not retained in the action snapshot");
            server.complete_historical_version_request_or_throw(3U);

            const std::string first_restore = anonsync::
                request_sync_local_status_historical_version_restore_exact_or_throw(
                    socket_path, historical_operation, historical_current);
            require(
                first_restore ==
                    "{\"schema\":\"anonsync.local-historical-version-restore.response.v2\","
                    "\"command\":\"restore\","
                    "\"terminal_class\":\"accepted\","
                    "\"request_generation\":4,\"operation_id\":\"" +
                        historical_operation +
                        "\",\"expected_current_operation_id\":\"" +
                        historical_current + "\",\"server_pid\":" +
                        process_id + "}",
                "exact-current historical restore must return exact acceptance");
            const auto exact_restore_snapshot = server.action_snapshot();
            require(
                exact_restore_snapshot.historical_version_request.has_value() &&
                    exact_restore_snapshot.historical_version_request
                            ->restore_request ==
                        anonsync::SyncReplicaHistoricalVersionRestoreRequest{
                            .operation_id = historical_operation,
                            .expected_current_operation_id = historical_current,
                        },
                "combined action snapshot lost the exact restore current-head fence");
            const std::string conflicting_restore = anonsync::
                request_sync_local_status_historical_version_restore_exact_or_throw(
                    socket_path, historical_other, historical_current);
            require(
                conflicting_restore ==
                    "{\"schema\":\"anonsync.local-historical-version-restore.response.v2\","
                    "\"command\":\"restore\","
                    "\"terminal_class\":\"rejected\","
                    "\"reason\":\"different_historical_version_pending\","
                    "\"request_generation\":4,\"operation_id\":\"" +
                        historical_other +
                        "\",\"expected_current_operation_id\":\"" +
                        historical_current + "\",\"server_pid\":" +
                        process_id + "}",
                "a different exact restore must not replace pending authority");
            const std::string legacy_restore_while_exact_pending =
                raw_local_request_or_throw(
                    socket_path, "restore " + historical_operation + "\n");
            require(
                legacy_restore_while_exact_pending ==
                    "{\"schema\":\"anonsync.local-historical-version-restore.response.v1\","
                    "\"command\":\"restore\","
                    "\"terminal_class\":\"rejected\","
                    "\"reason\":\"different_historical_version_pending\","
                    "\"request_generation\":4,\"operation_id\":\"" +
                        historical_operation + "\",\"server_pid\":" +
                        process_id + "}\n",
                "rev0966 unbound restore frame was not retained as a distinct request");
            require_throws(
                [&] {
                    (void)anonsync::
                        request_sync_local_status_historical_version_restore_or_throw(
                            socket_path, "not-a-digest");
                },
                "historical restore client accepted a malformed operation ID");
            require_throws(
                [&] {
                    (void)anonsync::
                        request_sync_local_status_historical_version_restore_exact_or_throw(
                            socket_path, historical_operation,
                            "not-a-digest");
                },
                "exact historical restore client accepted a malformed current operation ID");
            require_throws(
                [&] {
                    (void)anonsync::
                        request_sync_local_status_historical_version_restore_exact_or_throw(
                            socket_path, historical_operation,
                            historical_operation);
                },
                "exact historical restore client accepted equal historical and current IDs");
            server.complete_historical_version_request_or_throw(4U);
            require_throws(
                [&] {
                    server.complete_historical_version_request_or_throw(5U);
                },
                "historical completion accepted a future generation");

            const std::string first_pin = anonsync::
                request_sync_local_status_historical_version_pin_or_throw(
                    socket_path, historical_operation);
            require(
                first_pin ==
                    "{\"schema\":\"anonsync.local-historical-version-pin.response.v1\","
                    "\"command\":\"version-pin\","
                    "\"terminal_class\":\"accepted\","
                    "\"request_generation\":5,\"operation_id\":\"" +
                        historical_operation + "\",\"server_pid\":" +
                        process_id + "}",
                "historical pin did not return exact owner admission");
            const auto pin_snapshot = server.action_snapshot();
            require(
                pin_snapshot.historical_version_request.has_value() &&
                    pin_snapshot.historical_version_request->operation ==
                        anonsync::
                            SyncLocalStatusSocketHistoricalVersionOperation::Pin &&
                    pin_snapshot.historical_version_request
                            ->retention_operation_id == historical_operation &&
                    pin_snapshot.historical_version_request->query ==
                        anonsync::SyncReplicaHistoricalVersionQuery{} &&
                    pin_snapshot.historical_version_request->restore_request ==
                        anonsync::SyncReplicaHistoricalVersionRestoreRequest{},
                "historical pin admission leaked into query or restore authority");
            const std::string coalesced_pin = anonsync::
                request_sync_local_status_historical_version_pin_or_throw(
                    socket_path, historical_operation);
            require(
                coalesced_pin.find("\"request_generation\":6") !=
                    std::string::npos,
                "same historical pin did not coalesce by generation");
            const std::string conflicting_unpin = anonsync::
                request_sync_local_status_historical_version_unpin_or_throw(
                    socket_path, historical_operation);
            require(
                conflicting_unpin ==
                    "{\"schema\":\"anonsync.local-historical-version-unpin.response.v1\","
                    "\"command\":\"version-unpin\","
                    "\"terminal_class\":\"rejected\","
                    "\"reason\":\"different_historical_version_pending\","
                    "\"request_generation\":6,\"operation_id\":\"" +
                        historical_operation + "\",\"server_pid\":" +
                        process_id + "}",
                "unpin overwrote a pending pin in the shared history lane");
            server.complete_historical_version_request_or_throw(5U);
            require(
                server.action_snapshot().historical_version_request
                        .has_value() &&
                    server.action_snapshot().historical_version_request
                            ->request_generation == 6U,
                "older pin completion cleared a coalesced generation");
            server.complete_historical_version_request_or_throw(6U);
            const std::string accepted_unpin = anonsync::
                request_sync_local_status_historical_version_unpin_or_throw(
                    socket_path, historical_operation);
            require(
                accepted_unpin ==
                    "{\"schema\":\"anonsync.local-historical-version-unpin.response.v1\","
                    "\"command\":\"version-unpin\","
                    "\"terminal_class\":\"accepted\","
                    "\"request_generation\":7,\"operation_id\":\"" +
                        historical_operation + "\",\"server_pid\":" +
                        process_id + "}",
                "historical unpin did not return exact owner admission");
            server.complete_historical_version_request_or_throw(7U);
            require_throws(
                [&] {
                    (void)anonsync::
                        request_sync_local_status_historical_version_pin_or_throw(
                            socket_path, "not-a-digest");
                },
                "historical pin client accepted a malformed operation ID");
            require_throws(
                [&] {
                    (void)anonsync::
                        request_sync_local_status_historical_version_unpin_or_throw(
                            socket_path, "not-a-digest");
                },
                "historical unpin client accepted a malformed operation ID");

            std::atomic<bool> stop_wait_started{false};
            std::atomic<bool> stop_wait_completed{false};
            const auto stop_wait_started_at = std::chrono::steady_clock::now();
            std::jthread stop_waiter([&] {
                stop_wait_started.store(true, std::memory_order_release);
                stop_wait_completed.store(
                    server.wait_for_action_request_or_timeout(
                        anonsync::SyncLocalStatusSocketActionSnapshot{false, 2U, std::nullopt, std::nullopt}, 5000U),
                    std::memory_order_release);
            });
            while (!stop_wait_started.load(std::memory_order_acquire)) {
                std::this_thread::yield();
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(20));
            const std::string first_stop =
                anonsync::request_sync_local_status_stop_or_throw(socket_path);
            stop_waiter.join();
            const auto stop_wait_elapsed =
                std::chrono::steady_clock::now() - stop_wait_started_at;
            require(
                first_stop ==
                    "{\"schema\":\"anonsync.local-stop.response.v1\","
                    "\"command\":\"stop\",\"terminal_class\":\"completed\","
                    "\"stop_mode\":\"drain\",\"first_request\":true,"
                    "\"server_pid\":" + process_id + "}",
                "first stop request must return the exact drain response");
            require(server.action_snapshot().stop_requested,
                    "stop request must latch the drain observation");
            require(
                stop_wait_completed.load(std::memory_order_acquire),
                "stop request must wake an in-progress bounded wait");
            require(
                stop_wait_elapsed < std::chrono::seconds(1),
                "stop request must not wait for the five-second fallback timeout");
            require(server.wait_for_action_request_or_timeout(
                    anonsync::SyncLocalStatusSocketActionSnapshot{false, 2U, std::nullopt, std::nullopt}, 100U),
                    "latched stop request must wake bounded wait immediately");
            const std::string repeated_stop =
                anonsync::request_sync_local_status_stop_or_throw(socket_path);
            require(
                repeated_stop ==
                    "{\"schema\":\"anonsync.local-stop.response.v1\","
                    "\"command\":\"stop\",\"terminal_class\":\"completed\","
                    "\"stop_mode\":\"drain\",\"first_request\":false,"
                    "\"server_pid\":" + process_id + "}",
                "repeated stop request must remain idempotent");
            require(
                anonsync::query_sync_local_status_socket_or_throw(socket_path) ==
                    updated,
                "drain request must not revoke the status snapshot boundary");
            const std::string rejected_recheck =
                anonsync::request_sync_local_status_recheck_or_throw(
                    socket_path);
            require(
                rejected_recheck ==
                    "{\"schema\":\"anonsync.local-recheck.response.v1\","
                    "\"command\":\"recheck\","
                    "\"terminal_class\":\"rejected\","
                    "\"reason\":\"drain_requested\","
                    "\"request_generation\":2,\"server_pid\":" +
                        process_id + "}",
                "recheck serialized after drain must be rejected exactly");
            require(
                server.action_snapshot().recheck_request_generation == 2U,
                "post-drain rejection must not advance generation");
            const std::string rejected_quarantine =
                anonsync::request_sync_local_status_payload_quarantine_or_throw(
                    socket_path, quarantine_expected, quarantine_observed);
            require(
                rejected_quarantine ==
                    "{\"schema\":\"anonsync.local-quarantine.response.v1\","
                    "\"command\":\"quarantine\","
                    "\"terminal_class\":\"rejected\","
                    "\"reason\":\"drain_requested\","
                    "\"request_generation\":3,"
                    "\"expected_content_sha256\":\"" +
                        quarantine_expected +
                        "\",\"observed_content_sha256\":\"" +
                        quarantine_observed +
                        "\",\"server_pid\":" + process_id + "}",
                "payload quarantine serialized after drain must be rejected");
            const std::string rejected_release = anonsync::
                request_sync_local_status_payload_quarantine_release_or_throw(
                    socket_path, quarantine_expected, quarantine_observed);
            require(
                rejected_release ==
                    "{\"schema\":\"anonsync.local-quarantine-release.response.v1\","
                    "\"command\":\"quarantine-release\","
                    "\"terminal_class\":\"rejected\","
                    "\"reason\":\"drain_requested\","
                    "\"request_generation\":3,"
                    "\"expected_content_sha256\":\"" +
                        quarantine_expected +
                        "\",\"observed_content_sha256\":\"" +
                        quarantine_observed +
                        "\",\"server_pid\":" + process_id + "}",
                "quarantine release serialized after drain must be rejected");
            const std::string rejected_versions = anonsync::
                request_sync_local_status_historical_versions_or_throw(
                    socket_path);
            require(
                rejected_versions ==
                    "{\"schema\":\"anonsync.local-historical-versions.response.v5\","
                    "\"command\":\"versions\","
                    "\"terminal_class\":\"rejected\","
                    "\"reason\":\"drain_requested\","
                    "\"request_generation\":7,\"inspection_mode\":\"exact_payload_availability\",\"maximum_entries\":64,"
                    "\"canonical_path\":null,\"start_after_operation_id\":null,"
                    "\"expected_source_cutpoint\":null,\"server_pid\":" +
                        process_id + "}",
                "historical inspection serialized after drain must be rejected");
            const std::string rejected_restore = anonsync::
                request_sync_local_status_historical_version_restore_exact_or_throw(
                    socket_path, historical_operation, historical_current);
            require(
                rejected_restore ==
                    "{\"schema\":\"anonsync.local-historical-version-restore.response.v2\","
                    "\"command\":\"restore\","
                    "\"terminal_class\":\"rejected\","
                    "\"reason\":\"drain_requested\","
                    "\"request_generation\":7,\"operation_id\":\"" +
                        historical_operation +
                        "\",\"expected_current_operation_id\":\"" +
                        historical_current + "\",\"server_pid\":" +
                        process_id + "}",
                "exact historical restore serialized after drain must be rejected");
            require(
                server.action_snapshot() ==
                    anonsync::SyncLocalStatusSocketActionSnapshot{
                        true, 2U, std::nullopt, std::nullopt},
                "drain snapshot must retain every pre-drain generation");
            require(server.wait_for_action_request_or_timeout(
                    anonsync::SyncLocalStatusSocketActionSnapshot{false, 2U, std::nullopt, std::nullopt}, 100U),
                    "latched drain must wake the unified action wait");

            require(::chmod(socket_path.c_str(), 0660U) == 0,
                    "test must loosen socket mode");
            require_throws(
                [&] {
                    (void)anonsync::query_sync_local_status_socket_or_throw(
                        socket_path);
                },
                "query must reject a socket without exact mode 0600");
            require_throws(
                [&] {
                    (void)anonsync::
                        query_sync_local_process_resources_or_throw(socket_path);
                },
                "resources must reject a socket without exact mode 0600");
            require_throws(
                [&] {
                    (void)anonsync::request_sync_local_status_stop_or_throw(
                        socket_path);
                },
                "stop must reject a socket without exact mode 0600");
            require_throws(
                [&] {
                    (void)anonsync::request_sync_local_status_recheck_or_throw(
                        socket_path);
                },
                "recheck must reject a socket without exact mode 0600");
            require_throws(
                [&] {
                    (void)anonsync::
                        request_sync_local_status_payload_quarantine_or_throw(
                            socket_path, quarantine_expected,
                            quarantine_observed);
                },
                "quarantine must reject a socket without exact mode 0600");
            require_throws(
                [&] {
                    (void)anonsync::
                        request_sync_local_status_payload_quarantine_release_or_throw(
                            socket_path, quarantine_expected,
                            quarantine_observed);
                },
                "quarantine release must reject a socket without exact mode 0600");
            require_throws(
                [&] {
                    (void)anonsync::
                        request_sync_local_status_historical_versions_or_throw(
                            socket_path);
                },
                "historical inspection must reject a socket without exact mode 0600");
            require_throws(
                [&] {
                    (void)anonsync::
                        request_sync_local_status_historical_version_restore_exact_or_throw(
                            socket_path, historical_operation,
                            historical_current);
                },
                "historical restore must reject a socket without exact mode 0600");
            require_throws(
                [&] { server.require_healthy_or_throw(); },
                "server health must reject changed socket mode");
            require_throws(
                [&] { server.publish_or_throw(initial); },
                "publication must stop when the socket namespace is unhealthy");
            require(::chmod(socket_path.c_str(), 0600U) == 0,
                    "test must restore socket mode");
            server.require_healthy_or_throw();

            require(::chmod(temporary.path().c_str(), 0755U) == 0,
                    "test must loosen status parent mode");
            require_throws(
                [&] {
                    (void)anonsync::query_sync_local_status_socket_or_throw(
                        socket_path);
                },
                "query must reject a socket beneath a non-private parent");
            require_throws(
                [&] {
                    (void)anonsync::
                        query_sync_local_process_resources_or_throw(socket_path);
                },
                "resources must reject a socket beneath a non-private parent");
            require_throws(
                [&] {
                    (void)anonsync::request_sync_local_status_stop_or_throw(
                        socket_path);
                },
                "stop must reject a socket beneath a non-private parent");
            require_throws(
                [&] {
                    (void)anonsync::request_sync_local_status_recheck_or_throw(
                        socket_path);
                },
                "recheck must reject a socket beneath a non-private parent");
            require_throws(
                [&] {
                    (void)anonsync::
                        request_sync_local_status_payload_quarantine_or_throw(
                            socket_path, quarantine_expected,
                            quarantine_observed);
                },
                "quarantine must reject a socket beneath a non-private parent");
            require_throws(
                [&] {
                    (void)anonsync::
                        request_sync_local_status_payload_quarantine_release_or_throw(
                            socket_path, quarantine_expected,
                            quarantine_observed);
                },
                "quarantine release must reject a socket beneath a non-private parent");
            require(::chmod(temporary.path().c_str(), 0700U) == 0,
                    "test must restore status parent mode");

            require_throws(
                [&] {
                    anonsync::SyncLocalStatusSocketServer duplicate(
                        socket_path, initial, "duplicate status socket");
                },
                "a live status socket must exclude a second owner");
            require_throws(
                [&] { server.publish_or_throw("[]"); },
                "published status must remain a JSON object");
            require(
                anonsync::query_sync_local_status_socket_or_throw(socket_path) ==
                    updated,
                "rejected publication must preserve the last good snapshot");

            std::atomic<std::size_t> successful_queries{0U};
            std::vector<std::thread> clients;
            for (std::size_t index = 0U; index < 8U; ++index) {
                clients.emplace_back([&] {
                    if (anonsync::query_sync_local_status_socket_or_throw(
                            socket_path) == updated) {
                        ++successful_queries;
                    }
                });
            }
            for (auto& client : clients) client.join();
            require(
                successful_queries.load() == clients.size(),
                "concurrent read-only queries must all observe a valid snapshot");
            require(::unlink(socket_path.c_str()) == 0,
                    "test must remove the live socket pathname");
            require_throws(
                [&] { server.require_healthy_or_throw(); },
                "server health must reject a removed socket pathname");
        }
        require(!fs::exists(socket_path), "destruction must leave no socket path");

        {
            anonsync::SyncLocalStatusSocketServer metadata_server(
                socket_path, initial, "metadata history status socket");
            anonsync::SyncReplicaHistoricalVersionQuery metadata_query;
            metadata_query.inspection_mode = anonsync::
                SyncReplicaHistoricalVersionInspectionMode::
                    CausalMetadataOnly;
            metadata_query.maximum_entries = 3U;
            metadata_query.canonical_path = "folder/name with space";
            metadata_query.start_after_operation_id = historical_other;
            metadata_query.expected_source_cutpoint =
                anonsync::SyncReplicaHistoricalVersionSourceCutpoint{
                    .inspection_mode = anonsync::
                        SyncReplicaHistoricalVersionInspectionMode::
                            CausalMetadataOnly,
                    .operation_set_digest = historical_operation,
                    .evidence_set_digest = std::nullopt,
                    .historical_version_pin_set_digest =
                        std::string(64U, '1'),
                    .payload_snapshot_digest = std::nullopt,
                };
            const std::string metadata_token = anonsync::
                encode_sync_replica_historical_version_source_cutpoint_or_throw(
                    *metadata_query.expected_source_cutpoint,
                    "local status metadata source");
            const std::string accepted_metadata = anonsync::
                request_sync_local_status_historical_versions_query_or_throw(
                    socket_path, metadata_query);
            require(
                accepted_metadata ==
                    "{\"schema\":\"anonsync.local-historical-versions.response.v5\","
                    "\"command\":\"versions\","
                    "\"terminal_class\":\"accepted\","
                    "\"request_generation\":1,"
                    "\"inspection_mode\":\"causal_metadata_only\","
                    "\"maximum_entries\":3,"
                    "\"canonical_path\":\"folder/name with space\","
                    "\"start_after_operation_id\":\"" +
                        historical_other +
                        "\",\"expected_source_cutpoint\":\"" +
                        metadata_token + "\",\"server_pid\":" +
                        process_id + "}",
                "metadata-only history query did not preserve its exact mode");
            const auto metadata_action = metadata_server.action_snapshot();
            require(
                metadata_action.historical_version_request.has_value() &&
                    metadata_action.historical_version_request->query ==
                        metadata_query,
                "metadata-only history query was not retained as one action identity");
            metadata_server.complete_historical_version_request_or_throw(1U);

            const std::string legacy_mode_mismatch = raw_local_request_or_throw(
                socket_path,
                "versions-query 3 "
                "666f6c6465722f6e616d652077697468207370616365 " +
                    historical_other + " " + metadata_token + "\n");
            require(
                legacy_mode_mismatch ==
                    "{\"schema\":\"anonsync.local-status.response.v1\","
                    "\"ok\":false,\"error\":\"unsupported_request\"}\n",
                "legacy exact query frame accepted a metadata-only cutpoint");
        }
        require(
            !fs::exists(socket_path),
            "metadata history socket destruction left a pathname");

        {
            anonsync::SyncLocalStatusSocketServer plan_server(
                socket_path, initial, "retention plan status socket");
            anonsync::SyncReplicaRetentionPlanQuery plan_query;
            plan_query.maximum_entries = 2U;
            plan_query.start_after_content_sha256 = historical_other;
            plan_query.expected_source_cutpoint = historical_source;
            const std::string accepted_plan = anonsync::
                request_sync_local_status_retention_plan_or_throw(
                    socket_path, plan_query);
            require(
                accepted_plan ==
                    "{\"schema\":\"anonsync.local-retention-plan.response.v6\","
                    "\"command\":\"retention-plan\","
                    "\"terminal_class\":\"accepted\","
                    "\"request_generation\":1,\"maximum_entries\":2,"
                    "\"start_after_content_sha256\":\"" +
                        historical_other +
                        "\",\"expected_source_cutpoint\":\"" +
                        historical_source_token +
                        "\",\"server_pid\":" + process_id + "}",
                "retention-plan request did not return exact acceptance");
            const auto plan_action = plan_server.action_snapshot();
            require(
                plan_action.historical_version_request.has_value() &&
                    plan_action.historical_version_request
                            ->request_generation == 1U &&
                    plan_action.historical_version_request->operation ==
                        anonsync::
                            SyncLocalStatusSocketHistoricalVersionOperation::
                                RetentionPlan &&
                    plan_action.historical_version_request
                            ->retention_plan_query == plan_query &&
                    plan_action.historical_version_request->query ==
                        anonsync::SyncReplicaHistoricalVersionQuery{},
                "retention-plan query was not retained as one action identity");

            const std::string coalesced_plan = anonsync::
                request_sync_local_status_retention_plan_or_throw(
                    socket_path, plan_query);
            require(
                coalesced_plan.find("\"request_generation\":2") !=
                        std::string::npos &&
                    coalesced_plan.find(
                        "\"terminal_class\":\"accepted\"") !=
                        std::string::npos,
                "same retention-plan query did not coalesce by generation");

            anonsync::SyncReplicaRetentionPlanQuery different_plan =
                plan_query;
            different_plan.maximum_entries = 3U;
            const std::string rejected_plan = anonsync::
                request_sync_local_status_retention_plan_or_throw(
                    socket_path, different_plan);
            require(
                rejected_plan.find(
                    "\"reason\":\"different_historical_version_pending\"") !=
                        std::string::npos &&
                    rejected_plan.find("\"request_generation\":2") !=
                        std::string::npos,
                "different retention-plan query overwrote pending work");
            plan_server.complete_historical_version_request_or_throw(2U);
            require(
                !plan_server.action_snapshot().historical_version_request
                     .has_value(),
                "retention-plan completion did not free the action lane");
            require_throws(
                [&] {
                    anonsync::SyncReplicaRetentionPlanQuery malformed;
                    malformed.maximum_entries = 0U;
                    (void)anonsync::
                        request_sync_local_status_retention_plan_or_throw(
                            socket_path, malformed);
                },
                "retention-plan client accepted a zero entry limit");
            require(
                raw_local_request_or_throw(
                    socket_path,
                    "retention-plan 2 - v4:metadata:" +
                        historical_operation + ":" +
                        std::string(64U, '1') + "\n") ==
                    "{\"schema\":\"anonsync.local-status.response.v1\","
                    "\"ok\":false,\"error\":\"unsupported_request\"}\n",
                "retention-plan accepted a metadata-only source cutpoint");
        }
        require(
            !fs::exists(socket_path),
            "retention plan socket destruction left a pathname");

        {
            anonsync::SyncLocalStatusSocketServer sealed(
                socket_path, initial, "owner-sealed status socket");
            const std::string accepted =
                anonsync::request_sync_local_status_recheck_or_throw(
                    socket_path);
            require(
                accepted ==
                    "{\"schema\":\"anonsync.local-recheck.response.v1\","
                    "\"command\":\"recheck\","
                    "\"terminal_class\":\"accepted\","
                    "\"request_generation\":1,\"server_pid\":" +
                        process_id + "}",
                "owner-shutdown setup must accept one exact generation");
            const auto terminal_actions =
                sealed.seal_actions_for_owner_shutdown();
            require(
                terminal_actions ==
                    anonsync::SyncLocalStatusSocketActionSnapshot{true, 1U, std::nullopt, std::nullopt},
                "owner shutdown seal must bind all pre-seal actions");
            require(
                sealed.seal_actions_for_owner_shutdown() == terminal_actions,
                "owner shutdown seal must be idempotent");
            const std::string rejected =
                anonsync::request_sync_local_status_recheck_or_throw(
                    socket_path);
            require(
                rejected ==
                    "{\"schema\":\"anonsync.local-recheck.response.v1\","
                    "\"command\":\"recheck\","
                    "\"terminal_class\":\"rejected\","
                    "\"reason\":\"drain_requested\","
                    "\"request_generation\":1,\"server_pid\":" +
                        process_id + "}",
                "post-seal recheck must be rejected without generation advance");
            require(
                anonsync::query_sync_local_status_socket_or_throw(socket_path) ==
                    initial,
                "owner shutdown seal must preserve read-only status service");
            const std::string stop_after_seal =
                anonsync::request_sync_local_status_stop_or_throw(socket_path);
            require(
                stop_after_seal ==
                    "{\"schema\":\"anonsync.local-stop.response.v1\","
                    "\"command\":\"stop\",\"terminal_class\":\"completed\","
                    "\"stop_mode\":\"drain\",\"first_request\":false,"
                    "\"server_pid\":" + process_id + "}",
                "client stop after owner seal must remain idempotent");
        }
        require(!fs::exists(socket_path),
                "owner-sealed socket must be removed on destruction");

        bind_stale_socket_or_throw(socket_path);
        require_socket_mode(socket_path, 0600U);
        {
            anonsync::SyncLocalStatusSocketServer recovered(
                socket_path, initial, "stale recovery status socket");
            require(
                anonsync::query_sync_local_status_socket_or_throw(socket_path) ==
                    initial,
                "owner-controlled stale socket must be recovered");
        }
        require(!fs::exists(socket_path), "recovered socket must be unlinked");

        const fs::path loose = temporary.path() / "loose";
        fs::create_directory(loose);
        if (::chmod(loose.c_str(), 0755U) != 0) {
            throw std::runtime_error("loose directory chmod failed");
        }
        require_throws(
            [&] {
                anonsync::SyncLocalStatusSocketServer rejected(
                    loose / "status.sock", initial,
                    "loose-parent status socket");
            },
            "status parent must have exact mode 0700");

        const fs::path regular = temporary.path() / "occupied";
        {
            std::ofstream output(regular);
            output << "occupied";
        }
        require_throws(
            [&] {
                anonsync::SyncLocalStatusSocketServer rejected(
                    regular, initial, "occupied status socket");
            },
            "a non-socket path must not be removed");
        require(fs::is_regular_file(regular), "occupied file must remain intact");

        const fs::path disappearing_stop =
            temporary.path() / "disappearing-stop.sock";
        const std::string completed_stop_response =
            "{\"schema\":\"anonsync.local-stop.response.v1\","
            "\"command\":\"stop\",\"terminal_class\":\"completed\","
            "\"stop_mode\":\"drain\",\"first_request\":true,"
            "\"server_pid\":" + process_id + "}";
        with_raw_server_unlinked_before_response_or_throw(
            disappearing_stop, "stop\n", completed_stop_response + "\n",
            [&] {
                require(
                    anonsync::request_sync_local_status_stop_or_throw(
                        disappearing_stop) == completed_stop_response,
                    "completed stop must survive exact post-response socket disappearance");
            });
        require(
            !fs::exists(disappearing_stop),
            "completed stop disappearance test left a socket pathname");

        const fs::path malformed_disappearing_stop =
            temporary.path() / "malformed-disappearing-stop.sock";
        with_raw_server_unlinked_before_response_or_throw(
            malformed_disappearing_stop, "stop\n",
            "{\"pid\":" + process_id + "}\n",
            [&] {
                require_throws(
                    [&] {
                        (void)anonsync::request_sync_local_status_stop_or_throw(
                            malformed_disappearing_stop);
                    },
                    "socket disappearance must not bypass exact stop-response validation");
            });

        const fs::path disappearing_status =
            temporary.path() / "disappearing-status.sock";
        with_raw_server_unlinked_before_response_or_throw(
            disappearing_status, "status\n",
            "{\"pid\":" + process_id + "}\n",
            [&] {
                require_throws(
                    [&] {
                        (void)anonsync::query_sync_local_status_socket_or_throw(
                            disappearing_status);
                    },
                    "non-stop requests must retain final socket-path identity");
            });

        require_throws(
            [&] {
                (void)anonsync::query_sync_local_status_socket_or_throw(
                    temporary.path() / "missing.sock", 20U);
            },
            "querying a missing status socket must fail");
        require_throws(
            [&] {
                (void)anonsync::request_sync_local_status_stop_or_throw(
                    temporary.path() / "missing.sock", 20U);
            },
            "stopping through a missing local socket must fail");
        require_throws(
            [&] {
                (void)anonsync::request_sync_local_status_recheck_or_throw(
                    temporary.path() / "missing.sock", 20U);
            },
            "rechecking through a missing local socket must fail");
        require_throws(
            [&] {
                (void)anonsync::
                    request_sync_local_status_payload_quarantine_or_throw(
                        temporary.path() / "missing.sock",
                        quarantine_expected, quarantine_observed, 20U);
            },
            "quarantining through a missing local socket must fail");
        require_throws(
            [&] {
                (void)anonsync::
                    request_sync_local_status_payload_quarantine_release_or_throw(
                        temporary.path() / "missing.sock",
                        quarantine_expected, quarantine_observed, 20U);
            },
            "releasing quarantine through a missing local socket must fail");
        require_throws(
            [&] {
                (void)anonsync::
                    request_sync_local_status_payload_quarantine_or_throw(
                        socket_path, quarantine_expected,
                        quarantine_expected);
            },
            "quarantine client must reject an identical digest pair");
        require_throws(
            [&] {
                (void)anonsync::
                    request_sync_local_status_payload_quarantine_release_or_throw(
                        socket_path, quarantine_expected,
                        quarantine_expected);
            },
            "quarantine-release client must reject an identical digest pair");

        std::cout << "sync_local_status_socket_test: " << checks
                  << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync_local_status_socket_test failed after " << checks
                  << " checks: " << error.what() << '\n';
        return 1;
    }
}
