#include "sync_atomic_file_publication.hpp"
#include "sync_atomic_file_publication_state.hpp"

#include <iostream>
#include <stdexcept>
#include <string>

namespace {

class TestState final {
public:
    void check(bool condition, const std::string& label) {
        ++total_;
        if (condition) {
            ++passed_;
        } else {
            std::cerr << "FAIL: " << label << '\n';
        }
    }

    int finish() const {
        std::cout << "sync atomic publication state: " << passed_ << "/"
                  << total_ << " checks passed\n";
        return passed_ == total_ ? 0 : 1;
    }

private:
    int total_ = 0;
    int passed_ = 0;
};

}  // namespace

int main() {
    using anonsync::SyncAtomicFilePublicationError;
    using anonsync::SyncAtomicFilePublicationOutcome;
    using anonsync::SyncAtomicFilePublicationResidue;
    using anonsync::atomic_file_publication_detail::AtomicFilePublicationProgress;

    TestState state;
    AtomicFilePublicationProgress progress;

    state.check(progress.residue() == SyncAtomicFilePublicationResidue::None,
                "initial state has no possible temp residue");
    state.check(!progress.namespace_published(),
                "initial state has no namespace effect");
    state.check(!progress.directory_synced(),
                "initial state has no directory durability proof");
    state.check(progress.outcome() ==
                    SyncAtomicFilePublicationOutcome::NotPublished,
                "initial outcome is not published");
    state.check(std::string(anonsync::sync_atomic_file_publication_outcome_name(
                    progress.outcome())) == "not_published",
                "not-published outcome has stable machine name");
    state.check(std::string(anonsync::sync_atomic_file_publication_residue_name(
                    progress.residue())) == "none",
                "no-residue state has stable machine name");

    progress.mark_directory_synced();
    state.check(!progress.directory_synced(),
                "directory sync cannot precede namespace publication");

    progress.mark_temp_reserved();
    state.check(progress.residue() ==
                    SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain,
                "reserved temp records possible pre-publication residue");
    state.check(progress.outcome() ==
                    SyncAtomicFilePublicationOutcome::NotPublished,
                "temp reservation does not imply publication");
    state.check(std::string(anonsync::sync_atomic_file_publication_residue_name(
                    progress.residue())) ==
                    "temporary_artifact_may_remain",
                "possible residue has stable machine name");

    progress.mark_namespace_published();
    state.check(progress.namespace_published(),
                "namespace publication is retained");
    state.check(progress.residue() == SyncAtomicFilePublicationResidue::None,
                "namespace publication consumes the temp artifact name");
    state.check(progress.outcome() ==
                    SyncAtomicFilePublicationOutcome::PublishedDurabilityIndeterminate,
                "rename without directory sync is indeterminate");
    state.check(std::string(anonsync::sync_atomic_file_publication_outcome_name(
                    progress.outcome())) ==
                    "published_durability_indeterminate",
                "indeterminate outcome has stable machine name");

    progress.mark_temp_reserved();
    state.check(progress.residue() == SyncAtomicFilePublicationResidue::None,
                "possible temp residue cannot reopen after publication");

    progress.mark_directory_synced();
    state.check(progress.directory_synced(),
                "directory sync proof follows namespace publication");
    state.check(progress.outcome() ==
                    SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced,
                "directory-synced publication has durable outcome");
    state.check(std::string(anonsync::sync_atomic_file_publication_outcome_name(
                    progress.outcome())) ==
                    "published_and_directory_synced",
                "durable outcome has stable machine name");

    progress.mark_namespace_published();
    progress.mark_directory_synced();
    state.check(progress.outcome() ==
                    SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced &&
                    progress.residue() == SyncAtomicFilePublicationResidue::None,
                "repeated monotone evidence cannot regress outcome or residue");

    const SyncAtomicFilePublicationError error(
        SyncAtomicFilePublicationOutcome::PublishedDurabilityIndeterminate,
        SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain,
        "typed publication failure");
    state.check(error.outcome() ==
                    SyncAtomicFilePublicationOutcome::PublishedDurabilityIndeterminate,
                "typed exception retains machine-readable outcome");
    state.check(error.residue() ==
                    SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain,
                "typed exception retains machine-readable residue");
    state.check(std::string(error.what()) == "typed publication failure",
                "typed exception retains diagnostic text");
    bool runtime_error_compatible = false;
    try {
        throw error;
    } catch (const std::runtime_error&) {
        runtime_error_compatible = true;
    }
    state.check(runtime_error_compatible,
                "typed exception remains runtime_error-compatible");

    const SyncAtomicFilePublicationError compatibility_error(
        SyncAtomicFilePublicationOutcome::NotPublished,
        "compatibility publication failure");
    state.check(compatibility_error.residue() ==
                    SyncAtomicFilePublicationResidue::None,
                "two-argument compatibility constructor defaults to no residue");

    return state.finish();
}
