#include "test_harness.hpp"

#include "iotox/sync_multiwriter_store.hpp"
#include "iotox/sync_multiwriter_workspace.hpp"

#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <span>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

using iotox::security::DeviceIdentity;
using iotox::security::Sodium;
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::TreeV2BranchStore;
using iotox::sync::TreeV2Observation;
using iotox::sync::TreeV2WorkspaceDecision;
using iotox::sync::TreeV2WorkspacePhase;
using iotox::sync::TreeV2WorkspaceState;
using iotox::sync::TreeV2WorkspaceStore;

class TempDirectory {
  public:
    TempDirectory() {
        std::string pattern = "/tmp/iotox-sync-multiwriter-workspace-XXXXXX";
        std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
        mutable_pattern.push_back('\0');
        char *created = ::mkdtemp(mutable_pattern.data());
        if (created == nullptr) throw std::runtime_error("mkdtemp failed");
        path_ = created;
        if (::chmod(path_.c_str(), static_cast<mode_t>(0700)) != 0)
            throw std::runtime_error("chmod failed");
    }

    ~TempDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(path_, ignored);
    }

    [[nodiscard]] const std::filesystem::path &path() const noexcept {
        return path_;
    }

  private:
    std::filesystem::path path_;
};

Sodium sodium() {
    auto loaded = Sodium::load();
    if (!loaded) throw std::runtime_error(loaded.status().message());
    return std::move(loaded).value();
}

DeviceIdentity identity(const std::filesystem::path &path,
                        const Sodium &crypto) {
    auto loaded = DeviceIdentity::load_or_create(path, crypto, true);
    if (!loaded) throw std::runtime_error(loaded.status().message());
    return std::move(loaded).value();
}

std::vector<std::uint8_t> read_bytes(const std::filesystem::path &path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("read bytes failed");
    return std::vector<std::uint8_t>(
        std::istreambuf_iterator<char>(input),
        std::istreambuf_iterator<char>());
}

void write_bytes(const std::filesystem::path &path,
                 std::span<const std::uint8_t> bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    output.write(reinterpret_cast<const char *>(bytes.data()),
                 static_cast<std::streamsize>(bytes.size()));
    output.close();
    if (!output || ::chmod(path.c_str(), static_cast<mode_t>(0600)) != 0)
        throw std::runtime_error("write bytes failed");
}

Digest digest(std::uint8_t value) {
    Digest result{};
    result[0U] = value;
    return result;
}

TreeV2Observation observation(const DeviceIdentity &device,
                              std::uint64_t generation, std::uint8_t record) {
    return TreeV2Observation{device.public_key(), generation, digest(record)};
}

NamespacePolicy policy_for(const std::filesystem::path &root,
                           const DeviceIdentity &device) {
    NamespacePolicy policy;
    policy.id = "field-notes";
    policy.root = root.string();
    policy.engine = Engine::tree_v2;
    policy.writers = {device.public_key()};
    return policy;
}

} // namespace

IOTOX_TEST("tree-v2 workspace journal signs begin and finish transitions") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto device = identity(temporary.path() / "device.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    IOTOX_CHECK(std::filesystem::create_directory(root));
    IOTOX_CHECK(std::filesystem::create_directory(worktree));
    IOTOX_CHECK(::chmod(root.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(worktree.c_str(), static_cast<mode_t>(0700)) == 0);
    const NamespacePolicy policy = policy_for(root, device);
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    TreeV2BranchStore branches(root);
    IOTOX_CHECK(branches.prepare(policy, transaction.value()).ok());
    TreeV2WorkspaceStore store(root);

    const std::vector<TreeV2Observation> first_frontier{
        observation(device, 1U, 11U)};
    const std::vector<TreeV2Observation> second_frontier{
        observation(device, 2U, 12U)};
    auto initialized = store.initialize(policy, worktree, digest(1U),
                                        first_frontier, device, crypto);
    IOTOX_CHECK_MSG(initialized.ok(), initialized.status().message());
    IOTOX_CHECK(initialized.value().decision ==
                TreeV2WorkspaceDecision::initialized);
    IOTOX_CHECK(initialized.value().state.generation == 1U);
    IOTOX_CHECK(initialized.value().state.phase ==
                TreeV2WorkspacePhase::stable);
    auto duplicate = store.initialize(policy, worktree, digest(1U),
                                      first_frontier, device, crypto);
    IOTOX_CHECK(duplicate.ok());
    IOTOX_CHECK(duplicate.value().decision ==
                TreeV2WorkspaceDecision::duplicate);

    auto begun =
        store.begin_exchange(policy, digest(1U), digest(2U), digest(1U),
                             second_frontier, device, crypto);
    IOTOX_CHECK_MSG(begun.ok(), begun.status().message());
    IOTOX_CHECK(begun.value().state.generation == 2U);
    IOTOX_CHECK(begun.value().state.phase ==
                TreeV2WorkspacePhase::pending_exchange);
    IOTOX_CHECK(!store
                     .begin_exchange(policy, digest(9U), digest(3U), digest(1U),
                                     second_frontier, device, crypto)
                     .ok());
    duplicate = store.begin_exchange(policy, digest(1U), digest(2U), digest(1U),
                                     second_frontier, device, crypto);
    IOTOX_CHECK(duplicate.ok());
    IOTOX_CHECK(duplicate.value().decision ==
                TreeV2WorkspaceDecision::duplicate);

    auto finished = store.finish_exchange(policy, digest(2U), device, crypto);
    IOTOX_CHECK_MSG(finished.ok(), finished.status().message());
    IOTOX_CHECK(finished.value().state.generation == 3U);
    IOTOX_CHECK(finished.value().state.phase == TreeV2WorkspacePhase::stable);
    IOTOX_CHECK(finished.value().state.active_manifest == digest(2U));
    TreeV2WorkspaceStore restarted(root);
    auto loaded = restarted.load(policy, device.public_key(), crypto);
    IOTOX_CHECK_MSG(loaded.ok(), loaded.status().message());
    IOTOX_CHECK(loaded.value().has_value());
    IOTOX_CHECK(*loaded.value() == finished.value().state);
}

IOTOX_TEST(
    "tree-v2 workspace codec refuses padding tamper and foreign signer") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto device = identity(temporary.path() / "device.identity", crypto);
    auto foreign = identity(temporary.path() / "foreign.identity", crypto);
    TreeV2WorkspaceState state;
    state.namespace_id = "field-notes";
    state.worktree = temporary.path() / "worktree";
    state.generation = 1U;
    state.active_manifest = digest(1U);
    state.active_frontier = {observation(device, 1U, 11U)};
    state.signer = device.public_key();
    auto unsigned_bytes = iotox::sync::encode_tree_v2_workspace_state(state);
    IOTOX_CHECK(unsigned_bytes.ok());

    // Sign through the store so the public codec and signer verification are
    // exercised over the exact durable record.
    const std::filesystem::path root = temporary.path() / "namespace";
    IOTOX_CHECK(std::filesystem::create_directory(state.worktree));
    IOTOX_CHECK(::chmod(state.worktree.c_str(), static_cast<mode_t>(0700)) ==
                0);
    IOTOX_CHECK(std::filesystem::create_directory(root));
    IOTOX_CHECK(::chmod(root.c_str(), static_cast<mode_t>(0700)) == 0);
    const NamespacePolicy policy = policy_for(root, device);
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    TreeV2BranchStore branches(root);
    IOTOX_CHECK(branches.prepare(policy, transaction.value()).ok());
    TreeV2WorkspaceStore store(root);
    auto initialized =
        store.initialize(policy, state.worktree, state.active_manifest,
                         state.active_frontier, device, crypto);
    IOTOX_CHECK(initialized.ok());
    IOTOX_CHECK(iotox::sync::verify_tree_v2_workspace_state(
                    initialized.value().state, device.public_key(), crypto)
                    .ok());
    IOTOX_CHECK(!iotox::sync::verify_tree_v2_workspace_state(
                     initialized.value().state, foreign.public_key(), crypto)
                     .ok());

    auto encoded =
        iotox::sync::encode_tree_v2_workspace_state(initialized.value().state);
    IOTOX_CHECK(encoded.ok());
    encoded.value()[13U] = 1U;
    IOTOX_CHECK(
        !iotox::sync::decode_tree_v2_workspace_state(encoded.value()).ok());

    const std::filesystem::path record = root / "tree-v2" / "workspace.state";
    const std::vector<std::uint8_t> original = read_bytes(record);
    IOTOX_CHECK(!original.empty());
    std::vector<std::uint8_t> corrupt = original;
    corrupt.back() ^= 0x01U;
    write_bytes(record, corrupt);
    auto refused = store.load(policy, device.public_key(), crypto);
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK_MSG(
        refused.status().message().find("workspace state") != std::string::npos,
        refused.status().message());
    IOTOX_CHECK(read_bytes(record) == corrupt);
    auto overwrite =
        store.initialize(policy, state.worktree, state.active_manifest,
                         state.active_frontier, device, crypto);
    IOTOX_CHECK(!overwrite.ok());
    IOTOX_CHECK(read_bytes(record) == corrupt);
    write_bytes(record, original);
    auto restored = store.load(policy, device.public_key(), crypto);
    IOTOX_CHECK_MSG(restored.ok(), restored.status().message());
    IOTOX_CHECK(restored.value().has_value());
    IOTOX_CHECK(*restored.value() == initialized.value().state);
}
