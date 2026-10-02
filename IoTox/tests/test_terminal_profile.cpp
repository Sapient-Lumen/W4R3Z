#include "test_harness.hpp"

#include "iotox/terminal_profile.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <cerrno>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fcntl.h>
#include <limits>
#include <locale>
#include <stdexcept>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <thread>
#include <unistd.h>
#include <utility>
#include <vector>

namespace {

using iotox::ErrorCode;
using iotox::terminal::Binding;
using iotox::terminal::CgroupAggregateLimits;
using iotox::terminal::CgroupPressureAdmissionLimits;
using iotox::terminal::CgroupResourceLimits;
using iotox::terminal::Dimensions;
using iotox::terminal::EnvironmentEntry;
using iotox::terminal::Profile;
using iotox::terminal::ProfileRegistry;
using iotox::terminal::ProfileStoreData;

class TempDirectory {
  public:
    TempDirectory() {
        std::string pattern =
            (std::filesystem::temp_directory_path() / "iotox-terminal-profile-XXXXXX").string();
        std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
        mutable_pattern.push_back('\0');
        char *created = ::mkdtemp(mutable_pattern.data());
        if (created == nullptr) {
            throw std::runtime_error(
                "mkdtemp failed: " + std::string(std::strerror(errno)));
        }
        path_ = created;
        if (::chmod(path_.c_str(), static_cast<mode_t>(0700)) != 0) {
            throw std::runtime_error(
                "chmod temporary directory failed: " +
                std::string(std::strerror(errno)));
        }
    }

    ~TempDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(path_, ignored);
    }

    TempDirectory(const TempDirectory &) = delete;
    TempDirectory &operator=(const TempDirectory &) = delete;

    [[nodiscard]] const std::filesystem::path &path() const noexcept { return path_; }

  private:
    std::filesystem::path path_;
};

Profile sample_profile() {
    Profile profile;
    profile.id = "maintenance-shell";
    profile.enabled = true;
    profile.arguments = {"/bin/echo", "fixed argument", "--not-remote"};
    profile.working_directory = "/tmp";
    profile.terminal_type = "xterm-256color";
    profile.inherited_environment = {"TZ", "LANG"};
    profile.environment = {
        EnvironmentEntry{"ZETA", "last"},
        EnvironmentEntry{"ALPHA", "first"},
    };
    profile.dimensions.minimum = Dimensions{20U, 5U};
    profile.dimensions.initial = Dimensions{100U, 30U};
    profile.dimensions.maximum = Dimensions{240U, 80U};
    profile.dimensions.allow_resize = true;
    profile.limits.cpu_seconds = 10U;
    profile.limits.address_space_bytes = 128U * 1024U * 1024U;
    profile.limits.file_size_bytes = 1024U * 1024U;
    profile.limits.open_files = 32U;
    profile.limits.processes = 8U;
    profile.hangup_grace = std::chrono::milliseconds{20};
    profile.terminate_grace = std::chrono::milliseconds{40};
    profile.kill_reap_grace = std::chrono::milliseconds{60};
    return profile;
}

Binding sample_binding() {
    Binding binding;
    for (std::size_t index = 0U; index < binding.principal_id.size(); ++index) {
        binding.principal_id[index] = static_cast<std::uint8_t>(index + 1U);
    }
    binding.profile_id = "maintenance-shell";
    binding.enabled = true;
    return binding;
}

void create_owner_only_directory(const std::filesystem::path &path) {
    if (::mkdir(path.c_str(), static_cast<mode_t>(0700)) != 0) {
        throw std::runtime_error(
            "mkdir failed for " + path.string() + ": " + std::strerror(errno));
    }
}

void write_record(
    const std::filesystem::path &path, const std::vector<std::uint8_t> &bytes) {
    const int descriptor = ::open(
        path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC,
        static_cast<mode_t>(0600));
    if (descriptor < 0) {
        throw std::runtime_error(
            "open failed for " + path.string() + ": " + std::strerror(errno));
    }
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count =
            ::write(descriptor, bytes.data() + offset, bytes.size() - offset);
        if (count > 0) {
            offset += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) {
            continue;
        }
        const int saved_errno = errno;
        static_cast<void>(::close(descriptor));
        throw std::runtime_error(
            "write failed for " + path.string() + ": " +
            std::strerror(saved_errno));
    }
    if (::close(descriptor) != 0) {
        throw std::runtime_error(
            "close failed for " + path.string() + ": " + std::strerror(errno));
    }
}

std::string principal_hex(const iotox::terminal::PrincipalId &principal) {
    static constexpr char digits[] = "0123456789abcdef";
    std::string encoded;
    encoded.reserve(principal.size() * 2U);
    for (const std::uint8_t byte : principal) {
        encoded.push_back(digits[byte >> 4U]);
        encoded.push_back(digits[byte & 0x0fU]);
    }
    return encoded;
}

struct StoreFixture {
    TempDirectory temporary;
    std::filesystem::path profiles;
    std::filesystem::path bindings;
    Profile profile{sample_profile()};
    Binding binding{sample_binding()};

    StoreFixture()
        : profiles(temporary.path() / "profiles"),
          bindings(temporary.path() / "bindings") {
        create_owner_only_directory(profiles);
        create_owner_only_directory(bindings);
        auto profile_bytes = iotox::terminal::encode_profile_record(profile);
        auto binding_bytes = iotox::terminal::encode_binding_record(binding);
        if (!profile_bytes.ok() || !binding_bytes.ok()) {
            throw std::runtime_error("unable to encode terminal profile fixture");
        }
        write_record(profiles / (profile.id + ".profile"), profile_bytes.value());
        write_record(
            bindings / (principal_hex(binding.principal_id) + ".binding"),
            binding_bytes.value());
    }
};

class GroupedNumberPunctuation final : public std::numpunct<char> {
  protected:
    [[nodiscard]] char do_thousands_sep() const override { return '_'; }
    [[nodiscard]] std::string do_grouping() const override { return "\3"; }
};

}  // namespace

IOTOX_TEST("terminal profile validates and canonicalizes strict records") {
    Profile profile = sample_profile();
    IOTOX_CHECK(iotox::terminal::validate_profile(profile).ok());

    auto encoded = iotox::terminal::encode_profile_record(profile);
    IOTOX_CHECK(encoded.ok());
    const std::string encoded_text(encoded.value().begin(), encoded.value().end());
    IOTOX_CHECK(encoded_text.starts_with("iotox-terminal-profile-v7\n"));
    IOTOX_CHECK(
        encoded_text.find("executable-sha256=none\n") != std::string::npos);
    IOTOX_CHECK(
        encoded_text.find("toolbox-sha256=none\n") != std::string::npos);
    IOTOX_CHECK(
        encoded_text.find("allow-privilege-escalation=0\n") !=
        std::string::npos);
    IOTOX_CHECK(
        encoded_text.find("cgroup-pids-max=none\n") != std::string::npos);
    IOTOX_CHECK(
        encoded_text.find("cgroup-memory-high-bytes=none\n") !=
        std::string::npos);
    IOTOX_CHECK(
        encoded_text.find("cgroup-io-device=none\n") != std::string::npos);
    IOTOX_CHECK(
        encoded_text.find("cgroup-io-rbps=none\n") != std::string::npos);
    IOTOX_CHECK(
        encoded_text.find("cgroup-io-wbps=none\n") != std::string::npos);
    IOTOX_CHECK(
        encoded_text.find("cgroup-io-riops=none\n") != std::string::npos);
    IOTOX_CHECK(
        encoded_text.find("cgroup-io-wiops=none\n") != std::string::npos);
    auto decoded = iotox::terminal::decode_profile_record(encoded.value());
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value().id == profile.id);
    IOTOX_CHECK(decoded.value().arguments == profile.arguments);
    IOTOX_CHECK(
        decoded.value().confinement ==
        iotox::terminal::ConfinementMode::baseline);
    IOTOX_CHECK(decoded.value().cgroup_limits.empty());
    IOTOX_CHECK(decoded.value().inherited_environment ==
                std::vector<std::string>({"LANG", "TZ"}));
    IOTOX_CHECK(decoded.value().environment ==
                std::vector<EnvironmentEntry>({
                    EnvironmentEntry{"ALPHA", "first"},
                    EnvironmentEntry{"ZETA", "last"},
                }));
    auto reencoded = iotox::terminal::encode_profile_record(decoded.value());
    IOTOX_CHECK(reencoded.ok());
    IOTOX_CHECK(reencoded.value() == encoded.value());

    Binding binding = sample_binding();
    auto binding_bytes = iotox::terminal::encode_binding_record(binding);
    IOTOX_CHECK(binding_bytes.ok());
    auto decoded_binding =
        iotox::terminal::decode_binding_record(binding_bytes.value());
    IOTOX_CHECK(decoded_binding.ok());
    IOTOX_CHECK(decoded_binding.value() == binding);
}

IOTOX_TEST("terminal profile v7 retains owner account groups and explicit privilege policy") {
    Profile profile = sample_profile();
    profile.identity.mode = iotox::terminal::IdentityMode::account;
    profile.identity.uid = 1000U;
    profile.identity.gid = 100U;
    profile.identity.clear_supplementary_groups = false;
    profile.identity.supplementary_groups = {1U, 17U};
    profile.confinement = iotox::terminal::ConfinementMode::compatibility;
    profile.allow_privilege_escalation = true;
    IOTOX_CHECK(iotox::terminal::validate_profile(profile).ok());

    auto encoded = iotox::terminal::encode_profile_record(profile);
    IOTOX_CHECK(encoded.ok());
    const std::string text(encoded.value().begin(), encoded.value().end());
    IOTOX_CHECK(text.starts_with("iotox-terminal-profile-v7\n"));
    IOTOX_CHECK(text.find("identity=account:1000:100\n") !=
                std::string::npos);
    IOTOX_CHECK(text.find(
                    "supplementary-group=1\n"
                    "supplementary-group=17\n"
                    "confinement=compatibility\n"
                    "allow-privilege-escalation=1\n") !=
                std::string::npos);
    auto decoded = iotox::terminal::decode_profile_record(encoded.value());
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value().identity == profile.identity);
    IOTOX_CHECK(decoded.value().allow_privilege_escalation);
    auto reencoded =
        iotox::terminal::encode_profile_record(decoded.value());
    IOTOX_CHECK(reencoded.ok());
    IOTOX_CHECK(reencoded.value() == encoded.value());

    profile.confinement = iotox::terminal::ConfinementMode::baseline;
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());
    profile.confinement = iotox::terminal::ConfinementMode::compatibility;
    profile.identity.uid = 0U;
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());
    profile.identity.uid = 1000U;
    profile.allow_privilege_escalation = false;
    profile.identity.supplementary_groups = {17U, 1U};
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());
    profile.identity.supplementary_groups = {1U, 1U};
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());
    profile.identity.supplementary_groups = {100U};
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());
    profile.identity.supplementary_groups = {1U};
    profile.identity.clear_supplementary_groups = true;
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());
}

IOTOX_TEST("terminal profile v7 binds exact shell and rescue toolbox digests") {
    Profile profile = sample_profile();
    iotox::terminal::ExecutableDigest shell_digest{};
    iotox::terminal::ExecutableDigest toolbox_digest{};
    for (std::size_t index = 0U; index < shell_digest.size(); ++index) {
        shell_digest[index] = static_cast<std::uint8_t>(index);
        toolbox_digest[index] = static_cast<std::uint8_t>(0xffU - index);
    }
    profile.executable_sha256 = shell_digest;
    profile.toolbox_sha256 = toolbox_digest;
    profile.environment.push_back(
        EnvironmentEntry{"IOTOX_RESCUE_TOOLBOX", "/opt/iotox-rescue/bin"});
    IOTOX_CHECK(iotox::terminal::validate_profile(profile).ok());

    auto encoded = iotox::terminal::encode_profile_record(profile);
    IOTOX_CHECK(encoded.ok());
    const std::string text(encoded.value().begin(), encoded.value().end());
    IOTOX_CHECK(text.find(
                    "executable-sha256="
                    "000102030405060708090a0b0c0d0e0f"
                    "101112131415161718191a1b1c1d1e1f\n") !=
                std::string::npos);
    IOTOX_CHECK(text.find(
                    "toolbox-sha256="
                    "fffefdfcfbfaf9f8f7f6f5f4f3f2f1f0"
                    "efeeedecebeae9e8e7e6e5e4e3e2e1e0\n") !=
                std::string::npos);
    auto decoded = iotox::terminal::decode_profile_record(encoded.value());
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value().executable_sha256 == shell_digest);
    IOTOX_CHECK(decoded.value().toolbox_sha256 == toolbox_digest);
    IOTOX_CHECK(iotox::terminal::encode_profile_record(decoded.value()).value() ==
                encoded.value());

    profile.environment.erase(
        std::remove_if(
            profile.environment.begin(), profile.environment.end(),
            [](const EnvironmentEntry &entry) {
                return entry.name == "IOTOX_RESCUE_TOOLBOX";
            }),
        profile.environment.end());
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());
    profile.toolbox_sha256.reset();
    IOTOX_CHECK(iotox::terminal::validate_profile(profile).ok());
}

IOTOX_TEST("terminal profile migrates canonical v1 through v6 records to v7") {
    const long page_size = ::sysconf(_SC_PAGESIZE);
    IOTOX_CHECK(page_size > 0);
    Profile source = sample_profile();
    source.cgroup_limits.maximum_processes = 7U;
    source.cgroup_limits.maximum_memory_bytes =
        static_cast<std::uint64_t>(page_size) * 16U;
    source.cgroup_limits.maximum_swap_bytes = 0U;
    source.cgroup_limits.cpu_quota_microseconds = 25000U;
    source.cgroup_limits.cpu_period_microseconds = 100000U;
    auto encoded = iotox::terminal::encode_profile_record(source);
    IOTOX_CHECK(encoded.ok());

    const std::string v7_header = "iotox-terminal-profile-v7\n";
    const std::string v6_header = "iotox-terminal-profile-v6\n";
    const std::string v5_header = "iotox-terminal-profile-v5\n";
    const std::string v4_header = "iotox-terminal-profile-v4\n";
    const std::string v3_header = "iotox-terminal-profile-v3\n";
    const std::string v2_header = "iotox-terminal-profile-v2\n";
    const std::string v1_header = "iotox-terminal-profile-v1\n";

    std::string canonical_v6(encoded.value().begin(), encoded.value().end());
    IOTOX_CHECK(canonical_v6.starts_with(v7_header));
    canonical_v6.replace(0U, v7_header.size(), v6_header);
    for (const std::string_view key : {
             "executable-sha256=", "toolbox-sha256="}) {
        const std::size_t offset = canonical_v6.find(key);
        IOTOX_CHECK(offset != std::string::npos);
        const std::size_t end = canonical_v6.find('\n', offset);
        IOTOX_CHECK(end != std::string::npos);
        canonical_v6.erase(offset, end - offset + 1U);
    }
    const std::vector<std::uint8_t> v6_bytes(
        canonical_v6.begin(), canonical_v6.end());
    auto decoded_v6 = iotox::terminal::decode_profile_record(v6_bytes);
    IOTOX_CHECK(decoded_v6.ok());
    IOTOX_CHECK(!decoded_v6.value().executable_sha256.has_value());
    IOTOX_CHECK(!decoded_v6.value().toolbox_sha256.has_value());
    auto migrated_v6 =
        iotox::terminal::encode_profile_record(decoded_v6.value());
    IOTOX_CHECK(migrated_v6.ok());
    const std::string migrated_v6_text(
        migrated_v6.value().begin(), migrated_v6.value().end());
    IOTOX_CHECK(migrated_v6_text.starts_with(v7_header));

    std::string canonical_v5 = canonical_v6;
    canonical_v5.replace(0U, v6_header.size(), v5_header);
    const std::string privilege = "allow-privilege-escalation=0\n";
    const std::size_t privilege_offset = canonical_v5.find(privilege);
    IOTOX_CHECK(privilege_offset != std::string::npos);
    canonical_v5.erase(privilege_offset, privilege.size());
    const std::vector<std::uint8_t> v5_bytes(
        canonical_v5.begin(), canonical_v5.end());
    auto decoded_v5 = iotox::terminal::decode_profile_record(v5_bytes);
    IOTOX_CHECK(decoded_v5.ok());
    IOTOX_CHECK(!decoded_v5.value().allow_privilege_escalation);
    auto migrated_v5 =
        iotox::terminal::encode_profile_record(decoded_v5.value());
    IOTOX_CHECK(migrated_v5.ok());
    const std::string migrated_v5_text(
        migrated_v5.value().begin(), migrated_v5.value().end());
    IOTOX_CHECK(migrated_v5_text.starts_with(v7_header));

    std::string canonical_v4 = canonical_v5;
    canonical_v4.replace(0U, v5_header.size(), v4_header);
    for (const std::string_view key : {
             "cgroup-io-device=",
             "cgroup-io-rbps=",
             "cgroup-io-wbps=",
             "cgroup-io-riops=",
             "cgroup-io-wiops="}) {
        const std::size_t offset = canonical_v4.find(key);
        IOTOX_CHECK(offset != std::string::npos);
        const std::size_t end = canonical_v4.find('\n', offset);
        IOTOX_CHECK(end != std::string::npos);
        canonical_v4.erase(offset, end - offset + 1U);
    }
    const std::vector<std::uint8_t> v4_bytes(
        canonical_v4.begin(), canonical_v4.end());
    auto decoded_v4 = iotox::terminal::decode_profile_record(v4_bytes);
    IOTOX_CHECK(decoded_v4.ok());
    IOTOX_CHECK(!decoded_v4.value().cgroup_limits.io_device.has_value());
    IOTOX_CHECK(
        !decoded_v4.value().cgroup_limits
             .maximum_io_read_bytes_per_second.has_value());
    auto migrated_v4 =
        iotox::terminal::encode_profile_record(decoded_v4.value());
    IOTOX_CHECK(migrated_v4.ok());
    const std::string migrated_v4_text(
        migrated_v4.value().begin(), migrated_v4.value().end());
    IOTOX_CHECK(migrated_v4_text.starts_with(v7_header));

    std::string canonical_v3 = canonical_v4;
    canonical_v3.replace(0U, v4_header.size(), v3_header);
    const std::string memory_high = "cgroup-memory-high-bytes=none\n";
    const std::size_t memory_high_offset = canonical_v3.find(memory_high);
    IOTOX_CHECK(memory_high_offset != std::string::npos);
    canonical_v3.erase(memory_high_offset, memory_high.size());

    const std::vector<std::uint8_t> v3_bytes(
        canonical_v3.begin(), canonical_v3.end());
    auto decoded_v3 = iotox::terminal::decode_profile_record(v3_bytes);
    IOTOX_CHECK(decoded_v3.ok());
    IOTOX_CHECK(
        !decoded_v3.value().cgroup_limits.maximum_memory_high_bytes.has_value());
    IOTOX_CHECK(
        decoded_v3.value().cgroup_limits.maximum_processes ==
        source.cgroup_limits.maximum_processes);
    IOTOX_CHECK(
        decoded_v3.value().cgroup_limits.maximum_memory_bytes ==
        source.cgroup_limits.maximum_memory_bytes);
    IOTOX_CHECK(
        decoded_v3.value().cgroup_limits.maximum_swap_bytes ==
        source.cgroup_limits.maximum_swap_bytes);
    IOTOX_CHECK(
        decoded_v3.value().cgroup_limits.cpu_quota_microseconds ==
        source.cgroup_limits.cpu_quota_microseconds);
    IOTOX_CHECK(
        decoded_v3.value().cgroup_limits.cpu_period_microseconds ==
        source.cgroup_limits.cpu_period_microseconds);
    auto migrated_v3 =
        iotox::terminal::encode_profile_record(decoded_v3.value());
    IOTOX_CHECK(migrated_v3.ok());
    const std::string migrated_v3_text(
        migrated_v3.value().begin(), migrated_v3.value().end());
    IOTOX_CHECK(migrated_v3_text.starts_with(v7_header));

    std::string canonical_v2 = canonical_v3;
    canonical_v2.replace(0U, v3_header.size(), v2_header);
    for (const std::string_view key : {
             "cgroup-pids-max=",
             "cgroup-memory-max-bytes=",
             "cgroup-swap-max-bytes=",
             "cgroup-cpu-quota-us=",
             "cgroup-cpu-period-us="}) {
        const std::size_t offset = canonical_v2.find(key);
        IOTOX_CHECK(offset != std::string::npos);
        const std::size_t end = canonical_v2.find('\n', offset);
        IOTOX_CHECK(end != std::string::npos);
        canonical_v2.erase(offset, end - offset + 1U);
    }

    const std::vector<std::uint8_t> v2_bytes(
        canonical_v2.begin(), canonical_v2.end());
    auto decoded_v2 = iotox::terminal::decode_profile_record(v2_bytes);
    IOTOX_CHECK(decoded_v2.ok());
    IOTOX_CHECK(
        decoded_v2.value().confinement ==
        iotox::terminal::ConfinementMode::baseline);
    IOTOX_CHECK(decoded_v2.value().cgroup_limits.empty());
    auto migrated_v2 =
        iotox::terminal::encode_profile_record(decoded_v2.value());
    IOTOX_CHECK(migrated_v2.ok());
    const std::string migrated_v2_text(
        migrated_v2.value().begin(), migrated_v2.value().end());
    IOTOX_CHECK(migrated_v2_text.starts_with(v7_header));

    std::string canonical_v1 = canonical_v2;
    canonical_v1.replace(0U, v2_header.size(), v1_header);
    const std::string confinement = "confinement=baseline\n";
    const std::size_t field = canonical_v1.find(confinement);
    IOTOX_CHECK(field != std::string::npos);
    canonical_v1.erase(field, confinement.size());

    const std::vector<std::uint8_t> bytes(
        canonical_v1.begin(), canonical_v1.end());
    auto decoded = iotox::terminal::decode_profile_record(bytes);
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(
        decoded.value().confinement ==
        iotox::terminal::ConfinementMode::compatibility);
    IOTOX_CHECK(decoded.value().cgroup_limits.empty());

    auto migrated = iotox::terminal::encode_profile_record(decoded.value());
    IOTOX_CHECK(migrated.ok());
    const std::string migrated_text(
        migrated.value().begin(), migrated.value().end());
    IOTOX_CHECK(migrated_text.starts_with(v7_header));
    IOTOX_CHECK(
        migrated_text.find("confinement=compatibility\n") != std::string::npos);
}

IOTOX_TEST("terminal profile v7 round trips profile-scoped cgroup and I/O budgets") {
    const long page_size = ::sysconf(_SC_PAGESIZE);
    IOTOX_CHECK(page_size > 0);
    const auto page = static_cast<std::uint64_t>(page_size);

    Profile profile = sample_profile();
    profile.cgroup_limits.maximum_processes = 7U;
    profile.cgroup_limits.maximum_memory_high_bytes = 16384U * page;
    profile.cgroup_limits.maximum_memory_bytes = 32768U * page;
    profile.cgroup_limits.maximum_swap_bytes = 0U;
    profile.cgroup_limits.cpu_quota_microseconds = 25000U;
    profile.cgroup_limits.cpu_period_microseconds = 100000U;
    profile.cgroup_limits.io_device =
        iotox::terminal::CgroupIoDevice{8U, 16U};
    profile.cgroup_limits.maximum_io_read_bytes_per_second = 2097152U;
    profile.cgroup_limits.maximum_io_write_bytes_per_second = 1048576U;
    profile.cgroup_limits.maximum_io_read_operations_per_second = 200U;
    profile.cgroup_limits.maximum_io_write_operations_per_second = 100U;

    auto encoded = iotox::terminal::encode_profile_record(profile);
    IOTOX_CHECK(encoded.ok());
    const std::string text(encoded.value().begin(), encoded.value().end());
    IOTOX_CHECK(text.starts_with("iotox-terminal-profile-v7\n"));
    IOTOX_CHECK(text.find("cgroup-pids-max=7\n") != std::string::npos);
    IOTOX_CHECK(
        text.find("cgroup-memory-high-bytes=" +
                  std::to_string(16384U * page) + "\n") !=
        std::string::npos);
    IOTOX_CHECK(text.find("cgroup-swap-max-bytes=0\n") != std::string::npos);
    IOTOX_CHECK(text.find("cgroup-io-device=8:16\n") != std::string::npos);
    IOTOX_CHECK(text.find("cgroup-io-rbps=2097152\n") != std::string::npos);
    IOTOX_CHECK(text.find("cgroup-io-wbps=1048576\n") != std::string::npos);
    IOTOX_CHECK(text.find("cgroup-io-riops=200\n") != std::string::npos);
    IOTOX_CHECK(text.find("cgroup-io-wiops=100\n") != std::string::npos);

    auto decoded = iotox::terminal::decode_profile_record(encoded.value());
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value().cgroup_limits == profile.cgroup_limits);
    auto reencoded = iotox::terminal::encode_profile_record(decoded.value());
    IOTOX_CHECK(reencoded.ok());
    IOTOX_CHECK(reencoded.value() == encoded.value());
}

IOTOX_TEST("terminal cgroup budget composition preserves the stricter policy") {
    const long page_size = ::sysconf(_SC_PAGESIZE);
    IOTOX_CHECK(page_size > 0);
    const auto page = static_cast<std::uint64_t>(page_size);

    CgroupResourceLimits host;
    host.maximum_processes = 64U;
    host.maximum_memory_high_bytes = 384U * page;
    host.maximum_memory_bytes = 512U * page;
    host.maximum_swap_bytes = 4U * page;
    host.cpu_quota_microseconds = 50000U;
    host.cpu_period_microseconds = 100000U;
    host.io_device = iotox::terminal::CgroupIoDevice{8U, 16U};
    host.maximum_io_read_bytes_per_second = 10U * 1024U * 1024U;
    host.maximum_io_write_bytes_per_second = 5U * 1024U * 1024U;
    host.maximum_io_read_operations_per_second = 1000U;

    CgroupResourceLimits profile;
    profile.maximum_processes = 32U;
    profile.maximum_memory_high_bytes = 768U * page;
    profile.maximum_memory_bytes = 1024U * page;
    profile.maximum_swap_bytes = 0U;
    profile.cpu_quota_microseconds = 30000U;
    profile.cpu_period_microseconds = 100000U;
    profile.io_device = iotox::terminal::CgroupIoDevice{8U, 16U};
    profile.maximum_io_read_bytes_per_second = 8U * 1024U * 1024U;
    profile.maximum_io_write_bytes_per_second = 6U * 1024U * 1024U;
    profile.maximum_io_read_operations_per_second = 1200U;
    profile.maximum_io_write_operations_per_second = 400U;

    auto effective =
        iotox::terminal::compose_cgroup_resource_limits(host, profile);
    IOTOX_CHECK(effective.ok());
    IOTOX_CHECK(effective.value().maximum_processes == 32U);
    IOTOX_CHECK(
        effective.value().maximum_memory_high_bytes == 384U * page);
    IOTOX_CHECK(effective.value().maximum_memory_bytes == 512U * page);
    IOTOX_CHECK(effective.value().maximum_swap_bytes == 0U);
    IOTOX_CHECK(effective.value().cpu_quota_microseconds == 30000U);
    IOTOX_CHECK(effective.value().cpu_period_microseconds == 100000U);
    IOTOX_CHECK((
        effective.value().io_device ==
        iotox::terminal::CgroupIoDevice{8U, 16U}));
    IOTOX_CHECK(
        effective.value().maximum_io_read_bytes_per_second ==
        8U * 1024U * 1024U);
    IOTOX_CHECK(
        effective.value().maximum_io_write_bytes_per_second ==
        5U * 1024U * 1024U);
    IOTOX_CHECK(
        effective.value().maximum_io_read_operations_per_second == 1000U);
    IOTOX_CHECK(
        effective.value().maximum_io_write_operations_per_second == 400U);

    CgroupResourceLimits empty;
    auto inherited_host =
        iotox::terminal::compose_cgroup_resource_limits(host, empty);
    IOTOX_CHECK(inherited_host.ok());
    IOTOX_CHECK(inherited_host.value() == host);
    auto inherited_profile =
        iotox::terminal::compose_cgroup_resource_limits(empty, profile);
    IOTOX_CHECK(inherited_profile.ok());
    IOTOX_CHECK(inherited_profile.value() == profile);

    CgroupResourceLimits hard_host;
    hard_host.maximum_memory_bytes = 128U * page;
    CgroupResourceLimits soft_profile;
    soft_profile.maximum_memory_high_bytes = 256U * page;
    auto clamped = iotox::terminal::compose_cgroup_resource_limits(
        hard_host, soft_profile);
    IOTOX_CHECK(clamped.ok());
    IOTOX_CHECK(clamped.value().maximum_memory_bytes == 128U * page);
    IOTOX_CHECK(
        clamped.value().maximum_memory_high_bytes == 128U * page);

    CgroupResourceLimits equal_ratio;
    equal_ratio.cpu_quota_microseconds = 250000U;
    equal_ratio.cpu_period_microseconds = 500000U;
    auto equal =
        iotox::terminal::compose_cgroup_resource_limits(host, equal_ratio);
    IOTOX_CHECK(equal.ok());
    IOTOX_CHECK(equal.value().cpu_quota_microseconds == 50000U);
    IOTOX_CHECK(equal.value().cpu_period_microseconds == 100000U);

    CgroupResourceLimits huge_host;
    huge_host.cpu_quota_microseconds = static_cast<std::uint64_t>(
        std::numeric_limits<std::int64_t>::max());
    huge_host.cpu_period_microseconds = 1000000U;
    CgroupResourceLimits huge_profile;
    huge_profile.cpu_quota_microseconds = static_cast<std::uint64_t>(
        std::numeric_limits<std::int64_t>::max() - 1);
    huge_profile.cpu_period_microseconds = 999999U;
    auto exact = iotox::terminal::compose_cgroup_resource_limits(
        huge_host, huge_profile);
    IOTOX_CHECK(exact.ok());
    IOTOX_CHECK(
        exact.value().cpu_quota_microseconds ==
        huge_host.cpu_quota_microseconds);
    IOTOX_CHECK(
        exact.value().cpu_period_microseconds ==
        huge_host.cpu_period_microseconds);

    auto exact_reverse = iotox::terminal::compose_cgroup_resource_limits(
        huge_profile, huge_host);
    IOTOX_CHECK(exact_reverse.ok());
    IOTOX_CHECK(
        exact_reverse.value().cpu_quota_microseconds ==
        huge_host.cpu_quota_microseconds);
    IOTOX_CHECK(
        exact_reverse.value().cpu_period_microseconds ==
        huge_host.cpu_period_microseconds);

    CgroupResourceLimits mismatched = profile;
    mismatched.io_device = iotox::terminal::CgroupIoDevice{8U, 0U};
    IOTOX_CHECK(
        !iotox::terminal::compose_cgroup_resource_limits(host, mismatched).ok());
}

IOTOX_TEST("terminal aggregate cgroup reservation policy is exact and fail closed") {
    const long page_size = ::sysconf(_SC_PAGESIZE);
    IOTOX_CHECK(page_size > 0);
    const auto page = static_cast<std::uint64_t>(page_size);

    CgroupAggregateLimits aggregate;
    aggregate.maximum_reserved_processes = 32U;
    aggregate.maximum_reserved_memory_bytes = 64U * page;
    aggregate.maximum_reserved_swap_bytes = 0U;
    IOTOX_CHECK(
        iotox::terminal::validate_cgroup_aggregate_limits(aggregate).ok());

    CgroupResourceLimits session;
    session.maximum_processes = 8U;
    session.maximum_memory_bytes = 16U * page;
    session.maximum_swap_bytes = 0U;
    IOTOX_CHECK(iotox::terminal::validate_cgroup_aggregate_reservation(
                    aggregate, session)
                    .ok());

    CgroupResourceLimits missing = session;
    missing.maximum_memory_bytes.reset();
    const iotox::Status missing_result =
        iotox::terminal::validate_cgroup_aggregate_reservation(
            aggregate, missing);
    IOTOX_CHECK(!missing_result.ok());
    IOTOX_CHECK(missing_result.code() == ErrorCode::invalid_argument);
    IOTOX_CHECK(missing_result.message().find("finite per-session") !=
                std::string::npos);

    CgroupResourceLimits oversized = session;
    oversized.maximum_processes = 33U;
    const iotox::Status oversized_result =
        iotox::terminal::validate_cgroup_aggregate_reservation(
            aggregate, oversized);
    IOTOX_CHECK(!oversized_result.ok());
    IOTOX_CHECK(oversized_result.code() == ErrorCode::invalid_argument);
    IOTOX_CHECK(oversized_result.message().find("exceeds") !=
                std::string::npos);

    CgroupAggregateLimits unaligned;
    unaligned.maximum_reserved_memory_bytes = page + 1U;
    IOTOX_CHECK(!iotox::terminal::validate_cgroup_aggregate_limits(unaligned)
                     .ok());
}

IOTOX_TEST("terminal pressure admission policy validates exact hysteresis bounds") {
    CgroupPressureAdmissionLimits valid;
    valid.maximum_cpu_some_average_10_basis_points = 250U;
    valid.maximum_memory_full_average_10_basis_points = 100U;
    valid.hysteresis_basis_points = 75U;
    IOTOX_CHECK(
        iotox::terminal::validate_cgroup_pressure_admission_limits(valid).ok());

    CgroupPressureAdmissionLimits full_range;
    full_range.maximum_cpu_some_average_10_basis_points = 10000U;
    full_range.hysteresis_basis_points = 10000U;
    IOTOX_CHECK(iotox::terminal::validate_cgroup_pressure_admission_limits(
                    full_range)
                    .ok());

    CgroupPressureAdmissionLimits no_threshold;
    no_threshold.hysteresis_basis_points = 1U;
    auto detached =
        iotox::terminal::validate_cgroup_pressure_admission_limits(no_threshold);
    IOTOX_CHECK(!detached.ok());
    IOTOX_CHECK(detached.code() == ErrorCode::invalid_argument);

    CgroupPressureAdmissionLimits too_wide;
    too_wide.maximum_io_full_average_10_basis_points = 100U;
    too_wide.hysteresis_basis_points = 101U;
    auto wider =
        iotox::terminal::validate_cgroup_pressure_admission_limits(too_wide);
    IOTOX_CHECK(!wider.ok());
    IOTOX_CHECK(wider.code() == ErrorCode::invalid_argument);

    CgroupPressureAdmissionLimits percentage_overflow;
    percentage_overflow.maximum_cpu_some_average_10_basis_points = 10001U;
    auto overflow = iotox::terminal::validate_cgroup_pressure_admission_limits(
        percentage_overflow);
    IOTOX_CHECK(!overflow.ok());
    IOTOX_CHECK(overflow.code() == ErrorCode::invalid_argument);

    CgroupPressureAdmissionLimits triggers;
    triggers.maximum_cpu_some_average_10_basis_points = 500U;
    triggers.maximum_memory_full_average_10_basis_points = 250U;
    triggers.hysteresis_basis_points = 50U;
    triggers.trigger_window_microseconds = 2000000U;
    triggers.cpu_some_trigger_stall_microseconds = 250000U;
    triggers.memory_full_trigger_stall_microseconds = 100000U;
    IOTOX_CHECK(iotox::terminal::validate_cgroup_pressure_admission_limits(
                    triggers)
                    .ok());
    IOTOX_CHECK(!triggers.empty());
    IOTOX_CHECK(!triggers.triggers_empty());

    CgroupPressureAdmissionLimits missing_window = triggers;
    missing_window.trigger_window_microseconds.reset();
    IOTOX_CHECK(!iotox::terminal::validate_cgroup_pressure_admission_limits(
                     missing_window)
                     .ok());

    CgroupPressureAdmissionLimits detached_window;
    detached_window.trigger_window_microseconds = 2000000U;
    IOTOX_CHECK(!iotox::terminal::validate_cgroup_pressure_admission_limits(
                     detached_window)
                     .ok());

    CgroupPressureAdmissionLimits short_window = triggers;
    short_window.trigger_window_microseconds =
        iotox::terminal::kCgroupMinimumPressureTriggerWindowMicroseconds - 1U;
    IOTOX_CHECK(!iotox::terminal::validate_cgroup_pressure_admission_limits(
                     short_window)
                     .ok());

    CgroupPressureAdmissionLimits nonportable_window = triggers;
    nonportable_window.trigger_window_microseconds = 2500000U;
    IOTOX_CHECK(!iotox::terminal::validate_cgroup_pressure_admission_limits(
                     nonportable_window)
                     .ok());

    CgroupPressureAdmissionLimits long_window = triggers;
    long_window.trigger_window_microseconds =
        iotox::terminal::kCgroupMaximumPressureTriggerWindowMicroseconds + 1U;
    IOTOX_CHECK(!iotox::terminal::validate_cgroup_pressure_admission_limits(
                     long_window)
                     .ok());

    CgroupPressureAdmissionLimits zero_stall = triggers;
    zero_stall.cpu_some_trigger_stall_microseconds = 0U;
    IOTOX_CHECK(!iotox::terminal::validate_cgroup_pressure_admission_limits(
                     zero_stall)
                     .ok());

    CgroupPressureAdmissionLimits oversized_stall = triggers;
    oversized_stall.cpu_some_trigger_stall_microseconds = 2000001U;
    IOTOX_CHECK(!iotox::terminal::validate_cgroup_pressure_admission_limits(
                     oversized_stall)
                     .ok());

    CgroupPressureAdmissionLimits detached_metric = triggers;
    detached_metric.maximum_memory_full_average_10_basis_points.reset();
    IOTOX_CHECK(!iotox::terminal::validate_cgroup_pressure_admission_limits(
                     detached_metric)
                     .ok());
}

IOTOX_TEST("terminal aggregate CPU reservations normalize exact rational bandwidth") {
    CgroupAggregateLimits aggregate;
    aggregate.maximum_reserved_cpu_quota_microseconds = 300000U;
    aggregate.cpu_period_microseconds = 100000U;
    IOTOX_CHECK(
        iotox::terminal::validate_cgroup_aggregate_limits(aggregate).ok());

    CgroupResourceLimits session;
    session.cpu_quota_microseconds = 75000U;
    session.cpu_period_microseconds = 50000U;
    auto normalized = iotox::terminal::resolve_cgroup_aggregate_charge(
        aggregate, session);
    IOTOX_CHECK(normalized.ok());
    IOTOX_CHECK(
        normalized.value().reserved_cpu_quota_microseconds == 150000U);

    CgroupResourceLimits default_session_period;
    default_session_period.cpu_quota_microseconds = 50000U;
    auto default_session = iotox::terminal::resolve_cgroup_aggregate_charge(
        aggregate, default_session_period);
    IOTOX_CHECK(default_session.ok());
    IOTOX_CHECK(
        default_session.value().reserved_cpu_quota_microseconds == 50000U);

    CgroupAggregateLimits default_aggregate_period;
    default_aggregate_period.maximum_reserved_cpu_quota_microseconds = 100000U;
    CgroupResourceLimits half_cpu;
    half_cpu.cpu_quota_microseconds = 250000U;
    half_cpu.cpu_period_microseconds = 500000U;
    auto default_aggregate = iotox::terminal::resolve_cgroup_aggregate_charge(
        default_aggregate_period, half_cpu);
    IOTOX_CHECK(default_aggregate.ok());
    IOTOX_CHECK(
        default_aggregate.value().reserved_cpu_quota_microseconds == 50000U);

    CgroupResourceLimits missing_cpu;
    auto missing = iotox::terminal::resolve_cgroup_aggregate_charge(
        aggregate, missing_cpu);
    IOTOX_CHECK(!missing.ok());
    IOTOX_CHECK(missing.status().code() == ErrorCode::invalid_argument);
    IOTOX_CHECK(missing.status().message().find("finite per-session") !=
                std::string::npos);

    CgroupResourceLimits unrepresentable;
    unrepresentable.cpu_quota_microseconds = 1000U;
    unrepresentable.cpu_period_microseconds = 3000U;
    auto rounded = iotox::terminal::resolve_cgroup_aggregate_charge(
        aggregate, unrepresentable);
    IOTOX_CHECK(!rounded.ok());
    IOTOX_CHECK(rounded.status().code() == ErrorCode::invalid_argument);
    IOTOX_CHECK(rounded.status().message().find("exactly representable") !=
                std::string::npos);

    CgroupResourceLimits oversized;
    oversized.cpu_quota_microseconds = 300001U;
    oversized.cpu_period_microseconds = 100000U;
    auto exceeds = iotox::terminal::resolve_cgroup_aggregate_charge(
        aggregate, oversized);
    IOTOX_CHECK(!exceeds.ok());
    IOTOX_CHECK(exceeds.status().message().find("exceeds") !=
                std::string::npos);

    CgroupAggregateLimits period_without_quota;
    period_without_quota.cpu_period_microseconds = 100000U;
    IOTOX_CHECK(!iotox::terminal::validate_cgroup_aggregate_limits(
                     period_without_quota)
                     .ok());
    CgroupAggregateLimits too_small_quota;
    too_small_quota.maximum_reserved_cpu_quota_microseconds = 999U;
    IOTOX_CHECK(!iotox::terminal::validate_cgroup_aggregate_limits(
                     too_small_quota)
                     .ok());
    CgroupAggregateLimits too_large_period;
    too_large_period.maximum_reserved_cpu_quota_microseconds = 1000U;
    too_large_period.cpu_period_microseconds = 1000001U;
    IOTOX_CHECK(!iotox::terminal::validate_cgroup_aggregate_limits(
                     too_large_period)
                     .ok());

    CgroupAggregateLimits zero_aggregate_period;
    zero_aggregate_period.maximum_reserved_cpu_quota_microseconds = 1000U;
    zero_aggregate_period.cpu_period_microseconds = 0U;
    auto rejected_zero_aggregate_period =
        iotox::terminal::resolve_cgroup_aggregate_charge(
            zero_aggregate_period, session);
    IOTOX_CHECK(!rejected_zero_aggregate_period.ok());
    IOTOX_CHECK(
        rejected_zero_aggregate_period.status().code() ==
        ErrorCode::invalid_argument);

    CgroupResourceLimits zero_session_period = session;
    zero_session_period.cpu_period_microseconds = 0U;
    auto rejected_zero_session_period =
        iotox::terminal::resolve_cgroup_aggregate_charge(
            aggregate, zero_session_period);
    IOTOX_CHECK(!rejected_zero_session_period.ok());
    IOTOX_CHECK(
        rejected_zero_session_period.status().code() ==
        ErrorCode::invalid_argument);

    CgroupAggregateLimits scalar_only;
    scalar_only.maximum_reserved_processes = 4U;
    CgroupResourceLimits scalar_session;
    scalar_session.maximum_processes = 2U;
    scalar_session.cpu_quota_microseconds = 1000U;
    scalar_session.cpu_period_microseconds = 3000U;
    auto ignored_cpu = iotox::terminal::resolve_cgroup_aggregate_charge(
        scalar_only, scalar_session);
    IOTOX_CHECK(ignored_cpu.ok());
    IOTOX_CHECK(ignored_cpu.value().reserved_processes == 2U);
    IOTOX_CHECK(
        ignored_cpu.value().reserved_cpu_quota_microseconds == 0U);

    constexpr std::array<std::uint64_t, 4U> aggregate_periods{
        1000U, 3000U, 100000U, 1000000U};
    constexpr std::array<std::uint64_t, 5U> aggregate_quotas{
        1000U, 5000U, 100000U, 250000U, 1000000U};
    constexpr std::array<std::uint64_t, 8U> session_periods{
        1000U, 2000U, 3000U, 5000U,
        10000U, 100000U, 250000U, 1000000U};
    constexpr std::array<std::uint64_t, 7U> session_quotas{
        1000U, 1500U, 2000U, 3000U, 5000U, 10000U, 50000U};
    for (const std::uint64_t aggregate_period : aggregate_periods) {
        for (const std::uint64_t aggregate_quota : aggregate_quotas) {
            CgroupAggregateLimits lattice_aggregate;
            lattice_aggregate.maximum_reserved_cpu_quota_microseconds =
                aggregate_quota;
            lattice_aggregate.cpu_period_microseconds = aggregate_period;
            for (const std::uint64_t session_period : session_periods) {
                for (const std::uint64_t session_quota : session_quotas) {
                    CgroupResourceLimits lattice_session;
                    lattice_session.cpu_quota_microseconds = session_quota;
                    lattice_session.cpu_period_microseconds = session_period;
                    auto result =
                        iotox::terminal::resolve_cgroup_aggregate_charge(
                            lattice_aggregate, lattice_session);
                    const std::uint64_t normalized_numerator =
                        session_quota * aggregate_period;
                    const bool within_ceiling =
                        session_quota * aggregate_period <=
                        aggregate_quota * session_period;
                    const bool exactly_representable =
                        (normalized_numerator % session_period) == 0U;
                    if (within_ceiling && exactly_representable) {
                        IOTOX_CHECK(result.ok());
                        IOTOX_CHECK(
                            result.value()
                                .reserved_cpu_quota_microseconds ==
                            normalized_numerator / session_period);
                    } else {
                        IOTOX_CHECK(!result.ok());
                        IOTOX_CHECK(
                            result.status().code() ==
                            ErrorCode::invalid_argument);
                        if (!within_ceiling) {
                            IOTOX_CHECK(result.status().message().find(
                                            "exceeds") !=
                                        std::string::npos);
                        } else {
                            IOTOX_CHECK(result.status().message().find(
                                            "exactly representable") !=
                                        std::string::npos);
                        }
                    }
                }
            }
        }
    }
}

IOTOX_TEST("terminal canonical encoding ignores the process locale") {
    const Profile profile = sample_profile();
    const Binding binding = sample_binding();
    auto baseline_profile = iotox::terminal::encode_profile_record(profile);
    auto baseline_binding = iotox::terminal::encode_binding_record(binding);
    IOTOX_CHECK(baseline_profile.ok());
    IOTOX_CHECK(baseline_binding.ok());

    const std::locale original = std::locale();
    std::locale::global(
        std::locale(original, new GroupedNumberPunctuation));
    auto localized_profile = iotox::terminal::encode_profile_record(profile);
    auto localized_binding = iotox::terminal::encode_binding_record(binding);
    std::locale::global(original);

    IOTOX_CHECK(localized_profile.ok());
    IOTOX_CHECK(localized_binding.ok());
    IOTOX_CHECK(localized_profile.value() == baseline_profile.value());
    IOTOX_CHECK(localized_binding.value() == baseline_binding.value());
}

IOTOX_TEST("terminal profile rejects ambiguous paths identities and environment") {
    Profile profile = sample_profile();
    profile.arguments[0] = "/bin//echo";
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());

    profile = sample_profile();
    profile.arguments[0] = "/bin/../bin/echo";
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());

    profile = sample_profile();
    profile.inherited_environment.push_back("LD_PRELOAD");
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());

    profile = sample_profile();
    profile.environment.push_back(EnvironmentEntry{"TERM", "bad"});
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());

    profile = sample_profile();
    profile.identity.mode = iotox::terminal::IdentityMode::exact;
    profile.identity.uid = 1000U;
    profile.identity.gid = 1000U;
    profile.identity.clear_supplementary_groups = false;
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());

    profile = sample_profile();
    profile.confinement = iotox::terminal::ConfinementMode::strict;
    profile.working_directory = "/";
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());

    profile = sample_profile();
    profile.confinement =
        static_cast<iotox::terminal::ConfinementMode>(255U);
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());

    profile = sample_profile();
    profile.cgroup_limits.maximum_memory_high_bytes = 1U;
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());

    const long page_size = ::sysconf(_SC_PAGESIZE);
    IOTOX_CHECK(page_size > 0);
    profile = sample_profile();
    profile.cgroup_limits.maximum_memory_high_bytes =
        static_cast<std::uint64_t>(page_size) * 2U;
    profile.cgroup_limits.maximum_memory_bytes =
        static_cast<std::uint64_t>(page_size);
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());

    profile = sample_profile();
    profile.cgroup_limits.maximum_memory_bytes = 1U;
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());

    profile = sample_profile();
    profile.cgroup_limits.cpu_period_microseconds = 100000U;
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());


    profile = sample_profile();
    profile.cgroup_limits.io_device =
        iotox::terminal::CgroupIoDevice{8U, 16U};
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());

    profile = sample_profile();
    profile.cgroup_limits.maximum_io_read_bytes_per_second = 1U;
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());

    profile = sample_profile();
    profile.cgroup_limits.io_device =
        iotox::terminal::CgroupIoDevice{0U, 0U};
    profile.cgroup_limits.maximum_io_read_bytes_per_second = 1U;
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());

    profile = sample_profile();
    profile.cgroup_limits.io_device =
        iotox::terminal::CgroupIoDevice{8U, 16U};
    profile.cgroup_limits.maximum_io_read_bytes_per_second = 0U;
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());

    profile = sample_profile();
    profile.cgroup_limits.io_device =
        iotox::terminal::CgroupIoDevice{8U, 16U};
    profile.cgroup_limits.maximum_io_read_bytes_per_second =
        static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max()) +
        1U;
    IOTOX_CHECK(!iotox::terminal::validate_profile(profile).ok());
}

IOTOX_TEST("terminal profile decoder rejects noncanonical byte forms") {
    auto encoded = iotox::terminal::encode_profile_record(sample_profile());
    IOTOX_CHECK(encoded.ok());

    std::vector<std::uint8_t> missing_lf = encoded.value();
    missing_lf.pop_back();
    IOTOX_CHECK(!iotox::terminal::decode_profile_record(missing_lf).ok());

    std::vector<std::uint8_t> extra_lf = encoded.value();
    extra_lf.push_back(static_cast<std::uint8_t>('\n'));
    IOTOX_CHECK(!iotox::terminal::decode_profile_record(extra_lf).ok());

    std::vector<std::uint8_t> uppercase_hex = encoded.value();
    const std::string needle = "argument-hex=2f";
    auto found = std::search(
        uppercase_hex.begin(), uppercase_hex.end(), needle.begin(), needle.end());
    IOTOX_CHECK(found != uppercase_hex.end());
    *(found + static_cast<std::ptrdiff_t>(needle.size() - 1U)) =
        static_cast<std::uint8_t>('F');
    IOTOX_CHECK(!iotox::terminal::decode_profile_record(uppercase_hex).ok());

    std::string text(encoded.value().begin(), encoded.value().end());
    const std::size_t first = text.find("minimum-dimensions=");
    const std::size_t second = text.find("initial-dimensions=");
    IOTOX_CHECK(first != std::string::npos && second != std::string::npos && first < second);
    const std::size_t first_end = text.find('\n', first) + 1U;
    const std::size_t second_end = text.find('\n', second) + 1U;
    const std::string line_one = text.substr(first, first_end - first);
    const std::string line_two = text.substr(second, second_end - second);
    text.replace(second, second_end - second, line_one);
    text.replace(first, first_end - first, line_two);
    const std::vector<std::uint8_t> reordered(text.begin(), text.end());
    IOTOX_CHECK(!iotox::terminal::decode_profile_record(reordered).ok());

    std::string mixed_case(encoded.value().begin(), encoded.value().end());
    const std::string canonical_none = "cgroup-pids-max=none\n";
    const std::size_t none_offset = mixed_case.find(canonical_none);
    IOTOX_CHECK(none_offset != std::string::npos);
    mixed_case.replace(
        none_offset, canonical_none.size(), "cgroup-pids-max=None\n");
    const std::vector<std::uint8_t> mixed_case_bytes(
        mixed_case.begin(), mixed_case.end());
    IOTOX_CHECK(
        !iotox::terminal::decode_profile_record(mixed_case_bytes).ok());

    Profile budgeted = sample_profile();
    budgeted.cgroup_limits.maximum_processes = 7U;
    auto budgeted_encoded = iotox::terminal::encode_profile_record(budgeted);
    IOTOX_CHECK(budgeted_encoded.ok());
    std::string leading_zero(
        budgeted_encoded.value().begin(), budgeted_encoded.value().end());
    const std::string canonical_pids = "cgroup-pids-max=7\n";
    const std::size_t pids_offset = leading_zero.find(canonical_pids);
    IOTOX_CHECK(pids_offset != std::string::npos);
    leading_zero.replace(
        pids_offset, canonical_pids.size(), "cgroup-pids-max=07\n");
    const std::vector<std::uint8_t> leading_zero_bytes(
        leading_zero.begin(), leading_zero.end());
    IOTOX_CHECK(
        !iotox::terminal::decode_profile_record(leading_zero_bytes).ok());

    std::string period_without_quota(
        encoded.value().begin(), encoded.value().end());
    const std::string absent_period = "cgroup-cpu-period-us=none\n";
    const std::size_t period_offset =
        period_without_quota.find(absent_period);
    IOTOX_CHECK(period_offset != std::string::npos);
    period_without_quota.replace(
        period_offset, absent_period.size(),
        "cgroup-cpu-period-us=100000\n");
    const std::vector<std::uint8_t> period_without_quota_bytes(
        period_without_quota.begin(), period_without_quota.end());
    IOTOX_CHECK(
        !iotox::terminal::decode_profile_record(
             period_without_quota_bytes).ok());


    Profile io_budgeted = sample_profile();
    io_budgeted.cgroup_limits.io_device =
        iotox::terminal::CgroupIoDevice{8U, 16U};
    io_budgeted.cgroup_limits.maximum_io_read_bytes_per_second = 1U;
    auto io_encoded = iotox::terminal::encode_profile_record(io_budgeted);
    IOTOX_CHECK(io_encoded.ok());
    std::string alias_device(
        io_encoded.value().begin(), io_encoded.value().end());
    const std::string canonical_device = "cgroup-io-device=8:16\n";
    const std::size_t device_offset = alias_device.find(canonical_device);
    IOTOX_CHECK(device_offset != std::string::npos);
    alias_device.replace(
        device_offset, canonical_device.size(),
        "cgroup-io-device=08:16\n");
    const std::vector<std::uint8_t> alias_device_bytes(
        alias_device.begin(), alias_device.end());
    IOTOX_CHECK(
        !iotox::terminal::decode_profile_record(alias_device_bytes).ok());
}

IOTOX_TEST("terminal profile resolves only frozen allowlisted environment") {
    Profile profile = sample_profile();
    const std::array ambient{
        EnvironmentEntry{"LANG", "C.UTF-8"},
        EnvironmentEntry{"TZ", "UTC"},
        EnvironmentEntry{"PATH", "/untrusted-but-unselected"},
        EnvironmentEntry{"LD_PRELOAD", "/tmp/injected.so"},
    };
    auto resolved = iotox::terminal::resolve_environment(profile, ambient);
    IOTOX_CHECK(resolved.ok());
    const std::vector<EnvironmentEntry> expected{
        EnvironmentEntry{"ALPHA", "first"},
        EnvironmentEntry{"LANG", "C.UTF-8"},
        EnvironmentEntry{"TERM", "xterm-256color"},
        EnvironmentEntry{"TZ", "UTC"},
        EnvironmentEntry{"ZETA", "last"},
    };
    IOTOX_CHECK(resolved.value() == expected);

    const std::array duplicate{
        EnvironmentEntry{"LANG", "C"},
        EnvironmentEntry{"LANG", "C.UTF-8"},
    };
    auto ambiguous = iotox::terminal::resolve_environment(profile, duplicate);
    IOTOX_CHECK(!ambiguous.ok());
    IOTOX_CHECK(ambiguous.status().code() == ErrorCode::invalid_argument);
}

IOTOX_TEST("terminal dimension acceptance clamps both axes") {
    Profile profile = sample_profile();
    auto low = iotox::terminal::accept_dimensions(
        profile.dimensions, Dimensions{1U, 1U});
    IOTOX_CHECK(low.ok());
    IOTOX_CHECK(low.value() == profile.dimensions.minimum);

    auto high = iotox::terminal::accept_dimensions(
        profile.dimensions, Dimensions{1000U, 1000U});
    IOTOX_CHECK(high.ok());
    IOTOX_CHECK(high.value() == profile.dimensions.maximum);

    auto exact = iotox::terminal::accept_dimensions(
        profile.dimensions, Dimensions{120U, 40U});
    IOTOX_CHECK(exact.ok());
    IOTOX_CHECK((exact.value() == Dimensions{120U, 40U}));
}

IOTOX_TEST("terminal registry replacement is atomic and generation-bound") {
    Profile profile = sample_profile();
    Binding binding = sample_binding();
    ProfileRegistry registry;
    IOTOX_CHECK(registry.replace(ProfileStoreData{{profile}, {binding}}).ok());
    IOTOX_CHECK(registry.snapshot().generation == 1U);

    const std::array ambient{EnvironmentEntry{"LANG", "C"}};
    auto resolved = registry.resolve(
        binding.principal_id, Dimensions{500U, 2U}, ambient);
    IOTOX_CHECK(resolved.ok());
    IOTOX_CHECK(resolved.value().policy_generation == 1U);
    IOTOX_CHECK((resolved.value().accepted_dimensions == Dimensions{240U, 5U}));
    IOTOX_CHECK(resolved.value().profile.arguments[1] == "fixed argument");

    profile.arguments[1] = "mutated-after-commit";
    auto still_frozen = registry.resolve(
        binding.principal_id, Dimensions{80U, 24U}, ambient);
    IOTOX_CHECK(still_frozen.ok());
    IOTOX_CHECK(still_frozen.value().profile.arguments[1] == "fixed argument");

    Binding duplicate = binding;
    duplicate.profile_id = "maintenance-shell";
    const auto before = registry.snapshot();
    const auto rejected = registry.replace(
        ProfileStoreData{{sample_profile()}, {binding, duplicate}});
    IOTOX_CHECK(!rejected.ok());
    IOTOX_CHECK(registry.snapshot().generation == before.generation);
    IOTOX_CHECK(registry.snapshot().bindings == before.bindings);

    Profile disabled = sample_profile();
    disabled.enabled = false;
    IOTOX_CHECK(registry.replace(ProfileStoreData{{disabled}, {binding}}).ok());
    IOTOX_CHECK(registry.snapshot().generation == 2U);
    auto denied = registry.resolve(
        binding.principal_id, Dimensions{80U, 24U}, ambient);
    IOTOX_CHECK(!denied.ok());
    IOTOX_CHECK(denied.status().code() == ErrorCode::unavailable);
}

IOTOX_TEST("terminal registry publishes generation-coherent snapshots under concurrency") {
    ProfileRegistry registry;
    Binding binding = sample_binding();
    Profile profile = sample_profile();
    profile.arguments[1] = "odd-generation";
    IOTOX_CHECK(registry.replace(ProfileStoreData{{profile}, {binding}}).ok());

    std::atomic<std::size_t> ready{0U};
    std::atomic<bool> begin{false};
    std::atomic<bool> stop{false};
    std::atomic<bool> failed{false};
    std::atomic<std::uint64_t> observations{0U};
    std::vector<std::thread> readers;
    constexpr std::size_t reader_count = 4U;
    readers.reserve(reader_count);
    for (std::size_t index = 0U; index < reader_count; ++index) {
        readers.emplace_back([&] {
            ready.fetch_add(1U, std::memory_order_release);
            while (!begin.load(std::memory_order_acquire)) {
                std::this_thread::yield();
            }
            while (!stop.load(std::memory_order_acquire)) {
                auto resolved = registry.resolve(
                    binding.principal_id, Dimensions{80U, 24U}, {});
                if (!resolved.ok() || resolved.value().profile.arguments.size() < 2U) {
                    failed.store(true, std::memory_order_release);
                    continue;
                }
                const bool odd = (resolved.value().policy_generation & 1U) != 0U;
                const std::string_view expected =
                    odd ? "odd-generation" : "even-generation";
                if (resolved.value().profile.arguments[1] != expected) {
                    failed.store(true, std::memory_order_release);
                }
                const auto snapshot = registry.snapshot();
                if (snapshot.generation == 0U || snapshot.profiles != 1U ||
                    snapshot.bindings != 1U) {
                    failed.store(true, std::memory_order_release);
                }
                observations.fetch_add(1U, std::memory_order_relaxed);
            }
        });
    }

    while (ready.load(std::memory_order_acquire) != reader_count) {
        std::this_thread::yield();
    }
    begin.store(true, std::memory_order_release);
    // Do not let an optimized publisher complete the entire replacement loop
    // before the newly released readers have executed. This is a synchronization
    // contract for the test, not a scheduler-timing assumption.
    while (observations.load(std::memory_order_acquire) < reader_count) {
        std::this_thread::yield();
    }
    constexpr std::uint64_t final_generation = 513U;
    for (std::uint64_t generation = 2U; generation <= final_generation; ++generation) {
        Profile replacement = sample_profile();
        replacement.arguments[1] =
            (generation & 1U) != 0U ? "odd-generation" : "even-generation";
        if (!registry.replace(ProfileStoreData{{std::move(replacement)}, {binding}}).ok()) {
            failed.store(true, std::memory_order_release);
            break;
        }
        if ((generation & 15U) == 0U) std::this_thread::yield();
    }
    stop.store(true, std::memory_order_release);
    for (std::thread &reader : readers) reader.join();

    IOTOX_CHECK(!failed.load(std::memory_order_acquire));
    IOTOX_CHECK(observations.load(std::memory_order_relaxed) >= reader_count);
    const auto snapshot = registry.snapshot();
    IOTOX_CHECK(snapshot.generation == final_generation);
    IOTOX_CHECK(snapshot.profiles == 1U);
    IOTOX_CHECK(snapshot.bindings == 1U);
}

IOTOX_TEST("terminal profile store has one canonical semantic tree digest") {
    StoreFixture fixture;
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    ProfileStoreData ordered{{fixture.profile}, {fixture.binding}};
    auto first = iotox::terminal::profile_store_digest(
        ordered, sodium.value());
    IOTOX_CHECK_MSG(first.ok(), first.status().message());
    auto repeated = iotox::terminal::profile_store_digest(
        ordered, sodium.value());
    IOTOX_CHECK(repeated.ok());
    IOTOX_CHECK(first.value() == repeated.value());
    ordered.profiles.front().enabled = !ordered.profiles.front().enabled;
    auto changed = iotox::terminal::profile_store_digest(
        ordered, sodium.value());
    IOTOX_CHECK(changed.ok());
    IOTOX_CHECK(changed.value() != first.value());
}

IOTOX_TEST("terminal profile store loads an exact owner-only tree") {
    StoreFixture fixture;
    const auto owner = static_cast<std::uint32_t>(::geteuid());
    auto loaded = iotox::terminal::load_profile_store(
        fixture.temporary.path(), owner);
    IOTOX_CHECK(loaded.ok());
    IOTOX_CHECK(loaded.value().profiles.size() == 1U);
    IOTOX_CHECK(loaded.value().bindings.size() == 1U);
    IOTOX_CHECK(loaded.value().profiles.front().id == fixture.profile.id);
    IOTOX_CHECK(loaded.value().bindings.front() == fixture.binding);

    const auto traversal = iotox::terminal::remove_profile_record(
        fixture.temporary.path(), owner, "../escape");
    IOTOX_CHECK(!traversal.ok());
    IOTOX_CHECK(traversal.code() == ErrorCode::invalid_argument);
    const auto referenced = iotox::terminal::remove_profile_record(
        fixture.temporary.path(), owner, fixture.profile.id);
    IOTOX_CHECK(!referenced.ok());
    IOTOX_CHECK(referenced.code() == ErrorCode::unavailable);
    IOTOX_CHECK(iotox::terminal::remove_binding_record(
                    fixture.temporary.path(), owner,
                    fixture.binding.principal_id)
                    .ok());
    IOTOX_CHECK(iotox::terminal::remove_profile_record(
                    fixture.temporary.path(), owner, fixture.profile.id)
                    .ok());
    loaded = iotox::terminal::load_profile_store(
        fixture.temporary.path(), owner);
    IOTOX_CHECK(loaded.ok());
    IOTOX_CHECK(loaded.value().profiles.empty());
    IOTOX_CHECK(loaded.value().bindings.empty());
}

IOTOX_TEST("terminal profile store rejects writable links and unexpected entries") {
    {
        StoreFixture fixture;
        const auto record = fixture.profiles / (fixture.profile.id + ".profile");
        IOTOX_CHECK(::chmod(record.c_str(), static_cast<mode_t>(0644)) == 0);
        auto loaded = iotox::terminal::load_profile_store(
            fixture.temporary.path(), static_cast<std::uint32_t>(::geteuid()));
        IOTOX_CHECK(!loaded.ok());
    }
    {
        StoreFixture fixture;
        const auto record = fixture.profiles / (fixture.profile.id + ".profile");
        const auto second = fixture.profiles / "second.profile";
        IOTOX_CHECK(::link(record.c_str(), second.c_str()) == 0);
        auto loaded = iotox::terminal::load_profile_store(
            fixture.temporary.path(), static_cast<std::uint32_t>(::geteuid()));
        IOTOX_CHECK(!loaded.ok());
    }
    {
        StoreFixture fixture;
        const auto record = fixture.profiles / (fixture.profile.id + ".profile");
        IOTOX_CHECK(::unlink(record.c_str()) == 0);
        IOTOX_CHECK(::symlink("/dev/null", record.c_str()) == 0);
        auto loaded = iotox::terminal::load_profile_store(
            fixture.temporary.path(), static_cast<std::uint32_t>(::geteuid()));
        IOTOX_CHECK(!loaded.ok());
    }
    {
        StoreFixture fixture;
        write_record(
            fixture.temporary.path() / "unexpected",
            std::vector<std::uint8_t>{static_cast<std::uint8_t>('x')});
        auto loaded = iotox::terminal::load_profile_store(
            fixture.temporary.path(), static_cast<std::uint32_t>(::geteuid()));
        IOTOX_CHECK(!loaded.ok());
    }
}

IOTOX_TEST("terminal profile store rejects relative and symlinked root paths") {
    StoreFixture fixture;
    auto relative = iotox::terminal::load_profile_store(
        fixture.temporary.path().filename(),
        static_cast<std::uint32_t>(::geteuid()));
    IOTOX_CHECK(!relative.ok());
    IOTOX_CHECK(relative.status().code() == ErrorCode::invalid_argument);

    TempDirectory parent;
    const auto link = parent.path() / "store-link";
    IOTOX_CHECK(::symlink(fixture.temporary.path().c_str(), link.c_str()) == 0);
    auto symlinked = iotox::terminal::load_profile_store(
        link, static_cast<std::uint32_t>(::geteuid()));
    IOTOX_CHECK(!symlinked.ok());
}
