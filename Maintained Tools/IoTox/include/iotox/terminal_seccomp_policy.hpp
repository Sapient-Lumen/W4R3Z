#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

#include <linux/kd.h>
#include <linux/vt.h>
#include <sys/ioctl.h>
#include <termios.h>

namespace iotox::terminal::detail {

// One shared build-header-derived request set drives both the installed
// classic-BPF policy and the exec'd native payload oracle. Keeping the list in
// one translation-independent header prevents an include-order difference from
// silently shrinking the verifier relative to the enforcement boundary.
inline constexpr auto kDeniedTerminalIoctlRequests =
    std::to_array<std::uint32_t>({
#ifdef TIOCNOTTY
        static_cast<std::uint32_t>(TIOCNOTTY),
#endif
#ifdef TIOCSCTTY
        static_cast<std::uint32_t>(TIOCSCTTY),
#endif
#ifdef TIOCSTI
        static_cast<std::uint32_t>(TIOCSTI),
#endif
#ifdef TIOCLINUX
        static_cast<std::uint32_t>(TIOCLINUX),
#endif
#ifdef TIOCSETD
        static_cast<std::uint32_t>(TIOCSETD),
#endif
#ifdef TIOCCONS
        static_cast<std::uint32_t>(TIOCCONS),
#endif
#ifdef TIOCVHANGUP
        static_cast<std::uint32_t>(TIOCVHANGUP),
#endif
#ifdef KDENABIO
        static_cast<std::uint32_t>(KDENABIO),
#endif
#ifdef KDDISABIO
        static_cast<std::uint32_t>(KDDISABIO),
#endif
#ifdef KDSETMODE
        static_cast<std::uint32_t>(KDSETMODE),
#endif
#ifdef KDSKBMODE
        static_cast<std::uint32_t>(KDSKBMODE),
#endif
#ifdef KDSKBENT
        static_cast<std::uint32_t>(KDSKBENT),
#endif
#ifdef KDSKBSENT
        static_cast<std::uint32_t>(KDSKBSENT),
#endif
#ifdef KDSKBMETA
        static_cast<std::uint32_t>(KDSKBMETA),
#endif
#ifdef KDSKBLED
        static_cast<std::uint32_t>(KDSKBLED),
#endif
#ifdef KDFONTOP
        static_cast<std::uint32_t>(KDFONTOP),
#endif
#ifdef PIO_FONT
        static_cast<std::uint32_t>(PIO_FONT),
#endif
#ifdef PIO_FONTX
        static_cast<std::uint32_t>(PIO_FONTX),
#endif
#ifdef PIO_SCRNMAP
        static_cast<std::uint32_t>(PIO_SCRNMAP),
#endif
#ifdef PIO_UNISCRNMAP
        static_cast<std::uint32_t>(PIO_UNISCRNMAP),
#endif
#ifdef VT_SETMODE
        static_cast<std::uint32_t>(VT_SETMODE),
#endif
#ifdef VT_RELDISP
        static_cast<std::uint32_t>(VT_RELDISP),
#endif
#ifdef VT_ACTIVATE
        static_cast<std::uint32_t>(VT_ACTIVATE),
#endif
#ifdef VT_WAITACTIVE
        static_cast<std::uint32_t>(VT_WAITACTIVE),
#endif
#ifdef VT_DISALLOCATE
        static_cast<std::uint32_t>(VT_DISALLOCATE),
#endif
#ifdef VT_RESIZE
        static_cast<std::uint32_t>(VT_RESIZE),
#endif
#ifdef VT_RESIZEX
        static_cast<std::uint32_t>(VT_RESIZEX),
#endif
#ifdef VT_LOCKSWITCH
        static_cast<std::uint32_t>(VT_LOCKSWITCH),
#endif
#ifdef VT_UNLOCKSWITCH
        static_cast<std::uint32_t>(VT_UNLOCKSWITCH),
#endif
    });

template <std::size_t Size>
[[nodiscard]] consteval bool terminal_ioctl_requests_are_unique(
    const std::array<std::uint32_t, Size> &requests) {
    for (std::size_t left = 0U; left < requests.size(); ++left) {
        for (std::size_t right = left + 1U; right < requests.size(); ++right) {
            if (requests[left] == requests[right]) return false;
        }
    }
    return true;
}

template <std::size_t Size>
[[nodiscard]] consteval bool terminal_ioctl_requests_contain(
    const std::array<std::uint32_t, Size> &requests,
    std::uint32_t candidate) {
    for (const std::uint32_t request : requests) {
        if (request == candidate) return true;
    }
    return false;
}

static_assert(!kDeniedTerminalIoctlRequests.empty());
static_assert(kDeniedTerminalIoctlRequests.size() <= 64U);
static_assert(terminal_ioctl_requests_are_unique(
    kDeniedTerminalIoctlRequests));
#ifdef TIOCGWINSZ
static_assert(!terminal_ioctl_requests_contain(
    kDeniedTerminalIoctlRequests, static_cast<std::uint32_t>(TIOCGWINSZ)));
#endif
#ifdef TIOCSWINSZ
static_assert(!terminal_ioctl_requests_contain(
    kDeniedTerminalIoctlRequests, static_cast<std::uint32_t>(TIOCSWINSZ)));
#endif

}  // namespace iotox::terminal::detail
