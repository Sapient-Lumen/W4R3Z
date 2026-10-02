#include "iotox/local/peer_fifo.hpp"
#include "test_harness.hpp"

#include <atomic>
#include <cerrno>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fcntl.h>
#include <functional>
#include <mutex>
#include <span>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <thread>
#include <unistd.h>
#include <utility>
#include <vector>

namespace {

using namespace std::chrono_literals;

std::filesystem::path fifo_test_directory(std::string_view suffix) {
    static std::atomic<unsigned int> sequence{0U};
    return std::filesystem::temp_directory_path() /
           ("iotox-peer-fifo-test-" +
            std::to_string(static_cast<long long>(::getpid())) + "-" +
            std::to_string(sequence.fetch_add(1U)) + "-" +
            std::string(suffix));
}

struct Record {
    std::string public_key;
    std::string lane;
    std::vector<std::uint8_t> body;
};

struct ErrorRecord {
    std::string public_key;
    std::string lane;
    iotox::Status status;
};

struct Fixture {
    std::filesystem::path root;
    std::filesystem::path peers;
    std::string key = std::string(64U, 'A');
    std::mutex mutex;
    std::vector<Record> records;
    std::vector<ErrorRecord> errors;

    explicit Fixture(std::string_view suffix)
        : root(fifo_test_directory(suffix)), peers(root / "peers") {
        std::error_code ignored;
        std::filesystem::remove_all(root, ignored);
        IOTOX_CHECK(std::filesystem::create_directories(peers));
        IOTOX_CHECK(::chmod(root.c_str(), 0700) == 0);
        IOTOX_CHECK(::chmod(peers.c_str(), 0700) == 0);
    }

    ~Fixture() {
        std::error_code ignored;
        std::filesystem::remove_all(root, ignored);
    }

    std::filesystem::path create_peer_lane(
        std::string_view lane, std::string_view public_key = {}) {
        const std::string selected = public_key.empty()
            ? key
            : std::string(public_key);
        const auto directory = peers / selected;
        std::error_code ignored;
        static_cast<void>(std::filesystem::create_directories(directory, ignored));
        IOTOX_CHECK(!ignored);
        IOTOX_CHECK(::chmod(directory.c_str(), 0700) == 0);
        const auto fifo = directory / std::string(lane);
        IOTOX_CHECK(::mkfifo(fifo.c_str(), 0600) == 0);
        IOTOX_CHECK(::chmod(fifo.c_str(), 0600) == 0);
        return fifo;
    }

    void create_peer_all() {
        static_cast<void>(create_peer_lane("command"));
        static_cast<void>(create_peer_lane("message"));
        static_cast<void>(create_peer_lane("action"));
    }

    iotox::local::PeerFifoServer make_server(
        std::size_t command_maximum = 256U,
        std::size_t message_maximum = 1372U,
        std::chrono::milliseconds partial_timeout = 150ms) {
        iotox::local::PeerFifoServer::Config config;
        config.peers_root = peers;
        config.lanes = {
            {"command", command_maximum, true,
             iotox::local::PeerFifoRecordPolicy::printable_ascii},
            {"message", message_maximum, false,
             iotox::local::PeerFifoRecordPolicy::byte_line},
            {"action", message_maximum, false,
             iotox::local::PeerFifoRecordPolicy::byte_line},
        };
        config.rescan_interval = 20ms;
        config.partial_record_timeout = partial_timeout;
        return iotox::local::PeerFifoServer(
            std::move(config),
            [this](std::string_view public_key, std::string_view lane,
                   std::span<const std::uint8_t> record) {
                std::scoped_lock lock(mutex);
                records.push_back({std::string(public_key), std::string(lane),
                                   {record.begin(), record.end()}});
            },
            [this](std::string_view public_key, std::string_view lane,
                   const iotox::Status &status) {
                std::scoped_lock lock(mutex);
                errors.push_back(
                    {std::string(public_key), std::string(lane), status});
            });
    }

    bool wait_for(const std::function<bool()> &predicate,
                  std::chrono::milliseconds timeout = 2500ms) {
        const auto deadline = std::chrono::steady_clock::now() + timeout;
        while (std::chrono::steady_clock::now() < deadline) {
            {
                std::scoped_lock lock(mutex);
                if (predicate()) {
                    return true;
                }
            }
            std::this_thread::sleep_for(5ms);
        }
        std::scoped_lock lock(mutex);
        return predicate();
    }
};

void write_fifo(const std::filesystem::path &path,
                std::span<const std::uint8_t> bytes) {
    int descriptor = -1;
    const auto deadline = std::chrono::steady_clock::now() + 2s;
    while (descriptor < 0 && std::chrono::steady_clock::now() < deadline) {
        descriptor = ::open(path.c_str(), O_WRONLY | O_NONBLOCK | O_CLOEXEC);
        if (descriptor < 0 && (errno == ENXIO || errno == ENOENT)) {
            std::this_thread::sleep_for(5ms);
            continue;
        }
        if (descriptor < 0) {
            break;
        }
    }
    IOTOX_CHECK(descriptor >= 0);
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::write(
            descriptor, bytes.data() + offset, bytes.size() - offset);
        if (count < 0 && errno == EINTR) {
            continue;
        }
        IOTOX_CHECK(count > 0);
        offset += static_cast<std::size_t>(count);
    }
    IOTOX_CHECK(::close(descriptor) == 0);
}

void write_fifo(const std::filesystem::path &path, std::string_view text) {
    write_fifo(path, std::span<const std::uint8_t>{
                         reinterpret_cast<const std::uint8_t *>(text.data()),
                         text.size()});
}

}  // namespace

IOTOX_TEST("peer FIFO statistics are safe before start") {
    Fixture fixture("pre-start-stats");
    auto server = fixture.make_server();
    const iotox::local::PeerFifoStats stats = server.stats();
    IOTOX_CHECK(!stats.running);
    IOTOX_CHECK(stats.total_fifo_count == 0U);
    IOTOX_CHECK(stats.lane_fifo_counts.size() == 3U);
    IOTOX_CHECK(server.monitored_fifo_count("command") == 0U);
    IOTOX_CHECK(server.monitored_fifo_count("message") == 0U);
    IOTOX_CHECK(server.monitored_fifo_count("action") == 0U);
}

IOTOX_TEST("peer FIFO delivers command and text lanes independently") {
    Fixture fixture("lanes");
    fixture.create_peer_all();
    auto server = fixture.make_server();
    const iotox::Status started = server.start();
    IOTOX_CHECK_MSG(started.ok(), started.message());
    IOTOX_CHECK(server.monitored_fifo_count("command") == 1U);
    IOTOX_CHECK(server.monitored_fifo_count("message") == 1U);
    IOTOX_CHECK(server.monitored_fifo_count("action") == 1U);
    const iotox::local::PeerFifoStats stats = server.stats();
    IOTOX_CHECK(stats.running);
    IOTOX_CHECK(stats.total_fifo_count == 3U);

    write_fifo(fixture.peers / fixture.key / "command", "device.describe\n");
    write_fifo(fixture.peers / fixture.key / "message", "hello\n");
    write_fifo(fixture.peers / fixture.key / "action", "waves\n");
    IOTOX_CHECK(fixture.wait_for([&] { return fixture.records.size() == 3U; }));
    server.stop();

    IOTOX_CHECK(fixture.records[0U].lane == "command");
    IOTOX_CHECK(std::string(fixture.records[0U].body.begin(),
                            fixture.records[0U].body.end()) ==
                "device.describe");
    IOTOX_CHECK(fixture.records[1U].lane == "message");
    IOTOX_CHECK(fixture.records[2U].lane == "action");
    IOTOX_CHECK(fixture.errors.empty());
}

IOTOX_TEST("peer FIFO byte-line preserves NUL high bytes and carriage return") {
    Fixture fixture("byte-line");
    const auto path = fixture.create_peer_lane("message");
    auto server = fixture.make_server();
    IOTOX_CHECK(server.start().ok());

    const std::vector<std::uint8_t> bytes{
        'h', 'i', 0U, 0xFFU, '\r', 'x', '\n'};
    write_fifo(path, bytes);
    IOTOX_CHECK(fixture.wait_for([&] { return fixture.records.size() == 1U; }));
    server.stop();
    const std::vector<std::uint8_t> expected{
        'h', 'i', 0U, 0xFFU, '\r', 'x'};
    IOTOX_CHECK(fixture.records.front().body == expected);
    IOTOX_CHECK(fixture.errors.empty());
}

IOTOX_TEST("peer FIFO printable command lane rejects nonprintable bytes then recovers") {
    Fixture fixture("printable-recover");
    const auto path = fixture.create_peer_lane("command");
    auto server = fixture.make_server(8U);
    IOTOX_CHECK(server.start().ok());

    write_fifo(path, "123456789\n");
    const std::vector<std::uint8_t> nonprintable{'b', 'a', 'd', 1U, 'x', '\n'};
    write_fifo(path, nonprintable);
    write_fifo(path, "ok\n");
    IOTOX_CHECK(fixture.wait_for([&] {
        return fixture.errors.size() >= 2U && fixture.records.size() == 1U;
    }));
    server.stop();
    IOTOX_CHECK(fixture.records.front().body ==
                std::vector<std::uint8_t>({'o', 'k'}));
    IOTOX_CHECK(fixture.errors[0U].status.code() ==
                iotox::ErrorCode::resource_exhausted);
    IOTOX_CHECK(fixture.errors[1U].status.code() ==
                iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(fixture.errors[1U].lane == "command");
}

IOTOX_TEST("peer FIFO rejects empty text while command compatibility preserves empty record") {
    Fixture fixture("empty-policy");
    const auto command = fixture.create_peer_lane("command");
    const auto message = fixture.create_peer_lane("message");
    auto server = fixture.make_server();
    IOTOX_CHECK(server.start().ok());

    write_fifo(message, "\n");
    write_fifo(command, "\n");
    IOTOX_CHECK(fixture.wait_for([&] {
        return fixture.errors.size() == 1U && fixture.records.size() == 1U;
    }));
    server.stop();
    IOTOX_CHECK(fixture.errors.front().lane == "message");
    IOTOX_CHECK(fixture.records.front().lane == "command");
    IOTOX_CHECK(fixture.records.front().body.empty());
}

IOTOX_TEST("peer FIFO expires an unterminated writer fragment before later writer") {
    Fixture fixture("partial-expiry");
    const auto path = fixture.create_peer_lane("message");
    auto server = fixture.make_server(256U, 1372U, 120ms);
    IOTOX_CHECK(server.start().ok());

    write_fifo(path, "first-half");
    IOTOX_CHECK(fixture.wait_for([&] { return !fixture.errors.empty(); }));
    write_fifo(path, "whole\n");
    IOTOX_CHECK(fixture.wait_for([&] { return fixture.records.size() == 1U; }));
    server.stop();
    IOTOX_CHECK(fixture.records.front().body ==
                std::vector<std::uint8_t>({'w', 'h', 'o', 'l', 'e'}));
    IOTOX_CHECK(fixture.errors.front().status.message().find("unterminated") !=
                std::string::npos);
}

IOTOX_TEST("peer FIFO discovers lanes projected after server start") {
    Fixture fixture("discover");
    auto server = fixture.make_server();
    IOTOX_CHECK(server.start().ok());
    IOTOX_CHECK(server.stats().total_fifo_count == 0U);

    const auto message = fixture.create_peer_lane("message");
    const auto action = fixture.create_peer_lane("action");
    IOTOX_CHECK(fixture.wait_for([&] {
        return server.monitored_fifo_count("message") == 1U &&
               server.monitored_fifo_count("action") == 1U;
    }));
    write_fifo(message, "hello\n");
    write_fifo(action, "waves\n");
    IOTOX_CHECK(fixture.wait_for([&] { return fixture.records.size() == 2U; }));
    server.stop();
    IOTOX_CHECK(!server.running());
}

IOTOX_TEST("peer FIFO refuses regular-file substitution and adopts repaired lane") {
    Fixture fixture("regular-repair");
    const std::filesystem::path directory = fixture.peers / fixture.key;
    IOTOX_CHECK(std::filesystem::create_directories(directory));
    IOTOX_CHECK(::chmod(directory.c_str(), 0700) == 0);
    const std::filesystem::path path = directory / "message";
    const int regular = ::open(
        path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
    IOTOX_CHECK(regular >= 0);
    IOTOX_CHECK(::close(regular) == 0);

    auto server = fixture.make_server();
    IOTOX_CHECK(server.start().ok());
    IOTOX_CHECK(server.monitored_fifo_count("message") == 0U);
    IOTOX_CHECK(fixture.wait_for([&] { return !fixture.errors.empty(); }));
    {
        std::scoped_lock lock(fixture.mutex);
        IOTOX_CHECK(fixture.errors.front().status.code() ==
                    iotox::ErrorCode::io_error);
        IOTOX_CHECK(fixture.errors.front().lane == "message");
    }

    IOTOX_CHECK(::unlink(path.c_str()) == 0);
    IOTOX_CHECK(::mkfifo(path.c_str(), 0600) == 0);
    IOTOX_CHECK(::chmod(path.c_str(), 0600) == 0);
    IOTOX_CHECK(fixture.wait_for(
        [&] { return server.monitored_fifo_count("message") == 1U; }));
    write_fifo(path, "repaired\n");
    IOTOX_CHECK(fixture.wait_for([&] { return fixture.records.size() == 1U; }));
    server.stop();
}

IOTOX_TEST("peer FIFO refuses a lane whose record cannot fit one atomic write") {
    Fixture fixture("pipe-buf");
    static_cast<void>(fixture.create_peer_lane("message"));
    auto server = fixture.make_server(256U, 65536U);
    IOTOX_CHECK(server.start().ok());
    IOTOX_CHECK(server.monitored_fifo_count("message") == 0U);
    IOTOX_CHECK(fixture.wait_for([&] { return !fixture.errors.empty(); }));
    server.stop();
    IOTOX_CHECK(fixture.errors.front().lane == "message");
    IOTOX_CHECK(fixture.errors.front().status.code() ==
                iotox::ErrorCode::unsupported);
    IOTOX_CHECK(fixture.errors.front().status.message().find("PIPE_BUF") !=
                std::string::npos);
}
