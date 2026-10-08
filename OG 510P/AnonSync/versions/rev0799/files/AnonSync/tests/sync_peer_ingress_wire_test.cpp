#include "sync_peer_ingress_wire.hpp"

#include <cstdint>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>

int main() {
    std::uint64_t checks = 0;
    try {
        anonsync::run_peer_transport_ingress_wire_codec_selftests(
            [&](bool condition, const std::string& message) {
                ++checks;
                if (!condition) throw std::runtime_error(message);
            });
        std::cout << "sync peer ingress wire codec checks passed: " << checks << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "sync peer ingress wire codec test failed after " << checks
                  << " checks: " << e.what() << "\n";
        return 1;
    }
}
