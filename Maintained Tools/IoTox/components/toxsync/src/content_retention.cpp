#include "toxsync/content_retention.hpp"

#include "native_file.hpp"
#include "toxsync/content_availability.hpp"
#include "toxsync/content_store.hpp"
#include "toxsync/hash.hpp"

#include <algorithm>
#include <array>
#include <bit>
#include <cerrno>
#include <chrono>
#include <cstring>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <type_traits>
#include <utility>
#include <vector>

#if defined(__unix__) || defined(__APPLE__)
#include <fcntl.h>
#include <unistd.h>
#endif

namespace toxsync {
namespace {

constexpr std::array<std::byte, 8> kPinMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'P'}, std::byte{'I'},
    std::byte{'N'}, std::byte{'0'}, std::byte{'0'}, std::byte{'1'},
};
constexpr std::uint16_t kPinVersion = 1U;
constexpr std::size_t kPinRecordBodyBytes = 128U;
constexpr std::size_t kPinRecordBytes = 160U;
constexpr std::size_t kReplayRecordsPerBatch = 256U;
constexpr std::size_t kAgeBuckets = 64U;

enum class PinOperation : std::uint16_t { upsert = 1U, erase = 2U };

[[nodiscard]] bool all_zero(std::span<const std::byte> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(), [](std::byte value) {
        return value == std::byte{0};
    });
}

[[nodiscard]] bool digest_less(const Digest256& left,
                               const Digest256& right) noexcept {
    return std::lexicographical_compare(left.bytes.begin(), left.bytes.end(),
                                        right.bytes.begin(), right.bytes.end());
}

[[nodiscard]] bool pin_key_less_value(const ContentPin& left,
                                      const std::pair<Digest256, std::uint64_t>& right) noexcept {
    if (left.namespace_id != right.first) {
        return digest_less(left.namespace_id, right.first);
    }
    return left.generation < right.second;
}

template <typename T>
void store_le(std::byte* output, T value) noexcept {
    static_assert(std::is_unsigned_v<T>);
    for (std::size_t index = 0U; index < sizeof(T); ++index) {
        output[index] = static_cast<std::byte>(value >> (index * 8U));
    }
}

template <typename T>
[[nodiscard]] T load_le(const std::byte* input) noexcept {
    static_assert(std::is_unsigned_v<T>);
    std::uint64_t value{};
    for (std::size_t index = 0U; index < sizeof(T); ++index) {
        value |= static_cast<std::uint64_t>(
                     std::to_integer<unsigned>(input[index]))
                 << (index * 8U);
    }
    return static_cast<T>(value);
}

void validate_pin(const ContentPin& pin) {
    if (all_zero(pin.namespace_id.bytes)) {
        throw std::invalid_argument("content pin has an empty namespace id");
    }
    if (all_zero(pin.manifest.bytes)) {
        throw std::invalid_argument("content pin has an empty manifest digest");
    }
    if ((pin.flags & ~kKnownContentPinFlags) != 0U || pin.flags == 0U) {
        throw std::invalid_argument("content pin has invalid flags");
    }
}

[[nodiscard]] std::array<std::byte, kPinRecordBytes> encode_pin_record(
    PinOperation operation, std::uint64_t sequence, const ContentPin& pin) {
    std::array<std::byte, kPinRecordBytes> output{};
    std::copy(kPinMagic.begin(), kPinMagic.end(), output.begin());
    store_le<std::uint16_t>(output.data() + 8U, kPinVersion);
    store_le<std::uint16_t>(output.data() + 10U,
                            static_cast<std::uint16_t>(operation));
    store_le<std::uint32_t>(output.data() + 12U,
                            operation == PinOperation::upsert ? pin.flags : 0U);
    store_le<std::uint64_t>(output.data() + 16U, sequence);
    store_le<std::uint64_t>(output.data() + 24U, pin.generation);
    store_le<std::uint64_t>(output.data() + 32U,
                            operation == PinOperation::upsert
                                ? pin.retain_until_unix_seconds
                                : 0U);
    std::copy(pin.namespace_id.bytes.begin(), pin.namespace_id.bytes.end(),
              output.begin() + 40);
    if (operation == PinOperation::upsert) {
        std::copy(pin.manifest.bytes.begin(), pin.manifest.bytes.end(),
                  output.begin() + 72);
    }
    const auto checksum = sha256(std::span<const std::byte>(
        output.data(), kPinRecordBodyBytes));
    std::copy(checksum.bytes.begin(), checksum.bytes.end(),
              output.begin() + static_cast<std::ptrdiff_t>(kPinRecordBodyBytes));
    return output;
}

struct DecodedPinRecord {
    PinOperation operation{PinOperation::upsert};
    std::uint64_t sequence{};
    ContentPin pin{};
};

[[nodiscard]] DecodedPinRecord decode_pin_record(
    std::span<const std::byte, kPinRecordBytes> input) {
    if (!std::equal(kPinMagic.begin(), kPinMagic.end(), input.begin()) ||
        load_le<std::uint16_t>(input.data() + 8U) != kPinVersion) {
        throw std::runtime_error("invalid content pin journal record header");
    }
    const auto raw_operation = load_le<std::uint16_t>(input.data() + 10U);
    if (raw_operation != static_cast<std::uint16_t>(PinOperation::upsert) &&
        raw_operation != static_cast<std::uint16_t>(PinOperation::erase)) {
        throw std::runtime_error("invalid content pin journal operation");
    }
    const auto expected = sha256(input.first(kPinRecordBodyBytes));
    if (!std::equal(expected.bytes.begin(), expected.bytes.end(),
                    input.begin() + static_cast<std::ptrdiff_t>(
                        kPinRecordBodyBytes))) {
        throw std::runtime_error("content pin journal checksum mismatch");
    }
    if (!all_zero(input.subspan(104U, 24U))) {
        throw std::runtime_error("content pin journal reserved bytes are nonzero");
    }

    DecodedPinRecord result;
    result.operation = static_cast<PinOperation>(raw_operation);
    const auto flags = load_le<std::uint32_t>(input.data() + 12U);
    result.sequence = load_le<std::uint64_t>(input.data() + 16U);
    result.pin.generation = load_le<std::uint64_t>(input.data() + 24U);
    result.pin.retain_until_unix_seconds =
        load_le<std::uint64_t>(input.data() + 32U);
    std::copy_n(input.begin() + 40, result.pin.namespace_id.bytes.size(),
                result.pin.namespace_id.bytes.begin());
    std::copy_n(input.begin() + 72, result.pin.manifest.bytes.size(),
                result.pin.manifest.bytes.begin());
    result.pin.flags = flags;
    if (result.sequence == 0U || all_zero(result.pin.namespace_id.bytes)) {
        throw std::runtime_error("content pin journal record has invalid identity");
    }
    if (result.operation == PinOperation::upsert) {
        validate_pin(result.pin);
    } else if (flags != 0U || result.pin.retain_until_unix_seconds != 0U ||
               !all_zero(result.pin.manifest.bytes)) {
        throw std::runtime_error("content pin erase record contains payload data");
    }
    return result;
}

void ensure_parent_directory(const std::filesystem::path& path) {
    const auto parent = path.parent_path();
    if (parent.empty()) return;
    std::error_code error;
    std::filesystem::create_directories(parent, error);
    if (error) {
        throw std::runtime_error("cannot create content pin directory: " +
                                 error.message());
    }
}

void sync_parent_directory(const std::filesystem::path& path) {
#if defined(__unix__) || defined(__APPLE__)
    const auto parent = path.parent_path().empty()
        ? std::filesystem::path{"."}
        : path.parent_path();
    const int descriptor = ::open(parent.c_str(), O_RDONLY | O_CLOEXEC | O_DIRECTORY);
    if (descriptor < 0) {
        throw std::runtime_error("cannot open content pin parent directory for fsync");
    }
    const int result = ::fsync(descriptor);
    const int saved = errno;
    (void)::close(descriptor);
    if (result != 0) {
        throw std::runtime_error("cannot fsync content pin parent directory: " +
                                 std::string(std::strerror(saved)));
    }
#else
    (void)path;
#endif
}

[[nodiscard]] std::uint64_t current_unix_seconds() noexcept {
    const auto now = std::chrono::system_clock::now().time_since_epoch();
    const auto seconds =
        std::chrono::duration_cast<std::chrono::seconds>(now).count();
    return seconds < 0 ? 0U : static_cast<std::uint64_t>(seconds);
}

[[nodiscard]] bool valid_hex_name(std::string_view text,
                                  std::size_t expected) noexcept {
    if (text.size() != expected) return false;
    return std::all_of(text.begin(), text.end(), [](char value) {
        return (value >= '0' && value <= '9') ||
               (value >= 'a' && value <= 'f');
    });
}

[[nodiscard]] std::uint64_t file_age_seconds(
    const std::filesystem::file_time_type& modified,
    const std::filesystem::file_time_type& now) noexcept {
    if (modified >= now) return 0U;
    const auto age = std::chrono::duration_cast<std::chrono::seconds>(
        now - modified).count();
    return age < 0 ? 0U : static_cast<std::uint64_t>(age);
}

[[nodiscard]] std::size_t age_bucket(std::uint64_t age_seconds) noexcept {
    if (age_seconds == 0U) return 0U;
    return std::min<std::size_t>(
        static_cast<std::size_t>(std::bit_width(age_seconds)),
        kAgeBuckets - 1U);
}

struct BlobInfo {
    std::filesystem::path path;
    Digest256 digest{};
    std::uint64_t size{};
    std::uint64_t age_seconds{};
};

template <typename Visitor>
void for_each_store_blob(const std::filesystem::path& store_root,
                         std::uint64_t max_files,
                         Visitor&& visitor) {
    const auto sha_root = store_root / "sha256";
    std::error_code error;
    const auto root_status = std::filesystem::symlink_status(sha_root, error);
    if (error || !std::filesystem::is_directory(root_status) ||
        std::filesystem::is_symlink(root_status)) {
        throw std::runtime_error("content store sha256 root is not a real directory");
    }
    std::uint64_t visited{};
    const auto now = std::filesystem::file_time_type::clock::now();
    for (std::filesystem::directory_iterator prefixes(
             sha_root, std::filesystem::directory_options::skip_permission_denied,
             error), end;
         prefixes != end; prefixes.increment(error)) {
        if (error) {
            throw std::runtime_error("cannot iterate content store prefixes: " +
                                     error.message());
        }
        const auto prefix_name = prefixes->path().filename().string();
        const auto prefix_status = prefixes->symlink_status(error);
        if (error) {
            throw std::runtime_error("cannot inspect content store prefix: " +
                                     error.message());
        }
        if (!valid_hex_name(prefix_name, 2U) ||
            !std::filesystem::is_directory(prefix_status) ||
            std::filesystem::is_symlink(prefix_status)) {
            continue;
        }
        for (std::filesystem::directory_iterator files(
                 prefixes->path(),
                 std::filesystem::directory_options::skip_permission_denied,
                 error), file_end;
             files != file_end; files.increment(error)) {
            if (error) {
                throw std::runtime_error("cannot iterate content store blobs: " +
                                         error.message());
            }
            if (++visited > max_files) {
                throw std::runtime_error("content store file-count limit exceeded");
            }
            const auto name = files->path().filename().string();
            const auto status = files->symlink_status(error);
            if (error) {
                throw std::runtime_error("cannot inspect content store blob: " +
                                         error.message());
            }
            if (!valid_hex_name(name, 62U) ||
                !std::filesystem::is_regular_file(status) ||
                std::filesystem::is_symlink(status)) {
                continue;
            }
            const auto size = files->file_size(error);
            if (error) {
                throw std::runtime_error("cannot inspect content store blob size: " +
                                         error.message());
            }
            const auto modified = files->last_write_time(error);
            if (error) {
                throw std::runtime_error("cannot inspect content store blob age: " +
                                         error.message());
            }
            BlobInfo info;
            info.path = files->path();
            info.digest = Digest256::from_hex(prefix_name + name);
            info.size = size;
            info.age_seconds = file_age_seconds(modified, now);
            visitor(info);
        }
    }
}

struct MarkContext {
    ContentAvailabilitySketch* marks{};
    ContentGcStats* stats{};
};

void mark_chunk(void* opaque, const ContentChunkRef& chunk) {
    auto& context = *static_cast<MarkContext*>(opaque);
    context.marks->add(chunk.digest, chunk.length);
    ++context.stats->reachable_chunk_references;
}

void mark_page(void* opaque, const PagedContentPageRef& page) {
    auto& context = *static_cast<MarkContext*>(opaque);
    context.marks->add(page.digest, page.encoded_size);
    ++context.stats->reachable_page_references;
}

} // namespace

class ContentPinLedger::Impl final {
public:
    Impl(std::filesystem::path path, ContentPinLedgerOptions options)
        : path_(std::move(path)), options_(options) {
        if (path_.empty() || options_.max_pins == 0U ||
            options_.max_journal_records == 0U) {
            throw std::invalid_argument("invalid content pin ledger options");
        }
        pins_.reserve(options_.max_pins);
        ensure_parent_directory(path_);
        replay();
    }

    [[nodiscard]] auto lower_bound(const Digest256& namespace_id,
                                   std::uint64_t generation) noexcept {
        const auto key = std::pair{namespace_id, generation};
        return std::lower_bound(pins_.begin(), pins_.end(), key,
                                pin_key_less_value);
    }

    [[nodiscard]] auto lower_bound(const Digest256& namespace_id,
                                   std::uint64_t generation) const noexcept {
        const auto key = std::pair{namespace_id, generation};
        return std::lower_bound(pins_.begin(), pins_.end(), key,
                                pin_key_less_value);
    }

    void apply(const DecodedPinRecord& record, bool replaying) {
        auto found = lower_bound(record.pin.namespace_id, record.pin.generation);
        const bool exists = found != pins_.end() &&
                            found->namespace_id == record.pin.namespace_id &&
                            found->generation == record.pin.generation;
        if (record.operation == PinOperation::erase) {
            if (exists) pins_.erase(found);
        } else if (exists) {
            if (found->manifest != record.pin.manifest) {
                throw std::runtime_error(
                    "content pin journal contains a namespace-generation fork");
            }
            *found = record.pin;
        } else {
            if (pins_.size() >= options_.max_pins) {
                throw std::runtime_error("content pin ledger exceeds configured pin limit");
            }
            pins_.insert(found, record.pin);
        }
        if (replaying) ++stats_.records_replayed;
    }

    void replay() {
        detail::NativeFile journal(path_, detail::NativeOpenMode::read_write_create);
        const auto bytes = journal.size();
        const auto complete_bytes = bytes - bytes % kPinRecordBytes;
        const auto record_count = complete_bytes / kPinRecordBytes;
        if (record_count > options_.max_journal_records) {
            throw std::runtime_error("content pin journal record limit exceeded");
        }
        std::array<std::byte, kPinRecordBytes * kReplayRecordsPerBatch> buffer{};
        std::uint64_t offset{};
        std::uint64_t previous_sequence{};
        while (offset < complete_bytes) {
            const auto remaining = complete_bytes - offset;
            const auto count = static_cast<std::size_t>(std::min<std::uint64_t>(
                remaining, buffer.size()));
            auto batch = std::span<std::byte>(buffer).first(count);
            journal.read_exact_at(offset, batch);
            for (std::size_t local = 0U; local < count;
                 local += kPinRecordBytes) {
                const auto record = decode_pin_record(
                    std::span<const std::byte, kPinRecordBytes>(
                        batch.data() + local, kPinRecordBytes));
                if (record.sequence <= previous_sequence) {
                    throw std::runtime_error(
                        "content pin journal sequence is not strictly increasing");
                }
                previous_sequence = record.sequence;
                apply(record, true);
            }
            offset += count;
        }
        const auto tail = bytes - complete_bytes;
        if (tail != 0U) {
            stats_.ignored_torn_tail_bytes = tail;
            if (options_.repair_truncated_tail) {
                journal.resize(complete_bytes);
                if (options_.fsync_on_commit) journal.sync();
            }
        }
        stats_.journal_bytes = complete_bytes;
        stats_.next_sequence = previous_sequence + 1U;
        if (stats_.next_sequence == 0U) {
            throw std::runtime_error("content pin journal sequence exhausted");
        }
        journal.close();
        refresh_stats();
    }

    void append(PinOperation operation, const ContentPin& pin) {
        if (stats_.records_replayed + stats_.records_appended >=
            options_.max_journal_records) {
            throw std::runtime_error("content pin journal record limit reached");
        }
        const auto record = encode_pin_record(operation, stats_.next_sequence, pin);
        detail::NativeFile journal(path_, detail::NativeOpenMode::read_write_create);
        if (journal.size() != stats_.journal_bytes) {
            throw std::runtime_error(
                "content pin journal changed outside the active ledger");
        }
        journal.write_exact_at(stats_.journal_bytes, record);
        if (options_.fsync_on_commit) journal.sync();
        journal.close();
        stats_.journal_bytes += kPinRecordBytes;
        ++stats_.records_appended;
        ++stats_.next_sequence;
        if (stats_.next_sequence == 0U) {
            throw std::runtime_error("content pin journal sequence exhausted");
        }
    }

    void refresh_stats() noexcept {
        stats_.active_pins = pins_.size();
        stats_.resident_bytes = pins_.capacity() * sizeof(ContentPin);
    }

    std::filesystem::path path_;
    ContentPinLedgerOptions options_{};
    std::vector<ContentPin> pins_{};
    ContentPinLedgerStats stats_{};
};

ContentPinLedger::ContentPinLedger(
    std::filesystem::path journal_path,
    const ContentPinLedgerOptions& options)
    : impl_(std::make_unique<Impl>(std::move(journal_path), options)) {}

ContentPinLedger::~ContentPinLedger() = default;
ContentPinLedger::ContentPinLedger(ContentPinLedger&&) noexcept = default;
ContentPinLedger& ContentPinLedger::operator=(ContentPinLedger&&) noexcept = default;

ContentPinUpdate ContentPinLedger::upsert(const ContentPin& pin) {
    validate_pin(pin);
    auto found = impl_->lower_bound(pin.namespace_id, pin.generation);
    const bool exists = found != impl_->pins_.end() &&
                        found->namespace_id == pin.namespace_id &&
                        found->generation == pin.generation;
    if (exists) {
        if (found->manifest != pin.manifest) {
            return ContentPinUpdate::fork_rejected;
        }
        if (*found == pin) return ContentPinUpdate::unchanged;
        impl_->append(PinOperation::upsert, pin);
        *found = pin;
        impl_->refresh_stats();
        return ContentPinUpdate::updated;
    }
    if (impl_->pins_.size() >= impl_->options_.max_pins) {
        return ContentPinUpdate::capacity_exhausted;
    }
    impl_->append(PinOperation::upsert, pin);
    impl_->pins_.insert(found, pin);
    impl_->refresh_stats();
    return ContentPinUpdate::inserted;
}

bool ContentPinLedger::erase(const Digest256& namespace_id,
                             std::uint64_t generation) {
    if (all_zero(namespace_id.bytes)) {
        throw std::invalid_argument("cannot erase an empty content namespace");
    }
    auto found = impl_->lower_bound(namespace_id, generation);
    if (found == impl_->pins_.end() || found->namespace_id != namespace_id ||
        found->generation != generation) {
        return false;
    }
    ContentPin tombstone;
    tombstone.namespace_id = namespace_id;
    tombstone.generation = generation;
    impl_->append(PinOperation::erase, tombstone);
    impl_->pins_.erase(found);
    impl_->refresh_stats();
    return true;
}

std::optional<ContentPin> ContentPinLedger::find(
    const Digest256& namespace_id,
    std::uint64_t generation) const noexcept {
    const auto found = impl_->lower_bound(namespace_id, generation);
    if (found == impl_->pins_.end() || found->namespace_id != namespace_id ||
        found->generation != generation) {
        return std::nullopt;
    }
    return *found;
}

std::span<const ContentPin> ContentPinLedger::pins() const noexcept {
    return impl_->pins_;
}

std::size_t ContentPinLedger::active_count(
    std::uint64_t now_unix_seconds) const noexcept {
    return static_cast<std::size_t>(std::count_if(
        impl_->pins_.begin(), impl_->pins_.end(),
        [&](const ContentPin& pin) {
            return pin.retain_until_unix_seconds == 0U ||
                   pin.retain_until_unix_seconds >= now_unix_seconds;
        }));
}

void ContentPinLedger::compact() {
    auto temporary = impl_->path_;
    temporary += ".compact.part";
    std::error_code error;
    std::filesystem::remove(temporary, error);
    detail::NativeFile output(
        temporary, detail::NativeOpenMode::read_write_create_exclusive);
    std::uint64_t offset{};
    std::uint64_t sequence{1U};
    for (const auto& pin : impl_->pins_) {
        const auto record = encode_pin_record(PinOperation::upsert, sequence, pin);
        output.write_exact_at(offset, record);
        offset += kPinRecordBytes;
        ++sequence;
    }
    if (impl_->options_.fsync_on_commit) output.sync();
    output.close();
    std::filesystem::rename(temporary, impl_->path_, error);
    if (error) {
        const auto rename_message = error.message();
        std::error_code cleanup_error;
        std::filesystem::remove(temporary, cleanup_error);
        throw std::runtime_error("cannot atomically compact content pin journal: " +
                                 rename_message);
    }
    if (impl_->options_.fsync_on_commit) sync_parent_directory(impl_->path_);
    impl_->stats_.journal_bytes = offset;
    impl_->stats_.records_replayed = 0U;
    impl_->stats_.records_appended = impl_->pins_.size();
    impl_->stats_.next_sequence = sequence;
    impl_->stats_.ignored_torn_tail_bytes = 0U;
    ++impl_->stats_.compactions;
    impl_->refresh_stats();
}

const std::filesystem::path& ContentPinLedger::journal_path() const noexcept {
    return impl_->path_;
}

ContentPinLedgerStats ContentPinLedger::stats() const noexcept {
    return impl_->stats_;
}

ContentGcStats collect_content_store(
    const std::filesystem::path& store_root,
    const ContentPinLedger& ledger,
    const ContentGcOptions& options) {
    ContentStoreWorkspace workspace;
    return collect_content_store(store_root, ledger.pins(), workspace, options);
}

ContentGcStats collect_content_store(
    const std::filesystem::path& store_root,
    std::span<const ContentPin> pins,
    ContentStoreWorkspace& workspace,
    const ContentGcOptions& options) {
    if (options.maximum_store_bytes == 0U ||
        options.max_store_files == 0U ||
        options.reachability_filter_bytes < 64U ||
        !std::has_single_bit(options.reachability_filter_bytes) ||
        options.reachability_hash_functions == 0U ||
        options.reachability_hash_functions > 16U) {
        throw std::invalid_argument("invalid content GC limits");
    }
    const auto target = options.target_store_bytes == 0U
        ? options.maximum_store_bytes - options.maximum_store_bytes / 10U
        : options.target_store_bytes;
    if (target > options.maximum_store_bytes) {
        throw std::invalid_argument("content GC target exceeds maximum store size");
    }
    const auto now_unix = options.now_unix_seconds == 0U
        ? current_unix_seconds()
        : options.now_unix_seconds;

    ContentAvailabilityConfig filter_config;
    filter_config.filter_bytes = options.reachability_filter_bytes;
    filter_config.hash_functions = options.reachability_hash_functions;
    filter_config.salt = options.reachability_salt;
    ContentAvailabilitySketch marks(filter_config);
    const auto gc_identity = sha256(std::as_bytes(std::span(
        "toxsync-content-gc-reachability-v1",
        sizeof("toxsync-content-gc-reachability-v1") - 1U)));
    marks.reset(gc_identity);

    ContentGcStats stats;
    stats.reachability_filter_bytes = marks.resident_bytes();
    stats.dry_run = options.dry_run;
    ContentManifestWalkOptions flat_walk_options;
    flat_walk_options.manifest_buffer_bytes = options.manifest_buffer_bytes;
    flat_walk_options.limits = options.limits;
    PagedContentManifestWalkOptions paged_walk_options;
    paged_walk_options.manifest_buffer_bytes = options.manifest_buffer_bytes;
    paged_walk_options.limits = options.limits;
    MarkContext mark_context{.marks = &marks, .stats = &stats};
    for (const auto& pin : pins) {
        validate_pin(pin);
        if (pin.retain_until_unix_seconds != 0U &&
            pin.retain_until_unix_seconds < now_unix) {
            continue;
        }
        ++stats.active_pins;
        marks.add(pin.manifest);
        const auto manifest_path = content_store_path(store_root, pin.manifest);
        switch (detect_content_manifest_format(manifest_path)) {
            case ContentManifestFormat::flat_v1: {
                const auto walked = walk_content_manifest(
                    manifest_path, workspace, &mark_chunk, &mark_context,
                    flat_walk_options);
                if (walked.metadata.manifest_digest != pin.manifest) {
                    throw std::runtime_error(
                        "pinned flat content manifest digest does not match its store identity");
                }
                break;
            }
            case ContentManifestFormat::paged_v2: {
                const auto walked = walk_paged_content_manifest(
                    manifest_path, store_root, workspace, &mark_page,
                    &mark_context, &mark_chunk, &mark_context,
                    paged_walk_options);
                if (walked.metadata.root_digest != pin.manifest) {
                    throw std::runtime_error(
                        "pinned paged content root digest does not match its store identity");
                }
                break;
            }
        }
        ++stats.pinned_manifests;
    }
    stats.estimated_false_positive_rate = marks.estimated_false_positive_rate();

    std::array<std::uint64_t, kAgeBuckets> bucket_bytes{};
    std::array<std::uint64_t, kAgeBuckets> bucket_files{};
    for_each_store_blob(store_root, options.max_store_files,
        [&](const BlobInfo& blob) {
            ++stats.scanned_files;
            stats.scanned_bytes += blob.size;
            if (marks.possibly_contains(blob.digest)) {
                ++stats.protected_files;
                stats.protected_bytes += blob.size;
                return;
            }
            if (blob.age_seconds < options.minimum_unpinned_age_seconds) {
                ++stats.young_unpinned_files;
                stats.young_unpinned_bytes += blob.size;
                return;
            }
            ++stats.candidate_files;
            stats.candidate_bytes += blob.size;
            const auto bucket = age_bucket(blob.age_seconds);
            ++bucket_files[bucket];
            bucket_bytes[bucket] += blob.size;
        });

    stats.bytes_after = stats.scanned_bytes;
    if (stats.scanned_bytes <= options.maximum_store_bytes) {
        stats.budget_satisfied = true;
        return stats;
    }
    const auto required = stats.scanned_bytes > target
        ? stats.scanned_bytes - target
        : 0U;
    std::size_t cutoff_bucket{};
    std::uint64_t selected_bytes{};
    bool cutoff_found{};
    for (std::size_t reverse = kAgeBuckets; reverse != 0U; --reverse) {
        const auto bucket = reverse - 1U;
        if (bucket_files[bucket] == 0U) continue;
        cutoff_bucket = bucket;
        selected_bytes += bucket_bytes[bucket];
        if (selected_bytes >= required) {
            cutoff_found = true;
            break;
        }
    }
    if (!cutoff_found) cutoff_bucket = 0U;

    for_each_store_blob(store_root, options.max_store_files,
        [&](const BlobInfo& blob) {
            if (stats.deleted_bytes >= required ||
                marks.possibly_contains(blob.digest) ||
                blob.age_seconds < options.minimum_unpinned_age_seconds) {
                return;
            }
            const auto bucket = age_bucket(blob.age_seconds);
            if (bucket < cutoff_bucket) return;
            if (options.dry_run) {
                ++stats.deleted_files;
                stats.deleted_bytes += blob.size;
                return;
            }
            std::error_code error;
            const auto status = std::filesystem::symlink_status(blob.path, error);
            if (error || !std::filesystem::is_regular_file(status) ||
                std::filesystem::is_symlink(status) ||
                std::filesystem::file_size(blob.path, error) != blob.size || error) {
                ++stats.deletion_failures;
                return;
            }
            if (!std::filesystem::remove(blob.path, error) || error) {
                ++stats.deletion_failures;
                return;
            }
            ++stats.deleted_files;
            stats.deleted_bytes += blob.size;
        });

    stats.bytes_after = stats.scanned_bytes >= stats.deleted_bytes
        ? stats.scanned_bytes - stats.deleted_bytes
        : 0U;
    stats.budget_satisfied = stats.bytes_after <= options.maximum_store_bytes;

    if (!options.dry_run && options.remove_empty_prefix_directories) {
        const auto sha_root = store_root / "sha256";
        std::error_code error;
        for (std::filesystem::directory_iterator iterator(
                 sha_root,
                 std::filesystem::directory_options::skip_permission_denied,
                 error), end;
             iterator != end; iterator.increment(error)) {
            if (error) break;
            const auto status = iterator->symlink_status(error);
            if (error || !std::filesystem::is_directory(status) ||
                std::filesystem::is_symlink(status)) {
                continue;
            }
            std::filesystem::remove(iterator->path(), error);
            error.clear();
        }
    }
    return stats;
}

} // namespace toxsync
