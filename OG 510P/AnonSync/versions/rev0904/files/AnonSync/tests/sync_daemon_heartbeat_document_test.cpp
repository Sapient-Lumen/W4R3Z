#include "anonsync_json_value.hpp"
#include "sync_daemon_heartbeat_document.hpp"

#include <cstdint>
#include <iostream>
#include <locale>
#include <stdexcept>
#include <string>
#include <string_view>

namespace {

using anonsync::Json;
using anonsync::SyncDaemonHeartbeatDocument;
using anonsync::SyncDaemonHeartbeatPublication;
using anonsync::SyncProcessIdentityMatchKind;
using anonsync::decode_sync_daemon_heartbeat_document_or_throw;
using anonsync::encode_sync_daemon_heartbeat_document_or_throw;
using anonsync::evaluate_sync_daemon_heartbeat_lifecycle_or_throw;
using anonsync::kSyncDaemonHeartbeatMaximumJsonBytes;

struct TestState final {
    std::uint64_t passed = 0;
    std::uint64_t failed = 0;

    void require(bool condition, const std::string& label) {
        if (condition) {
            ++passed;
        } else {
            ++failed;
            std::cerr << "FAIL: " << label << "\n";
        }
    }
};

Json object() {
    Json value;
    value.type = Json::Type::Object;
    return value;
}

Json string_value(std::string value) {
    Json result;
    result.type = Json::Type::String;
    result.s = std::move(value);
    return result;
}

Json bool_value(bool value) {
    Json result;
    result.type = Json::Type::Bool;
    result.b = value;
    return result;
}

Json number_value(double value) {
    Json result;
    result.type = Json::Type::Number;
    result.n = value;
    return result;
}

Json canonical_document(bool owner_required = true) {
    Json root = object();
    root.o["format"] =
        string_value("anonsync-sync-daemon-service-heartbeat-v2");
    root.o["revision_id"] = string_value("rev0840");
    root.o["operation"] = string_value("sync-daemon-service-heartbeat");
    root.o["service_instance_id"] = string_value(
        "sync-daemon-service-instance:v1:" + std::string(64, 'a'));
    root.o["service_restart_epoch"] = number_value(7);
    root.o["state"] = string_value("scheduler-pass-started");
    root.o["final"] = bool_value(false);
    root.o["reason"] = string_value("focused heartbeat corpus");
    root.o["heartbeat_epoch"] = number_value(100);
    root.o["stale_after_seconds"] = number_value(20);
    root.o["stale_at_epoch"] = number_value(120);
    root.o["process_id"] = number_value(41);
    Json process = object();
    process.o["format"] = string_value("linux-proc-starttime-v1");
    process.o["process_id"] = number_value(41);
    process.o["boot_id"] =
        string_value("01234567-89ab-cdef-0123-456789abcdef");
    process.o["start_token"] = string_value("987654");
    root.o["process_incarnation"] = std::move(process);
    root.o["checkpoint_path"] = string_value("/tmp/anonsync-checkpoint.db");
    root.o["session_id"] = string_value("session-alpha");
    root.o["daemon_id"] = string_value("daemon-alpha");
    root.o["worker_id"] = string_value("worker-alpha");
    root.o["service_lifecycle"] = object();
    root.o["lease"] = object();
    root.o["progress"] = object();

    Json owner = object();
    owner.o["required"] = bool_value(owner_required);
    owner.o["acquired"] = bool_value(owner_required);
    owner.o["released"] = bool_value(false);
    owner.o["reclaimed_expired"] = bool_value(false);
    owner.o["owner_lock_id"] = string_value(
        owner_required
            ? "sync-resume-daemon-owner-lock:v1:" + std::string(64, 'b')
            : "");
    owner.o["owner_lock_epoch"] = number_value(owner_required ? 3 : 0);
    owner.o["acquired_at_epoch"] = number_value(owner_required ? 90 : 0);
    owner.o["expires_at_epoch"] = number_value(owner_required ? 130 : 0);
    owner.o["released_at_epoch"] = number_value(0);
    root.o["owner_lock"] = std::move(owner);
    return root;
}

bool rejects_with(Json document, std::string_view fragment) {
    try {
        (void)decode_sync_daemon_heartbeat_document_or_throw(document);
        return false;
    } catch (const std::exception& error) {
        return std::string_view(error.what()).find(fragment) !=
               std::string_view::npos;
    }
}

void test_valid_documents(TestState& test) {
    const SyncDaemonHeartbeatDocument live =
        decode_sync_daemon_heartbeat_document_or_throw(canonical_document());
    test.require(live.state == "scheduler-pass-started" && !live.final &&
                     live.owner_lock.required && !live.owner_lock.released &&
                     live.stale_at_epoch == 120 &&
                     live.process_identity_present &&
                     live.process_identity.process_id == 41,
                 "canonical live owner heartbeat decodes");

    Json legacy = canonical_document();
    legacy.o["format"] =
        string_value("anonsync-sync-daemon-service-heartbeat-v1");
    legacy.o["revision_id"] = string_value("rev0741");
    legacy.o.erase("process_incarnation");
    const SyncDaemonHeartbeatDocument legacy_document =
        decode_sync_daemon_heartbeat_document_or_throw(legacy);
    test.require(!legacy_document.process_identity_present &&
                     legacy_document.process_id == 41,
                 "legacy v1 heartbeat remains decodable without promoting PID evidence");

    const SyncDaemonHeartbeatDocument lockless =
        decode_sync_daemon_heartbeat_document_or_throw(
            canonical_document(false));
    test.require(!lockless.owner_lock.required &&
                     lockless.owner_lock.owner_lock_id.empty(),
                 "canonical lockless heartbeat has no authority residue");

    Json released = canonical_document();
    released.o["state"] = string_value("completed");
    released.o["final"] = bool_value(true);
    released.o["heartbeat_epoch"] = number_value(125);
    released.o["stale_at_epoch"] = number_value(145);
    released.o["owner_lock"].o["released"] = bool_value(true);
    released.o["owner_lock"].o["released_at_epoch"] = number_value(125);
    const SyncDaemonHeartbeatDocument final =
        decode_sync_daemon_heartbeat_document_or_throw(released);
    test.require(final.final && final.owner_lock.released &&
                     final.owner_lock.released_at_epoch == final.heartbeat_epoch,
                 "final heartbeat binds its epoch to owner retirement");

    for (const std::string state : {
             "completed-owner-lock-retained",
             "failed-owner-lock-retained",
             "failed-exception-owner-lock-retained"}) {
        Json retained = canonical_document();
        retained.o["state"] = string_value(state);
        test.require(
            decode_sync_daemon_heartbeat_document_or_throw(retained).state ==
                state,
            "retained-owner state remains non-final: " + state);
    }
}

void test_shape_and_scalar_rejections(TestState& test) {
    Json non_object;
    test.require(rejects_with(non_object, "root must be an object"),
                 "non-object roots are rejected");

    Json missing_progress = canonical_document();
    missing_progress.o.erase("progress");
    test.require(rejects_with(missing_progress, "object field progress"),
                 "observational progress must retain object shape");

    Json wrong_lease = canonical_document();
    wrong_lease.o["lease"] = string_value("not-an-object");
    test.require(rejects_with(wrong_lease, "object field lease"),
                 "observational lease cannot impersonate an object");

    Json bad_revision = canonical_document();
    bad_revision.o["revision_id"] = string_value("rev741");
    test.require(rejects_with(bad_revision, "revision_id"),
                 "revision marker geometry is strict");

    Json bad_operation = canonical_document();
    bad_operation.o["operation"] = string_value("other-operation");
    test.require(rejects_with(bad_operation, "operation marker mismatch"),
                 "operation markers are exact");

    Json bad_service_instance = canonical_document();
    bad_service_instance.o["service_instance_id"] =
        string_value("sync-daemon-service-instance:v1:test");
    test.require(rejects_with(bad_service_instance, "not canonical"),
                 "service incarnation identifiers are digest-bound");

    Json fractional = canonical_document();
    fractional.o["heartbeat_epoch"] = number_value(100.5);
    test.require(rejects_with(fractional, "exact nonnegative integer"),
                 "fractional heartbeat epochs are rejected");

    Json beyond_exact = canonical_document();
    beyond_exact.o["heartbeat_epoch"] = number_value(9007199254740992.0);
    test.require(rejects_with(beyond_exact, "exact nonnegative integer"),
                 "integers beyond interoperable JSON precision are rejected");

    Json negative = canonical_document();
    negative.o["process_id"] = number_value(-1);
    test.require(rejects_with(negative, "must be nonnegative"),
                 "negative process identifiers are rejected");

    Json missing_process_identity = canonical_document();
    missing_process_identity.o.erase("process_incarnation");
    test.require(rejects_with(missing_process_identity,
                              "process_incarnation"),
                 "v2 heartbeat requires typed process-incarnation evidence");

    Json mismatched_process_identity = canonical_document();
    mismatched_process_identity.o["process_incarnation"].o["process_id"] =
        number_value(42);
    test.require(rejects_with(mismatched_process_identity,
                              "does not match process_incarnation"),
                 "top-level PID cannot diverge from typed process identity");

    Json malformed_boot = canonical_document();
    malformed_boot.o["process_incarnation"].o["boot_id"] =
        string_value("01234567-89AB-cdef-0123-456789abcdef");
    test.require(rejects_with(malformed_boot, "canonical lowercase UUID"),
                 "Linux boot identity is canonical lowercase UUID evidence");

    Json leading_zero_start = canonical_document();
    leading_zero_start.o["process_incarnation"].o["start_token"] =
        string_value("0987654");
    test.require(rejects_with(leading_zero_start,
                              "canonical positive decimal"),
                 "Linux start token rejects alternate decimal spellings");

    Json legacy_with_process_identity = canonical_document();
    legacy_with_process_identity.o["format"] =
        string_value("anonsync-sync-daemon-service-heartbeat-v1");
    legacy_with_process_identity.o["revision_id"] = string_value("rev0741");
    test.require(rejects_with(legacy_with_process_identity,
                              "v1 cannot contain process_incarnation"),
                 "legacy format cannot smuggle unvalidated v2 evidence");

    Json zero_restart = canonical_document();
    zero_restart.o["service_restart_epoch"] = number_value(0);
    test.require(rejects_with(zero_restart, "must be positive"),
                 "service restart epochs are positive");

    Json zero_heartbeat = canonical_document();
    zero_heartbeat.o["heartbeat_epoch"] = number_value(0);
    zero_heartbeat.o["stale_at_epoch"] = number_value(20);
    test.require(rejects_with(zero_heartbeat, "heartbeat_epoch must be positive"),
                 "heartbeat epochs are positive");

    Json bad_horizon = canonical_document();
    bad_horizon.o["stale_at_epoch"] = number_value(121);
    test.require(rejects_with(bad_horizon, "does not equal"),
                 "stale horizons are recomputed rather than trusted");

    Json zero_horizon = canonical_document();
    zero_horizon.o["stale_after_seconds"] = number_value(0);
    zero_horizon.o["stale_at_epoch"] = number_value(120);
    test.require(rejects_with(zero_horizon, "requires zero stale_at_epoch"),
                 "disabled stale policy cannot retain stale authority");

    Json overflow_horizon = canonical_document();
    overflow_horizon.o["heartbeat_epoch"] = number_value(9007199254740991.0);
    overflow_horizon.o["stale_after_seconds"] = number_value(1);
    overflow_horizon.o["stale_at_epoch"] = number_value(9007199254740991.0);
    test.require(rejects_with(overflow_horizon, "exceeds exact JSON range"),
                 "stale-horizon addition is overflow fenced");

    Json nul_path = canonical_document();
    nul_path.o["checkpoint_path"] =
        string_value(std::string("/tmp/prefix\0suffix", 18));
    test.require(rejects_with(nul_path, "embedded NUL"),
                 "checkpoint path identity cannot be truncated by C APIs");

    Json uppercase_id = canonical_document();
    uppercase_id.o["worker_id"] = string_value("Worker-alpha");
    test.require(rejects_with(uppercase_id, "portable sync ids"),
                 "authority identities use one portable alphabet");

    Json unknown_state = canonical_document();
    unknown_state.o["state"] = string_value("mystery-state");
    test.require(rejects_with(unknown_state, "not recognized"),
                 "unknown lifecycle states fail closed");

    Json final_flag_mismatch = canonical_document();
    final_flag_mismatch.o["final"] = bool_value(true);
    test.require(rejects_with(final_flag_mismatch, "contradicts its state"),
                 "final flags cannot upgrade non-final states");

    Json final_state_mismatch = canonical_document();
    final_state_mismatch.o["state"] = string_value("completed");
    test.require(rejects_with(final_state_mismatch,
                              "non-final state is not recognized"),
                 "final states cannot be published as non-final");
}

void test_owner_authority_rejections(TestState& test) {
    Json not_acquired = canonical_document();
    not_acquired.o["owner_lock"].o["acquired"] = bool_value(false);
    test.require(rejects_with(not_acquired, "was not acquired"),
                 "required owner authority must have been acquired");

    Json malformed_id = canonical_document();
    malformed_id.o["owner_lock"].o["owner_lock_id"] =
        string_value("sync-resume-daemon-owner-lock:v1:short");
    test.require(rejects_with(malformed_id, "not canonical"),
                 "owner generation identifiers are canonical digests");

    Json zero_epoch = canonical_document();
    zero_epoch.o["owner_lock"].o["owner_lock_epoch"] = number_value(0);
    test.require(rejects_with(zero_epoch, "epoch geometry is invalid"),
                 "owner generation epochs are positive");

    Json inverted_expiry = canonical_document();
    inverted_expiry.o["owner_lock"].o["expires_at_epoch"] = number_value(90);
    test.require(rejects_with(inverted_expiry, "epoch geometry is invalid"),
                 "owner expiry follows acquisition");

    Json predates_owner = canonical_document();
    predates_owner.o["heartbeat_epoch"] = number_value(89);
    predates_owner.o["stale_at_epoch"] = number_value(109);
    test.require(rejects_with(predates_owner, "predates its owner acquisition"),
                 "heartbeat evidence cannot predate its owner capability");

    Json release_without_final = canonical_document();
    release_without_final.o["owner_lock"].o["released"] = bool_value(true);
    release_without_final.o["owner_lock"].o["released_at_epoch"] =
        number_value(100);
    test.require(rejects_with(release_without_final,
                              "released owner generation must be final"),
                 "retired authority cannot remain a live heartbeat");

    Json final_without_release = canonical_document();
    final_without_release.o["state"] = string_value("failed");
    final_without_release.o["final"] = bool_value(true);
    test.require(rejects_with(final_without_release,
                              "remains unreleased"),
                 "final evidence requires durable owner retirement");

    Json final_wrong_release_epoch = canonical_document();
    final_wrong_release_epoch.o["state"] = string_value("failed");
    final_wrong_release_epoch.o["final"] = bool_value(true);
    final_wrong_release_epoch.o["heartbeat_epoch"] = number_value(110);
    final_wrong_release_epoch.o["stale_at_epoch"] = number_value(130);
    final_wrong_release_epoch.o["owner_lock"].o["released"] = bool_value(true);
    final_wrong_release_epoch.o["owner_lock"].o["released_at_epoch"] =
        number_value(109);
    test.require(rejects_with(final_wrong_release_epoch,
                              "final epoch does not equal owner release epoch"),
                 "finality is bound to the exact release transition");

    Json unreleased_with_epoch = canonical_document();
    unreleased_with_epoch.o["owner_lock"].o["released_at_epoch"] =
        number_value(99);
    test.require(rejects_with(unreleased_with_epoch,
                              "unreleased owner has a release epoch"),
                 "release epochs cannot exist without release state");

    Json lockless_residue = canonical_document(false);
    lockless_residue.o["owner_lock"].o["owner_lock_epoch"] = number_value(1);
    test.require(rejects_with(lockless_residue, "authority residue"),
                 "lockless documents contain no latent owner capability");
}

void test_lifecycle_policy(TestState& test) {
    const SyncDaemonHeartbeatDocument live =
        decode_sync_daemon_heartbeat_document_or_throw(canonical_document());

    const auto healthy = evaluate_sync_daemon_heartbeat_lifecycle_or_throw(
        live,
        true,
        100,
        true,
        SyncProcessIdentityMatchKind::Match,
        "exact");
    test.require(healthy.existing_fresh && !healthy.existing_stale &&
                     !healthy.service_start_allowed &&
                     !healthy.operator_attention_required,
                 "fresh exact process plus live owner is healthy but blocks a second start");

    const auto fresh_expired_owner =
        evaluate_sync_daemon_heartbeat_lifecycle_or_throw(
            live,
            true,
            100,
            false,
            SyncProcessIdentityMatchKind::Match,
            "exact");
    test.require(fresh_expired_owner.existing_fresh &&
                     fresh_expired_owner.operator_attention_required &&
                     fresh_expired_owner.reason.find("blocks service re-entry") !=
                         std::string::npos,
                 "fresh heartbeat remains a blocker after owner expiry");

    const auto fresh_recycled_pid =
        evaluate_sync_daemon_heartbeat_lifecycle_or_throw(
            live,
            true,
            100,
            true,
            SyncProcessIdentityMatchKind::Mismatch,
            "recycled");
    test.require(fresh_recycled_pid.operator_attention_required &&
                     fresh_recycled_pid.reason.find("no longer exact") !=
                         std::string::npos,
                 "process mismatch cannot bypass the stale horizon");

    const auto stale_live_owner =
        evaluate_sync_daemon_heartbeat_lifecycle_or_throw(
            live,
            true,
            120,
            true,
            SyncProcessIdentityMatchKind::Mismatch,
            "recycled");
    test.require(stale_live_owner.existing_stale &&
                     stale_live_owner.operator_attention_required &&
                     !stale_live_owner.service_start_allowed &&
                     stale_live_owner.reason.find("owner generation is still live") !=
                         std::string::npos,
                 "clock staleness cannot supersede live durable owner authority");

    const auto stale_live_process =
        evaluate_sync_daemon_heartbeat_lifecycle_or_throw(
            live,
            true,
            120,
            false,
            SyncProcessIdentityMatchKind::Match,
            "exact");
    test.require(stale_live_process.existing_stale &&
                     stale_live_process.operator_attention_required &&
                     !stale_live_process.service_start_allowed &&
                     stale_live_process.reason.find("exact process incarnation remains live") !=
                         std::string::npos,
                 "clock staleness cannot impersonate exact process death");

    for (const SyncProcessIdentityMatchKind process_kind : {
             SyncProcessIdentityMatchKind::Mismatch,
             SyncProcessIdentityMatchKind::NotRunning}) {
        const auto takeover =
            evaluate_sync_daemon_heartbeat_lifecycle_or_throw(
                live,
                true,
                120,
                false,
                process_kind,
                "prior process gone");
        test.require(takeover.existing_stale && takeover.service_start_allowed &&
                         takeover.reentry_from_stale_heartbeat &&
                         !takeover.operator_attention_required,
                     "stale plus expired owner plus absent or recycled process permits re-entry");
    }

    const auto indeterminate =
        evaluate_sync_daemon_heartbeat_lifecycle_or_throw(
            live,
            true,
            120,
            false,
            SyncProcessIdentityMatchKind::Indeterminate,
            "observation failed");
    test.require(indeterminate.operator_attention_required &&
                     !indeterminate.service_start_allowed &&
                     indeterminate.reason.find("could not be verified") !=
                         std::string::npos,
                 "indeterminate process observation fails closed");

    Json legacy_json = canonical_document();
    legacy_json.o["format"] =
        string_value("anonsync-sync-daemon-service-heartbeat-v1");
    legacy_json.o["revision_id"] = string_value("rev0741");
    legacy_json.o.erase("process_incarnation");
    const auto legacy = evaluate_sync_daemon_heartbeat_lifecycle_or_throw(
        decode_sync_daemon_heartbeat_document_or_throw(legacy_json),
        true,
        120,
        false,
        SyncProcessIdentityMatchKind::Invalid,
        "");
    test.require(legacy.operator_attention_required &&
                     !legacy.service_start_allowed &&
                     legacy.reason.find("only PID process evidence") !=
                         std::string::npos,
                 "legacy non-final PID-only evidence fails closed");

    Json final_json = canonical_document();
    final_json.o["state"] = string_value("completed");
    final_json.o["final"] = bool_value(true);
    final_json.o["heartbeat_epoch"] = number_value(125);
    final_json.o["stale_at_epoch"] = number_value(145);
    final_json.o["owner_lock"].o["released"] = bool_value(true);
    final_json.o["owner_lock"].o["released_at_epoch"] = number_value(125);
    const auto final = evaluate_sync_daemon_heartbeat_lifecycle_or_throw(
        decode_sync_daemon_heartbeat_document_or_throw(final_json),
        false,
        0,
        false,
        SyncProcessIdentityMatchKind::Indeterminate,
        "unavailable");
    test.require(final.service_start_allowed &&
                     !final.operator_attention_required &&
                     !final.reentry_from_stale_heartbeat,
                 "final owner-retirement evidence does not depend on live process observation");
}

SyncDaemonHeartbeatPublication canonical_publication() {
    SyncDaemonHeartbeatPublication publication;
    SyncDaemonHeartbeatDocument& document = publication.document;
    document.format = "anonsync-sync-daemon-service-heartbeat-v2";
    document.revision_id = "rev0840";
    document.operation = "sync-daemon-service-heartbeat";
    document.service_instance_id =
        "sync-daemon-service-instance:v1:" + std::string(64, 'c');
    document.service_restart_epoch = 7;
    document.state = "scheduler-pass-started";
    document.final = false;
    document.reason = "quoted \"reason\"\nline";
    document.heartbeat_epoch = 100;
    document.stale_after_seconds = 20;
    document.stale_at_epoch = 120;
    document.process_id = 41;
    document.process_identity_present = true;
    document.process_identity.format = "linux-proc-starttime-v1";
    document.process_identity.process_id = 41;
    document.process_identity.boot_id =
        "01234567-89ab-cdef-0123-456789abcdef";
    document.process_identity.start_token = "987654";
    document.checkpoint_path = "/tmp/anonsync-checkpoint.db";
    document.session_id = "session-alpha";
    document.daemon_id = "daemon-alpha";
    document.worker_id = "worker-alpha";
    document.owner_lock.required = true;
    document.owner_lock.acquired = true;
    document.owner_lock.owner_lock_id =
        "sync-resume-daemon-owner-lock:v1:" + std::string(64, 'd');
    document.owner_lock.owner_lock_epoch = 3;
    document.owner_lock.acquired_at_epoch = 90;
    document.owner_lock.expires_at_epoch = 130;

    publication.service_lifecycle.preflight_checked = true;
    publication.service_lifecycle.preflight_passed = true;
    publication.service_lifecycle.heartbeat_checked = true;
    publication.service_lifecycle.preflight_reason = "focused preflight";
    publication.lease.worker_lease_id = "lease-alpha";
    publication.lease.final_worker_lease_epoch = 93;
    publication.lease.next_worker_lease_epoch = 94;
    publication.lease.next_scheduler_now_epoch = 101;
    publication.progress.passes_attempted = 8;
    publication.progress.passes_completed = 7;
    publication.progress.mutating_passes = 3;
    publication.progress.idle_passes = 4;
    publication.progress.checkpoint_schema_version = "v19";
    publication.progress.workorder_rows_claimed = 5;
    publication.progress.workorder_rows_completed = 4;
    publication.progress.chunks_written = 6;
    publication.progress.bytes_written = 7000;
    return publication;
}

class GroupedNumberPunctuation final : public std::numpunct<char> {
protected:
    [[nodiscard]] char do_thousands_sep() const override { return '_'; }
    [[nodiscard]] std::string do_grouping() const override { return "\3"; }
};

class ScopedGlobalLocale final {
public:
    explicit ScopedGlobalLocale(const std::locale& replacement)
        : previous_(std::locale::global(replacement)) {}

    ScopedGlobalLocale(const ScopedGlobalLocale&) = delete;
    ScopedGlobalLocale& operator=(const ScopedGlobalLocale&) = delete;

    ~ScopedGlobalLocale() { std::locale::global(previous_); }

private:
    std::locale previous_;
};

bool encode_rejects_with(const SyncDaemonHeartbeatPublication& publication,
                         std::string_view fragment) {
    try {
        (void)encode_sync_daemon_heartbeat_document_or_throw(publication);
        return false;
    } catch (const std::exception& error) {
        return std::string_view(error.what()).find(fragment) !=
               std::string_view::npos;
    }
}

void test_serializer(TestState& test) {
    SyncDaemonHeartbeatPublication publication = canonical_publication();
    const std::string live =
        encode_sync_daemon_heartbeat_document_or_throw(publication);
    test.require(live.find(
                         "\"format\": \"anonsync-sync-daemon-service-heartbeat-v2\"") !=
                         std::string::npos &&
                     live.find("\"revision_id\": \"rev0840\"") !=
                         std::string::npos &&
                     live.find("\"process_incarnation\": {") !=
                         std::string::npos &&
                     live.find("\"start_token\": \"987654\"") !=
                         std::string::npos &&
                     live.find("\"state\": \"scheduler-pass-started\"") !=
                         std::string::npos &&
                     live.find("quoted \\\"reason\\\"\\nline") !=
                         std::string::npos &&
                     live.size() <= kSyncDaemonHeartbeatMaximumJsonBytes,
                 "serializer emits the exact frozen v2 publication within the reader bound");

    publication.document.state = "completed";
    publication.document.final = true;
    publication.document.reason = "owner generation retired";
    publication.document.heartbeat_epoch = 125;
    publication.document.stale_at_epoch = 145;
    publication.document.owner_lock.released = true;
    publication.document.owner_lock.released_at_epoch = 125;
    const std::string final =
        encode_sync_daemon_heartbeat_document_or_throw(publication);
    test.require(final.find("\"released\": true") != std::string::npos &&
                     final.find("\"final\": true") != std::string::npos,
                 "serializer emits finality only with owner release evidence");

    publication.document.owner_lock.released = false;
    publication.document.owner_lock.released_at_epoch = 0;
    test.require(encode_rejects_with(publication, "remains unreleased"),
                 "serializer cannot mint final evidence for a retained owner");

    publication = canonical_publication();
    publication.progress.bytes_written = 9007199254740992ULL;
    test.require(encode_rejects_with(publication, "bytes_written"),
                 "serializer rejects observational integers JSON cannot preserve");

    publication = canonical_publication();
    publication.document.format =
        "anonsync-sync-daemon-service-heartbeat-v1";
    publication.document.process_identity_present = false;
    publication.document.process_identity = {};
    test.require(encode_rejects_with(publication, "current v2 format"),
                 "publication codec cannot mint legacy PID-only evidence");

    publication = canonical_publication();
    publication.document.reason.assign(kSyncDaemonHeartbeatMaximumJsonBytes,
                                       'x');
    test.require(encode_rejects_with(publication, "reader byte bound"),
                 "publisher cannot emit a document its bounded reader rejects");
}

void test_locale_independence(TestState& test) {
    const std::locale grouped(std::locale::classic(),
                              new GroupedNumberPunctuation);
    const ScopedGlobalLocale restore_locale(grouped);
    const std::string encoded =
        encode_sync_daemon_heartbeat_document_or_throw(
            canonical_publication());
    test.require(encoded.find("7_000") == std::string::npos &&
                     encoded.find("\"bytes_written\": 7000") !=
                         std::string::npos,
                 "JSON integer spelling is independent of the process-global locale");
}

}  // namespace

int main() {
    try {
        TestState test;
        test_valid_documents(test);
        test_shape_and_scalar_rejections(test);
        test_owner_authority_rejections(test);
        test_lifecycle_policy(test);
        test_serializer(test);
        test_locale_independence(test);
        std::cout << "sync daemon heartbeat document tests passed: "
                  << test.passed << "/" << (test.passed + test.failed) << "\n";
        return test.failed == 0 ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << "FATAL: " << error.what() << "\n";
        return 2;
    }
}
