#include "sync_atomic_file_publication.hpp"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>

namespace fs = std::filesystem;

static std::string read_all(const fs::path& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) return {};
    return std::string(std::istreambuf_iterator<char>(in),
                       std::istreambuf_iterator<char>());
}

int main(int argc, char** argv) {
    if (argc != 2) return 64;
    const fs::path root = fs::path(argv[1]);
    const fs::path intended = root / "intended";
    const fs::path displaced = root / "displaced";
    const fs::path final_path = intended / "receipt.json";
    fs::remove_all(root);
    fs::create_directories(intended);

    const std::string payload = "{\"receipt\":\"authority-drift\"}\n";
    anonsync::preflight_sync_file_create_new_no_symlink_or_throw(
        final_path, "rebind defect probe");
    fs::rename(intended, displaced);
    fs::create_directories(intended);
    anonsync::write_sync_json_file_atomically_create_new_no_symlink_or_throw(
        final_path, payload, "rebind defect probe");

    const bool replacement_received = read_all(final_path) == payload;
    const bool pinned_parent_received = fs::exists(displaced / "receipt.json");
    std::cout << "replacement_received=" << replacement_received << "\n";
    std::cout << "pinned_parent_received=" << pinned_parent_received << "\n";
    return replacement_received && !pinned_parent_received ? 0 : 1;
}
