#include "sync_local_status_socket.hpp"

#if !defined(_WIN32)

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <thread>
#include <vector>

#include <sys/mman.h>
#include <unistd.h>

namespace {

[[nodiscard]] std::uint64_t parse_uint64_or_throw(
    std::string_view text,
    std::string_view label) {
    if (text.empty()) throw std::invalid_argument(std::string(label) + " is empty");
    std::uint64_t value = 0U;
    for (const unsigned char byte : text) {
        if (byte < '0' || byte > '9') {
            throw std::invalid_argument(
                std::string(label) + " is not an unsigned decimal integer");
        }
        const std::uint64_t digit = static_cast<std::uint64_t>(byte - '0');
        if (value > (std::numeric_limits<std::uint64_t>::max() - digit) / 10U) {
            throw std::out_of_range(std::string(label) + " overflows uint64");
        }
        value = value * 10U + digit;
    }
    return value;
}

class AnonymousReservation final {
public:
    explicit AnonymousReservation(std::uint64_t size_bytes) {
        if (size_bytes == 0U) return;
        if (size_bytes > static_cast<std::uint64_t>(
                             std::numeric_limits<std::size_t>::max())) {
            throw std::out_of_range("anonymous reservation exceeds size_t");
        }
        const long page_size = ::sysconf(_SC_PAGESIZE);
        if (page_size <= 0) throw std::runtime_error("page-size query failed");
        size_ = static_cast<std::size_t>(size_bytes);
        address_ = ::mmap(
            nullptr, size_, PROT_READ | PROT_WRITE,
            MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (address_ == MAP_FAILED) {
            address_ = nullptr;
            throw std::runtime_error("anonymous mmap failed");
        }
        auto* bytes = static_cast<volatile unsigned char*>(address_);
        const std::size_t stride = static_cast<std::size_t>(page_size);
        for (std::size_t offset = 0U; offset < size_; offset += stride) {
            bytes[offset] = static_cast<unsigned char>((offset / stride) & 0xffU);
        }
        bytes[size_ - 1U] = 0x5aU;
    }

    ~AnonymousReservation() noexcept {
        if (address_ != nullptr) (void)::munmap(address_, size_);
    }

    AnonymousReservation(const AnonymousReservation&) = delete;
    AnonymousReservation& operator=(const AnonymousReservation&) = delete;

private:
    void* address_ = nullptr;
    std::size_t size_ = 0U;
};

}  // namespace

int main(int argc, char** argv) {
    try {
        std::vector<std::filesystem::path> sockets;
        std::uint64_t anonymous_bytes = 0U;
        std::optional<std::filesystem::path> trigger_file;
        std::uint64_t trigger_anonymous_bytes = 0U;
        for (int index = 1; index < argc; ++index) {
            const std::string_view argument(argv[index]);
            if (argument == "--socket" && index + 1 < argc) {
                std::filesystem::path socket(argv[++index]);
                if (!socket.is_absolute()) {
                    throw std::invalid_argument("--socket must be absolute");
                }
                sockets.push_back(std::move(socket));
            } else if (argument == "--anonymous-bytes" && index + 1 < argc) {
                anonymous_bytes = parse_uint64_or_throw(
                    argv[++index], "--anonymous-bytes");
            } else if (argument == "--trigger-file" && index + 1 < argc) {
                std::filesystem::path selected(argv[++index]);
                if (!selected.is_absolute()) {
                    throw std::invalid_argument("--trigger-file must be absolute");
                }
                trigger_file = std::move(selected);
            } else if (argument == "--trigger-anonymous-bytes" &&
                       index + 1 < argc) {
                trigger_anonymous_bytes = parse_uint64_or_throw(
                    argv[++index], "--trigger-anonymous-bytes");
            } else {
                throw std::invalid_argument(
                    "usage: resource fixture --socket ABSOLUTE [--socket ABSOLUTE] "
                    "[--anonymous-bytes N] [--trigger-file ABSOLUTE "
                    "--trigger-anonymous-bytes N]");
            }
        }
        if (sockets.empty() || sockets.size() > 2U) {
            throw std::invalid_argument(
                "resource fixture requires one or two sockets");
        }
        if (trigger_file.has_value() != (trigger_anonymous_bytes != 0U)) {
            throw std::invalid_argument(
                "resource fixture trigger file and trigger bytes must be supplied together");
        }
        constexpr std::uint64_t maximum_anonymous_bytes =
            256U * 1024U * 1024U;
        if (anonymous_bytes > maximum_anonymous_bytes ||
            trigger_anonymous_bytes > maximum_anonymous_bytes - anonymous_bytes) {
            throw std::invalid_argument(
                "resource fixture combined anonymous reservation exceeds 256 MiB");
        }

        AnonymousReservation reservation(anonymous_bytes);
        std::unique_ptr<AnonymousReservation> triggered_reservation;
        const std::string status =
            "{\"schema\":\"anonsync.resource-fixture.status.v1\","
            "\"ready\":true,\"anonymous_bytes\":" +
            std::to_string(anonymous_bytes) +
            ",\"trigger_anonymous_bytes\":" +
            std::to_string(trigger_anonymous_bytes) + ",\"pid\":" +
            std::to_string(static_cast<long long>(::getpid())) + "}";
        std::vector<std::unique_ptr<anonsync::SyncLocalStatusSocketServer>>
            servers;
        servers.reserve(sockets.size());
        for (const auto& socket : sockets) {
            servers.push_back(
                std::make_unique<anonsync::SyncLocalStatusSocketServer>(
                    socket, status, "resource fixture status socket"));
        }
        std::cout << status << '\n';
        std::cout.flush();

        for (;;) {
            bool stop = false;
            for (const auto& server : servers) {
                server->require_healthy_or_throw();
                if (server->action_snapshot().stop_requested) stop = true;
            }
            if (stop) break;
            if (trigger_file.has_value() && !triggered_reservation) {
                std::error_code error;
                const bool triggered = std::filesystem::exists(
                    *trigger_file, error);
                if (error) {
                    throw std::runtime_error(
                        "resource fixture trigger observation failed: " +
                        error.message());
                }
                if (triggered) {
                    triggered_reservation =
                        std::make_unique<AnonymousReservation>(
                            trigger_anonymous_bytes);
                }
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "resource fixture failed: " << error.what() << '\n';
        return 1;
    }
}

#else

int main() { return 0; }

#endif
