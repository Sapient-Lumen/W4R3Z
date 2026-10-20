#include "test_harness.hpp"

#include "iotox/agent_config.hpp"

#include <filesystem>
#include <fstream>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

class TemporaryDirectory {
  public:
    TemporaryDirectory() {
        std::string pattern = "/tmp/iotox-agent-config-XXXXXX";
        std::vector<char> bytes(pattern.begin(), pattern.end());
        bytes.push_back('\0');
        if (char *created = ::mkdtemp(bytes.data()); created != nullptr) {
            root_ = created;
        }
    }
    ~TemporaryDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(root_, ignored);
    }
    [[nodiscard]] const std::filesystem::path &root() const { return root_; }

  private:
    std::filesystem::path root_;
};

void write_bytes(const std::filesystem::path &path,
                 std::span<const std::uint8_t> bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    output.write(reinterpret_cast<const char *>(bytes.data()),
                 static_cast<std::streamsize>(bytes.size()));
    output.close();
    IOTOX_CHECK(output.good());
    IOTOX_CHECK(::chmod(path.c_str(), 0600) == 0);
}

}  // namespace

IOTOX_TEST("Agent configuration record is canonical and owner private") {
    iotox::AgentConfigRecord record;
    record.arguments = {
        "--state", "/var/lib/iotox/device.toxsave",
        "--enable-sync", "--sync-policy-root", "/var/lib/iotox/sync",
    };
    auto encoded = iotox::encode_agent_config_record(record);
    IOTOX_CHECK(encoded.ok());
    auto decoded = iotox::decode_agent_config_record(encoded.value());
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value() == record);

    TemporaryDirectory directory;
    const auto path = directory.root() / "agent.conf";
    write_bytes(path, encoded.value());
    auto loaded = iotox::load_agent_config_record(
        path, static_cast<std::uint32_t>(::geteuid()));
    IOTOX_CHECK(loaded.ok());
    IOTOX_CHECK(loaded.value() == record);

    IOTOX_CHECK(::chmod(path.c_str(), 0640) == 0);
    IOTOX_CHECK(!iotox::load_agent_config_record(
                     path, static_cast<std::uint32_t>(::geteuid()))
                     .ok());
}

IOTOX_TEST("Agent configuration rejects noncanonical and duplicate fields") {
    const auto decode = [](std::string_view text) {
        return iotox::decode_agent_config_record(
            std::span<const std::uint8_t>{
                reinterpret_cast<const std::uint8_t *>(text.data()),
                text.size()});
    };
    IOTOX_CHECK(!decode(
        "iotox-agent-config-v1\nargument-0001=--enable-sync\n").ok());
    IOTOX_CHECK(!decode(
        "iotox-agent-config-v1\nargument-0000=--enable-sync\n"
        "argument-0001=--enable-sync\n").ok());
    IOTOX_CHECK(!decode(
        "iotox-agent-config-v1\nargument-0000=--config\n"
        "argument-0001=/tmp/other\n").ok());
    IOTOX_CHECK(!decode(
        "iotox-agent-config-v1\nargument-0000=--state\n").ok());
}

IOTOX_TEST("Agent command-line fields replace exact file fields") {
    const std::vector<std::string> file{
        "--state", "/var/lib/iotox/old.toxsave",
        "--network", "tox/native",
        "--bootstrap", "192.0.2.1:33445:1111111111111111111111111111111111111111111111111111111111111111",
        "--bootstrap", "192.0.2.2:33445:2222222222222222222222222222222222222222222222222222222222222222",
        "--enable-ratox-terminal-client",
    };
    const std::vector<std::string_view> overrides{
        "--state", "/var/lib/iotox/new.toxsave",
        "--bootstrap", "192.0.2.3:33445:3333333333333333333333333333333333333333333333333333333333333333",
    };
    auto merged = iotox::merge_agent_config_arguments(file, overrides);
    IOTOX_CHECK(merged.ok());
    const std::vector<std::string> expected{
        "--network", "tox/native",
        "--enable-ratox-terminal-client",
        "--state", "/var/lib/iotox/new.toxsave",
        "--bootstrap", "192.0.2.3:33445:3333333333333333333333333333333333333333333333333333333333333333",
    };
    IOTOX_CHECK(merged.value() == expected);

    const std::vector<std::string_view> duplicate{
        "--state", "/one", "--state", "/two"};
    IOTOX_CHECK(!iotox::merge_agent_config_arguments(file, duplicate).ok());
}
