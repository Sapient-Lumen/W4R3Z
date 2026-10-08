#pragma once

#include "sync_atomic_file_publication.hpp"

namespace anonsync::atomic_file_publication_detail {

// Allocation-free state owner for the three materially different publication
// outcomes. State changes occur immediately after the corresponding kernel
// effect and before any callback, diagnostic construction, or later syscall.
class AtomicFilePublicationProgress final {
public:
    void mark_temp_reserved() noexcept;
    void mark_namespace_published() noexcept;
    void mark_directory_synced() noexcept;

    [[nodiscard]] SyncAtomicFilePublicationResidue residue() const noexcept;
    [[nodiscard]] bool namespace_published() const noexcept;
    [[nodiscard]] bool directory_synced() const noexcept;
    [[nodiscard]] SyncAtomicFilePublicationOutcome outcome() const noexcept;

private:
    bool temp_artifact_may_remain_ = false;
    bool namespace_published_ = false;
    bool directory_synced_ = false;
};

}  // namespace anonsync::atomic_file_publication_detail
