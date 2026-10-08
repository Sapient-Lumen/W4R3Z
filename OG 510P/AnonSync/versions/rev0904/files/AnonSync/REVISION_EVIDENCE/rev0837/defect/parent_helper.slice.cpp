std::string read_regular_file_bounded_no_symlink_or_throw(const fs::path& path,
                                                          std::uint64_t maximum_bytes,
                                                          const std::string& label) {
    if (maximum_bytes == 0) throw std::runtime_error(label + " maximum bytes must be positive");
#if defined(_WIN32)
    std::error_code ec;
    const fs::file_status status = fs::symlink_status(path, ec);
    if (ec) throw std::runtime_error(label + " could not inspect file: " + ec.message());
    if (!fs::exists(status)) throw std::runtime_error(label + " file is missing");
    if (fs::is_symlink(status)) throw std::runtime_error(label + " file must not be a symlink");
    if (!fs::is_regular_file(status)) throw std::runtime_error(label + " path is not a regular file");
    const auto size = fs::file_size(path, ec);
    if (ec) throw std::runtime_error(label + " size could not be inspected: " + ec.message());
    if (size > maximum_bytes) throw std::runtime_error(label + " exceeds bounded read limit");
    return read_file(path.string());
#else
    int flags = O_RDONLY;
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
    const std::string native = path.string();
    int fd = ::open(native.c_str(), flags);
    if (fd < 0) throw std::runtime_error(label + " open failed: " + std::strerror(errno));
    int saved_errno = 0;
    std::string out;
    try {
        struct stat st;
        if (::fstat(fd, &st) != 0) throw std::runtime_error(label + " fstat failed: " + std::strerror(errno));
        if (!S_ISREG(st.st_mode)) throw std::runtime_error(label + " path is not a regular file");
        if (st.st_size < 0) throw std::runtime_error(label + " file size is negative");
        if (static_cast<std::uint64_t>(st.st_size) > maximum_bytes) throw std::runtime_error(label + " exceeds bounded read limit");
        out.resize(static_cast<std::size_t>(st.st_size));
        std::size_t offset = 0;
        while (offset < out.size()) {
            const ssize_t got = ::read(fd, out.data() + offset, out.size() - offset);
            if (got < 0) {
                if (errno == EINTR) continue;
                throw std::runtime_error(label + " read failed: " + std::strerror(errno));
            }
            if (got == 0) break;
            offset += static_cast<std::size_t>(got);
        }
        out.resize(offset);
    } catch (...) {
        if (::close(fd) != 0 && saved_errno == 0) saved_errno = errno;
        throw;
    }
    if (::close(fd) != 0 && saved_errno == 0) saved_errno = errno;
    if (saved_errno != 0) throw std::runtime_error(label + " close failed: " + std::strerror(saved_errno));
    return out;
#endif
}
