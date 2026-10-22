#include "slopos/e0/provisioned_expectation.hpp"
#include "slopos/e0/recipient_claim_canary_linux.hpp"

#ifdef __linux__

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstdlib>
#include <filesystem>
#include <fcntl.h>
#include <iostream>
#include <sstream>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

namespace canary = slopos::e0::recipient_canary;
using slopos::e0::provisioned::Byte;
using slopos::e0::provisioned::Bytes;
using slopos::e0::provisioned::hex;
using slopos::e0::provisioned::sha256;

namespace {

[[noreturn]] void fail(const std::string& detail) {
  std::cerr << "RECIPIENT_CLAIM_CANARY_LINUX=FAIL detail=" << detail << '\n';
  std::exit(1);
}

void require(const bool condition, const std::string& detail) {
  if (!condition) fail(detail);
}

Bytes as_bytes(const std::string& text) {
  Bytes out;
  out.reserve(text.size());
  for (const unsigned char value : text) {
    out.push_back(static_cast<Byte>(value));
  }
  return out;
}

class TempTree final {
 public:
  TempTree() {
    std::array<char, 64U> pattern{};
    const std::string base = "/tmp/slopos-recipient-claim-canary-XXXXXX";
    std::copy(base.begin(), base.end(), pattern.begin());
    char* made = ::mkdtemp(pattern.data());
    if (made == nullptr) fail("mkdtemp failed");
    path_ = made;
    if (::chmod(path_.c_str(), S_IRWXU) != 0) {
      fail("chmod temp root failed");
    }
  }
  TempTree(const TempTree&) = delete;
  TempTree& operator=(const TempTree&) = delete;
  ~TempTree() {
    std::error_code ignored;
    std::filesystem::remove_all(path_, ignored);
  }

  [[nodiscard]] std::string store(const std::string_view name) const {
    const std::filesystem::path child =
        std::filesystem::path(path_) / std::string(name);
    std::filesystem::create_directory(child);
    if (::chmod(child.c_str(), S_IRWXU) != 0) fail("chmod store failed");
    return child.string();
  }

  [[nodiscard]] std::string copy_store(const std::string_view name,
                                       const std::string& source) const {
    const std::filesystem::path child =
        std::filesystem::path(path_) / std::string(name);
    std::filesystem::copy(source, child,
                          std::filesystem::copy_options::recursive |
                              std::filesystem::copy_options::copy_symlinks);
    if (::chmod(child.c_str(), S_IRWXU) != 0) {
      fail("chmod copied store failed");
    }
    return child.string();
  }

  [[nodiscard]] const std::string& path() const noexcept { return path_; }

 private:
  std::string path_;
};

[[nodiscard]] canary::Operation operation() {
  return canary::Operation{
      "incarnation-1",
      "operation-0950",
      "canary-route",
      "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"};
}

[[nodiscard]] std::string incarnation_bytes(const std::string_view value) {
  return "SLOPOS-CANARY-INCARNATION-V1\nincarnation=" + std::string(value) +
         "\n";
}

[[nodiscard]] std::string intent_bytes(const canary::Operation& op) {
  return "SLOPOS-CANARY-INTENT-V1\nincarnation=" + op.incarnation +
         "\noperation=" + op.operation + "\nroute=" + op.route +
         "\npayload_sha256=" + op.payload_sha256 + "\n";
}

[[nodiscard]] std::string effect_bytes(const canary::Operation& op) {
  return "SLOPOS-CANARY-EFFECT-V1\nincarnation=" + op.incarnation +
         "\noperation=" + op.operation + "\nroute=" + op.route +
         "\npayload_sha256=" + op.payload_sha256 + "\n";
}

[[nodiscard]] std::string result_bytes(const std::string_view result,
                                       const canary::Operation& op) {
  return "SLOPOS-CANARY-RESULT-V2\nresult=" + std::string(result) +
         "\nincarnation=" + op.incarnation + "\noperation=" + op.operation +
         "\nroute=" + op.route + "\npayload_sha256=" + op.payload_sha256 +
         "\n";
}

void write_raw_record(const std::string& root, const std::string& name,
                      const std::string& bytes) {
  const std::filesystem::path path = std::filesystem::path(root) / name;
  const int fd = ::open(path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC,
                        S_IRUSR);
  if (fd < 0) fail("raw record open failed");
  std::size_t offset = 0U;
  while (offset < bytes.size()) {
    const ssize_t amount =
        ::write(fd, bytes.data() + offset, bytes.size() - offset);
    if (amount < 0) {
      if (errno == EINTR) continue;
      (void)::close(fd);
      fail("raw record write failed");
    }
    if (amount == 0) {
      (void)::close(fd);
      fail("raw record short write");
    }
    offset += static_cast<std::size_t>(amount);
  }
  if (::fsync(fd) != 0 || ::close(fd) != 0) fail("raw record close failed");
  const int root_fd =
      ::open(root.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
  if (root_fd < 0) fail("raw record root open failed");
  if (::fsync(root_fd) != 0 || ::close(root_fd) != 0) {
    fail("raw record directory sync failed");
  }
}

void prepare_pending(const std::string& root, const canary::Operation& op,
                     const std::string_view retained_incarnation =
                         "incarnation-1") {
  write_raw_record(root, "INCARNATION",
                   incarnation_bytes(retained_incarnation));
  write_raw_record(root, "INTENT", intent_bytes(op));
}

[[nodiscard]] int exit_code(const int status) {
  require(WIFEXITED(status), "child did not exit normally");
  return WEXITSTATUS(status);
}

[[nodiscard]] std::array<int, 2U> run_claim_race(
    const std::string& root) {
  int gate[2]{};
  if (::pipe(gate) != 0) fail("pipe failed");
  std::array<pid_t, 2U> children{};
  for (std::size_t index = 0U; index < children.size(); ++index) {
    const pid_t child = ::fork();
    if (child < 0) fail("fork failed");
    if (child == 0) {
      (void)::close(gate[1]);
      char token_value{};
      while (::read(gate[0], &token_value, 1U) < 0 && errno == EINTR) {}
      (void)::close(gate[0]);
      const std::string claimant = index == 0U ? "claimant-a" : "claimant-b";
      const auto result = canary::claim_pending(root, claimant);
      if (result.disposition == canary::ClaimDisposition::won_with_permit &&
          result.permit.has_value()) {
        _exit(20);
      }
      if (result.disposition == canary::ClaimDisposition::duplicate) _exit(21);
      _exit(22);
    }
    children[index] = child;
  }
  (void)::close(gate[0]);
  const std::array<char, 2U> release{{'a', 'b'}};
  std::size_t offset = 0U;
  while (offset < release.size()) {
    const ssize_t amount =
        ::write(gate[1], release.data() + offset, release.size() - offset);
    if (amount < 0) {
      if (errno == EINTR) continue;
      fail("gate release failed");
    }
    offset += static_cast<std::size_t>(amount);
  }
  (void)::close(gate[1]);

  std::array<int, 2U> codes{};
  for (std::size_t index = 0U; index < children.size(); ++index) {
    int status{};
    if (::waitpid(children[index], &status, 0) != children[index]) {
      fail("waitpid failed");
    }
    codes[index] = exit_code(status);
  }
  return codes;
}

void require_one_each(std::array<int, 2U> codes, const int first,
                      const int second, const std::string& detail) {
  std::sort(codes.begin(), codes.end());
  require(codes[0] == std::min(first, second) &&
              codes[1] == std::max(first, second),
          detail);
}

void complete_effect(const std::string& root, const canary::Operation& op,
                     const std::string_view claimant,
                     const bool retain_result) {
  auto claim = canary::claim_pending(root, claimant);
  require(claim.disposition == canary::ClaimDisposition::won_with_permit &&
              claim.permit.has_value(),
          "claim did not produce permit");
  auto entered = canary::enter_effect(std::move(*claim.permit), op);
  require(entered.disposition == canary::EnterDisposition::entered &&
              entered.permit.has_value(),
          "exact meaning did not produce effect permit");
  const auto effect =
      canary::emit_canary_effect(std::move(*entered.permit), retain_result);
  require(effect.disposition == canary::EffectDisposition::emitted,
          "canary effect was not emitted");
}

[[nodiscard]] bool fixed_record_safe(const std::string& root,
                                     const std::string_view name) {
  const std::filesystem::path path =
      std::filesystem::path(root) / std::string(name);
  struct stat st {};
  return ::lstat(path.c_str(), &st) == 0 && S_ISREG(st.st_mode) &&
         st.st_uid == ::geteuid() && st.st_nlink == 1 &&
         (st.st_mode & 0777) == 0400;
}

}  // namespace

int main() {
  static_assert(canary::pinned_store_descriptor());
  static_assert(!canary::path_reopen_after_claim());
  static_assert(canary::full_result_binding());
  static_assert(canary::exact_record_mode());
  static_assert(canary::all_component_symlink_rejection());
  static_assert(!canary::mount_traversal_rejected());
  static_assert(!canary::same_uid_writer_exclusion_proved());
  static_assert(!canary::external_join_instantiated());
  static_assert(!canary::response_authority_present());
  static_assert(!canary::independent_custody_proved());
  static_assert(!canary::rollback_independence_proved());
  static_assert(!canary::global_one_use_proved());
  static_assert(!canary::authority_granted());

  TempTree tree;
  const canary::Operation op = operation();
  std::ostringstream witness;
  unsigned cases = 0U;

  // Absence is an unjoined observation, never terminal no-effect.
  const std::string unjoined = tree.store("unjoined");
  require(canary::reopen(unjoined).state == canary::ReopenState::unjoined,
          "empty operated root was not classified as unjoined");
  witness << "unjoined\tclassification=observation_only\tno_effect=0\n";
  ++cases;

  // A partial join topology is malformed rather than pending or no-effect.
  const std::string partial_join = tree.store("partial-join");
  write_raw_record(partial_join, "INCARNATION",
                   incarnation_bytes("incarnation-1"));
  require(canary::reopen(partial_join).state ==
              canary::ReopenState::malformed,
          "partial join topology was not rejected");
  witness << "partial-join\tmalformed=1\tno_effect=0\n";
  ++cases;

  // 1. No response bytes are needed once one exact pending intent exists.
  const std::string joined = tree.store("joined-intent");
  prepare_pending(joined, op);
  require(canary::reopen(joined).state == canary::ReopenState::pending,
          "joined intent did not reopen pending");
  complete_effect(joined, op, "claimant-joined", true);
  require(canary::reopen(joined).state ==
              canary::ReopenState::settled_effect,
          "joined intent did not settle effect");
  witness << "joined-intent\tresponse_bytes=0\teffect=1\n";
  ++cases;

  // 2. A real process race leaves one retained claim and no second permit.
  const std::string claim_race = tree.store("claim-race");
  prepare_pending(claim_race, op);
  require_one_each(run_claim_race(claim_race), 20, 21,
                   "claim race did not have one winner and one duplicate");
  require(canary::reopen(claim_race).state ==
              canary::ReopenState::claimed_uncertain,
          "claim race did not retain one burned claim");
  witness << "claim-race\twinner=1\tduplicate=1\n";
  ++cases;

  // 3. Wrong meaning burns the claim into a bound no-effect result.
  const std::string mismatch = tree.store("mismatch");
  prepare_pending(mismatch, op);
  auto mismatch_claim = canary::claim_pending(mismatch, "claimant-mismatch");
  require(mismatch_claim.permit.has_value(), "mismatch claim lacked permit");
  canary::Operation wrong = op;
  wrong.route = "other-route";
  const auto mismatch_enter =
      canary::enter_effect(std::move(*mismatch_claim.permit), wrong);
  require(mismatch_enter.disposition ==
              canary::EnterDisposition::rejected_mismatch &&
              canary::reopen(mismatch).state ==
                  canary::ReopenState::settled_no_effect &&
              canary::claim_pending(mismatch, "claimant-again").disposition ==
                  canary::ClaimDisposition::duplicate,
          "mismatch did not burn claim closed");
  witness << "mismatch\tclaim_burned=1\teffect=0\n";
  ++cases;

  // 4. Caller meaning is validated only after move-consuming the permit.
  const std::string noncanonical = tree.store("noncanonical");
  prepare_pending(noncanonical, op);
  auto noncanonical_claim =
      canary::claim_pending(noncanonical, "claimant-noncanonical");
  require(noncanonical_claim.permit.has_value(),
          "noncanonical claim lacked permit");
  canary::Operation bad = op;
  bad.operation = "NOT-CANONICAL";
  const auto noncanonical_enter =
      canary::enter_effect(std::move(*noncanonical_claim.permit), bad);
  require(noncanonical_enter.disposition ==
              canary::EnterDisposition::rejected_noncanonical &&
              canary::reopen(noncanonical).state ==
                  canary::ReopenState::settled_no_effect,
          "noncanonical meaning did not burn claim closed");
  witness << "noncanonical\tclaim_burned=1\teffect=0\n";
  ++cases;

  // 5. Missing intent: CLAIM is published before the first INTENT open.
  const std::string absent = tree.store("absent");
  write_raw_record(absent, "INCARNATION", incarnation_bytes("incarnation-1"));
  const auto absent_claim = canary::claim_pending(absent, "claimant-absent");
  require(absent_claim.disposition ==
              canary::ClaimDisposition::won_missing_intent &&
              !absent_claim.permit.has_value() &&
              fixed_record_safe(absent, "CLAIM") &&
              canary::reopen(absent).state ==
                  canary::ReopenState::claimed_uncertain,
          "absent intent was inspected before claim or yielded a permit");
  witness << "absent-intent\tclaim_precedes_read=1\tpermit=0\n";
  ++cases;

  // 6. Malformed intent likewise leaves a burned fixed claim.
  const std::string malformed = tree.store("malformed");
  write_raw_record(malformed, "INCARNATION",
                   incarnation_bytes("incarnation-1"));
  write_raw_record(malformed, "INTENT", "not-an-intent\n");
  const auto malformed_claim =
      canary::claim_pending(malformed, "claimant-malformed");
  require(malformed_claim.disposition ==
              canary::ClaimDisposition::won_malformed_intent &&
              !malformed_claim.permit.has_value() &&
              fixed_record_safe(malformed, "CLAIM") &&
              canary::reopen(malformed).state ==
                  canary::ReopenState::claimed_uncertain,
          "malformed intent was inspected before claim or yielded a permit");
  witness << "malformed-intent\tclaim_precedes_decode=1\tpermit=0\n";
  ++cases;

  // 7. Wrong incarnation is discovered only after the claim is fixed.
  const std::string wrong_incarnation = tree.store("wrong-incarnation");
  canary::Operation other_incarnation = op;
  other_incarnation.incarnation = "incarnation-2";
  prepare_pending(wrong_incarnation, other_incarnation, "incarnation-1");
  const auto wrong_incarnation_claim =
      canary::claim_pending(wrong_incarnation, "claimant-incarnation");
  require(wrong_incarnation_claim.disposition ==
              canary::ClaimDisposition::won_wrong_incarnation &&
              !wrong_incarnation_claim.permit.has_value() &&
              canary::reopen(wrong_incarnation).state ==
                  canary::ReopenState::claimed_uncertain,
          "wrong incarnation authorized or escaped the burned claim");
  witness << "wrong-incarnation\tclaim_burned=1\tpermit=0\n";
  ++cases;

  // 8. Crash after claim cannot recreate the move-only descriptor permit.
  const std::string claim_crash = tree.store("claim-crash");
  prepare_pending(claim_crash, op);
  {
    auto claim = canary::claim_pending(claim_crash, "claimant-crash");
    require(claim.permit.has_value(), "claim-crash lacked permit");
  }
  require(canary::reopen(claim_crash).state ==
              canary::ReopenState::claimed_uncertain &&
              canary::claim_pending(claim_crash, "claimant-reopen")
                      .disposition == canary::ClaimDisposition::duplicate,
          "claim crash recreated permit");
  witness << "claim-crash\treopen=claimed_uncertain\treclaim=0\n";
  ++cases;

  // 9. Crash after EFFECT but before RESULT is query-only reconciliation.
  const std::string effect_crash = tree.store("effect-crash");
  prepare_pending(effect_crash, op);
  complete_effect(effect_crash, op, "claimant-effect-crash", false);
  require(canary::reopen(effect_crash).state ==
              canary::ReopenState::effect_unsettled &&
              canary::reconcile_effect_result(effect_crash) &&
              canary::reopen(effect_crash).state ==
                  canary::ReopenState::settled_effect &&
              canary::reconcile_effect_result(effect_crash),
          "effect crash did not reconcile idempotently");
  witness << "effect-crash\teffects=1\treconcile_effects=0\n";
  ++cases;

  // 10. Abandoned staging names are inert to the fixed-name reopener.
  const std::string residue = tree.store("stage-residue");
  prepare_pending(residue, op);
  write_raw_record(residue, ".stage.residue", "junk\n");
  require(canary::reopen(residue).state == canary::ReopenState::pending,
          "stage residue changed fixed-name reopen state");
  witness << "stage-residue\tinert=1\n";
  ++cases;

  // 11. A group/other-writable root is rejected before fixed-name work.
  const std::string unsafe_root = tree.store("unsafe-root");
  prepare_pending(unsafe_root, op);
  require(::chmod(unsafe_root.c_str(), 0777) == 0,
          "could not prepare unsafe root");
  require(canary::claim_pending(unsafe_root, "claimant-unsafe").disposition ==
              canary::ClaimDisposition::unsafe &&
              canary::reopen(unsafe_root).state == canary::ReopenState::unsafe,
          "unsafe root was admitted");
  witness << "unsafe-root\trejected=1\n";
  ++cases;

  // 12. Fixed-name symlinks are never followed; the claim remains burned.
  const std::string symlink_root = tree.store("symlink");
  write_raw_record(symlink_root, "INCARNATION",
                   incarnation_bytes("incarnation-1"));
  const std::filesystem::path intent_link =
      std::filesystem::path(symlink_root) / "INTENT";
  require(::symlink("/etc/passwd", intent_link.c_str()) == 0,
          "could not prepare symlink case");
  const auto symlink_claim =
      canary::claim_pending(symlink_root, "claimant-symlink");
  require(symlink_claim.disposition ==
              canary::ClaimDisposition::won_malformed_intent &&
              !symlink_claim.permit.has_value() &&
              canary::reopen(symlink_root).state ==
                  canary::ReopenState::malformed,
          "fixed-name symlink was followed or authorized");
  witness << "symlink\tfollowed=0\tpermit=0\n";
  ++cases;

  // An existing unsafe CLAIM object is not a benign duplicate.
  const std::string claim_collision = tree.store("claim-collision");
  prepare_pending(claim_collision, op);
  const std::filesystem::path claim_link =
      std::filesystem::path(claim_collision) / "CLAIM";
  require(::symlink("/etc/passwd", claim_link.c_str()) == 0,
          "could not prepare unsafe claim collision");
  require(canary::claim_pending(claim_collision, "claimant-collision")
                  .disposition == canary::ClaimDisposition::unsafe &&
              canary::reopen(claim_collision).state ==
                  canary::ReopenState::malformed,
          "unsafe claim collision was accepted as duplicate");
  witness << "claim-collision\tunsafe_duplicate_rejected=1\n";
  ++cases;

  // 13. RESULT and reconciliation require the complete exact operation chain.
  const std::string result_mismatch = tree.store("result-mismatch");
  prepare_pending(result_mismatch, op);
  complete_effect(result_mismatch, op, "claimant-result", false);
  canary::Operation other = op;
  other.route = "other-route";
  write_raw_record(result_mismatch, "RESULT", result_bytes("effect", other));
  require(canary::reopen(result_mismatch).state ==
              canary::ReopenState::malformed &&
              !canary::reconcile_effect_result(result_mismatch),
          "mismatched result was accepted");
  const std::string orphan = tree.store("orphan-effect");
  prepare_pending(orphan, op);
  write_raw_record(orphan, "EFFECT", effect_bytes(op));
  require(canary::reopen(orphan).state == canary::ReopenState::malformed &&
              !canary::reconcile_effect_result(orphan),
          "orphan effect was promoted to a result");
  witness << "result-binding\tmismatch_rejected=1\torphan_rejected=1\n";
  ++cases;

  // 14. Path replacement cannot redirect a permit carrying an open dirfd.
  const std::string path_swap = tree.store("path-swap");
  prepare_pending(path_swap, op);
  auto pinned_claim = canary::claim_pending(path_swap, "claimant-pinned");
  require(pinned_claim.permit.has_value(), "pinned claim lacked permit");
  const std::string replacement = tree.store("path-swap-replacement");
  prepare_pending(replacement, op);
  const std::string saved = tree.path() + "/path-swap-original";
  std::filesystem::rename(path_swap, saved);
  std::filesystem::rename(replacement, path_swap);
  auto pinned_enter =
      canary::enter_effect(std::move(*pinned_claim.permit), op);
  require(pinned_enter.disposition == canary::EnterDisposition::entered &&
              pinned_enter.permit.has_value(),
          "pinned directory permit did not enter");
  const auto pinned_effect =
      canary::emit_canary_effect(std::move(*pinned_enter.permit), true);
  require(pinned_effect.disposition == canary::EffectDisposition::emitted &&
              canary::reopen(saved).state ==
                  canary::ReopenState::settled_effect &&
              canary::reopen(path_swap).state == canary::ReopenState::pending,
          "path substitution redirected the effect permit");
  witness << "path-swap\toriginal_effect=1\treplacement_effect=0\n";
  ++cases;

  // 15. EFFECT and RESULT are malformed without the consumed CLAIM topology.
  const std::string topology = tree.store("topology");
  prepare_pending(topology, op);
  complete_effect(topology, op, "claimant-topology", true);
  const std::filesystem::path topology_claim =
      std::filesystem::path(topology) / "CLAIM";
  require(::unlink(topology_claim.c_str()) == 0,
          "topology claim removal failed");
  const int topology_fd = ::open(
      topology.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
  require(topology_fd >= 0 && ::fsync(topology_fd) == 0 &&
              ::close(topology_fd) == 0,
          "topology directory sync failed");
  require(canary::reopen(topology).state == canary::ReopenState::malformed &&
              !canary::reconcile_effect_result(topology),
          "terminal records without claim were accepted");
  witness << "topology\tclaim_required=1\tmalformed=1\n";
  ++cases;

  // 16. A fixed retained record must have exact mode 0400.
  const std::string record_mode = tree.store("record-mode");
  prepare_pending(record_mode, op);
  complete_effect(record_mode, op, "claimant-record-mode", true);
  const std::filesystem::path result_path =
      std::filesystem::path(record_mode) / "RESULT";
  require(::chmod(result_path.c_str(), S_IRUSR | S_IWUSR) == 0,
          "record mode mutation failed");
  require(canary::reopen(record_mode).state ==
              canary::ReopenState::malformed &&
              !canary::reconcile_effect_result(record_mode),
          "non-0400 record was accepted");
  witness << "record-mode\texact_0400_required=1\n";
  ++cases;

  // 17. openat2 rejects a symlink in an intermediate root-path component.
  const std::filesystem::path real_parent =
      std::filesystem::path(tree.path()) / "root-real-parent";
  const std::filesystem::path real_store = real_parent / "store";
  const std::filesystem::path alias_parent =
      std::filesystem::path(tree.path()) / "root-alias-parent";
  std::filesystem::create_directory(real_parent);
  std::filesystem::create_directory(real_store);
  require(::chmod(real_parent.c_str(), S_IRWXU) == 0 &&
              ::chmod(real_store.c_str(), S_IRWXU) == 0,
          "root symlink fixture chmod failed");
  prepare_pending(real_store.string(), op);
  require(::symlink(real_parent.c_str(), alias_parent.c_str()) == 0,
          "root symlink fixture failed");
  const std::string alias_store = (alias_parent / "store").string();
  require(canary::reopen(alias_store).state == canary::ReopenState::unsafe &&
              canary::claim_pending(alias_store, "claimant-root-symlink")
                      .disposition == canary::ClaimDisposition::unsafe,
          "intermediate root-path symlink was followed");
  witness << "root-symlink\tall_components_rejected=1\n";
  ++cases;

  // 18. A complete pending-history clone permits one effect in each copy.
  const std::string clone_source = tree.store("clone-source");
  prepare_pending(clone_source, op);
  const std::string clone_a = tree.copy_store("clone-a", clone_source);
  const std::string clone_b = tree.copy_store("clone-b", clone_source);
  complete_effect(clone_a, op, "claimant-clone-a", true);
  complete_effect(clone_b, op, "claimant-clone-b", true);
  const unsigned clone_effects =
      static_cast<unsigned>(canary::reopen(clone_a).state ==
                            canary::ReopenState::settled_effect) +
      static_cast<unsigned>(canary::reopen(clone_b).state ==
                            canary::ReopenState::settled_effect);
  require(clone_effects == 2U, "clone counterexample did not emit twice");
  witness << "clone\teffects=" << clone_effects << "\n";
  ++cases;

  // 19. Two restores of the same pending snapshot do the same.
  const std::string restore_source = tree.store("restore-source");
  prepare_pending(restore_source, op);
  const std::string restore_a = tree.copy_store("restore-a", restore_source);
  const std::string restore_b = tree.copy_store("restore-b", restore_source);
  complete_effect(restore_a, op, "claimant-restore-a", true);
  complete_effect(restore_b, op, "claimant-restore-b", true);
  const unsigned restored_effects =
      static_cast<unsigned>(canary::reopen(restore_a).state ==
                            canary::ReopenState::settled_effect) +
      static_cast<unsigned>(canary::reopen(restore_b).state ==
                            canary::ReopenState::settled_effect);
  require(restored_effects == 2U,
          "restore counterexample did not emit twice");
  witness << "restore\teffects=" << restored_effects << "\n";
  ++cases;

  // 20. Every fixed retained record is owner-bound, single-link, and 0400.
  for (const std::string_view name :
       {"INCARNATION", "INTENT", "CLAIM", "EFFECT", "RESULT"}) {
    require(fixed_record_safe(joined, name),
            "fixed record safety profile changed");
  }
  witness << "fixed-records\tregular=1\towner=1\tnlink=1\tmode=0400\n";
  ++cases;

  require(cases == 23U, "case cardinality changed");

  const std::string witness_text = witness.str();
  const std::string witness_digest = hex(sha256(as_bytes(witness_text)));
  std::cout
      << "RECIPIENT_CLAIM_CANARY_LINUX=PASS"
      << " cases=" << cases
      << " unjoined_observations=1"
      << " partial_join_rejections=1"
      << " claim_race_winners=1"
      << " response_authorizations=0"
      << " failed_meaning_burns=2"
      << " absent_claim_burns=1"
      << " malformed_claim_burns=1"
      << " wrong_incarnation_burns=1"
      << " claim_crash_uncertain=1"
      << " effect_crash_reconciled=1"
      << " stage_residue_inert=1"
      << " unsafe_root_rejections=1"
      << " symlink_rejections=1"
      << " claim_collision_rejections=1"
      << " result_binding_rejections=2"
      << " path_substitution_redirects=0"
      << " topology_rejections=1"
      << " exact_mode_rejections=1"
      << " parent_symlink_rejections=1"
      << " malformed_reconcile_rejections=4"
      << " clone_effects=" << clone_effects
      << " restored_effects=" << restored_effects
      << " max_effects_per_history=1"
      << " fixed_records=5"
      << " no_replace=true"
      << " claim_before_meaning=true"
      << " pinned_dirfd=true"
      << " path_reopen_after_claim=false"
      << " result_full_binding=true"
      << " exact_record_mode=true"
      << " all_component_symlink_rejection=true"
      << " mount_traversal_rejected=false"
      << " same_uid_writer_exclusion=false"
      << " external_join_instantiated=false"
      << " response_authority=false"
      << " independent_custody=false"
      << " rollback_independence=false"
      << " global_one_use_proved=false"
      << " authority_granted=false"
      << " witness_sha256=" << witness_digest << '\n';
  return 0;
}

#else
int main() { return 77; }
#endif
