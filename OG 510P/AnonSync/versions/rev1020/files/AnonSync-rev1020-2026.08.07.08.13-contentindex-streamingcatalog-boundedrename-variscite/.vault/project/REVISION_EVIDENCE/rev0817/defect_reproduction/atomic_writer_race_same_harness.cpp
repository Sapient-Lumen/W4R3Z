#include <atomic>
#include <barrier>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

namespace anonsync {
void write_sync_json_file_atomically_no_symlink_or_throw(
    const std::filesystem::path& final_path,
    const std::string& payload,
    const std::string& label);
}

static std::string read_all(const std::filesystem::path& path) {
    std::ifstream in(path, std::ios::binary);
    return std::string(std::istreambuf_iterator<char>(in), {});
}

int main() {
    namespace fs = std::filesystem;
    const fs::path root = fs::temp_directory_path() / "anonsync-parent-atomic-writer-race";
    std::error_code ec;
    fs::remove_all(root, ec);
    fs::create_directories(root);
    const fs::path final_path = root / "report.json";
    std::string payload = "{\"format\":\"race\",\"pad\":\"";
    payload.append(8u * 1024u * 1024u, 'x');
    payload += "\"}\n";

    constexpr int kThreads = 12;
    constexpr int kRounds = 12;
    std::atomic<int> exceptions{0};
    std::atomic<int> mismatches{0};
    std::mutex messages_mutex;
    std::vector<std::string> messages;

    for (int round = 0; round < kRounds; ++round) {
        std::barrier start(kThreads);
        std::vector<std::thread> threads;
        threads.reserve(kThreads);
        for (int i = 0; i < kThreads; ++i) {
            threads.emplace_back([&, i] {
                start.arrive_and_wait();
                try {
                    anonsync::write_sync_json_file_atomically_no_symlink_or_throw(
                        final_path, payload, "parent race writer " + std::to_string(i));
                } catch (const std::exception& e) {
                    ++exceptions;
                    std::lock_guard lock(messages_mutex);
                    if (messages.size() < 12) messages.emplace_back(e.what());
                }
            });
        }
        for (auto& thread : threads) thread.join();
        if (!fs::is_regular_file(final_path) || read_all(final_path) != payload) {
            ++mismatches;
        }
    }

    int tmp_entries = 0;
    for (const auto& entry : fs::directory_iterator(root)) {
        if (entry.path() != final_path) ++tmp_entries;
    }
    std::cout << "threads=" << kThreads << " rounds=" << kRounds
              << " calls=" << (kThreads * kRounds)
              << " exceptions=" << exceptions.load()
              << " final_mismatches=" << mismatches.load()
              << " temp_residue=" << tmp_entries << "\n";
    for (const auto& message : messages) std::cout << "error=" << message << "\n";
    fs::remove_all(root, ec);
    return (exceptions.load() == 0 && mismatches.load() == 0 && tmp_entries == 0) ? 0 : 1;
}
