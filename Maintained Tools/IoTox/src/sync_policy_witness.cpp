#include "iotox/sync_policy_witness.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <span>
#include <string_view>
#include <vector>

namespace iotox::sync {
namespace {

void append_u32(std::vector<std::uint8_t> &output, std::uint32_t value) {
  output.push_back(static_cast<std::uint8_t>(value >> 24U));
  output.push_back(static_cast<std::uint8_t>(value >> 16U));
  output.push_back(static_cast<std::uint8_t>(value >> 8U));
  output.push_back(static_cast<std::uint8_t>(value));
}

Status append_record(std::vector<std::uint8_t> &output,
                     std::span<const std::uint8_t> record) {
  if (record.size() >
      static_cast<std::size_t>(std::numeric_limits<std::uint32_t>::max())) {
    return Status{ErrorCode::resource_exhausted,
                  "sync policy witness record is too large"};
  }
  append_u32(output, static_cast<std::uint32_t>(record.size()));
  output.insert(output.end(), record.begin(), record.end());
  return Status::success();
}

}  // namespace

Result<SyncPolicyTree> load_sync_policy_tree(
    const std::filesystem::path &policy_root,
    std::uint32_t expected_owner_uid,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) {
  auto namespaces = load_namespace_store(policy_root, expected_owner_uid);
  if (!namespaces) return namespaces.status();
  SyncAutomationStore store(policy_root);
  auto automations = store.load(expected_device, sodium);
  if (!automations) return automations.status();
  return SyncPolicyTree{std::move(namespaces).value(),
                        std::move(automations).value()};
}

Result<security::Digest> sync_policy_tree_digest(
    const SyncPolicyTree &tree, const security::Sodium &sodium) {
  if (tree.namespaces.size() > kMaximumNamespaces ||
      tree.automations.size() > kMaximumNamespaces ||
      tree.namespaces.size() >
          static_cast<std::size_t>(std::numeric_limits<std::uint32_t>::max()) ||
      tree.automations.size() >
          static_cast<std::size_t>(std::numeric_limits<std::uint32_t>::max())) {
    return Status{ErrorCode::resource_exhausted,
                  "sync policy witness population exceeds its bound"};
  }
  std::vector<NamespacePolicy> namespaces = tree.namespaces;
  std::vector<SyncAutomationPolicy> automations = tree.automations;
  std::sort(namespaces.begin(), namespaces.end(),
            [](const NamespacePolicy &left, const NamespacePolicy &right) {
              return left.id < right.id;
            });
  std::sort(automations.begin(), automations.end(),
            [](const SyncAutomationPolicy &left,
               const SyncAutomationPolicy &right) {
              return left.namespace_id < right.namespace_id;
            });
  for (std::size_t index = 1U; index < namespaces.size(); ++index) {
    if (namespaces[index - 1U].id == namespaces[index].id) {
      return Status{ErrorCode::protocol_error,
                    "sync policy witness contains duplicate namespaces"};
    }
  }
  for (std::size_t index = 1U; index < automations.size(); ++index) {
    if (automations[index - 1U].namespace_id ==
        automations[index].namespace_id) {
      return Status{ErrorCode::protocol_error,
                    "sync policy witness contains duplicate automations"};
    }
  }

  constexpr std::string_view header{"iotox-sync-policy-tree-v1\n"};
  std::vector<std::uint8_t> material(header.begin(), header.end());
  append_u32(material, static_cast<std::uint32_t>(namespaces.size()));
  for (const NamespacePolicy &policy : namespaces) {
    auto encoded = encode_namespace_policy(policy);
    if (!encoded) return encoded.status();
    const Status appended = append_record(material, encoded.value());
    if (!appended.ok()) return appended;
  }
  append_u32(material, static_cast<std::uint32_t>(automations.size()));
  for (const SyncAutomationPolicy &policy : automations) {
    auto encoded = encode_sync_automation_policy(policy);
    if (!encoded) return encoded.status();
    const Status appended = append_record(material, encoded.value());
    if (!appended.ok()) return appended;
  }
  return sodium.hash("iotox-sync-policy-tree-v1", material);
}

}  // namespace iotox::sync
