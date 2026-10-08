#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <iostream>
#include <string>
#include <sys/stat.h>
#include <unistd.h>

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: otmpfile_probe DIR\n";
        return 64;
    }
    const char* dir = argv[1];
    const std::string name = "otmpfile-linked-probe";
    int dirfd = ::open(dir, O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    if (dirfd < 0) {
        std::cout << "directory_open=failed errno=" << errno << " text=" << std::strerror(errno) << "\n";
        return 2;
    }
    ::unlinkat(dirfd, name.c_str(), 0);
    int fd = ::open(dir, O_TMPFILE | O_RDWR | O_CLOEXEC, 0600);
    if (fd < 0) {
        std::cout << "otmpfile_open=unsupported_or_failed errno=" << errno << " text=" << std::strerror(errno) << "\n";
        ::close(dirfd);
        return 0;
    }
    std::cout << "otmpfile_open=ok\n";
    const char payload[] = "anonsync-otmpfile-probe\n";
    if (::write(fd, payload, sizeof(payload) - 1) != static_cast<ssize_t>(sizeof(payload) - 1)) {
        std::cout << "write=failed errno=" << errno << " text=" << std::strerror(errno) << "\n";
        ::close(fd); ::close(dirfd); return 3;
    }
    if (::fsync(fd) != 0) {
        std::cout << "file_fsync=failed errno=" << errno << " text=" << std::strerror(errno) << "\n";
        ::close(fd); ::close(dirfd); return 4;
    }
    if (::linkat(fd, "", dirfd, name.c_str(), AT_EMPTY_PATH) != 0) {
        std::cout << "linkat_empty_path=failed errno=" << errno << " text=" << std::strerror(errno) << "\n";
        ::close(fd); ::close(dirfd); return 0;
    }
    std::cout << "linkat_empty_path=ok\n";
    if (::fsync(dirfd) != 0) {
        std::cout << "directory_fsync=failed errno=" << errno << " text=" << std::strerror(errno) << "\n";
    } else {
        std::cout << "directory_fsync=ok\n";
    }
    struct stat st{};
    if (::fstatat(dirfd, name.c_str(), &st, AT_SYMLINK_NOFOLLOW) == 0) {
        std::cout << "linked_mode=" << std::oct << (st.st_mode & 07777) << std::dec
                  << " size=" << st.st_size << " nlink=" << st.st_nlink << "\n";
    }
    if (::unlinkat(dirfd, name.c_str(), 0) == 0) {
        (void)::fsync(dirfd);
        std::cout << "cleanup=ok\n";
    }
    ::close(fd);
    ::close(dirfd);
    return 0;
}
