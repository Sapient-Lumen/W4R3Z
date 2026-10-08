#pragma once

#if !defined(_WIN32)

#include <cstdint>
#include <filesystem>
#include <string>
#include <string_view>
#include <vector>

namespace anonsync {

// Resolves one executable installed beside the currently running ELF image.
// Product composition deliberately does not consult PATH: share bootstrap must
// invoke the exact anonsync_replica/anonsync_folder build shipped with this
// anonsync_sync binary rather than an unrelated command selected by ambient
// environment state.
[[nodiscard]] std::filesystem::path
resolve_sync_sibling_executable_or_throw(
    std::string_view executable_basename,
    std::string_view label = "sync sibling executable");

// Executes one exact sibling without a shell, drains stdout and stderr
// concurrently under independent byte ceilings, and requires a normal zero
// exit. A failure retains the bounded child diagnostic in the parent command's
// structured error instead of reducing setup failures to an exit number; a
// successful child's diagnostics are replayed to the parent stderr. Arguments
// exclude argv[0]. This owner is intentionally synchronous: it is for bounded
// setup composition, never the retained sync service or its retry scheduler.
[[nodiscard]] std::string run_sync_sibling_process_or_throw(
    const std::filesystem::path& absolute_executable,
    const std::vector<std::string>& arguments,
    std::uint64_t maximum_stdout_bytes,
    std::string_view label = "sync sibling process");

}  // namespace anonsync

#endif
