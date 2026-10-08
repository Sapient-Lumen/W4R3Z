#pragma once

#include "sync_atomic_file_publication.hpp"

#include <filesystem>
#include <span>
#include <string>

namespace anonsync::atomic_file_publication_detail {

// Namespace effect selected by the invariant owner. ReplaceExisting is used
// by mutable reports; CreateNew is reserved for immutable evidence whose name
// must never destroy an existing entry.
enum class AtomicFilePublicationDisposition {
    ReplaceExisting,
    CreateNew,
};

// Test and deterministic-simulation frontiers. Each callback runs immediately
// after the named effect completed and before the next effect begins.
enum class AtomicFilePublicationCutpoint {
    TempReserved,
    PayloadWritten,
    TempFileSynced,
    TempNameRevalidated,
    ParentDirectoryRevalidated,
    TempDescriptorClosed,
    FinalEntryRevalidated,
    NamespacePublished,
    DirectorySynced,
    ParentDirectoryPostpublicationRevalidated,
    ParentDirectoryDescriptorClosed
};

struct AtomicFilePublicationObservation {
    AtomicFilePublicationCutpoint cutpoint;
    SyncAtomicFilePublicationOutcome outcome;
    SyncAtomicFilePublicationResidue residue;
};

using AtomicFilePublicationObserver = void (*)(
    const AtomicFilePublicationObservation& observation,
    void* context);

// Internal deterministic-simulation access to the exact prepared capability
// used by production cross-resource protocols. The public publish_or_throw()
// path delegates here with no observer, so tests do not exercise a parallel
// implementation. The call consumes the capability on every success or
// failure, exactly like the public method.
class PreparedImmutableJsonPublicationObserverAccess final {
public:
    static void publish_or_throw(
        SyncPreparedImmutableJsonPublication& publication,
        AtomicFilePublicationObserver observer,
        void* observer_context);
};

[[nodiscard]] const char* atomic_file_publication_cutpoint_name(
    AtomicFilePublicationCutpoint cutpoint) noexcept;

// Internal deterministic-observer entry point. Production callers use the
// public wrapper, which supplies no observer. The observer may throw to model a
// caught failure or terminate the process to model a crash frontier.
void write_sync_json_file_atomically_with_observer_or_throw(
    const std::filesystem::path& final_path,
    const std::string& payload,
    const std::string& label,
    AtomicFilePublicationObserver observer,
    void* observer_context);

// Internal create-new equivalent used by race and crash-frontier proofs. The
// production public wrapper supplies no observer.
void write_sync_json_file_atomically_create_new_with_observer_or_throw(
    const std::filesystem::path& final_path,
    const std::string& payload,
    const std::string& label,
    AtomicFilePublicationObserver observer,
    void* observer_context);

// Binary equivalent used by invariant owners that already hold exact bytes.
// The observer contract and typed publication outcomes are identical to the
// JSON wrapper.
void write_sync_file_atomically_with_observer_or_throw(
    const std::filesystem::path& final_path,
    std::span<const unsigned char> payload,
    const std::string& label,
    AtomicFilePublicationObserver observer,
    void* observer_context);

// Binary immutable create-new equivalent used by receiver-effect crash-frontier
// tests. Production callers use the public no-observer wrapper.
void write_sync_file_atomically_create_new_with_observer_or_throw(
    const std::filesystem::path& final_path,
    std::span<const unsigned char> payload,
    const std::string& label,
    AtomicFilePublicationObserver observer,
    void* observer_context);

}  // namespace anonsync::atomic_file_publication_detail
