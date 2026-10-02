#include "toxsync/content_retention.hpp"
#include "toxsync/content_store.hpp"
#include "toxsync/index.hpp"
#include "toxsync/treepack.hpp"

#include <algorithm>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <span>
#include <stdexcept>
#include <string>
#include <vector>

#include <unistd.h>

namespace {

std::vector<std::byte> read_file(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary | std::ios::ate);
  if (!input)
    throw std::runtime_error("unable to read fuzz seed");
  const auto end = input.tellg();
  if (end < 0)
    throw std::runtime_error("unable to size fuzz seed");
  std::vector<std::byte> bytes(static_cast<std::size_t>(end));
  input.seekg(0, std::ios::beg);
  input.read(reinterpret_cast<char *>(bytes.data()), end);
  if (!input)
    throw std::runtime_error("unable to load fuzz seed");
  return bytes;
}

void write_file(const std::filesystem::path &path,
                std::span<const std::byte> bytes) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  if (!output)
    throw std::runtime_error("unable to open fuzz input");
  output.write(reinterpret_cast<const char *>(bytes.data()),
               static_cast<std::streamsize>(bytes.size()));
  if (!output)
    throw std::runtime_error("unable to write fuzz input");
}

class Workspace final {
public:
  Workspace() {
    const auto stamp =
        std::chrono::steady_clock::now().time_since_epoch().count();
    const auto base = std::filesystem::temp_directory_path();
    for (unsigned int attempt = 0U; attempt < 100U; ++attempt) {
      root_ = base / ("txf-" + std::to_string(::getpid()) + "-" +
                      std::to_string(stamp) + "-" + std::to_string(attempt));
      std::error_code error;
      if (std::filesystem::create_directory(root_, error))
        break;
      if (error && error != std::errc::file_exists) {
        throw std::runtime_error("unable to create fuzz workspace");
      }
    }
    if (root_.empty() || !std::filesystem::is_directory(root_)) {
      throw std::runtime_error("unable to allocate fuzz workspace");
    }

    const auto artifact = root_ / "artifact";
    const std::vector<std::byte> payload(4096U, std::byte{0x5a});
    write_file(artifact, payload);

    toxsync::ContentStoreOptions flat_options;
    flat_options.fsync_on_commit = false;
    flat_options.publish_manifest_to_store = false;
    const auto flat_path = root_ / "flat";
    static_cast<void>(toxsync::build_content_store(
        artifact, root_ / "flat-store", flat_path, flat_options));
    flat_ = read_file(flat_path);

    toxsync::PagedContentStoreOptions paged_options;
    paged_options.fsync_on_commit = false;
    paged_options.publish_root_to_store = false;
    const auto paged_path = root_ / "paged";
    static_cast<void>(toxsync::build_paged_content_store(
        artifact, root_ / "paged-store", paged_path, paged_options));
    paged_ = read_file(paged_path);

    const auto tree_root = root_ / "tree";
    std::filesystem::create_directory(tree_root);
    write_file(tree_root / "file", payload);
    const auto treepack_path = root_ / "treepack";
    static_cast<void>(toxsync::pack_tree(tree_root, treepack_path));
    treepack_ = read_file(treepack_path);

    toxsync::Index index;
    index.target_size = 1U;
    index.blocks.push_back(toxsync::BlockRecord{1U, 1U, {}});
    index_ = index.encode();

    const auto pin_path = root_ / "pins-seed";
    {
      toxsync::ContentPinLedgerOptions options;
      options.fsync_on_commit = false;
      options.max_pins = 4U;
      options.max_journal_records = 8U;
      toxsync::ContentPinLedger ledger(pin_path, options);
      toxsync::ContentPin pin;
      pin.namespace_id.bytes[0] = std::byte{1U};
      pin.generation = 1U;
      pin.manifest.bytes[0] = std::byte{2U};
      static_cast<void>(ledger.upsert(pin));
    }
    pins_ = read_file(pin_path);
  }

  ~Workspace() {
    std::error_code ignored;
    std::filesystem::remove_all(root_, ignored);
  }

  Workspace(const Workspace &) = delete;
  Workspace &operator=(const Workspace &) = delete;

  void exercise(std::span<const std::byte> input) noexcept {
    if (input.empty())
      return;
    const auto selector = std::to_integer<unsigned int>(input.front()) % 5U;
    try {
      switch (selector) {
      case 0U:
        exercise_flat(input);
        break;
      case 1U:
        exercise_paged(input);
        break;
      case 2U:
        exercise_treepack(input);
        break;
      case 3U:
        exercise_index(input);
        break;
      case 4U:
        exercise_pins(input);
        break;
      default:
        __builtin_trap();
      }
    } catch (...) {
    }
  }

private:
  [[nodiscard]] static std::vector<std::byte>
  mutated(const std::vector<std::byte> &canonical,
          std::span<const std::byte> input) {
    auto result = canonical;
    for (std::size_t index = 8U; index < result.size(); ++index) {
      result[index] ^= input[(index - 8U) % input.size()];
    }
    return result;
  }

  [[nodiscard]] toxsync::ContentStoreLimits content_limits() const {
    toxsync::ContentStoreLimits limits;
    limits.max_artifact_size = 1024U * 1024U;
    limits.max_chunks = 64U;
    limits.min_chunk_bytes = 1U;
    limits.max_chunk_bytes = 1024U * 1024U;
    return limits;
  }

  void exercise_flat(std::span<const std::byte> input) {
    const auto path = root_ / "input-flat";
    write_file(path, mutated(flat_, input));
    static_cast<void>(
        toxsync::inspect_content_manifest(path, content_limits()));
  }

  void exercise_paged(std::span<const std::byte> input) {
    const auto path = root_ / "input-paged";
    write_file(path, mutated(paged_, input));
    static_cast<void>(
        toxsync::inspect_paged_content_manifest(path, content_limits()));
  }

  void exercise_treepack(std::span<const std::byte> input) {
    const auto path = root_ / "input-treepack";
    write_file(path, mutated(treepack_, input));
    const auto destination = root_ / "unpacked";
    std::error_code ignored;
    std::filesystem::remove_all(destination, ignored);
    toxsync::TreePackLimits limits;
    limits.max_entries = 32U;
    limits.max_file_size = 1024U * 1024U;
    limits.max_path_bytes = 256U;
    static_cast<void>(toxsync::unpack_tree(path, destination, limits));
  }

  void exercise_index(std::span<const std::byte> input) {
    const auto path = root_ / "input-index";
    write_file(path, mutated(index_, input));
    toxsync::IndexLimits limits;
    limits.max_target_size = 1024U * 1024U;
    limits.max_blocks = 64U;
    static_cast<void>(toxsync::Index::read_file(path, limits));
  }

  void exercise_pins(std::span<const std::byte> input) {
    const auto path = root_ / "input-pins";
    write_file(path, mutated(pins_, input));
    toxsync::ContentPinLedgerOptions options;
    options.max_pins = 32U;
    options.max_journal_records = 64U;
    options.fsync_on_commit = false;
    options.repair_truncated_tail = false;
    const toxsync::ContentPinLedger ledger(path, options);
    static_cast<void>(ledger.stats());
  }

  std::filesystem::path root_;
  std::vector<std::byte> flat_;
  std::vector<std::byte> paged_;
  std::vector<std::byte> treepack_;
  std::vector<std::byte> index_;
  std::vector<std::byte> pins_;
};

} // namespace

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t *data,
                                      std::size_t size) {
  static Workspace workspace;
  const auto input = std::span<const std::byte>{
      reinterpret_cast<const std::byte *>(data), size};
  workspace.exercise(input);
  return 0;
}
