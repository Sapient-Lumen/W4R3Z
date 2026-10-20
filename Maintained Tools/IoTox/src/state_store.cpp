#include "iotox/state_store.hpp"

#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <fstream>
#include <string>
#include <system_error>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace iotox {
namespace {

Status io_status(const std::string &operation, const std::filesystem::path &path) {
    return Status{ErrorCode::io_error,
                  operation + " '" + path.string() + "': " + std::strerror(errno)};
}

}  // namespace

Result<std::vector<std::uint8_t>> StateStore::read(const std::filesystem::path &path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        if (errno == ENOENT) {
            return Status{ErrorCode::not_found, "state file does not exist: " + path.string()};
        }
        return io_status("unable to open state file", path);
    }

    input.seekg(0, std::ios::end);
    const std::streamoff size = input.tellg();
    if (size < 0) {
        return Status{ErrorCode::io_error, "unable to determine state-file size: " + path.string()};
    }
    input.seekg(0, std::ios::beg);

    std::vector<std::uint8_t> data(static_cast<std::size_t>(size));
    if (!data.empty()) {
        input.read(reinterpret_cast<char *>(data.data()), size);
        if (!input) {
            return Status{ErrorCode::io_error, "unable to read complete state file: " + path.string()};
        }
    }
    return data;
}

Status StateStore::write_atomic(const std::filesystem::path &path, std::span<const std::uint8_t> bytes) {
    const std::filesystem::path parent =
        path.has_parent_path() ? path.parent_path() : std::filesystem::path{"."};
    std::error_code directory_error;
    std::vector<std::filesystem::path> absent_parents;
    for (std::filesystem::path candidate = parent; !candidate.empty();) {
        const auto state = std::filesystem::symlink_status(
            candidate, directory_error);
        if (!directory_error && std::filesystem::exists(state)) break;
        if ((!directory_error &&
             state.type() != std::filesystem::file_type::not_found) ||
            (directory_error &&
             directory_error != std::errc::no_such_file_or_directory)) {
            return Status{ErrorCode::io_error,
                          "unable to inspect state directory '" +
                              candidate.string() + "': " +
                              directory_error.message()};
        }
        directory_error.clear();
        absent_parents.push_back(candidate);
        const auto next = candidate.parent_path();
        if (next == candidate) break;
        candidate = next;
    }
    std::filesystem::create_directories(parent, directory_error);
    if (directory_error) {
        return Status{ErrorCode::io_error,
                      "unable to create state directory '" + parent.string() +
                          "': " + directory_error.message()};
    }
    for (const auto &created : absent_parents) {
        std::filesystem::permissions(
            created, std::filesystem::perms::owner_all,
            std::filesystem::perm_options::replace, directory_error);
        if (directory_error) {
            return Status{ErrorCode::io_error,
                          "unable to make state directory private '" +
                              created.string() + "': " +
                              directory_error.message()};
        }
    }

    const std::string temporary_pattern =
        (parent / (".iotox-" + path.filename().string() + ".tmp.XXXXXX")).string();
    std::vector<char> mutable_pattern(temporary_pattern.begin(), temporary_pattern.end());
    mutable_pattern.push_back('\0');

    const int descriptor = ::mkstemp(mutable_pattern.data());
    if (descriptor < 0) {
        return io_status("unable to create temporary state file", temporary_pattern);
    }
    const std::filesystem::path temporary{mutable_pattern.data()};

    Status status = Status::success();
    const int descriptor_flags = ::fcntl(descriptor, F_GETFD);
    if (descriptor_flags < 0 || ::fcntl(descriptor, F_SETFD, descriptor_flags | FD_CLOEXEC) != 0) {
        status = io_status("unable to mark temporary state file close-on-exec", temporary);
    }
    if (status.ok() && ::fchmod(descriptor, S_IRUSR | S_IWUSR) != 0) {
        status = io_status("unable to set private temporary state permissions", temporary);
    }

    std::size_t written = 0;
    while (status.ok() && written < bytes.size()) {
        const ssize_t count = ::write(descriptor, bytes.data() + written, bytes.size() - written);
        if (count < 0) {
            if (errno == EINTR) {
                continue;
            }
            status = io_status("unable to write temporary state file", temporary);
            break;
        }
        if (count == 0) {
            status = Status{ErrorCode::io_error,
                            "unable to write temporary state file '" + temporary.string() +
                                "': write made no progress"};
            break;
        }
        written += static_cast<std::size_t>(count);
    }

    if (status.ok() && ::fsync(descriptor) != 0) {
        status = io_status("unable to fsync temporary state file", temporary);
    }
    if (::close(descriptor) != 0 && status.ok()) {
        status = io_status("unable to close temporary state file", temporary);
    }

    if (!status.ok()) {
        std::error_code ignored;
        std::filesystem::remove(temporary, ignored);
        return status;
    }

    if (::rename(temporary.c_str(), path.c_str()) != 0) {
        const Status rename_status = io_status("unable to atomically replace state file", path);
        std::error_code ignored;
        std::filesystem::remove(temporary, ignored);
        return rename_status;
    }

    const int directory_fd = ::open(parent.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    if (directory_fd < 0) {
        return io_status("unable to open state directory for fsync", parent);
    }
    if (::fsync(directory_fd) != 0) {
        const Status directory_status = io_status("unable to fsync state directory", parent);
        static_cast<void>(::close(directory_fd));
        return directory_status;
    }
    if (::close(directory_fd) != 0) {
        return io_status("unable to close state directory", parent);
    }

    return Status::success();
}

}  // namespace iotox
