#include "sync_atomic_file_publication_state.hpp"

#include <utility>

namespace anonsync {

const char* sync_atomic_file_publication_outcome_name(
    SyncAtomicFilePublicationOutcome outcome) noexcept {
    switch (outcome) {
        case SyncAtomicFilePublicationOutcome::NotPublished:
            return "not_published";
        case SyncAtomicFilePublicationOutcome::PublishedDurabilityIndeterminate:
            return "published_durability_indeterminate";
        case SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced:
            return "published_and_directory_synced";
    }
    return "unknown";
}

const char* sync_atomic_file_publication_residue_name(
    SyncAtomicFilePublicationResidue residue) noexcept {
    switch (residue) {
        case SyncAtomicFilePublicationResidue::None:
            return "none";
        case SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain:
            return "temporary_artifact_may_remain";
    }
    return "unknown";
}

SyncAtomicFilePublicationError::SyncAtomicFilePublicationError(
    SyncAtomicFilePublicationOutcome outcome,
    SyncAtomicFilePublicationResidue residue,
    std::string message)
    : std::runtime_error(std::move(message)),
      outcome_(outcome),
      residue_(residue) {}

SyncAtomicFilePublicationError::SyncAtomicFilePublicationError(
    SyncAtomicFilePublicationOutcome outcome,
    std::string message)
    : SyncAtomicFilePublicationError(outcome,
                                     SyncAtomicFilePublicationResidue::None,
                                     std::move(message)) {}

SyncAtomicFilePublicationOutcome
SyncAtomicFilePublicationError::outcome() const noexcept {
    return outcome_;
}

SyncAtomicFilePublicationResidue
SyncAtomicFilePublicationError::residue() const noexcept {
    return residue_;
}

namespace atomic_file_publication_detail {

void AtomicFilePublicationProgress::mark_temp_reserved() noexcept {
    if (!namespace_published_) temp_artifact_may_remain_ = true;
}

void AtomicFilePublicationProgress::mark_namespace_published() noexcept {
    namespace_published_ = true;
    temp_artifact_may_remain_ = false;
}

void AtomicFilePublicationProgress::mark_directory_synced() noexcept {
    if (namespace_published_) directory_synced_ = true;
}

SyncAtomicFilePublicationResidue
AtomicFilePublicationProgress::residue() const noexcept {
    return temp_artifact_may_remain_ && !namespace_published_
               ? SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain
               : SyncAtomicFilePublicationResidue::None;
}

bool AtomicFilePublicationProgress::namespace_published() const noexcept {
    return namespace_published_;
}

bool AtomicFilePublicationProgress::directory_synced() const noexcept {
    return directory_synced_;
}

SyncAtomicFilePublicationOutcome
AtomicFilePublicationProgress::outcome() const noexcept {
    if (directory_synced_) {
        return SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced;
    }
    if (namespace_published_) {
        return SyncAtomicFilePublicationOutcome::PublishedDurabilityIndeterminate;
    }
    return SyncAtomicFilePublicationOutcome::NotPublished;
}

}  // namespace atomic_file_publication_detail
}  // namespace anonsync
