#include "sync_atomic_file_publication.hpp"

#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

#include <unistd.h>

namespace fs = std::filesystem;

std::string read_all(const fs::path& path) {
    std::ifstream in(path, std::ios::binary);
    return std::string(std::istreambuf_iterator<char>(in),
                       std::istreambuf_iterator<char>());
}

int main() {
    const auto seed = static_cast<std::uint64_t>(
        std::chrono::steady_clock::now().time_since_epoch().count());
    const fs::path root = fs::temp_directory_path() /
        ("anonsync-intermediate-link-repro-" + std::to_string(::getpid()) +
         "-" + std::to_string(seed));
    try {
        fs::create_directories(root / "real" / "subdirectory");
        fs::create_directory_symlink("real", root / "link");
        const fs::path requested = root / "link" / "subdirectory" / "report.json";
        const fs::path redirected = root / "real" / "subdirectory" / "report.json";
        bool call_succeeded = false;
        std::string error;
        try {
            anonsync::write_sync_json_file_atomically_no_symlink_or_throw(
                requested, "{\"redirected\":true}\n", "intermediate link repro");
            call_succeeded = true;
        } catch (const std::exception& caught) {
            error = caught.what();
        }
        const bool redirected_exists = fs::exists(redirected);
        const bool redirected_exact = redirected_exists &&
            read_all(redirected) == "{\"redirected\":true}\n";
        std::cout << "{\n"
                  << "  \"call_succeeded\": " << (call_succeeded ? "true" : "false") << ",\n"
                  << "  \"redirected_target_exists\": " << (redirected_exists ? "true" : "false") << ",\n"
                  << "  \"redirected_bytes_exact\": " << (redirected_exact ? "true" : "false") << ",\n"
                  << "  \"error_contains_component_symlink_rejection\": "
                  << (error.find("component must not be a symlink") != std::string::npos ? "true" : "false") << "\n"
                  << "}\n";
        std::error_code ignored;
        fs::remove_all(root, ignored);
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FATAL: " << error.what() << '\n';
        std::error_code ignored;
        fs::remove_all(root, ignored);
        return 2;
    }
}
