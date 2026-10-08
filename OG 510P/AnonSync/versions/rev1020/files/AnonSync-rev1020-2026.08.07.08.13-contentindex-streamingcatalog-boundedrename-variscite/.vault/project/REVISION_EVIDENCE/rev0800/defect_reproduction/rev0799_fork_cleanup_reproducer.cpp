#include "sqlite_snapshot_seal.hpp"

#include <sqlite3.h>
#include <sys/wait.h>
#include <unistd.h>

#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>

namespace fs = std::filesystem;
using anonsync::persistence::SealedSqliteSnapshot;

void sqlite_or_throw(int rc, sqlite3* db, const char* operation) {
    if (rc != SQLITE_OK) {
        const std::string detail = db == nullptr ? "unknown" : sqlite3_errmsg(db);
        throw std::runtime_error(std::string(operation) + ": " + detail);
    }
}

int main() {
    char pattern[] = "/tmp/anonsync-rev0799-fork-repro-XXXXXX";
    char* root_text = ::mkdtemp(pattern);
    if (root_text == nullptr) return 2;
    const fs::path root(root_text);
    const fs::path source = root / "source.sqlite";
    try {
        sqlite3* raw = nullptr;
        sqlite_or_throw(sqlite3_open(source.c_str(), &raw), raw, "open fixture");
        sqlite_or_throw(sqlite3_exec(raw,
            "CREATE TABLE evidence(value TEXT NOT NULL);"
            "INSERT INTO evidence VALUES('parent');",
            nullptr, nullptr, nullptr), raw, "create fixture");
        sqlite_or_throw(sqlite3_close(raw), raw, "close fixture");

        SealedSqliteSnapshot seal = SealedSqliteSnapshot::capture(
            source, "rev0799 fork cleanup reproducer");
        const fs::path staged = seal.staged_path();

        const pid_t child = ::fork();
        if (child < 0) throw std::runtime_error("fork failed");
        if (child == 0) {
            seal = SealedSqliteSnapshot{};
            std::_Exit(0);
        }
        int status = 0;
        if (::waitpid(child, &status, 0) != child) {
            throw std::runtime_error("waitpid failed");
        }
        const int child_exit = WIFEXITED(status) ? WEXITSTATUS(status) : 255;
        const bool staged_exists = fs::exists(staged);
        bool verification_failed = false;
        std::string parent_error;
        try {
            seal.verify_unchanged_or_throw("parent post-child verification");
        } catch (const std::exception& error) {
            verification_failed = true;
            parent_error = error.what();
        }

        std::cout << "child_exit=" << child_exit << "\n";
        std::cout << "staged_exists_after_child_cleanup="
                  << (staged_exists ? "true" : "false") << "\n";
        std::cout << "parent_error=" << parent_error << "\n";
        std::cout << "parent_verification_failed="
                  << (verification_failed ? "true" : "false") << "\n";
        fs::remove_all(root);
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "reproducer failed: " << error.what() << "\n";
        fs::remove_all(root);
        return 3;
    }
}
