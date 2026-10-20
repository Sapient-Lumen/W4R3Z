#include "toxsync/content_fabric.hpp"

#include <algorithm>
#include <cstring>
#include <limits>
#include <stdexcept>
#include <utility>

namespace toxsync {
namespace {

[[nodiscard]] MultiSourceSchedulerLimits scheduler_limits(
    const ContentFabricConfig& config) {
    if (config.chunk_window_objects == 0U ||
        config.page_window_objects == 0U ||
        config.object_io_buffer_bytes == 0U ||
        config.manifest_buffer_bytes == 0U) {
        throw std::invalid_argument("content-fabric bounds must be nonzero");
    }
    const auto required = std::max(config.chunk_window_objects,
                                   config.page_window_objects);
    if (required > std::numeric_limits<std::uint32_t>::max() ||
        config.scheduler.maximum_window_chunks < required) {
        throw std::invalid_argument(
            "content-fabric scheduler window is smaller than configured windows");
    }
    auto limits = config.scheduler;
    limits.window_storage = MultiSourceWindowStorage::borrowed;
    return limits;
}

[[nodiscard]] std::filesystem::path staging_path_for(
    const std::filesystem::path& root,
    const Digest256& digest,
    std::uint64_t request_id) {
    const auto hex = digest.hex();
    return root / "objects" / hex.substr(0U, 2U) /
           (hex.substr(2U) + "." + std::to_string(request_id) + ".part");
}

[[nodiscard]] std::uint64_t checked_add(std::uint64_t left,
                                        std::uint64_t right) {
    if (left > std::numeric_limits<std::uint64_t>::max() - right) {
        throw std::overflow_error("content-fabric byte counter overflows");
    }
    return left + right;
}

} // namespace

class ContentFabricSession::Impl final {
public:
    Impl(std::filesystem::path manifest,
         std::filesystem::path store,
         std::filesystem::path staging,
         ContentFabricConfig requested)
        : manifest_path(std::move(manifest)),
          store_root(std::move(store)),
          staging_root(std::move(staging)),
          config(std::move(requested)),
          scheduler(scheduler_limits(config)) {
        maximum_window = std::max(config.chunk_window_objects,
                                  config.page_window_objects);
        window_refs = std::make_unique_for_overwrite<ContentChunkRef[]>(
            maximum_window);
        page_refs = std::make_unique_for_overwrite<PagedContentPageRef[]>(
            config.page_window_objects);
        availability_bytes = (maximum_window + 7U) / 8U;
        availability_scratch = std::make_unique_for_overwrite<std::byte[]>(
            availability_bytes);
    }

    void prepare() {
        if (phase != ContentFabricPhase::unprepared) {
            throw std::logic_error("content-fabric session is already prepared");
        }
        if (manifest_path.empty() || store_root.empty() || staging_root.empty()) {
            throw std::invalid_argument("content-fabric paths must be nonempty");
        }
        format = detect_content_manifest_format(manifest_path);
        if (format == ContentManifestFormat::paged_v2) {
            load_page_window(0U);
            if (manifest_pages == 0U) {
                phase = ContentFabricPhase::complete;
                current_window = {};
            }
        } else {
            load_chunk_window(0U, 0U, false);
            if (manifest_chunks == 0U) {
                phase = ContentFabricPhase::complete;
                current_window = {};
            }
        }
    }

    void load_page_window(std::uint64_t first_page) {
        PagedContentPageWindowOptions options;
        options.verify_root_manifest = config.verify_manifest && !manifest_verified;
        options.root_buffer_bytes = config.manifest_buffer_bytes;
        options.limits = config.limits;
        auto output = std::span<PagedContentPageRef>(
            page_refs.get(), config.page_window_objects);
        const auto loaded = read_paged_content_page_window(
            manifest_path, first_page, output, workspace, options);
        manifest_verified = manifest_verified || options.verify_root_manifest;
        manifest_pages = loaded.metadata.page_count;
        manifest_chunks = loaded.metadata.chunk_count;
        artifact_size = loaded.metadata.artifact_size;
        artifact_digest = loaded.metadata.artifact_digest;
        manifest_digest = loaded.metadata.root_digest;
        page_next = loaded.next_page;
        if (loaded.pages_loaded == 0U) {
            current_window = {};
            return;
        }
        std::uint64_t fake_offset{};
        for (std::size_t local = 0U; local < loaded.pages_loaded; ++local) {
            const auto& page = page_refs[local];
            window_refs[local] = ContentChunkRef{
                .index = page.page_index,
                .artifact_offset = fake_offset,
                .length = page.encoded_size,
                .digest = page.digest,
            };
            fake_offset = checked_add(fake_offset, page.encoded_size);
        }
        phase = ContentFabricPhase::manifest_pages;
        current_window = ContentFabricWindow{
            .kind = ContentFabricObjectKind::manifest_page,
            .first_object = first_page,
            .object_count = loaded.pages_loaded,
            .bytes_described = fake_offset,
        };
        scheduler.set_window(
            first_page,
            std::span<const ContentChunkRef>(window_refs.get(), loaded.pages_loaded));
        mark_local_objects(ContentFabricObjectKind::manifest_page);
    }

    void load_chunk_window(std::uint64_t first_chunk,
                           std::uint64_t offset_hint,
                           bool have_offset_hint) {
        ContentChunkWindowOptions options;
        options.artifact_offset_hint_valid = have_offset_hint;
        options.artifact_offset_hint = offset_hint;
        options.verify_manifest = config.verify_manifest && !manifest_verified;
        options.verify_page_digests = config.verify_page_digests;
        options.manifest_buffer_bytes = config.manifest_buffer_bytes;
        options.limits = config.limits;
        auto output = std::span<ContentChunkRef>(
            window_refs.get(), config.chunk_window_objects);
        const auto loaded = read_content_chunk_window(
            manifest_path, store_root, first_chunk, output, workspace, options);
        manifest_verified = manifest_verified || options.verify_manifest;
        format = loaded.format;
        manifest_chunks = loaded.manifest_chunks;
        artifact_size = loaded.artifact_size;
        artifact_digest = loaded.artifact_digest;
        if (loaded.manifest_digest != Digest256{}) {
            manifest_digest = loaded.manifest_digest;
        }
        chunk_next = loaded.next_chunk;
        chunk_next_offset = loaded.next_artifact_offset;
        if (loaded.chunks_loaded == 0U) {
            current_window = {};
            return;
        }
        phase = ContentFabricPhase::artifact_chunks;
        current_window = ContentFabricWindow{
            .kind = ContentFabricObjectKind::artifact_chunk,
            .first_object = first_chunk,
            .object_count = loaded.chunks_loaded,
            .bytes_described = loaded.bytes_described,
        };
        scheduler.set_window(
            first_chunk,
            std::span<const ContentChunkRef>(window_refs.get(), loaded.chunks_loaded));
        mark_local_objects(ContentFabricObjectKind::artifact_chunk);
    }

    void mark_local_objects(ContentFabricObjectKind kind) {
        for (std::size_t local = 0U; local < current_window.object_count; ++local) {
            const auto& object = window_refs[local];
            if (!content_object_available(
                    store_root, object.digest, object.length,
                    config.verify_local_objects, &workspace,
                    config.object_io_buffer_bytes)) {
                continue;
            }
            if (!scheduler.mark_complete(object.index)) {
                throw std::runtime_error(
                    "content-fabric could not mark local object complete");
            }
            if (kind == ContentFabricObjectKind::manifest_page) {
                ++page_objects_reused;
                page_bytes_reused += object.length;
            } else {
                ++chunk_objects_reused;
                chunk_bytes_reused += object.length;
            }
        }
    }

    [[nodiscard]] ContentFabricAssignment convert(
        const ChunkAssignment& assignment) const {
        const auto kind = current_window.kind;
        const auto staging = staging_path_for(
            staging_root, assignment.chunk.digest, assignment.request_id);
        return ContentFabricAssignment{
            .request_id = assignment.request_id,
            .peer_id = assignment.peer_id,
            .kind = kind,
            .object = assignment.chunk.digest,
            .object_size = assignment.chunk.length,
            .logical_index = assignment.chunk.index,
            .artifact_offset =
                kind == ContentFabricObjectKind::artifact_chunk
                    ? assignment.chunk.artifact_offset
                    : 0U,
            .attempt = assignment.attempt,
            .staging_path = staging,
        };
    }

    [[nodiscard]] std::optional<ContentFabricAssignment> next(
        std::uint64_t request_id) {
        if (phase == ContentFabricPhase::unprepared) {
            throw std::logic_error("content-fabric session is not prepared");
        }
        if (phase == ContentFabricPhase::complete) return std::nullopt;
        const auto scheduled = scheduler.next(request_id);
        if (!scheduled) return std::nullopt;
        auto result = convert(*scheduled);
        std::error_code error;
        if (std::filesystem::exists(result.staging_path, error) || error) {
            if (scheduler.fail(request_id,
                               SourceFailureDisposition::retry_source)) {
                ++request_failures;
            }
            throw std::runtime_error(
                "content-fabric staging path already exists or cannot be inspected");
        }
        ++requests_issued;
        return result;
    }

    [[nodiscard]] std::optional<ContentFabricAssignment> assignment(
        std::uint64_t request_id) const {
        const auto scheduled = scheduler.assignment(request_id);
        if (!scheduled) return std::nullopt;
        return convert(*scheduled);
    }

    [[nodiscard]] ContentFabricCommitStats commit(
        std::uint64_t request_id,
        const std::filesystem::path& supplied_path,
        bool source_preverified) {
        const auto current = assignment(request_id);
        if (!current) {
            throw std::invalid_argument(
                "content-fabric request is not currently in flight");
        }
        const auto& source = supplied_path.empty()
            ? current->staging_path
            : supplied_path;
        ContentObjectInstallOptions options;
        options.io_buffer_bytes = config.object_io_buffer_bytes;
        options.fsync_on_commit = config.fsync_on_commit;
        options.verify_existing_object = config.verify_local_objects;
        options.consume_source = true;
        options.prefer_hard_link = config.prefer_hard_link_ingest;
        options.source_preverified = source_preverified;
        ContentObjectInstallStats installed;
        try {
            installed = install_content_object(
                source, store_root, current->object, current->object_size,
                workspace, options);
        } catch (...) {
            ++verification_failures;
            if (scheduler.fail(
                    request_id,
                    SourceFailureDisposition::remove_source_for_chunk)) {
                ++request_failures;
            }
            throw;
        }
        if (!scheduler.complete(request_id)) {
            throw std::runtime_error(
                "content-fabric scheduler lost completed request");
        }
        switch (installed.method) {
            case ContentObjectInstallMethod::moved_by_hard_link:
                ++hard_link_ingests;
                break;
            case ContentObjectInstallMethod::copied:
                ++copied_ingests;
                break;
            case ContentObjectInstallMethod::reused_existing:
                ++existing_ingests;
                break;
        }
        if (current->kind == ContentFabricObjectKind::manifest_page) {
            ++page_objects_fetched;
            page_bytes_fetched += current->object_size;
        } else {
            ++chunk_objects_fetched;
            chunk_bytes_fetched += current->object_size;
        }
        return ContentFabricCommitStats{
            .kind = current->kind,
            .logical_index = current->logical_index,
            .object = current->object,
            .install = installed,
        };
    }

    [[nodiscard]] bool ready_to_advance() const noexcept {
        if (phase == ContentFabricPhase::complete) return true;
        if (phase == ContentFabricPhase::unprepared) return false;
        const auto current = scheduler.stats();
        return current.window_chunks != 0U &&
               current.completed_chunks == current.window_chunks &&
               current.pending_chunks == 0U &&
               current.in_flight_chunks == 0U &&
               current.failed_chunks == 0U;
    }

    [[nodiscard]] bool advance_window() {
        if (phase == ContentFabricPhase::unprepared) {
            throw std::logic_error("content-fabric session is not prepared");
        }
        if (phase == ContentFabricPhase::complete) return true;
        const auto current = scheduler.stats();
        if (current.failed_chunks != 0U) {
            throw std::runtime_error(
                "content-fabric window contains terminally failed objects");
        }
        if (!ready_to_advance()) return false;
        ++windows_completed;
        if (phase == ContentFabricPhase::manifest_pages) {
            if (page_next < manifest_pages) {
                load_page_window(page_next);
                return true;
            }
            if (manifest_chunks == 0U) {
                phase = ContentFabricPhase::complete;
                scheduler.clear();
                current_window = {};
                return true;
            }
            load_chunk_window(0U, 0U, false);
            return true;
        }
        if (chunk_next < manifest_chunks) {
            load_chunk_window(chunk_next, chunk_next_offset, true);
            return true;
        }
        phase = ContentFabricPhase::complete;
        scheduler.clear();
        current_window = {};
        return true;
    }

    [[nodiscard]] std::size_t resident_bytes() const noexcept {
        return sizeof(Impl) + maximum_window * sizeof(ContentChunkRef) +
               config.page_window_objects * sizeof(PagedContentPageRef) +
               availability_bytes + scheduler.resident_bytes() +
               workspace.resident_bytes();
    }

    std::filesystem::path manifest_path;
    std::filesystem::path store_root;
    std::filesystem::path staging_root;
    ContentFabricConfig config;
    ContentManifestFormat format{ContentManifestFormat::flat_v1};
    ContentFabricPhase phase{ContentFabricPhase::unprepared};
    ContentFabricWindow current_window{};
    MultiSourceScheduler scheduler;
    ContentStoreWorkspace workspace;
    std::unique_ptr<ContentChunkRef[]> window_refs;
    std::unique_ptr<PagedContentPageRef[]> page_refs;
    std::unique_ptr<std::byte[]> availability_scratch;
    std::size_t maximum_window{};
    std::size_t availability_bytes{};
    bool manifest_verified{};
    std::uint64_t artifact_size{};
    std::uint64_t manifest_chunks{};
    std::uint64_t manifest_pages{};
    Digest256 artifact_digest{};
    Digest256 manifest_digest{};
    std::uint64_t page_next{};
    std::uint64_t chunk_next{};
    std::uint64_t chunk_next_offset{};
    std::uint64_t windows_completed{};
    std::uint64_t page_objects_reused{};
    std::uint64_t page_objects_fetched{};
    std::uint64_t page_bytes_reused{};
    std::uint64_t page_bytes_fetched{};
    std::uint64_t chunk_objects_reused{};
    std::uint64_t chunk_objects_fetched{};
    std::uint64_t chunk_bytes_reused{};
    std::uint64_t chunk_bytes_fetched{};
    std::uint64_t requests_issued{};
    std::uint64_t request_failures{};
    std::uint64_t verification_failures{};
    std::uint64_t hard_link_ingests{};
    std::uint64_t copied_ingests{};
    std::uint64_t existing_ingests{};
};

ContentFabricSession::ContentFabricSession(
    std::filesystem::path manifest_path,
    std::filesystem::path store_root,
    std::filesystem::path staging_root,
    ContentFabricConfig config)
    : impl_(std::make_unique<Impl>(
          std::move(manifest_path), std::move(store_root),
          std::move(staging_root), std::move(config))) {}

ContentFabricSession::~ContentFabricSession() = default;
ContentFabricSession::ContentFabricSession(ContentFabricSession&&) noexcept = default;
ContentFabricSession& ContentFabricSession::operator=(
    ContentFabricSession&&) noexcept = default;

void ContentFabricSession::prepare() { impl_->prepare(); }

void ContentFabricSession::update_peer(
    const SourcePeerUpdate& peer,
    std::uint64_t first_object,
    std::uint32_t bit_count,
    std::span<const std::byte> availability_bits) {
    if (impl_->phase == ContentFabricPhase::unprepared ||
        impl_->phase == ContentFabricPhase::complete) {
        throw std::logic_error(
            "content-fabric has no active window for peer availability");
    }
    impl_->scheduler.update_peer(
        peer, first_object, bit_count, availability_bits);
}

void ContentFabricSession::update_peer_complete_window(
    const SourcePeerUpdate& peer) {
    if (impl_->phase == ContentFabricPhase::unprepared ||
        impl_->phase == ContentFabricPhase::complete ||
        impl_->current_window.object_count == 0U) {
        throw std::logic_error(
            "content-fabric has no active window for peer availability");
    }
    const auto bytes = (static_cast<std::size_t>(
        impl_->current_window.object_count) + 7U) / 8U;
    std::memset(impl_->availability_scratch.get(), 0xff, bytes);
    const auto remainder = static_cast<unsigned>(
        impl_->current_window.object_count % 8U);
    if (remainder != 0U) {
        impl_->availability_scratch[bytes - 1U] = static_cast<std::byte>(
            (1U << remainder) - 1U);
    }
    impl_->scheduler.update_peer(
        peer, impl_->current_window.first_object,
        impl_->current_window.object_count,
        std::span<const std::byte>(impl_->availability_scratch.get(), bytes));
}

void ContentFabricSession::remove_peer(SourcePeerId peer_id) noexcept {
    impl_->scheduler.remove_peer(peer_id);
}

std::optional<ContentFabricAssignment> ContentFabricSession::next(
    std::uint64_t request_id) {
    return impl_->next(request_id);
}

std::optional<ContentFabricAssignment> ContentFabricSession::assignment(
    std::uint64_t request_id) const {
    return impl_->assignment(request_id);
}

ContentFabricCommitStats ContentFabricSession::commit(
    std::uint64_t request_id,
    const std::filesystem::path& completed_staging_path,
    bool source_preverified) {
    return impl_->commit(
        request_id, completed_staging_path, source_preverified);
}

bool ContentFabricSession::fail(
    std::uint64_t request_id,
    SourceFailureDisposition disposition) noexcept {
    const bool failed = impl_->scheduler.fail(request_id, disposition);
    if (failed) ++impl_->request_failures;
    return failed;
}

bool ContentFabricSession::ready_to_advance() const noexcept {
    return impl_->ready_to_advance();
}

bool ContentFabricSession::advance_window() {
    return impl_->advance_window();
}

bool ContentFabricSession::complete() const noexcept {
    return impl_->phase == ContentFabricPhase::complete;
}

ContentReconstructStats ContentFabricSession::reconstruct(
    const std::filesystem::path& output_path,
    const ContentReconstructOptions& options) {
    if (!complete()) {
        throw std::logic_error(
            "content-fabric reconstruction requires complete content");
    }
    if (impl_->format == ContentManifestFormat::paged_v2) {
        return reconstruct_paged_content_manifest(
            impl_->manifest_path, impl_->store_root, output_path,
            impl_->workspace, options);
    }
    return reconstruct_content_manifest(
        impl_->manifest_path, impl_->store_root, output_path,
        impl_->workspace, options);
}

ContentFabricPhase ContentFabricSession::phase() const noexcept {
    return impl_->phase;
}

ContentManifestFormat ContentFabricSession::format() const noexcept {
    return impl_->format;
}

ContentFabricWindow ContentFabricSession::window() const noexcept {
    return impl_->current_window;
}

ContentFabricStats ContentFabricSession::stats() const noexcept {
    ContentFabricStats result;
    result.phase = impl_->phase;
    result.format = impl_->format;
    result.artifact_size = impl_->artifact_size;
    result.manifest_chunks = impl_->manifest_chunks;
    result.manifest_pages = impl_->manifest_pages;
    result.artifact_digest = impl_->artifact_digest;
    result.manifest_digest = impl_->manifest_digest;
    result.window = impl_->current_window;
    result.scheduler = impl_->scheduler.stats();
    result.windows_completed = impl_->windows_completed;
    result.page_objects_reused = impl_->page_objects_reused;
    result.page_objects_fetched = impl_->page_objects_fetched;
    result.page_bytes_reused = impl_->page_bytes_reused;
    result.page_bytes_fetched = impl_->page_bytes_fetched;
    result.chunk_objects_reused = impl_->chunk_objects_reused;
    result.chunk_objects_fetched = impl_->chunk_objects_fetched;
    result.chunk_bytes_reused = impl_->chunk_bytes_reused;
    result.chunk_bytes_fetched = impl_->chunk_bytes_fetched;
    result.requests_issued = impl_->requests_issued;
    result.request_failures = impl_->request_failures;
    result.verification_failures = impl_->verification_failures;
    result.hard_link_ingests = impl_->hard_link_ingests;
    result.copied_ingests = impl_->copied_ingests;
    result.existing_ingests = impl_->existing_ingests;
    result.workspace_reserved_bytes = impl_->workspace.resident_bytes();
    result.resident_bytes = impl_->resident_bytes();
    return result;
}

std::size_t ContentFabricSession::resident_bytes() const noexcept {
    return impl_->resident_bytes();
}

const char* content_fabric_phase_name(ContentFabricPhase phase) noexcept {
    switch (phase) {
        case ContentFabricPhase::unprepared: return "unprepared";
        case ContentFabricPhase::manifest_pages: return "manifest-pages";
        case ContentFabricPhase::artifact_chunks: return "artifact-chunks";
        case ContentFabricPhase::complete: return "complete";
    }
    return "unknown";
}

const char* content_fabric_object_kind_name(
    ContentFabricObjectKind kind) noexcept {
    switch (kind) {
        case ContentFabricObjectKind::manifest_page: return "manifest-page";
        case ContentFabricObjectKind::artifact_chunk: return "artifact-chunk";
    }
    return "unknown";
}

} // namespace toxsync
