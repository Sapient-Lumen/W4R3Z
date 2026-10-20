#include "test_harness.hpp"

#include "iotox/agent.hpp"
#include "iotox/protected_state.hpp"

#include <filesystem>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

class TemporaryDirectory {
  public:
    TemporaryDirectory() {
        std::string pattern = "/tmp/iotox-protected-state-XXXXXX";
        std::vector<char> bytes(pattern.begin(), pattern.end());
        bytes.push_back('\0');
        if (char *created = ::mkdtemp(bytes.data())) root_ = created;
    }
    ~TemporaryDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(root_, ignored);
    }
    [[nodiscard]] const std::filesystem::path &root() const { return root_; }

  private:
    std::filesystem::path root_;
};

iotox::Agent::Config protected_config(const std::filesystem::path &root) {
    iotox::Agent::Config config;
    config.transport.state_path = root / "core" / "device.toxsave";
    config.runtime.root = root / "runtime";
    config.protected_state.require_fscrypt_v2 = true;
    config.protected_state.root = root;
    config.protected_state.policy_identifier =
        "00000000000000000000000000000000";
    iotox::Agent::normalize_config(config);
    return config;
}

}  // namespace

IOTOX_TEST("protected state is default-off and rejects ambiguous selection") {
    iotox::Agent::Config config;
    auto disabled = iotox::protected_state::inspect(config);
    IOTOX_CHECK(disabled.ok());
    IOTOX_CHECK(!disabled.value().enabled);

    config.protected_state.root = "/tmp/iotox-protected-only-root";
    auto ambiguous = iotox::protected_state::inspect(config);
    IOTOX_CHECK(!ambiguous.ok());
    IOTOX_CHECK(ambiguous.status().code() == iotox::ErrorCode::invalid_argument);
}

IOTOX_TEST("required protected state refuses plaintext before runtime mutation") {
    TemporaryDirectory directory;
    IOTOX_CHECK(!directory.root().empty());
    IOTOX_CHECK(::chmod(directory.root().c_str(), 0700) == 0);
    auto config = protected_config(directory.root());

    auto inspection = iotox::protected_state::inspect(config);
    IOTOX_CHECK(!inspection.ok());
    IOTOX_CHECK(inspection.status().code() == iotox::ErrorCode::unsupported);

    const std::filesystem::path runtime = config.runtime.root;
    iotox::Agent agent(std::move(config));
    const iotox::Status started = agent.start();
    IOTOX_CHECK(!started.ok());
    IOTOX_CHECK(started.code() == iotox::ErrorCode::unsupported);
    IOTOX_CHECK(!std::filesystem::exists(runtime));
}
