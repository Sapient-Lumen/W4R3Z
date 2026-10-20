#include "iotox/local/friend_request_fifo.hpp"
#include "iotox/local/peer_fifo.hpp"
#include "test_harness.hpp"

#include <atomic>
#include <cerrno>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fcntl.h>
#include <mutex>
#include <span>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <thread>
#include <unistd.h>
#include <vector>

namespace {

using namespace std::chrono_literals;

std::string hex_address(bool lower_case = false) {
    static constexpr char upper[] = "0123456789ABCDEF";
    static constexpr char lower[] = "0123456789abcdef";
    const char *digits = lower_case ? lower : upper;
    std::string encoded;
    encoded.reserve(iotox::local::kFriendRequestAddressHexBytes);
    for (std::size_t index = 0U; index < iotox::toxcore::abi::kAddressSize;
         ++index) {
        const std::uint8_t value = static_cast<std::uint8_t>(index);
        encoded.push_back(digits[(value >> 4U) & 0x0FU]);
        encoded.push_back(digits[value & 0x0FU]);
    }
    return encoded;
}

std::vector<std::uint8_t> record_with(
    std::string_view address, std::span<const std::uint8_t> message) {
    std::vector<std::uint8_t> record(address.begin(), address.end());
    record.push_back(static_cast<std::uint8_t>('\t'));
    record.insert(record.end(), message.begin(), message.end());
    return record;
}

std::filesystem::path request_fifo_test_directory(std::string_view suffix) {
    static std::atomic<unsigned int> sequence{0U};
    return std::filesystem::temp_directory_path() /
           ("iotox-request-fifo-test-" +
            std::to_string(static_cast<long long>(::getpid())) + "-" +
            std::to_string(sequence.fetch_add(1U)) + "-" +
            std::string(suffix));
}

void write_one_record(
    const std::filesystem::path &fifo,
    std::span<const std::uint8_t> record_without_lf) {
    std::vector<std::uint8_t> write{
        record_without_lf.begin(), record_without_lf.end()};
    write.push_back(static_cast<std::uint8_t>('\n'));

    int descriptor = -1;
    const auto deadline = std::chrono::steady_clock::now() + 2s;
    while (descriptor < 0 && std::chrono::steady_clock::now() < deadline) {
        descriptor = ::open(
            fifo.c_str(), O_WRONLY | O_NONBLOCK | O_CLOEXEC | O_NOFOLLOW);
        if (descriptor < 0 &&
            (errno == ENXIO || errno == ENOENT || errno == EINTR)) {
            std::this_thread::sleep_for(5ms);
            continue;
        }
        break;
    }
    IOTOX_CHECK(descriptor >= 0);
    ssize_t count = -1;
    do {
        count = ::write(descriptor, write.data(), write.size());
    } while (count < 0 && errno == EINTR);
    IOTOX_CHECK(count == static_cast<ssize_t>(write.size()));
    IOTOX_CHECK(::close(descriptor) == 0);
}

}  // namespace

IOTOX_TEST("outgoing friend request record preserves complete address and message bytes") {
    const std::vector<std::uint8_t> message{
        'h', 'i', '\t', 0x00U, '\r', 0x80U, 0xFFU};
    const auto record = record_with(hex_address(true), message);
    auto decoded = iotox::local::decode_friend_request_fifo_record(record);
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value().address.size() ==
                iotox::toxcore::abi::kAddressSize);
    for (std::size_t index = 0U; index < decoded.value().address.size();
         ++index) {
        IOTOX_CHECK(decoded.value().address[index] ==
                    static_cast<std::uint8_t>(index));
    }
    IOTOX_CHECK(decoded.value().message == message);
}

IOTOX_TEST("outgoing friend request record freezes one exact bounded grammar") {
    const std::vector<std::uint8_t> one{'x'};

    auto missing_tab = record_with(hex_address(), one);
    missing_tab[iotox::local::kFriendRequestAddressHexBytes] = ' ';
    IOTOX_CHECK(!iotox::local::decode_friend_request_fifo_record(missing_tab));

    auto bad_hex = record_with(hex_address(), one);
    bad_hex[17U] = 'G';
    IOTOX_CHECK(!iotox::local::decode_friend_request_fifo_record(bad_hex));

    const std::string address = hex_address();
    std::vector<std::uint8_t> empty_message(address.begin(), address.end());
    empty_message.push_back('\t');
    IOTOX_CHECK(!iotox::local::decode_friend_request_fifo_record(empty_message));

    const std::vector<std::uint8_t> maximum(
        iotox::local::kFriendRequestMaximumMessageBytes, 0xA5U);
    auto maximum_record = record_with(address, maximum);
    IOTOX_CHECK(maximum_record.size() ==
                iotox::local::kFriendRequestMaximumRecordBytes);
    IOTOX_CHECK(iotox::local::decode_friend_request_fifo_record(maximum_record));

    maximum_record.push_back(0xA5U);
    IOTOX_CHECK(!iotox::local::decode_friend_request_fifo_record(maximum_record));
}

IOTOX_TEST("peer FIFO server monitors a direct private root lane") {
    const std::filesystem::path root =
        request_fifo_test_directory("root-layout");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(root));
    IOTOX_CHECK(::chmod(root.c_str(), 0700) == 0);
    const std::filesystem::path fifo = root / "request";
    IOTOX_CHECK(::mkfifo(fifo.c_str(), 0600) == 0);
    IOTOX_CHECK(::chmod(fifo.c_str(), 0600) == 0);

    std::mutex mutex;
    bool delivered = false;
    std::string selector;
    std::string lane;
    std::vector<std::uint8_t> body;
    std::vector<iotox::Status> errors;

    iotox::local::PeerFifoServer::Config config;
    config.peers_root = root;
    config.layout = iotox::local::PeerFifoLayout::root_lanes;
    config.lanes = {{
        "request", iotox::local::kFriendRequestMaximumRecordBytes, false,
        iotox::local::PeerFifoRecordPolicy::byte_line}};
    config.rescan_interval = 20ms;
    config.partial_record_timeout = 150ms;
    iotox::local::PeerFifoServer server(
        std::move(config),
        [&](std::string_view delivered_selector,
            std::string_view delivered_lane,
            std::span<const std::uint8_t> record) {
            std::scoped_lock lock(mutex);
            delivered = true;
            selector = delivered_selector;
            lane = delivered_lane;
            body.assign(record.begin(), record.end());
        },
        [&](std::string_view, std::string_view,
            const iotox::Status &status) {
            std::scoped_lock lock(mutex);
            errors.push_back(status);
        });
    IOTOX_CHECK_MSG(server.start().ok(), "root-lane server did not start");
    IOTOX_CHECK(server.monitored_fifo_count("request") == 1U);

    const std::vector<std::uint8_t> message{'r', 'o', 'o', 't'};
    const auto record = record_with(hex_address(), message);
    write_one_record(fifo, record);

    const auto deadline = std::chrono::steady_clock::now() + 2s;
    while (std::chrono::steady_clock::now() < deadline) {
        {
            std::scoped_lock lock(mutex);
            if (delivered) {
                break;
            }
        }
        std::this_thread::sleep_for(5ms);
    }
    {
        std::scoped_lock lock(mutex);
        IOTOX_CHECK(delivered);
        IOTOX_CHECK(selector.empty());
        IOTOX_CHECK(lane == "request");
        IOTOX_CHECK(body == record);
        IOTOX_CHECK(errors.empty());
    }

    server.stop();
    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("root FIFO server follows a safely replaced promised lane") {
    const std::filesystem::path root =
        request_fifo_test_directory("root-replacement");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(root));
    IOTOX_CHECK(::chmod(root.c_str(), 0700) == 0);
    const std::filesystem::path fifo = root / "request";
    IOTOX_CHECK(::mkfifo(fifo.c_str(), 0600) == 0);
    IOTOX_CHECK(::chmod(fifo.c_str(), 0600) == 0);

    std::mutex mutex;
    std::vector<std::vector<std::uint8_t>> delivered;
    std::vector<iotox::Status> errors;

    iotox::local::PeerFifoServer::Config config;
    config.peers_root = root;
    config.layout = iotox::local::PeerFifoLayout::root_lanes;
    config.lanes = {{
        "request", iotox::local::kFriendRequestMaximumRecordBytes, false,
        iotox::local::PeerFifoRecordPolicy::byte_line}};
    config.rescan_interval = 20ms;
    config.partial_record_timeout = 150ms;
    iotox::local::PeerFifoServer server(
        std::move(config),
        [&](std::string_view, std::string_view,
            std::span<const std::uint8_t> record) {
            std::scoped_lock lock(mutex);
            delivered.emplace_back(record.begin(), record.end());
        },
        [&](std::string_view, std::string_view,
            const iotox::Status &status) {
            std::scoped_lock lock(mutex);
            errors.push_back(status);
        });
    IOTOX_CHECK_MSG(server.start().ok(), "root-lane server did not start");

    const auto first = record_with(
        hex_address(), std::vector<std::uint8_t>{'f', 'i', 'r', 's', 't'});
    write_one_record(fifo, first);
    const auto first_deadline = std::chrono::steady_clock::now() + 2s;
    while (std::chrono::steady_clock::now() < first_deadline) {
        {
            std::scoped_lock lock(mutex);
            if (delivered.size() >= 1U) {
                break;
            }
        }
        std::this_thread::sleep_for(5ms);
    }

    IOTOX_CHECK(::unlink(fifo.c_str()) == 0);
    IOTOX_CHECK(::mkfifo(fifo.c_str(), 0600) == 0);
    IOTOX_CHECK(::chmod(fifo.c_str(), 0600) == 0);

    const auto second = record_with(
        hex_address(true),
        std::vector<std::uint8_t>{'s', 'e', 'c', 'o', 'n', 'd'});
    write_one_record(fifo, second);
    const auto second_deadline = std::chrono::steady_clock::now() + 2s;
    while (std::chrono::steady_clock::now() < second_deadline) {
        {
            std::scoped_lock lock(mutex);
            if (delivered.size() >= 2U) {
                break;
            }
        }
        std::this_thread::sleep_for(5ms);
    }

    {
        std::scoped_lock lock(mutex);
        IOTOX_CHECK(delivered.size() == 2U);
        IOTOX_CHECK(delivered[0] == first);
        IOTOX_CHECK(delivered[1] == second);
        IOTOX_CHECK(errors.empty());
    }
    IOTOX_CHECK(server.monitored_fifo_count("request") == 1U);

    server.stop();
    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("root FIFO layout fails startup when its promised lane is absent") {
    const std::filesystem::path root =
        request_fifo_test_directory("missing-root-lane");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(root));
    IOTOX_CHECK(::chmod(root.c_str(), 0700) == 0);

    std::vector<iotox::Status> errors;
    iotox::local::PeerFifoServer::Config config;
    config.peers_root = root;
    config.layout = iotox::local::PeerFifoLayout::root_lanes;
    config.lanes = {{
        "request", iotox::local::kFriendRequestMaximumRecordBytes, false,
        iotox::local::PeerFifoRecordPolicy::byte_line}};
    iotox::local::PeerFifoServer server(
        std::move(config),
        [](std::string_view, std::string_view,
           std::span<const std::uint8_t>) {},
        [&](std::string_view, std::string_view,
            const iotox::Status &status) { errors.push_back(status); });

    const iotox::Status started = server.start();
    IOTOX_CHECK(!started.ok());
    IOTOX_CHECK(started.code() == iotox::ErrorCode::io_error);
    IOTOX_CHECK(started.message().find("every required root lane") !=
                std::string::npos);
    IOTOX_CHECK(!server.running());
    IOTOX_CHECK(server.monitored_fifo_count("request") == 0U);

    std::filesystem::remove_all(root, ignored);
}

IOTOX_TEST("peer FIFO server rejects an unknown layout value") {
    const std::filesystem::path root =
        request_fifo_test_directory("unknown-layout");
    std::error_code ignored;
    std::filesystem::remove_all(root, ignored);
    IOTOX_CHECK(std::filesystem::create_directories(root));
    IOTOX_CHECK(::chmod(root.c_str(), 0700) == 0);

    iotox::local::PeerFifoServer::Config config;
    config.peers_root = root;
    config.layout = static_cast<iotox::local::PeerFifoLayout>(99);
    config.lanes = {{
        "request", iotox::local::kFriendRequestMaximumRecordBytes, false,
        iotox::local::PeerFifoRecordPolicy::byte_line}};
    iotox::local::PeerFifoServer server(
        std::move(config),
        [](std::string_view, std::string_view,
           std::span<const std::uint8_t>) {});

    const iotox::Status started = server.start();
    IOTOX_CHECK(!started.ok());
    IOTOX_CHECK(started.code() == iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(started.message().find("layout is not recognized") !=
                std::string::npos);

    std::filesystem::remove_all(root, ignored);
}
