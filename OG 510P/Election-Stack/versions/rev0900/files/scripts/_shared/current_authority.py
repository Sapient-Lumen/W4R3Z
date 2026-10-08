"""Shared current-authority source classification helpers.

Why this exists:
- Source-pressure, current-authority queue, and burndown-batch reports were
  carrying near-duplicate tag/host logic.
- rev0867 found real drift: one report counted Nevada/get.gov/tsapps.nist.gov
  differently than another, so maintainer work could be hidden or double-counted.

This module is deliberately stdlib-only and classification-only.  It does not
refresh sources, fetch network resources, or decide legal/current voter guidance.
"""

from __future__ import annotations

import datetime as dt
import re
from urllib.parse import urlparse

CURRENT_AUTHORITY_TAGS = {
    "ada", "accessibility", "aria", "cisa", "doj", "eac",
    "election_security", "nass", "nist", "rumor_control", "section508",
    "section_508", "vote_gov", "vvsg",
}

# State/local tags mean a row might be current jurisdiction-specific authority.
# They must not be generalized into national voter guidance.
STATE_HINT_TAGS = {
    "arizona", "california", "colorado", "delaware", "florida", "georgia",
    "indiana", "maryland", "michigan", "minnesota", "montana", "nevada",
    "new_hampshire", "new_mexico", "north_carolina", "north_dakota", "ohio",
    "oregon", "texas", "washington",
}

PLATFORM_TAGS = {
    "adobe", "android", "apple", "browser", "chrome", "css", "design",
    "digital_gov", "drive", "forms", "google", "gsa", "html", "mdn",
    "microsoft", "mobile", "notifications", "onedrive", "powerpoint",
    "safari", "search", "search_central", "sharepoint", "slides", "teams",
    "uswds", "video_players", "vimeo", "w3c", "wai", "wcag", "web_dev",
    "workspace", "youtube", "mozilla", "firefox", "slack", "open_graph",
    "link_previews", "social_share", "metadata", "unfurls",
}

AUTHORITY_HOST_SUFFIXES = (
    "eac.gov", "cisa.gov", "get.gov", "nist.gov", "csrc.nist.gov", "tsapps.nist.gov",
    "justice.gov", "civilrights.justice.gov", "vote.gov", "nass.org", "canivote.org",
    "ada.gov", "section508.gov", "uscis.gov",
)

PDFISH_RE = re.compile(r"\.(pdf|txt|csv|json|xml)(\?|$)", flags=re.I)
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


def host_of(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def path_of(url: str) -> str:
    return urlparse(url).path.lower()


def parsed_url_parts(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    return parsed.netloc.lower().removeprefix("www."), parsed.path.lower()


def tags_of(row: dict) -> set[str]:
    return {str(t).strip() for t in (row.get("tags") or []) if str(t).strip()}


def is_pinned(row: dict) -> bool:
    return bool(HEX64_RE.fullmatch(str(row.get("sha256") or "").strip()))


def review_by_date(row: dict) -> dt.date | None:
    rb = row.get("review_by")
    if not rb:
        return None
    try:
        return dt.date.fromisoformat(str(rb))
    except Exception:
        return None


def is_expired(row: dict, release_date: dt.date) -> bool:
    if is_pinned(row):
        return False
    review_by = review_by_date(row)
    return bool(review_by and review_by < release_date)


def is_due_soon(row: dict, release_date: dt.date, horizon_days: int) -> bool:
    if is_pinned(row):
        return False
    review_by = review_by_date(row)
    if review_by is None:
        return False
    return release_date <= review_by <= release_date + dt.timedelta(days=horizon_days)


def review_status(row: dict, release_date: dt.date, horizon_days: int) -> str:
    if is_expired(row, release_date):
        return "expired"
    if is_due_soon(row, release_date, horizon_days):
        return "due_soon"
    return "not_due"


def is_authority_host(host: str) -> bool:
    return host.endswith(AUTHORITY_HOST_SUFFIXES)


def is_current_authority(row: dict) -> bool:
    tags = tags_of(row)
    host = host_of(str(row.get("url") or ""))
    # rev0868: state/local rows can be retained as example/routing xrefs only.
    # Once explicitly quarantined, they must not be counted as current authority
    # until an adopter-specific review promotes them back out of quarantine.
    if {"jurisdiction_quarantine", "not_current_voter_instruction"} <= tags:
        return False
    if tags & STATE_HINT_TAGS:
        return True
    # `official_websites`, `ai`, and `public_comms` are not enough by themselves:
    # vendor/browser/link-preview documentation can be official for that vendor
    # without being current election/cyber/accessibility authority.
    if is_authority_host(host):
        return True
    if tags & CURRENT_AUTHORITY_TAGS and not (tags & PLATFORM_TAGS):
        return True
    return False


def lane_for(row: dict) -> str:
    tags = tags_of(row)
    host = host_of(str(row.get("url") or ""))
    if tags & STATE_HINT_TAGS:
        return "state_or_local_authority"
    if "eac" in tags or host.endswith("eac.gov") or "vvsg" in tags:
        return "federal_election_authority"
    if "cisa" in tags or "election_security" in tags or host.endswith(("cisa.gov", "get.gov")):
        return "federal_cyber_authority"
    if "nist" in tags or host.endswith(("nist.gov", "csrc.nist.gov", "tsapps.nist.gov")):
        return "federal_standards_or_ai_authority"
    if tags & {"doj", "ada", "accessibility", "wcag", "wai", "aria", "section508", "section_508"} or host.endswith(("justice.gov", "ada.gov", "section508.gov")):
        return "accessibility_or_rights_authority"
    if host.endswith(("vote.gov", "nass.org", "canivote.org")) or tags & {"vote_gov", "rumor_control"}:
        return "official_public_comms_authority"
    return "other_current_authority"


def dominant_topic(row: dict) -> str:
    tags = tags_of(row)
    ordered = [
        "vvsg", "certification", "voter_information", "registration", "accessibility",
        "election_security", "incident_comms", "gov_domains", "rumor_control",
        "citation_backfill", "official_websites", "nist", "ai", "state_law",
    ]
    for tag in ordered:
        if tag in tags:
            return tag
    if tags:
        return sorted(tags)[0]
    return "untagged"


def is_pin_first_candidate(row: dict) -> bool:
    return bool(PDFISH_RE.search(str(row.get("url") or "")))
