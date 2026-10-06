#!/usr/bin/env python3
"""Static guard for the FreeBSD Capsicum fd-only worker scaffold.

This does not pretend to compile or run Capsicum inside the cloudtainer.  It
prevents the future FreeBSD apply path from regressing into another Python
fixture-only proof: the cube must carry a concrete worker source that enters
capability mode, limits the two delegated descriptors, closes all higher fds,
truthfully reports startup and post-stdio failures through fd 4, and accepts no
path/device arguments.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REL = "tools/freebsd/rm_post_detach_capsicum_worker.c"
SOURCE = ROOT / SOURCE_REL
DOC_REL = "docs/current/removable-media-local-fallback-freebsd-backend-run.md"


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    if not SOURCE.exists():
        print("Capsicum worker source check FAILED.")
        print(f"- missing {SOURCE_REL}")
        return 1

    text = SOURCE.read_text(encoding="utf-8", errors="replace")
    compact = re.sub(r"\s+", " ", text)
    after_cap_enter = text.split("cap_enter()", 1)[-1] if "cap_enter()" in text else text

    required_tokens = [
        "#ifdef __FreeBSD__",
        "#include <sys/capsicum.h>",
        "#include <sys/stat.h>",
        "#error",
        "#define REMEDIA_INPUT_FD 3",
        "#define REMEDIA_OUTPUT_FD 4",
        "closefrom(FD_AFTER_DELEGATED_SET)",
        "verify_extra_fds_closed_before_cap_enter();",
        "EXTRA_FD_SCAN_LIMIT",
        "extra_fds_closed_before_cap_enter",
        "extra_fd_still_open_before_cap_enter",
        "observe_extra_fd_canary_before_closefrom();",
        "extra_fd_canary_observed_before_closefrom",
        '\\\"extra_fd_canary_source\\\":\\\"broker-nonmedia-canary-not-source-media',
        "close_standard_fds();",
        "STDIN_FILENO, STDOUT_FILENO, STDERR_FILENO",
        "cap_rights_limit(REMEDIA_INPUT_FD",
        "cap_rights_init(&input_rights, CAP_READ, CAP_FSTAT)",
        "cap_rights_limit(REMEDIA_OUTPUT_FD",
        "cap_rights_init(&output_rights, CAP_WRITE, CAP_FSTAT, CAP_FSYNC)",
        "cap_enter()",
        "verify_delegated_fds_regular();",
        "fstat(REMEDIA_INPUT_FD",
        "fstat(REMEDIA_OUTPUT_FD",
        "S_ISREG(input_st.st_mode)",
        "S_ISREG(output_st.st_mode)",
        "input_fd_not_regular",
        "output_fd_not_regular",
        "input_fd_regular\\\":true",
        "output_fd_regular\\\":true",
        "path_arguments_rejected",
        "path_arguments_accepted\\\":false",
        "delegated-output-fd-before-stdio-close",
        "delegated-output-fd-after-stdio-close",
        "startup_failure_report_channel\\\":\\\"delegated-output-fd-before-or-after-stdio-close",
    ]
    for token in required_tokens:
        require(errors, token in text, f"{SOURCE_REL} missing token {token!r}")

    forbidden_anywhere = [
        "/dev/",
        "/mnt",
        "argv[1]",
        "getenv(",
        "system(",
        "popen(",
        "execv(",
        "execl(",
        "fork(",
    ]
    for token in forbidden_anywhere:
        require(errors, token not in text, f"{SOURCE_REL} must not contain {token!r}")

    forbidden_after_cap_enter = [r"\bopen\s*\(", r"\bopenat\s*\(", r"\bfopen\s*\(", r"\bstat\s*\(", r"\blstat\s*\("]
    for pattern in forbidden_after_cap_enter:
        require(errors, re.search(pattern, after_cap_enter) is None, f"{SOURCE_REL} must not acquire pathname resources after cap_enter: matched {pattern!r}")

    require(errors, "int main(int argc, char **argv)" in compact, "worker main signature should make argv visible for no-argument enforcement")
    require(errors, "if (argc != 1)" in compact, "worker must reject all argv path/device arguments")
    require(errors, "err(" not in text and "errx(" not in text and "#include <err.h>" not in text, "worker must not depend on stderr err()/errx() at startup or after stdio closure")
    require(errors, 'fatal_to_delegated_output("path_arguments_rejected", false)' in text, "path-argument rejection must not claim stdio was already closed")
    require(errors, 'fatal_to_delegated_output("input_fd_not_regular", true)' in text, "post-cap fd validation failures must report after stdio closure")
    require(errors, 'standard_fds_closed ? "true" : "false"' in text, "failure reports must not hard-code stdio closure state")
    require(errors, 'failure_channel_for_current_stdio_state()' in text and 'if (standard_fds_closed)' in text, "failure reports must derive the before/after-stdio channel from real closure state")
    require(errors, "stdio_fds_closed_before_report" in text, "failure reports must expose whether stdio was closed before the report")

    order_text = re.sub(r"\s+", " ", text)
    require(errors, "observe_extra_fd_canary_before_closefrom();" in text and order_text.find("observe_extra_fd_canary_before_closefrom();") < order_text.find("closefrom(FD_AFTER_DELEGATED_SET)"), "worker must observe fd-5 before closefrom so the canary proof is real")
    require(errors, order_text.find("close_standard_fds();") != -1 and order_text.find("limit_delegated_rights();") != -1 and order_text.find("close_standard_fds();") < order_text.find("limit_delegated_rights();"), "worker must close stdio before delegated-right limiting so later failure paths cannot write to misdelegated fd 0/1/2")
    require(errors, order_text.find("close_standard_fds();") != -1 and order_text.find("if (cap_enter()") != -1 and order_text.find("close_standard_fds();") < order_text.find("if (cap_enter()"), "worker must close stdio fds before cap_enter so fd 0/1/2 cannot carry source-media authority")
    after_stdio_close = text.split("close_standard_fds();", 1)[-1] if "close_standard_fds();" in text else text
    require(errors, "err(" not in after_stdio_close and "errx(" not in after_stdio_close, "worker must not rely on stderr/err() after closing fd 0/1/2; use delegated output failure reports")

    doc = ROOT / DOC_REL
    if doc.exists():
        doc_text = doc.read_text(encoding="utf-8", errors="replace")
        for token in [SOURCE_REL, "cap_enter", "cap_rights_limit", "closefrom", "fstat", "delegated-output-fd-before-stdio-close", "delegated-output-fd-before-or-after-stdio-close", "extra_fds_closed_before_cap_enter", "extra_fd_scan_limit", "input_sha256"]:
            require(errors, token in doc_text, f"{DOC_REL} missing Capsicum worker token {token!r}")
    else:
        errors.append(f"missing {DOC_REL}")

    if errors:
        print("Capsicum worker source check FAILED.")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Capsicum worker source check OK")
    print(f"{SOURCE_REL}: FreeBSD-only fd worker scaffold closes stdio before rights/cap_enter, truthfully separates pre-stdio and post-stdio fd-4 failure reports, closes unexpected inherited fds before cap_enter, limits input/output rights, verifies regular fds, and accepts no path arguments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
