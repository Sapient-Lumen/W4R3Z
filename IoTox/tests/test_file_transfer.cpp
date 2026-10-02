#include "iotox/file_transfer.hpp"
#include "iotox/transport.hpp"
#include "test_harness.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iterator>
#include <optional>
#include <string>
#include <thread>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

std::filesystem::path transfer_test_directory(std::string_view suffix) {
    static std::atomic<unsigned int> sequence{0U};
    return std::filesystem::temp_directory_path() /
           ("iotox-transfer-test-" +
            std::to_string(static_cast<unsigned long long>(::getpid())) + "-" +
            std::to_string(sequence.fetch_add(1U)) + "-" + std::string(suffix));
}

class ScopedEnvironment {
  public:
    ScopedEnvironment(const char *name, const std::string &value) : name_(name) {
        if (const char *existing = std::getenv(name); existing != nullptr) {
            previous_ = existing;
        }
        IOTOX_CHECK(::setenv(name, value.c_str(), 1) == 0);
    }

    ~ScopedEnvironment() {
        if (previous_) {
            static_cast<void>(::setenv(name_.c_str(), previous_->c_str(), 1));
        } else {
            static_cast<void>(::unsetenv(name_.c_str()));
        }
    }

  private:
    std::string name_;
    std::optional<std::string> previous_;
};

void write_bytes(
    const std::filesystem::path &path,
    const std::vector<std::uint8_t> &bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    IOTOX_CHECK(output.good());
    output.write(
        reinterpret_cast<const char *>(bytes.data()),
        static_cast<std::streamsize>(bytes.size()));
    IOTOX_CHECK(output.good());
}

std::vector<std::uint8_t> read_bytes(const std::filesystem::path &path) {
    std::ifstream input(path, std::ios::binary);
    return {std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>()};
}

bool pump_until(
    iotox::ToxTransport &transport, iotox::FileTransferManager &manager,
    const std::function<bool()> &done) {
    // Full ASan/UBSan suites can temporarily delay the mock toxcore owner
    // thread while hundreds of instrumented checks share one constrained CI
    // host. Keep the wait finite, but do not turn scheduler pressure into a
    // false file-transfer failure.
    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(10);
    while (std::chrono::steady_clock::now() < deadline) {
        if (done()) {
            return true;
        }
        if (auto event = transport.poll_event(std::chrono::milliseconds(50)); event) {
            const iotox::Status handled = manager.handle_event(*event);
            IOTOX_CHECK_MSG(handled.ok(), handled.message());
        }
    }
    return done();
}

}  // namespace

IOTOX_TEST("file transfer manager binds an explicit file ID to an immutable outgoing snapshot") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory = transfer_test_directory("send");
    const std::filesystem::path source = directory / "ratox-successor.bin";
    const std::filesystem::path captured = directory / "captured.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    const std::vector<std::uint8_t> expected{'I', 'o', 'T', 'o', 'x', '!'};
    write_bytes(source, expected);
    ScopedEnvironment capture_environment(
        "IOTOX_MOCK_CAPTURE_SENT_FILE", captured.string());

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x91U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());

    iotox::FileTransferManager manager(transport);
    iotox::FileId zero_id{};
    IOTOX_CHECK(!manager.send_path_with_file_id(
        peer.value(), std::filesystem::absolute(source), zero_id).ok());
    IOTOX_CHECK(manager.list().empty());
    iotox::FileId requested_id{};
    requested_id.fill(0x5CU);
    auto offered = manager.send_path_with_file_id(
        peer.value(), std::filesystem::absolute(source), requested_id);
    IOTOX_CHECK_MSG(offered.ok(), offered.status().message());
    IOTOX_CHECK(offered.value().direction == iotox::FileTransferDirection::outgoing);
    IOTOX_CHECK(offered.value().file_size == expected.size());
    IOTOX_CHECK(offered.value().has_file_id);
    IOTOX_CHECK(offered.value().file_id == requested_id);

    IOTOX_CHECK(pump_until(transport, manager, [&] {
        return manager.list().empty() && std::filesystem::exists(captured);
    }));
    IOTOX_CHECK(read_bytes(captured) == expected);

    manager.stop();
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("file transfer manager offers one canonical concatenated range view without a bundle file") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory =
        transfer_test_directory("send-ranges");
    const std::filesystem::path source = directory / "source.bin";
    const std::filesystem::path captured = directory / "captured.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    const std::vector<std::uint8_t> input{
        '0', '1', '2', '3', '4', '5', '6', '7',
        '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'};
    write_bytes(source, input);
    ScopedEnvironment capture_environment(
        "IOTOX_MOCK_CAPTURE_SENT_FILE", captured.string());

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0xA2U));
    IOTOX_CHECK(peer.ok());
    iotox::FileTransferManager manager(transport);
    iotox::FileId requested_id{};
    requested_id.fill(0x6DU);
    const std::array<iotox::FileByteRange, 3U> ranges{{
        {1U, 3U}, {6U, 2U}, {11U, 4U}}};
    auto offered = manager.send_path_ranges_with_file_id(
        peer.value(), std::filesystem::absolute(source), ranges,
        requested_id);
    IOTOX_CHECK_MSG(offered.ok(), offered.status().message());
    IOTOX_CHECK(offered.value().file_size == 9U);
    IOTOX_CHECK(offered.value().file_id == requested_id);
    IOTOX_CHECK(pump_until(transport, manager, [&] {
        return manager.list().empty() && std::filesystem::exists(captured);
    }));
    const std::vector<std::uint8_t> expected{
        '1', '2', '3', '6', '7', 'b', 'c', 'd', 'e'};
    IOTOX_CHECK(read_bytes(captured) == expected);

    manager.stop();
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("file transfer manager rejects aliased empty and escaping range views before offer") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);
    const std::filesystem::path directory =
        transfer_test_directory("send-range-reject");
    const std::filesystem::path source = directory / "source.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    write_bytes(source, {'0', '1', '2', '3', '4', '5'});

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0xA3U));
    IOTOX_CHECK(peer.ok());
    iotox::FileTransferManager manager(transport);
    iotox::FileId requested_id{};
    requested_id.fill(0x7EU);
    IOTOX_CHECK(!manager.send_path_ranges_with_file_id(
        peer.value(), std::filesystem::absolute(source), {}, requested_id).ok());
    const std::array<iotox::FileByteRange, 1U> empty{{{1U, 0U}}};
    IOTOX_CHECK(!manager.send_path_ranges_with_file_id(
        peer.value(), std::filesystem::absolute(source), empty, requested_id).ok());
    const std::array<iotox::FileByteRange, 2U> adjacent{{
        {0U, 2U}, {2U, 2U}}};
    IOTOX_CHECK(!manager.send_path_ranges_with_file_id(
        peer.value(), std::filesystem::absolute(source), adjacent,
        requested_id).ok());
    const std::array<iotox::FileByteRange, 1U> escaping{{{5U, 2U}}};
    IOTOX_CHECK(!manager.send_path_ranges_with_file_id(
        peer.value(), std::filesystem::absolute(source), escaping,
        requested_id).ok());
    IOTOX_CHECK(manager.list().empty());
    manager.stop();
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("file transfer manager answers every toxcore chunk request inside its callback") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory =
        transfer_test_directory("inline-chunks");
    const std::filesystem::path source = directory / "multi-chunk.bin";
    const std::filesystem::path captured = directory / "captured.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    std::vector<std::uint8_t> expected(1024U);
    for (std::size_t index = 0U; index < expected.size(); ++index) {
        expected[index] = static_cast<std::uint8_t>(
            (index * 37U + index / 251U) & 0xFFU);
    }
    write_bytes(source, expected);
    ScopedEnvironment capture_environment(
        "IOTOX_MOCK_CAPTURE_SENT_FILE", captured.string());
    ScopedEnvironment inline_environment(
        "IOTOX_MOCK_REQUIRE_INLINE_FILE_CHUNKS", "1");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x98U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());

    iotox::FileTransferManager manager(transport);
    auto offered = manager.send_path(
        peer.value(), std::filesystem::absolute(source));
    IOTOX_CHECK_MSG(offered.ok(), offered.status().message());
    IOTOX_CHECK(pump_until(transport, manager, [&] {
        return manager.list().empty() && std::filesystem::exists(captured);
    }));
    IOTOX_CHECK(read_bytes(captured) == expected);

    manager.stop();
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("file transfer manager exposes exact local pause resume and idempotent cancel state") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory = transfer_test_directory("local-control");
    const std::filesystem::path source = directory / "controlled.bin";
    const std::filesystem::path captured = directory / "captured.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    // Sixteen mock chunks keep the transfer live across the immediate PAUSE/RESUME
    // boundary without making this state-machine test depend on ten seconds of
    // owner-thread scheduling under sanitizers. Bulk streaming is covered above.
    const std::vector<std::uint8_t> expected(64U, 0x50U);
    write_bytes(source, expected);
    ScopedEnvironment capture_environment(
        "IOTOX_MOCK_CAPTURE_SENT_FILE", captured.string());

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x90U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());

    iotox::FileTransferManager manager(transport);
    auto offered = manager.send_path(peer.value(), std::filesystem::absolute(source));
    IOTOX_CHECK_MSG(offered.ok(), offered.status().message());

    auto paused = manager.control(
        peer.value(), offered.value().file_number, iotox::TransferControl::pause);
    IOTOX_CHECK_MSG(paused.ok(), paused.status().message());
    IOTOX_CHECK(paused.value().state == iotox::FileTransferState::paused);
    IOTOX_CHECK(paused.value().local_paused);
    IOTOX_CHECK(!paused.value().peer_paused);

    auto paused_again = manager.control(
        peer.value(), offered.value().file_number, iotox::TransferControl::pause);
    IOTOX_CHECK_MSG(paused_again.ok(), paused_again.status().message());
    IOTOX_CHECK(paused_again.value().detail == "already-paused-locally");

    auto resumed = manager.control(
        peer.value(), offered.value().file_number, iotox::TransferControl::resume);
    IOTOX_CHECK_MSG(resumed.ok(), resumed.status().message());
    IOTOX_CHECK(resumed.value().state == iotox::FileTransferState::active);
    IOTOX_CHECK(!resumed.value().local_paused);

    auto invalid_resume = manager.control(
        peer.value(), offered.value().file_number, iotox::TransferControl::resume);
    IOTOX_CHECK(!invalid_resume.ok());
    IOTOX_CHECK(invalid_resume.status().code() == iotox::ErrorCode::invalid_argument);

    IOTOX_CHECK(pump_until(transport, manager, [&] {
        return manager.list().empty() && std::filesystem::exists(captured);
    }));
    IOTOX_CHECK(read_bytes(captured) == expected);

    // A terminal transfer is gone from local state; cancellation must not
    // silently target a future reuse of the same friend-scoped file number.
    auto terminal_cancel = manager.control(
        peer.value(), offered.value().file_number, iotox::TransferControl::cancel);
    IOTOX_CHECK(!terminal_cancel.ok());
    IOTOX_CHECK(terminal_cancel.status().code() == iotox::ErrorCode::not_found);

    manager.stop();
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("file transfer manager accepts paused offers into private no-clobber destinations") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory = transfer_test_directory("receive");
    const std::filesystem::path destination = directory / "received.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    ScopedEnvironment incoming_environment(
        "IOTOX_MOCK_INCOMING_FILE", "remote-name.bin");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x92U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());
    iotox::FileTransferManager manager(transport);

    IOTOX_CHECK(pump_until(transport, manager, [&] {
        const auto records = manager.list();
        return records.size() == 1U &&
               records.front().state == iotox::FileTransferState::offered;
    }));
    const auto offers = manager.list();
    IOTOX_CHECK(offers.size() == 1U);
    IOTOX_CHECK(offers.front().filename ==
                std::vector<std::uint8_t>({'r', 'e', 'm', 'o', 't', 'e', '-',
                                           'n', 'a', 'm', 'e', '.', 'b', 'i', 'n'}));

    auto accepted = manager.receive_to_path(
        peer.value(), offers.front().file_number,
        std::filesystem::absolute(destination));
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
    IOTOX_CHECK(accepted.value().state == iotox::FileTransferState::active);

    IOTOX_CHECK(pump_until(transport, manager, [&] {
        return manager.list().empty() && std::filesystem::exists(destination);
    }));
    const std::vector<std::uint8_t> expected{'D', 'A', 'T', 'A'};
    IOTOX_CHECK(read_bytes(destination) == expected);

    struct stat metadata {};
    IOTOX_CHECK(::lstat(destination.c_str(), &metadata) == 0);
    IOTOX_CHECK((metadata.st_mode & 0777) == 0600);
    for (const auto &entry : std::filesystem::directory_iterator(directory)) {
        IOTOX_CHECK(entry.path().filename().string().find(".part-") == std::string::npos);
    }

    manager.stop();
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("file transfer manager resumes an exact private prefix and receives only the suffix") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory =
        transfer_test_directory("receive-resume");
    const std::filesystem::path destination = directory / "partial.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    write_bytes(destination, {'D', 'A'});
    IOTOX_CHECK(::chmod(destination.c_str(), 0644) == 0);
    ScopedEnvironment incoming_environment(
        "IOTOX_MOCK_INCOMING_FILE", "resume.bin");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0xC1U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());
    iotox::FileTransferManager manager(transport);

    IOTOX_CHECK(pump_until(transport, manager, [&] {
        return manager.list().size() == 1U;
    }));
    const auto offer = manager.list().front();
    IOTOX_CHECK(!manager.receive_to_path_from_offset(
        peer.value(), offer.file_number,
        std::filesystem::absolute(destination), 0U).ok());
    auto insecure = manager.receive_to_path_from_offset(
        peer.value(), offer.file_number,
        std::filesystem::absolute(destination), 2U);
    IOTOX_CHECK(!insecure.ok());
    IOTOX_CHECK(insecure.status().code() == iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(read_bytes(destination) ==
                std::vector<std::uint8_t>({'D', 'A'}));

    IOTOX_CHECK(::chmod(destination.c_str(), 0600) == 0);
    auto accepted = manager.receive_to_path_from_offset(
        peer.value(), offer.file_number,
        std::filesystem::absolute(destination), 2U);
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
    IOTOX_CHECK(accepted.value().position == 2U);
    IOTOX_CHECK(accepted.value().detail == "resuming-from=2");
    IOTOX_CHECK(pump_until(transport, manager, [&] {
        return manager.list().empty() &&
            std::filesystem::file_size(destination) == 4U;
    }));
    IOTOX_CHECK(read_bytes(destination) ==
                std::vector<std::uint8_t>({'D', 'A', 'T', 'A'}));

    manager.stop();
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("file transfer manager preserves a resumed private prefix across carrier loss") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory =
        transfer_test_directory("receive-resume-loss");
    const std::filesystem::path destination = directory / "partial.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    write_bytes(destination, {'D', 'A'});
    IOTOX_CHECK(::chmod(destination.c_str(), 0600) == 0);
    ScopedEnvironment incoming_environment(
        "IOTOX_MOCK_INCOMING_FILE", "resume-loss.bin");
    ScopedEnvironment deferred_environment(
        "IOTOX_MOCK_DEFER_INCOMING_FILE", "1");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0xC2U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());
    iotox::FileTransferManager manager(transport);

    IOTOX_CHECK(pump_until(transport, manager, [&] {
        return manager.list().size() == 1U;
    }));
    const auto offer = manager.list().front();
    auto accepted = manager.receive_to_path_from_offset(
        peer.value(), offer.file_number,
        std::filesystem::absolute(destination), 2U);
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());

    iotox::TransportEvent offline;
    offline.kind = iotox::TransportEventKind::friend_connection;
    offline.friend_number = peer.value();
    offline.connection_status = 0;
    IOTOX_CHECK(manager.handle_event(offline).ok());
    IOTOX_CHECK(manager.list().empty());
    IOTOX_CHECK(read_bytes(destination) ==
                std::vector<std::uint8_t>({'D', 'A'}));
    struct stat metadata {};
    IOTOX_CHECK(::lstat(destination.c_str(), &metadata) == 0);
    IOTOX_CHECK((metadata.st_mode & 0777) == 0600);
    IOTOX_CHECK(metadata.st_nlink == 1);

    manager.stop();
    IOTOX_CHECK(std::filesystem::exists(destination));
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("file transfer manager locally retires a dead carrier receive without control") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory =
        transfer_test_directory("receive-local-retirement");
    const std::filesystem::path destination = directory / "retired.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    ScopedEnvironment incoming_environment(
        "IOTOX_MOCK_INCOMING_FILE", "retired.bin");
    ScopedEnvironment deferred_environment(
        "IOTOX_MOCK_DEFER_INCOMING_FILE", "1");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(
        std::vector<std::uint8_t>(32U, 0xC4U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());
    iotox::FileTransferManager manager(transport);

    IOTOX_CHECK(pump_until(transport, manager, [&] {
        return manager.list().size() == 1U;
    }));
    const auto offer = manager.list().front();
    IOTOX_CHECK(manager.receive_to_path(
        peer.value(), offer.file_number,
        std::filesystem::absolute(destination)).ok());
    IOTOX_CHECK(!std::filesystem::exists(destination));
    IOTOX_CHECK(manager.retire_incoming(
        peer.value(), offer.file_number).ok());
    IOTOX_CHECK(manager.retire_incoming(
        peer.value(), offer.file_number).ok());
    IOTOX_CHECK(manager.list().empty());
    IOTOX_CHECK(!std::filesystem::exists(destination));
    for (const auto &entry : std::filesystem::directory_iterator(directory)) {
        IOTOX_CHECK(entry.path().filename().string().find(".part-") ==
                    std::string::npos);
    }

    iotox::TransportEvent stale_chunk;
    stale_chunk.kind = iotox::TransportEventKind::file_chunk;
    stale_chunk.friend_number = peer.value();
    stale_chunk.file_number = offer.file_number;
    stale_chunk.file_position = 0U;
    stale_chunk.data = {'D', 'A', 'T', 'A'};
    IOTOX_CHECK(manager.handle_event(stale_chunk).ok());
    stale_chunk.file_position = 4U;
    stale_chunk.data.clear();
    IOTOX_CHECK(manager.handle_event(stale_chunk).ok());
    IOTOX_CHECK(!std::filesystem::exists(destination));

    manager.stop();
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("incoming completion publication is serialized with local retirement") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory =
        transfer_test_directory("completion-retirement-race");
    const std::filesystem::path destination = directory / "raced.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    ScopedEnvironment incoming_environment(
        "IOTOX_MOCK_INCOMING_FILE", "raced.bin");
    ScopedEnvironment deferred_environment(
        "IOTOX_MOCK_DEFER_INCOMING_FILE", "1");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(
        std::vector<std::uint8_t>(32U, 0xC5U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());
    iotox::FileTransferManager manager(transport);

    IOTOX_CHECK(pump_until(transport, manager, [&] {
        return manager.list().size() == 1U;
    }));
    const auto initial = manager.list().front();
    constexpr std::uint64_t total_bytes = 64U * 1024U * 1024U;
    iotox::TransportEvent offer;
    offer.kind = iotox::TransportEventKind::file_offer;
    offer.friend_number = peer.value();
    offer.file_number = initial.file_number;
    offer.file_kind = initial.file_kind;
    offer.file_size = total_bytes;
    offer.file_id = initial.file_id;
    offer.has_file_id = initial.has_file_id;
    offer.filename = {'r', 'a', 'c', 'e', 'd', '.', 'b', 'i', 'n'};
    IOTOX_CHECK(manager.handle_event(offer).ok());
    IOTOX_CHECK(manager.receive_to_path(
        peer.value(), offer.file_number,
        std::filesystem::absolute(destination)).ok());

    std::vector<std::uint8_t> chunk(4U * 1024U * 1024U, 0xA5U);
    iotox::TransportEvent data;
    data.kind = iotox::TransportEventKind::file_chunk;
    data.friend_number = peer.value();
    data.file_number = offer.file_number;
    for (std::uint64_t offset = 0U; offset < total_bytes;
         offset += chunk.size()) {
        data.file_position = offset;
        data.data = chunk;
        IOTOX_CHECK(manager.handle_event(data).ok());
    }

    iotox::TransportEvent completed = data;
    completed.file_position = total_bytes;
    completed.data.clear();
    iotox::Status completion{
        iotox::ErrorCode::unavailable, "completion did not run"};
    std::thread finisher([&] {
        completion = manager.handle_event(completed);
    });
    bool detached = false;
    for (std::size_t attempt = 0U; attempt < 100000U; ++attempt) {
        if (manager.list().empty()) {
            detached = true;
            break;
        }
        std::this_thread::yield();
    }
    const iotox::Status retirement = manager.retire_incoming(
        peer.value(), offer.file_number);
    static_cast<void>(std::filesystem::remove(destination, ignored));
    finisher.join();
    IOTOX_CHECK(detached);
    IOTOX_CHECK(retirement.ok());
    IOTOX_CHECK_MSG(completion.ok(), completion.message());
    IOTOX_CHECK(!std::filesystem::exists(destination));
    for (const auto &entry : std::filesystem::directory_iterator(directory)) {
        IOTOX_CHECK(entry.path().filename().string().find(".part-") ==
                    std::string::npos);
    }

    manager.stop();
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("file transfer manager rejects resume destination substitution at completion") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory =
        transfer_test_directory("receive-resume-substitution");
    const std::filesystem::path destination = directory / "partial.bin";
    const std::filesystem::path displaced = directory / "displaced.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    write_bytes(destination, {'D', 'A'});
    IOTOX_CHECK(::chmod(destination.c_str(), 0600) == 0);
    ScopedEnvironment incoming_environment(
        "IOTOX_MOCK_INCOMING_FILE", "resume-substitution.bin");
    ScopedEnvironment deferred_environment(
        "IOTOX_MOCK_DEFER_INCOMING_FILE", "1");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0xC3U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());
    iotox::FileTransferManager manager(transport);

    IOTOX_CHECK(pump_until(transport, manager, [&] {
        return manager.list().size() == 1U;
    }));
    const auto offer = manager.list().front();
    IOTOX_CHECK(manager.receive_to_path_from_offset(
        peer.value(), offer.file_number,
        std::filesystem::absolute(destination), 2U).ok());
    IOTOX_CHECK(::rename(destination.c_str(), displaced.c_str()) == 0);
    write_bytes(destination, {'N', 'O'});
    IOTOX_CHECK(::chmod(destination.c_str(), 0600) == 0);

    iotox::TransportEvent chunk;
    chunk.kind = iotox::TransportEventKind::file_chunk;
    chunk.friend_number = peer.value();
    chunk.file_number = offer.file_number;
    chunk.file_position = 2U;
    chunk.data = {'T', 'A'};
    IOTOX_CHECK(manager.handle_event(chunk).ok());
    chunk.file_position = 4U;
    chunk.data.clear();
    const iotox::Status completed = manager.handle_event(chunk);
    IOTOX_CHECK(!completed.ok());
    IOTOX_CHECK(completed.code() == iotox::ErrorCode::unavailable);
    IOTOX_CHECK(manager.list().empty());
    IOTOX_CHECK(read_bytes(destination) ==
                std::vector<std::uint8_t>({'N', 'O'}));
    IOTOX_CHECK(read_bytes(displaced) ==
                std::vector<std::uint8_t>({'D', 'A', 'T', 'A'}));

    manager.stop();
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("file carrier admits one receive per peer and rotates every waiting transfer") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory =
        transfer_test_directory("carrier-window");
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    ScopedEnvironment incoming_environment(
        "IOTOX_MOCK_INCOMING_FILE", "carrier.bin");
    ScopedEnvironment count_environment(
        "IOTOX_MOCK_INCOMING_FILE_COUNT", "3");
    ScopedEnvironment deferred_environment(
        "IOTOX_MOCK_DEFER_INCOMING_FILE", "1");

    iotox::ToxTransport::Config transport_config;
    transport_config.toxcore_library = mock_library;
    transport_config.save_state_after_mutation = false;
    transport_config.save_state_on_stop = false;
    iotox::ToxTransport transport(transport_config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0xB3U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());

    iotox::FileTransferManager::Config manager_config;
    manager_config.carrier_window_per_peer = 1U;
    manager_config.carrier_rotation_quantum = std::chrono::milliseconds(5);
    iotox::FileTransferManager manager(transport, manager_config);
    IOTOX_CHECK(pump_until(transport, manager, [&] {
        const auto records = manager.list();
        return records.size() == 3U &&
            std::all_of(records.begin(), records.end(), [](const auto &record) {
                return record.state == iotox::FileTransferState::offered;
            });
    }));

    const auto offers = manager.list();
    std::vector<std::filesystem::path> destinations;
    for (std::size_t index = 0U; index < offers.size(); ++index) {
        const std::filesystem::path destination =
            directory / ("received-" + std::to_string(index));
        auto accepted = manager.receive_to_path(
            peer.value(), offers[index].file_number,
            std::filesystem::absolute(destination));
        IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
        IOTOX_CHECK(
            accepted.value().state ==
            (index == 0U ? iotox::FileTransferState::active
                         : iotox::FileTransferState::paused));
        destinations.push_back(destination);
    }
    iotox::FileCarrierStats stats = manager.stats();
    IOTOX_CHECK(stats.window_per_peer == 1U);
    IOTOX_CHECK(stats.rotation_quantum_ms == 5U);
    IOTOX_CHECK(stats.runnable_receives == 1U);
    IOTOX_CHECK(stats.waiting_receives == 2U);
    IOTOX_CHECK(stats.admission_count == 1U);

    std::this_thread::sleep_for(std::chrono::milliseconds(6));
    IOTOX_CHECK(manager.service_carrier().ok());
    std::this_thread::sleep_for(std::chrono::milliseconds(6));
    IOTOX_CHECK(manager.service_carrier().ok());
    stats = manager.stats();
    IOTOX_CHECK(stats.runnable_receives == 1U);
    IOTOX_CHECK(stats.waiting_receives == 2U);
    IOTOX_CHECK(stats.admission_count == 3U);
    IOTOX_CHECK(stats.rotation_count == 2U);
    IOTOX_CHECK(stats.pause_count == 2U);
    IOTOX_CHECK(stats.resume_count == 3U);
    IOTOX_CHECK(stats.control_failure_count == 0U);
    IOTOX_CHECK(stats.maximum_wait_us >= 5000U);

    for (const auto &record : manager.list()) {
        IOTOX_CHECK(manager.cancel(
                        record.friend_number, record.file_number)
                        .ok());
    }
    IOTOX_CHECK(manager.list().empty());
    iotox::TransportEvent late_chunk;
    late_chunk.kind = iotox::TransportEventKind::file_chunk;
    late_chunk.friend_number = peer.value();
    late_chunk.file_number = offers.front().file_number;
    late_chunk.file_position = 0U;
    late_chunk.data = {'L', 'A', 'T', 'E'};
    IOTOX_CHECK(manager.handle_event(late_chunk).ok());
    late_chunk.file_position = 4U;
    late_chunk.data.clear();
    IOTOX_CHECK(manager.handle_event(late_chunk).ok());
    late_chunk.file_number = offers.back().file_number + 1U;
    late_chunk.file_position = 0U;
    late_chunk.data = {'N', 'O'};
    IOTOX_CHECK(
        manager.handle_event(late_chunk).code() ==
        iotox::ErrorCode::protocol_error);
    for (const auto &destination : destinations) {
        IOTOX_CHECK(!std::filesystem::exists(destination));
    }
    stats = manager.stats();
    IOTOX_CHECK(stats.runnable_receives == 0U);
    IOTOX_CHECK(stats.waiting_receives == 0U);

    manager.stop();
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}



IOTOX_TEST("file transfer manager preserves independent local and peer pause truth") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory = transfer_test_directory("pause-truth");
    const std::filesystem::path source = directory / "outgoing.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    write_bytes(source, std::vector<std::uint8_t>(2048U, 0x50U));
    ScopedEnvironment incoming_environment(
        "IOTOX_MOCK_INCOMING_FILE", "remote-pause.bin");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0xA2U));
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());
    iotox::FileTransferManager manager(transport);

    IOTOX_CHECK(pump_until(transport, manager, [&] {
        const auto records = manager.list();
        return std::any_of(records.begin(), records.end(), [](const auto &record) {
            return record.direction == iotox::FileTransferDirection::incoming &&
                   record.state == iotox::FileTransferState::offered;
        });
    }));
    auto records = manager.list();
    const auto offered = std::find_if(
        records.begin(), records.end(), [](const auto &record) {
            return record.direction == iotox::FileTransferDirection::incoming;
        });
    IOTOX_CHECK(offered != records.end());
    const std::uint32_t incoming_number = offered->file_number;

    iotox::TransportEvent remote_pause;
    remote_pause.kind = iotox::TransportEventKind::file_control;
    remote_pause.friend_number = peer.value();
    remote_pause.file_number = incoming_number;
    remote_pause.file_control = iotox::TransferControl::pause;
    IOTOX_CHECK(manager.handle_event(remote_pause).ok());
    records = manager.list();
    const auto paused_offer = std::find_if(
        records.begin(), records.end(), [incoming_number](const auto &record) {
            return record.file_number == incoming_number;
        });
    IOTOX_CHECK(paused_offer != records.end());
    IOTOX_CHECK(paused_offer->state == iotox::FileTransferState::offered);
    IOTOX_CHECK(paused_offer->local_paused);
    IOTOX_CHECK(paused_offer->peer_paused);

    auto redundant_local_pause = manager.control(
        peer.value(), incoming_number, iotox::TransferControl::pause);
    IOTOX_CHECK_MSG(
        redundant_local_pause.ok(), redundant_local_pause.status().message());
    IOTOX_CHECK(redundant_local_pause.value().state ==
                iotox::FileTransferState::offered);
    IOTOX_CHECK(redundant_local_pause.value().local_paused);
    IOTOX_CHECK(redundant_local_pause.value().peer_paused);

    remote_pause.file_control = iotox::TransferControl::resume;
    IOTOX_CHECK(manager.handle_event(remote_pause).ok());
    records = manager.list();
    const auto resumed_offer = std::find_if(
        records.begin(), records.end(), [incoming_number](const auto &record) {
            return record.file_number == incoming_number;
        });
    IOTOX_CHECK(resumed_offer != records.end());
    IOTOX_CHECK(resumed_offer->state == iotox::FileTransferState::offered);
    IOTOX_CHECK(resumed_offer->local_paused);
    IOTOX_CHECK(!resumed_offer->peer_paused);

    auto outgoing = manager.send_path(peer.value(), std::filesystem::absolute(source));
    IOTOX_CHECK_MSG(outgoing.ok(), outgoing.status().message());
    auto locally_paused = manager.control(
        peer.value(), outgoing.value().file_number,
        iotox::TransferControl::pause);
    IOTOX_CHECK_MSG(locally_paused.ok(), locally_paused.status().message());
    IOTOX_CHECK(locally_paused.value().state == iotox::FileTransferState::paused);
    IOTOX_CHECK(locally_paused.value().local_paused);
    IOTOX_CHECK(!locally_paused.value().peer_paused);

    auto locally_resumed = manager.control(
        peer.value(), outgoing.value().file_number,
        iotox::TransferControl::resume);
    IOTOX_CHECK_MSG(locally_resumed.ok(), locally_resumed.status().message());
    IOTOX_CHECK(locally_resumed.value().state == iotox::FileTransferState::active);
    IOTOX_CHECK(!locally_resumed.value().local_paused);
    IOTOX_CHECK(!locally_resumed.value().peer_paused);

    auto invalid_resume = manager.control(
        peer.value(), outgoing.value().file_number,
        iotox::TransferControl::resume);
    IOTOX_CHECK(!invalid_resume.ok());
    IOTOX_CHECK(invalid_resume.status().code() ==
                iotox::ErrorCode::invalid_argument);

    IOTOX_CHECK(manager.cancel(peer.value(), incoming_number).ok());
    IOTOX_CHECK(manager.cancel(
                    peer.value(), outgoing.value().file_number)
                    .ok());
    manager.stop();
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("incoming file acceptance never clobbers an existing destination") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory = transfer_test_directory("no-clobber");
    const std::filesystem::path destination = directory / "keep.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    write_bytes(destination, {'K', 'E', 'E', 'P'});
    ScopedEnvironment incoming_environment("IOTOX_MOCK_INCOMING_FILE", "remote.bin");

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x93U));
    IOTOX_CHECK(peer.ok());
    iotox::FileTransferManager manager(transport);

    IOTOX_CHECK(pump_until(transport, manager, [&] {
        return manager.list().size() == 1U;
    }));
    const auto offers = manager.list();
    auto accepted = manager.receive_to_path(
        peer.value(), offers.front().file_number,
        std::filesystem::absolute(destination));
    IOTOX_CHECK(!accepted.ok());
    IOTOX_CHECK(accepted.status().code() == iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(read_bytes(destination) ==
                std::vector<std::uint8_t>({'K', 'E', 'E', 'P'}));
    IOTOX_CHECK(manager.list().size() == 1U);
    IOTOX_CHECK(manager.cancel(peer.value(), offers.front().file_number).ok());
    IOTOX_CHECK(manager.list().empty());
    for (const auto &entry : std::filesystem::directory_iterator(directory)) {
        IOTOX_CHECK(entry.path().filename().string().find(".part-") == std::string::npos);
    }

    manager.stop();
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("outgoing file transfer fails closed when the opened source mutates") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory = transfer_test_directory("source-mutation");
    const std::filesystem::path source = directory / "mutable.bin";
    const std::filesystem::path captured = directory / "captured.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    write_bytes(source, std::vector<std::uint8_t>(2048U, 0x4FU));
    ScopedEnvironment capture_environment("IOTOX_MOCK_CAPTURE_SENT_FILE", captured.string());

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x94U));
    IOTOX_CHECK(peer.ok());
    iotox::FileTransferManager manager(transport);
    IOTOX_CHECK(manager.send_path(peer.value(), std::filesystem::absolute(source)).ok());

    {
        std::ofstream output(source, std::ios::binary | std::ios::app);
        output << "!";
        IOTOX_CHECK(output.good());
    }

    bool rejected = false;
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(3);
    while (std::chrono::steady_clock::now() < deadline && !rejected) {
        if (auto event = transport.poll_event(std::chrono::milliseconds(50)); event) {
            const iotox::Status handled = manager.handle_event(*event);
            if (!handled.ok()) {
                IOTOX_CHECK(handled.code() == iotox::ErrorCode::io_error);
                rejected = true;
            }
        }
    }
    IOTOX_CHECK(rejected);
    IOTOX_CHECK(manager.list().empty());
    IOTOX_CHECK(!std::filesystem::exists(captured));

    manager.stop();
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("zero-byte regular files complete without a synthetic send chunk") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    const std::filesystem::path directory = transfer_test_directory("zero-send");
    const std::filesystem::path source = directory / "empty.bin";
    const std::filesystem::path captured = directory / "captured.bin";
    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    write_bytes(source, {});
    ScopedEnvironment capture_environment("IOTOX_MOCK_CAPTURE_SENT_FILE", captured.string());

    iotox::ToxTransport::Config config;
    config.toxcore_library = mock_library;
    config.save_state_after_mutation = false;
    config.save_state_on_stop = false;
    iotox::ToxTransport transport(config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x95U));
    IOTOX_CHECK(peer.ok());
    iotox::FileTransferManager manager(transport);
    auto offered = manager.send_path(peer.value(), std::filesystem::absolute(source));
    IOTOX_CHECK_MSG(offered.ok(), offered.status().message());
    IOTOX_CHECK(offered.value().file_size == 0U);
    IOTOX_CHECK(pump_until(transport, manager, [&] {
        return manager.list().empty() && std::filesystem::exists(captured);
    }));
    IOTOX_CHECK(read_bytes(captured).empty());

    manager.stop();
    transport.stop();
    std::filesystem::remove_all(directory, ignored);
}

IOTOX_TEST("pending incoming file offers are bounded and rejected at toxcore") {
    const char *mock_library = std::getenv("IOTOX_TEST_MOCK_TOXCORE");
    IOTOX_CHECK(mock_library != nullptr);

    ScopedEnvironment incoming_environment("IOTOX_MOCK_INCOMING_FILE", "overflow.bin");
    iotox::ToxTransport::Config transport_config;
    transport_config.toxcore_library = mock_library;
    transport_config.save_state_after_mutation = false;
    transport_config.save_state_on_stop = false;
    iotox::ToxTransport transport(transport_config);
    IOTOX_CHECK(transport.start().ok());
    auto peer = transport.accept_friend(std::vector<std::uint8_t>(32U, 0x96U));
    IOTOX_CHECK(peer.ok());

    iotox::FileTransferManager::Config manager_config;
    manager_config.max_pending_offers = 0U;
    iotox::FileTransferManager manager(transport, manager_config);
    bool rejected = false;
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(3);
    while (std::chrono::steady_clock::now() < deadline && !rejected) {
        if (auto event = transport.poll_event(std::chrono::milliseconds(50)); event) {
            const iotox::Status handled = manager.handle_event(*event);
            if (!handled.ok()) {
                IOTOX_CHECK(handled.code() == iotox::ErrorCode::resource_exhausted);
                rejected = true;
            }
        }
    }
    IOTOX_CHECK(rejected);
    IOTOX_CHECK(manager.list().empty());

    manager.stop();
    transport.stop();
}


IOTOX_TEST("file transfer line rendering escapes untrusted and local delimiters") {
    iotox::FileTransferRecord record;
    record.direction = iotox::FileTransferDirection::incoming;
    record.state = iotox::FileTransferState::offered;
    record.friend_number = 2U;
    record.file_number = 65536U;
    record.filename = {'a', '\n', 0U, '\\'};
    record.local_path = "/tmp/line\npath";
    record.detail = "waiting\rfor-owner";
    const std::string rendered = iotox::render_file_transfer(record);
    IOTOX_CHECK(rendered.find('\n') == std::string::npos);
    IOTOX_CHECK(rendered.find('\r') == std::string::npos);
    IOTOX_CHECK(rendered.find("filename=a\\x0A\\x00\\\\") != std::string::npos);
    IOTOX_CHECK(rendered.find("local-path=/tmp/line\\x0Apath") != std::string::npos);
    IOTOX_CHECK(rendered.find("detail=waiting\\x0Dfor-owner") != std::string::npos);
}
