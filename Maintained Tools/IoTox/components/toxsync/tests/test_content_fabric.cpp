#include "test_harness.hpp"
#include "test_support.hpp"

#include "toxsync/content_fabric.hpp"
#include "toxsync/content_store.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>

namespace {

toxsync::PagedContentStoreOptions paged_options() {
    toxsync::PagedContentStoreOptions options;
    options.chunking = {
        .min_bytes = 4096U,
        .average_bytes = 16384U,
        .max_bytes = 65536U,
    };
    options.entries_per_page = 8U;
    options.io_buffer_bytes = 32768U;
    options.root_buffer_bytes = 4096U;
    options.fsync_on_commit = false;
    return options;
}

toxsync::ContentStoreOptions flat_options() {
    toxsync::ContentStoreOptions options;
    options.chunking = {
        .min_bytes = 4096U,
        .average_bytes = 16384U,
        .max_bytes = 65536U,
    };
    options.io_buffer_bytes = 32768U;
    options.manifest_buffer_bytes = 4096U;
    options.fsync_on_commit = false;
    return options;
}

toxsync::ContentFabricConfig fabric_config() {
    toxsync::ContentFabricConfig config;
    config.chunk_window_objects = 13U;
    config.page_window_objects = 2U;
    config.scheduler.maximum_peers = 4U;
    config.scheduler.maximum_window_chunks = 13U;
    config.scheduler.maximum_lanes_per_peer = 2U;
    config.scheduler.maximum_attempts_per_chunk = 4U;
    config.object_io_buffer_bytes = 8192U;
    config.manifest_buffer_bytes = 320U;
    config.fsync_on_commit = false;
    return config;
}

void copy_remote_object(const std::filesystem::path& remote_store,
                        const toxsync::ContentFabricAssignment& assignment) {
    const auto source = toxsync::content_store_path(
        remote_store, assignment.object);
    std::filesystem::create_directories(
        assignment.staging_path.parent_path());
    std::filesystem::copy_file(
        source, assignment.staging_path,
        std::filesystem::copy_options::none);
}

void drive_all(toxsync::ContentFabricSession& session,
               const std::filesystem::path& remote_store,
               std::uint64_t& request_id) {
    while (!session.complete()) {
        session.update_peer_complete_window({
            .peer_id = 10U,
            .maximum_lanes = 2U,
            .useful_bytes_per_second = 8U * 1024U * 1024U,
        });
        session.update_peer_complete_window({
            .peer_id = 20U,
            .maximum_lanes = 2U,
            .useful_bytes_per_second = 4U * 1024U * 1024U,
        });
        for (;;) {
            const auto assignment = session.next(request_id++);
            if (!assignment) break;
            copy_remote_object(remote_store, *assignment);
            const auto committed = session.commit(assignment->request_id);
            REQUIRE(committed.object == assignment->object);
        }
        REQUIRE(session.ready_to_advance());
        REQUIRE(session.advance_window());
    }
}

} // namespace

TOXSYNC_TEST(content_fabric_bootstraps_pages_then_swarms_chunks_and_reconstructs) {
    test::TempDir temp;
    const auto artifact = test::pattern(
        3U * 1024U * 1024U + 471U, 0xfab1cU);
    test::write_file(temp.path() / "artifact", artifact);
    toxsync::ContentStoreWorkspace build_workspace;
    const auto built = toxsync::build_paged_content_store(
        temp.path() / "artifact", temp.path() / "remote-store",
        temp.path() / "remote-root.txp", build_workspace, paged_options());
    std::filesystem::copy_file(
        temp.path() / "remote-root.txp", temp.path() / "local-root.txp");

    toxsync::ContentFabricSession session(
        temp.path() / "local-root.txp", temp.path() / "local-store",
        temp.path() / "incoming", fabric_config());
    session.prepare();
    REQUIRE(session.phase() == toxsync::ContentFabricPhase::manifest_pages);
    REQUIRE(session.window().object_count <= 2U);
    const auto initial_resident = session.resident_bytes();

    std::uint64_t request_id{1U};
    drive_all(session, temp.path() / "remote-store", request_id);
    REQUIRE(session.complete());
    const auto stats = session.stats();
    REQUIRE(stats.manifest_pages == built.metadata.page_count);
    REQUIRE(stats.manifest_chunks == built.metadata.chunk_count);
    REQUIRE(stats.page_objects_fetched == built.metadata.page_count);
    REQUIRE(stats.chunk_objects_fetched == built.metadata.chunk_count);
    REQUIRE(stats.page_objects_reused == 0U);
    REQUIRE(stats.chunk_objects_reused == 0U);
    REQUIRE(stats.hard_link_ingests ==
            stats.page_objects_fetched + stats.chunk_objects_fetched);
    REQUIRE(session.resident_bytes() >= initial_resident);
    REQUIRE(session.resident_bytes() < 512U * 1024U);

    toxsync::ContentReconstructOptions reconstruct;
    reconstruct.io_buffer_bytes = 8192U;
    reconstruct.manifest_buffer_bytes = 320U;
    reconstruct.fsync_on_commit = false;
    const auto rebuilt = session.reconstruct(
        temp.path() / "rebuilt", reconstruct);
    REQUIRE(rebuilt.metadata.artifact_digest == built.metadata.artifact_digest);
    REQUIRE(test::read_file(temp.path() / "rebuilt") == artifact);
}

TOXSYNC_TEST(content_fabric_restart_rediscovers_committed_objects_without_progress_journal) {
    test::TempDir temp;
    const auto artifact = test::pattern(
        2U * 1024U * 1024U + 99U, 0x5155U);
    test::write_file(temp.path() / "artifact", artifact);
    toxsync::ContentStoreWorkspace build_workspace;
    const auto built = toxsync::build_content_store(
        temp.path() / "artifact", temp.path() / "remote-store",
        temp.path() / "remote.txc", build_workspace, flat_options());
    std::filesystem::copy_file(
        temp.path() / "remote.txc", temp.path() / "local.txc");

    std::uint64_t request_id{100U};
    std::uint64_t first_wave{};
    {
        toxsync::ContentFabricSession first(
            temp.path() / "local.txc", temp.path() / "local-store",
            temp.path() / "incoming-a", fabric_config());
        first.prepare();
        REQUIRE(first.phase() == toxsync::ContentFabricPhase::artifact_chunks);
        first.update_peer_complete_window({
            .peer_id = 1U,
            .maximum_lanes = 2U,
            .useful_bytes_per_second = 1U,
        });
        for (std::size_t count = 0U; count < 5U; ++count) {
            const auto assignment = first.next(request_id++);
            REQUIRE(assignment.has_value());
            copy_remote_object(temp.path() / "remote-store", *assignment);
            (void)first.commit(assignment->request_id);
            ++first_wave;
        }
        REQUIRE(!first.complete());
    }

    toxsync::ContentFabricSession resumed(
        temp.path() / "local.txc", temp.path() / "local-store",
        temp.path() / "incoming-b", fabric_config());
    resumed.prepare();
    REQUIRE(resumed.stats().chunk_objects_reused == first_wave);
    drive_all(resumed, temp.path() / "remote-store", request_id);
    REQUIRE(resumed.complete());
    REQUIRE(resumed.stats().chunk_objects_reused >= first_wave);
    REQUIRE(resumed.stats().chunk_objects_fetched +
                resumed.stats().chunk_objects_reused >=
            built.metadata.chunk_count);

    toxsync::ContentReconstructOptions reconstruct;
    reconstruct.fsync_on_commit = false;
    (void)resumed.reconstruct(temp.path() / "rebuilt", reconstruct);
    REQUIRE(test::read_file(temp.path() / "rebuilt") == artifact);
}

TOXSYNC_TEST(content_fabric_bad_object_removes_only_that_source_for_retry) {
    test::TempDir temp;
    const auto artifact = test::pattern(512U * 1024U + 7U, 0xdeadU);
    test::write_file(temp.path() / "artifact", artifact);
    toxsync::ContentStoreWorkspace workspace;
    (void)toxsync::build_content_store(
        temp.path() / "artifact", temp.path() / "remote-store",
        temp.path() / "remote.txc", workspace, flat_options());
    std::filesystem::copy_file(
        temp.path() / "remote.txc", temp.path() / "local.txc");

    toxsync::ContentFabricSession session(
        temp.path() / "local.txc", temp.path() / "local-store",
        temp.path() / "incoming", fabric_config());
    session.prepare();
    session.update_peer_complete_window({.peer_id = 1U, .maximum_lanes = 1U});
    session.update_peer_complete_window({.peer_id = 2U, .maximum_lanes = 1U});
    const auto first = session.next(1U);
    REQUIRE(first.has_value());
    auto corrupt = test::read_file(toxsync::content_store_path(
        temp.path() / "remote-store", first->object));
    corrupt.front() ^= std::byte{0xff};
    std::filesystem::create_directories(first->staging_path.parent_path());
    test::write_file(first->staging_path, corrupt);
    REQUIRE_THROWS(session.commit(first->request_id));
    REQUIRE(session.stats().verification_failures == 1U);
    REQUIRE(session.stats().request_failures == 1U);

    const auto retry = session.next(2U);
    REQUIRE(retry.has_value());
    REQUIRE(retry->logical_index == first->logical_index);
    REQUIRE(retry->peer_id != first->peer_id);
    copy_remote_object(temp.path() / "remote-store", *retry);
    (void)session.commit(retry->request_id);
}
