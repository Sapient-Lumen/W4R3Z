#include "slopos/e0/recipient_claim_canary_linux.hpp"

#ifdef __linux__

#include <atomic>
#include <cerrno>
#include <cstdint>
#include <fcntl.h>
#include <linux/openat2.h>
#include <optional>
#include <sstream>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <unistd.h>
#include <utility>

#ifndef RENAME_NOREPLACE
#define RENAME_NOREPLACE (1U << 0U)
#endif

namespace slopos::e0::recipient_canary {
namespace {

constexpr std::size_t kMaximumRecord = 4096U;
constexpr std::string_view kIncarnationName = "INCARNATION";
constexpr std::string_view kIntentName = "INTENT";
constexpr std::string_view kClaimName = "CLAIM";
constexpr std::string_view kEffectName = "EFFECT";
constexpr std::string_view kResultName = "RESULT";
std::atomic<unsigned long long> g_stage_counter{0ULL};

class Fd final {
 public:
  explicit Fd(const int value = -1) noexcept : value_(value) {}
  Fd(const Fd&) = delete;
  Fd& operator=(const Fd&) = delete;
  Fd(Fd&& other) noexcept : value_(std::exchange(other.value_, -1)) {}
  Fd& operator=(Fd&& other) noexcept {
    if (this != &other) {
      reset();
      value_ = std::exchange(other.value_, -1);
    }
    return *this;
  }
  ~Fd() { reset(); }
  [[nodiscard]] int get() const noexcept { return value_; }
  [[nodiscard]] bool valid() const noexcept { return value_ >= 0; }
  [[nodiscard]] int release() noexcept { return std::exchange(value_, -1); }

 private:
  void reset() noexcept {
    if (value_ >= 0) {
      // On Linux, retrying close after EINTR can close a reused descriptor.
      (void)::close(value_);
      value_ = -1;
    }
  }
  int value_;
};

enum class ReadKind { missing, present, unsafe };
struct ReadResult final {
  ReadKind kind{ReadKind::unsafe};
  std::string bytes{};
};
enum class PublishKind { created, exists, unsafe };

[[nodiscard]] bool token(const std::string_view value) noexcept {
  if (value.empty() || value.size() > 128U) return false;
  for (const unsigned char ch : value) {
    const bool accepted =
        (ch >= 'a' && ch <= 'z') || (ch >= '0' && ch <= '9') ||
        ch == '.' || ch == '_' || ch == '-';
    if (!accepted) return false;
  }
  return true;
}

[[nodiscard]] bool digest(const std::string_view value) noexcept {
  if (value.size() != 64U) return false;
  for (const unsigned char ch : value) {
    if (!((ch >= '0' && ch <= '9') || (ch >= 'a' && ch <= 'f'))) {
      return false;
    }
  }
  return true;
}

[[nodiscard]] bool fixed_name(const std::string_view value) noexcept {
  if (value.empty() || value.size() > 64U) return false;
  for (const unsigned char ch : value) {
    if (!(ch >= 'A' && ch <= 'Z') && ch != '_') return false;
  }
  return true;
}

[[nodiscard]] bool safe_root_fd(const int root_fd) noexcept {
  struct stat st {};
  return root_fd >= 0 && ::fstat(root_fd, &st) == 0 &&
         S_ISDIR(st.st_mode) && st.st_uid == ::geteuid() &&
         (st.st_mode & 0777) == 0700;
}

[[nodiscard]] Fd open_safe_root(const std::string& root) noexcept {
  struct open_how how {};
  how.flags = static_cast<__u64>(O_RDONLY | O_DIRECTORY | O_CLOEXEC |
                                 O_NOFOLLOW);
  how.resolve = static_cast<__u64>(RESOLVE_NO_SYMLINKS |
                                   RESOLVE_NO_MAGICLINKS);
  const long opened = ::syscall(SYS_openat2, AT_FDCWD, root.c_str(), &how,
                                sizeof(how));
  if (opened < 0) return Fd{};
  Fd fd(static_cast<int>(opened));
  if (!safe_root_fd(fd.get())) return Fd{};
  return fd;
}

[[nodiscard]] bool write_all(const int fd,
                             const std::string_view bytes) noexcept {
  std::size_t offset = 0U;
  while (offset < bytes.size()) {
    const ssize_t written =
        ::write(fd, bytes.data() + offset, bytes.size() - offset);
    if (written < 0) {
      if (errno == EINTR) continue;
      return false;
    }
    if (written == 0) return false;
    offset += static_cast<std::size_t>(written);
  }
  return true;
}

[[nodiscard]] bool same_record_profile(const struct stat& first,
                                       const struct stat& second) noexcept {
  return first.st_dev == second.st_dev && first.st_ino == second.st_ino &&
         first.st_uid == second.st_uid && first.st_nlink == second.st_nlink &&
         first.st_mode == second.st_mode && first.st_size == second.st_size;
}

[[nodiscard]] ReadResult read_record(const int root_fd,
                                     const std::string_view name) noexcept {
  if (!safe_root_fd(root_fd) || !fixed_name(name)) return ReadResult{};
  const std::string path(name);
  Fd fd(::openat(root_fd, path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
  if (!fd.valid()) {
    if (errno == ENOENT) return ReadResult{ReadKind::missing, {}};
    return ReadResult{};
  }
  struct stat before {};
  if (::fstat(fd.get(), &before) != 0 || !S_ISREG(before.st_mode) ||
      before.st_uid != ::geteuid() || before.st_nlink != 1 ||
      (before.st_mode & 0777) != 0400 || before.st_size < 0 ||
      static_cast<std::uintmax_t>(before.st_size) > kMaximumRecord) {
    return ReadResult{};
  }
  std::string bytes(static_cast<std::size_t>(before.st_size), '\0');
  std::size_t offset = 0U;
  while (offset < bytes.size()) {
    const ssize_t amount =
        ::read(fd.get(), bytes.data() + offset, bytes.size() - offset);
    if (amount < 0) {
      if (errno == EINTR) continue;
      return ReadResult{};
    }
    if (amount == 0) return ReadResult{};
    offset += static_cast<std::size_t>(amount);
  }
  char extra{};
  ssize_t tail = -1;
  do {
    tail = ::read(fd.get(), &extra, 1U);
  } while (tail < 0 && errno == EINTR);
  if (tail != 0) return ReadResult{};
  struct stat after {};
  if (::fstat(fd.get(), &after) != 0 ||
      !same_record_profile(before, after)) {
    return ReadResult{};
  }
  return ReadResult{ReadKind::present, std::move(bytes)};
}

[[nodiscard]] PublishKind publish_no_replace(
    const int root_fd, const std::string_view name,
    const std::string_view bytes) noexcept {
  if (!safe_root_fd(root_fd) || !fixed_name(name) || bytes.empty() ||
      bytes.size() > kMaximumRecord) {
    return PublishKind::unsafe;
  }
  const auto serial = g_stage_counter.fetch_add(1ULL);
  std::ostringstream stage_builder;
  stage_builder << ".stage." << static_cast<unsigned long long>(::getpid())
                << '.' << serial;
  const std::string stage = stage_builder.str();
  Fd fd(::openat(root_fd, stage.c_str(),
                 O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW,
                 S_IRUSR | S_IWUSR));
  if (!fd.valid()) return PublishKind::unsafe;
  if (!write_all(fd.get(), bytes) || ::fchmod(fd.get(), S_IRUSR) != 0 ||
      ::fsync(fd.get()) != 0) {
    (void)::unlinkat(root_fd, stage.c_str(), 0);
    return PublishKind::unsafe;
  }

  const std::string fixed(name);
  long renamed = ::syscall(SYS_renameat2, root_fd, stage.c_str(), root_fd,
                           fixed.c_str(), RENAME_NOREPLACE);
  if (renamed != 0 && (errno == ENOSYS || errno == EINVAL)) {
    if (::linkat(root_fd, stage.c_str(), root_fd, fixed.c_str(), 0) == 0) {
      // The fallback is successful only after the staging alias is removed.
      // Otherwise the retained fixed record has link count two and the caller
      // must not receive a live permit derived from it.
      if (::unlinkat(root_fd, stage.c_str(), 0) == 0) {
        renamed = 0;
      } else {
        return PublishKind::unsafe;
      }
    }
  }
  if (renamed != 0) {
    const int saved = errno;
    (void)::unlinkat(root_fd, stage.c_str(), 0);
    if (saved == EEXIST) return PublishKind::exists;
    return PublishKind::unsafe;
  }
  if (::fsync(root_fd) != 0) return PublishKind::unsafe;
  return PublishKind::created;
}

[[nodiscard]] std::string intent_bytes(const Operation& operation) {
  return "SLOPOS-CANARY-INTENT-V1\nincarnation=" + operation.incarnation +
         "\noperation=" + operation.operation + "\nroute=" + operation.route +
         "\npayload_sha256=" + operation.payload_sha256 + "\n";
}

[[nodiscard]] std::string claim_bytes(const std::string_view claimant) {
  return "SLOPOS-CANARY-CLAIM-V1\nclaimant=" + std::string(claimant) + "\n";
}

[[nodiscard]] std::string effect_bytes(const Operation& operation) {
  return "SLOPOS-CANARY-EFFECT-V1\nincarnation=" + operation.incarnation +
         "\noperation=" + operation.operation + "\nroute=" + operation.route +
         "\npayload_sha256=" + operation.payload_sha256 + "\n";
}

[[nodiscard]] std::string result_bytes(const std::string_view result,
                                       const Operation& operation) {
  return "SLOPOS-CANARY-RESULT-V2\nresult=" + std::string(result) +
         "\nincarnation=" + operation.incarnation +
         "\noperation=" + operation.operation + "\nroute=" + operation.route +
         "\npayload_sha256=" + operation.payload_sha256 + "\n";
}

[[nodiscard]] std::optional<std::string> field(
    const std::string& bytes, const std::string_view key) {
  const std::string needle = std::string(key) + '=';
  const std::size_t start = bytes.find(needle);
  if (start == std::string::npos ||
      (start != 0U && bytes[start - 1U] != '\n')) {
    return std::nullopt;
  }
  const std::size_t value_start = start + needle.size();
  const std::size_t end = bytes.find('\n', value_start);
  if (end == std::string::npos) return std::nullopt;
  return bytes.substr(value_start, end - value_start);
}

[[nodiscard]] std::optional<Operation> parse_intent(
    const std::string& bytes) {
  if (!bytes.starts_with("SLOPOS-CANARY-INTENT-V1\n")) return std::nullopt;
  const auto incarnation = field(bytes, "incarnation");
  const auto operation = field(bytes, "operation");
  const auto route = field(bytes, "route");
  const auto payload = field(bytes, "payload_sha256");
  if (!incarnation || !operation || !route || !payload) return std::nullopt;
  Operation parsed{*incarnation, *operation, *route, *payload};
  if (!canonical(parsed) || intent_bytes(parsed) != bytes) return std::nullopt;
  return parsed;
}

[[nodiscard]] bool parse_incarnation(const std::string& bytes,
                                     std::string& value) {
  if (!bytes.starts_with("SLOPOS-CANARY-INCARNATION-V1\n")) return false;
  const auto parsed = field(bytes, "incarnation");
  if (!parsed || !token(*parsed) ||
      "SLOPOS-CANARY-INCARNATION-V1\nincarnation=" + *parsed + "\n" !=
          bytes) {
    return false;
  }
  value = *parsed;
  return true;
}

[[nodiscard]] bool claim_valid(const std::string& bytes) {
  if (!bytes.starts_with("SLOPOS-CANARY-CLAIM-V1\n")) return false;
  const auto claimant = field(bytes, "claimant");
  return claimant && token(*claimant) && claim_bytes(*claimant) == bytes;
}

[[nodiscard]] std::optional<Operation> parse_effect(
    const std::string& bytes) {
  if (!bytes.starts_with("SLOPOS-CANARY-EFFECT-V1\n")) return std::nullopt;
  const auto incarnation = field(bytes, "incarnation");
  const auto operation = field(bytes, "operation");
  const auto route = field(bytes, "route");
  const auto payload = field(bytes, "payload_sha256");
  if (!incarnation || !operation || !route || !payload) return std::nullopt;
  Operation parsed{*incarnation, *operation, *route, *payload};
  if (!canonical(parsed) || effect_bytes(parsed) != bytes) return std::nullopt;
  return parsed;
}

struct ParsedResult final {
  std::string result;
  Operation operation;
};

[[nodiscard]] std::optional<ParsedResult> parse_result(
    const std::string& bytes) {
  if (!bytes.starts_with("SLOPOS-CANARY-RESULT-V2\n")) return std::nullopt;
  const auto result = field(bytes, "result");
  const auto incarnation = field(bytes, "incarnation");
  const auto operation = field(bytes, "operation");
  const auto route = field(bytes, "route");
  const auto payload = field(bytes, "payload_sha256");
  if (!result || !incarnation || !operation || !route || !payload ||
      (*result != "effect" && *result != "no_effect")) {
    return std::nullopt;
  }
  Operation parsed{*incarnation, *operation, *route, *payload};
  if (!canonical(parsed) || result_bytes(*result, parsed) != bytes) {
    return std::nullopt;
  }
  return ParsedResult{*result, std::move(parsed)};
}

[[nodiscard]] bool retain_no_effect(const int root_fd,
                                    const Operation& operation) noexcept {
  const std::string bytes = result_bytes("no_effect", operation);
  const PublishKind published =
      publish_no_replace(root_fd, kResultName, bytes);
  if (published == PublishKind::created) return true;
  if (published != PublishKind::exists) return false;
  const ReadResult existing = read_record(root_fd, kResultName);
  return existing.kind == ReadKind::present && existing.bytes == bytes;
}

[[nodiscard]] bool exact_effect_chain(const int root_fd) noexcept {
  const ReadResult incarnation = read_record(root_fd, kIncarnationName);
  const ReadResult intent = read_record(root_fd, kIntentName);
  const ReadResult claim = read_record(root_fd, kClaimName);
  const ReadResult effect = read_record(root_fd, kEffectName);
  const ReadResult result = read_record(root_fd, kResultName);
  if (incarnation.kind != ReadKind::present ||
      intent.kind != ReadKind::present || claim.kind != ReadKind::present ||
      effect.kind != ReadKind::present || result.kind != ReadKind::present ||
      !claim_valid(claim.bytes)) {
    return false;
  }
  std::string retained_incarnation;
  const auto parsed_intent = parse_intent(intent.bytes);
  const auto parsed_effect = parse_effect(effect.bytes);
  const auto parsed_result = parse_result(result.bytes);
  return parse_incarnation(incarnation.bytes, retained_incarnation) &&
         parsed_intent && parsed_effect && parsed_result &&
         parsed_result->result == "effect" &&
         parsed_intent->incarnation == retained_incarnation &&
         *parsed_intent == *parsed_effect &&
         *parsed_intent == parsed_result->operation;
}

}  // namespace

ClaimPermit::ClaimPermit(const int root_fd, Operation operation)
    : root_fd_(root_fd), operation_(std::move(operation)) {}
ClaimPermit::ClaimPermit(ClaimPermit&& other) noexcept
    : root_fd_(std::exchange(other.root_fd_, -1)),
      operation_(std::move(other.operation_)),
      live_(std::exchange(other.live_, false)) {}
ClaimPermit& ClaimPermit::operator=(ClaimPermit&& other) noexcept {
  if (this != &other) {
    if (root_fd_ >= 0) (void)::close(root_fd_);
    root_fd_ = std::exchange(other.root_fd_, -1);
    operation_ = std::move(other.operation_);
    live_ = std::exchange(other.live_, false);
  }
  return *this;
}
ClaimPermit::~ClaimPermit() {
  if (root_fd_ >= 0) (void)::close(root_fd_);
}
ClaimPermit make_claim_permit(const int root_fd, Operation operation) {
  return ClaimPermit(root_fd, std::move(operation));
}

EffectPermit::EffectPermit(const int root_fd, Operation operation)
    : root_fd_(root_fd), operation_(std::move(operation)) {}
EffectPermit::EffectPermit(EffectPermit&& other) noexcept
    : root_fd_(std::exchange(other.root_fd_, -1)),
      operation_(std::move(other.operation_)),
      live_(std::exchange(other.live_, false)) {}
EffectPermit& EffectPermit::operator=(EffectPermit&& other) noexcept {
  if (this != &other) {
    if (root_fd_ >= 0) (void)::close(root_fd_);
    root_fd_ = std::exchange(other.root_fd_, -1);
    operation_ = std::move(other.operation_);
    live_ = std::exchange(other.live_, false);
  }
  return *this;
}
EffectPermit::~EffectPermit() {
  if (root_fd_ >= 0) (void)::close(root_fd_);
}
EffectPermit make_effect_permit(const int root_fd, Operation operation) {
  return EffectPermit(root_fd, std::move(operation));
}

bool canonical(const Operation& operation) noexcept {
  return token(operation.incarnation) && token(operation.operation) &&
         token(operation.route) && digest(operation.payload_sha256);
}

ClaimResult claim_pending(const std::string& root,
                          const std::string_view claimant) noexcept {
  if (!token(claimant)) return ClaimResult{ClaimDisposition::unsafe, {}};
  Fd root_fd = open_safe_root(root);
  if (!root_fd.valid()) return ClaimResult{ClaimDisposition::unsafe, {}};

  // The authority-consuming cut: publish before touching candidate meaning.
  const PublishKind claim =
      publish_no_replace(root_fd.get(), kClaimName, claim_bytes(claimant));
  if (claim == PublishKind::exists) {
    const ReadResult existing = read_record(root_fd.get(), kClaimName);
    if (existing.kind == ReadKind::present && claim_valid(existing.bytes)) {
      return ClaimResult{ClaimDisposition::duplicate, {}};
    }
    return ClaimResult{ClaimDisposition::unsafe, {}};
  }
  if (claim != PublishKind::created) {
    return ClaimResult{ClaimDisposition::unsafe, {}};
  }

  const ReadResult intent = read_record(root_fd.get(), kIntentName);
  if (intent.kind == ReadKind::missing) {
    return ClaimResult{ClaimDisposition::won_missing_intent, {}};
  }
  if (intent.kind != ReadKind::present) {
    return ClaimResult{ClaimDisposition::won_malformed_intent, {}};
  }
  const auto operation = parse_intent(intent.bytes);
  if (!operation) {
    return ClaimResult{ClaimDisposition::won_malformed_intent, {}};
  }

  const ReadResult incarnation = read_record(root_fd.get(), kIncarnationName);
  std::string retained_incarnation;
  if (incarnation.kind != ReadKind::present ||
      !parse_incarnation(incarnation.bytes, retained_incarnation)) {
    return ClaimResult{ClaimDisposition::won_malformed_intent, {}};
  }
  if (retained_incarnation != operation->incarnation) {
    return ClaimResult{ClaimDisposition::won_wrong_incarnation, {}};
  }

  ClaimResult result;
  result.disposition = ClaimDisposition::won_with_permit;
  result.permit.emplace(make_claim_permit(root_fd.release(), *operation));
  return result;
}

EnterResult enter_effect(ClaimPermit&& permit,
                         const Operation& expected) noexcept {
  // Consume the move-only authority before interpreting caller meaning.
  if (!permit.live_) {
    return EnterResult{EnterDisposition::invalid_permit, {}};
  }
  permit.live_ = false;
  Fd root_fd(std::exchange(permit.root_fd_, -1));
  Operation operation = std::move(permit.operation_);
  if (!safe_root_fd(root_fd.get())) {
    return EnterResult{EnterDisposition::unsafe, {}};
  }

  if (!canonical(expected)) {
    if (!retain_no_effect(root_fd.get(), operation)) {
      return EnterResult{EnterDisposition::unsafe, {}};
    }
    return EnterResult{EnterDisposition::rejected_noncanonical, {}};
  }
  if (!(expected == operation)) {
    if (!retain_no_effect(root_fd.get(), operation)) {
      return EnterResult{EnterDisposition::unsafe, {}};
    }
    return EnterResult{EnterDisposition::rejected_mismatch, {}};
  }

  EnterResult result;
  result.disposition = EnterDisposition::entered;
  result.permit.emplace(
      make_effect_permit(root_fd.release(), std::move(operation)));
  return result;
}

EffectResult emit_canary_effect(EffectPermit&& permit,
                                const bool retain_result) noexcept {
  if (!permit.live_) {
    return EffectResult{EffectDisposition::invalid_permit};
  }
  permit.live_ = false;
  Fd root_fd(std::exchange(permit.root_fd_, -1));
  Operation operation = std::move(permit.operation_);
  if (!safe_root_fd(root_fd.get())) {
    return EffectResult{EffectDisposition::unsafe};
  }

  const std::string bytes = effect_bytes(operation);
  const PublishKind effect =
      publish_no_replace(root_fd.get(), kEffectName, bytes);
  if (effect == PublishKind::unsafe) {
    return EffectResult{EffectDisposition::unsafe};
  }
  if (effect == PublishKind::exists) {
    const ReadResult existing = read_record(root_fd.get(), kEffectName);
    if (existing.kind != ReadKind::present || existing.bytes != bytes) {
      return EffectResult{EffectDisposition::conflict};
    }
  }

  if (retain_result) {
    const std::string result = result_bytes("effect", operation);
    const PublishKind retained =
        publish_no_replace(root_fd.get(), kResultName, result);
    if (retained == PublishKind::unsafe) {
      return EffectResult{EffectDisposition::unsafe};
    }
    if (retained == PublishKind::exists) {
      const ReadResult existing = read_record(root_fd.get(), kResultName);
      if (existing.kind != ReadKind::present || existing.bytes != result) {
        return EffectResult{EffectDisposition::conflict};
      }
    }
  }

  return EffectResult{effect == PublishKind::created
                          ? EffectDisposition::emitted
                          : EffectDisposition::already_exact};
}

ReopenResult reopen(const std::string& root) noexcept {
  Fd root_fd = open_safe_root(root);
  if (!root_fd.valid()) return ReopenResult{ReopenState::unsafe};

  const ReadResult incarnation = read_record(root_fd.get(), kIncarnationName);
  const ReadResult intent = read_record(root_fd.get(), kIntentName);
  const ReadResult claim = read_record(root_fd.get(), kClaimName);
  const ReadResult effect = read_record(root_fd.get(), kEffectName);
  const ReadResult result = read_record(root_fd.get(), kResultName);
  for (const ReadResult* record :
       {&incarnation, &intent, &claim, &effect, &result}) {
    if (record->kind == ReadKind::unsafe) {
      return ReopenResult{ReopenState::malformed};
    }
  }

  if (incarnation.kind == ReadKind::missing &&
      intent.kind == ReadKind::missing && claim.kind == ReadKind::missing &&
      effect.kind == ReadKind::missing && result.kind == ReadKind::missing) {
    // Absence is only an unjoined observation. It is never terminal no-effect.
    return ReopenResult{ReopenState::unjoined};
  }
  if (incarnation.kind != ReadKind::present) {
    return ReopenResult{ReopenState::malformed};
  }
  std::string retained_incarnation;
  if (!parse_incarnation(incarnation.bytes, retained_incarnation)) {
    return ReopenResult{ReopenState::malformed};
  }

  const bool has_intent = intent.kind == ReadKind::present;
  const bool has_claim = claim.kind == ReadKind::present;
  const bool has_effect = effect.kind == ReadKind::present;
  const bool has_result = result.kind == ReadKind::present;
  if (has_claim && !claim_valid(claim.bytes)) {
    return ReopenResult{ReopenState::malformed};
  }
  if ((has_effect || has_result) && (!has_claim || !has_intent)) {
    return ReopenResult{ReopenState::malformed};
  }

  const auto parsed_intent =
      has_intent ? parse_intent(intent.bytes) : std::optional<Operation>{};
  if (has_intent && !parsed_intent) {
    return ReopenResult{has_claim && !has_effect && !has_result
                            ? ReopenState::claimed_uncertain
                            : ReopenState::malformed};
  }
  if (parsed_intent &&
      parsed_intent->incarnation != retained_incarnation) {
    return ReopenResult{has_claim && !has_effect && !has_result
                            ? ReopenState::claimed_uncertain
                            : ReopenState::malformed};
  }

  const auto parsed_effect =
      has_effect ? parse_effect(effect.bytes) : std::optional<Operation>{};
  if (has_effect &&
      (!parsed_effect || !parsed_intent ||
       !(*parsed_effect == *parsed_intent))) {
    return ReopenResult{ReopenState::malformed};
  }

  if (has_result) {
    const auto parsed_result = parse_result(result.bytes);
    if (!parsed_result || !parsed_intent ||
        !(parsed_result->operation == *parsed_intent)) {
      return ReopenResult{ReopenState::malformed};
    }
    if (parsed_result->result == "effect" && parsed_effect &&
        *parsed_effect == *parsed_intent) {
      return ReopenResult{ReopenState::settled_effect};
    }
    if (parsed_result->result == "no_effect" && !has_effect) {
      return ReopenResult{ReopenState::settled_no_effect};
    }
    return ReopenResult{ReopenState::malformed};
  }

  if (has_effect) return ReopenResult{ReopenState::effect_unsettled};
  if (has_claim) return ReopenResult{ReopenState::claimed_uncertain};
  if (has_intent) return ReopenResult{ReopenState::pending};
  return ReopenResult{ReopenState::malformed};
}

bool reconcile_effect_result(const std::string& root) noexcept {
  Fd root_fd = open_safe_root(root);
  if (!root_fd.valid()) return false;

  const ReadResult result = read_record(root_fd.get(), kResultName);
  if (result.kind == ReadKind::unsafe) return false;
  if (result.kind == ReadKind::present) {
    return exact_effect_chain(root_fd.get());
  }

  const ReadResult incarnation = read_record(root_fd.get(), kIncarnationName);
  const ReadResult intent = read_record(root_fd.get(), kIntentName);
  const ReadResult claim = read_record(root_fd.get(), kClaimName);
  const ReadResult effect = read_record(root_fd.get(), kEffectName);
  if (incarnation.kind != ReadKind::present ||
      intent.kind != ReadKind::present || claim.kind != ReadKind::present ||
      effect.kind != ReadKind::present || !claim_valid(claim.bytes)) {
    return false;
  }

  std::string retained_incarnation;
  const auto parsed_intent = parse_intent(intent.bytes);
  const auto parsed_effect = parse_effect(effect.bytes);
  if (!parse_incarnation(incarnation.bytes, retained_incarnation) ||
      !parsed_intent || !parsed_effect ||
      parsed_intent->incarnation != retained_incarnation ||
      !(*parsed_intent == *parsed_effect)) {
    return false;
  }

  const std::string retained = result_bytes("effect", *parsed_effect);
  const PublishKind published =
      publish_no_replace(root_fd.get(), kResultName, retained);
  if (published == PublishKind::unsafe) return false;
  return exact_effect_chain(root_fd.get());
}

std::string_view to_string(const ClaimDisposition value) noexcept {
  switch (value) {
    case ClaimDisposition::won_with_permit: return "won_with_permit";
    case ClaimDisposition::duplicate: return "duplicate";
    case ClaimDisposition::won_missing_intent: return "won_missing_intent";
    case ClaimDisposition::won_malformed_intent:
      return "won_malformed_intent";
    case ClaimDisposition::won_wrong_incarnation:
      return "won_wrong_incarnation";
    case ClaimDisposition::unsafe: return "unsafe";
  }
  return "invalid";
}

std::string_view to_string(const EnterDisposition value) noexcept {
  switch (value) {
    case EnterDisposition::entered: return "entered";
    case EnterDisposition::rejected_mismatch: return "rejected_mismatch";
    case EnterDisposition::rejected_noncanonical:
      return "rejected_noncanonical";
    case EnterDisposition::invalid_permit: return "invalid_permit";
    case EnterDisposition::unsafe: return "unsafe";
  }
  return "invalid";
}

std::string_view to_string(const EffectDisposition value) noexcept {
  switch (value) {
    case EffectDisposition::emitted: return "emitted";
    case EffectDisposition::already_exact: return "already_exact";
    case EffectDisposition::conflict: return "conflict";
    case EffectDisposition::invalid_permit: return "invalid_permit";
    case EffectDisposition::unsafe: return "unsafe";
  }
  return "invalid";
}

std::string_view to_string(const ReopenState value) noexcept {
  switch (value) {
    case ReopenState::unjoined: return "unjoined";
    case ReopenState::pending: return "pending";
    case ReopenState::claimed_uncertain: return "claimed_uncertain";
    case ReopenState::effect_unsettled: return "effect_unsettled";
    case ReopenState::settled_effect: return "settled_effect";
    case ReopenState::settled_no_effect: return "settled_no_effect";
    case ReopenState::malformed: return "malformed";
    case ReopenState::unsafe: return "unsafe";
  }
  return "invalid";
}

}  // namespace slopos::e0::recipient_canary

#endif  // __linux__
