"""Surface intelligence — GlassTTY's drift-hunting wing.

The problem this solves: ChatGPT's UI changes without warning, and when it does,
GlassTTY fails in ways that look like *your* bug. The existing surface contract
can only answer "is what I already knew about still there?" — it is structurally
incapable of noticing anything new.

This module closes the loop:

    probe    → a full, classified inventory of the live UI (extension side)
    snapshot → normalize + store it, so the UI has a *history*
    diff     → what changed between two moments
    triage   → which GlassTTY capabilities that change breaks, and how badly
    repair   → concrete candidate selectors to fix a broken anchor

The payoff is that a failure stops being a mystery. When `glassttyd ask` fails,
`--diagnose` captures the surface at the moment of failure, diffs it against the
last known-good snapshot, and tells you *what changed and what it broke* — instead
of leaving you to bisect a 4,000-line userscript at 2am.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JsonDict = dict[str, Any]

SNAPSHOT_SCHEMA = "glasstty-surface-snapshot/v1"

# Which GlassTTY commands die when a capability is lost. This is the map that
# turns "the DOM changed" into "your `ask` is broken", which is the only framing
# an operator can act on.
CAPABILITY_IMPACT: dict[str, dict[str, Any]] = {
    "write_prompt": {
        "breaks": ["ask", "chat", "run"],
        "severity": "critical",
        "anchor": "composer",
        "why": "nothing can be typed into the page",
    },
    "submit_prompt": {
        "breaks": ["ask", "chat", "run"],
        "severity": "critical",
        "anchor": "send",
        "why": "a prompt can be staged but never sent",
    },
    "read_latest_output": {
        "breaks": ["ask", "chat", "run"],
        "severity": "critical",
        "anchor": "latest_assistant_turn",
        "why": "an answer can be produced but never read back",
    },
    "detect_generation": {
        "breaks": ["ask", "chat", "run"],
        "severity": "degraded",
        "anchor": None,
        "why": "the engine falls back to text-stability detection, which is slower and can truncate a slow answer",
    },
    "continue_generation": {
        # Absent whenever nothing needs continuing, i.e. almost always. Reported
        # for completeness but never treated as damage.
        "breaks": [],
        "severity": "info",
        "anchor": "generation_continue",
        "why": "long answers stop at the continue gate instead of being stitched",
    },
    "attach_files": {
        "breaks": ["ask --attach", "run --attach"],
        "severity": "degraded",
        "anchor": None,
        "why": "no file input was found, so nothing can be attached to a prompt",
    },
    "read_user_turn": {
        "breaks": [],
        "severity": "info",
        "anchor": "latest_user_turn",
        "why": "turn-pair witnesses become unavailable (proof lane only)",
    },
}

# Anchors that are absent *by design* whenever the page is idle. A missing "stop
# generating" button is not drift — it means nothing is generating. Proposing a
# repair for these would be crying wolf, and a drift detector that cries wolf is
# one that gets ignored on the day it is right.
TRANSIENT_ANCHORS = {"generation_stop", "generation_continue"}

# Same idea, one level up: `continue_generation` is false whenever nothing needs
# continuing — i.e. almost always, on a perfectly healthy page. Reporting it as a
# lost capability made a pristine surface look drifted, which is precisely the
# false positive that trains an operator to ignore the tool.
TRANSIENT_CAPABILITIES = {"continue_generation"}

# When an anchor breaks, these classified roles are plausible replacements.
# Ranking a live control against the role it *should* fill is what turns a
# detected drift into an actionable repair.
ANCHOR_ROLE_HINTS: dict[str, list[str]] = {
    "composer": [],
    "send": ["send", "unknown"],
    "generation_stop": ["stop", "unknown"],
    "generation_continue": ["continue", "unknown"],
}


# Framework-generated ids. Observed live on 2026-07-11: 65 nodes matching
# [id^="radix-"], including the composer's own effort pill (#radix-_r_ds_).
# They are regenerated on every page load. An override written against one of
# these looks perfectly precise and silently stops matching tomorrow — which is
# worse than never having repaired anything, because you think you fixed it.
VOLATILE_ID_PATTERNS = [
    re.compile(r"(^|#)radix-", re.I),
    re.compile(r"(^|#):r[0-9a-z]+:", re.I),
    re.compile(r"(^|#)headlessui-", re.I),
    re.compile(r"(^|#)mui-", re.I),
    re.compile(r"(^|#)react-aria-", re.I),
]


def is_volatile_id(value: str | None) -> bool:
    if not value:
        return True
    return any(pattern.search(value) for pattern in VOLATILE_ID_PATTERNS)


def is_stable_selector(selector: str | None) -> bool:
    """A selector we are willing to persist as a repair."""
    if not selector:
        return False
    # A volatile id poisons the selector wherever it appears, not just at the front:
    # `button#radix-_r_ds_` is exactly as worthless as `#radix-_r_ds_`.
    if any(pattern.search(selector) for pattern in VOLATILE_ID_PATTERNS):
        return False
    if "#" in selector:
        fragment = selector.split("#", 1)[1].split()[0].split(">")[0].split("[")[0]
        if is_volatile_id(fragment):
            return False
    # Structural paths (div:nth-of-type(1) > ...) are as brittle as volatile ids.
    if "nth-of-type" in selector or "nth-child" in selector:
        return False
    return True


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# --------------------------------------------------------------------------- #
# Snapshot
# --------------------------------------------------------------------------- #
def build_snapshot(probe: JsonDict, *, label: str | None = None, source: str = "live") -> JsonDict:
    """Normalize a raw extension probe into a stored, diffable snapshot."""
    controls = probe.get("controls") if isinstance(probe.get("controls"), list) else []
    anchors = probe.get("anchors") if isinstance(probe.get("anchors"), list) else []

    snapshot: JsonDict = {
        "schema": SNAPSHOT_SCHEMA,
        "captured_at": probe.get("captured_at") or utcnow(),
        "stored_at": utcnow(),
        "label": label,
        "source": source,
        "probe_version": probe.get("probe_version"),
        "url": probe.get("url"),
        "route": probe.get("route") or {},
        "authentication": probe.get("authentication") or {},
        "composer": probe.get("composer") or {},
        "capabilities": probe.get("capabilities") or {},
        "anchors": {a.get("name"): a for a in anchors if isinstance(a, dict) and a.get("name")},
        "controls": {c.get("key"): c for c in controls if isinstance(c, dict) and c.get("key")},
        "oddities": probe.get("oddities") or [],
        "counts": probe.get("counts") or {},
    }
    snapshot["fingerprint"] = fingerprint(snapshot)
    return snapshot


def fingerprint(snapshot: JsonDict) -> str:
    """A stable hash of the *structural* surface — not of timestamps or text.

    Two snapshots with the same fingerprint describe the same UI, so a watcher can
    detect "the UI changed" without diffing everything on every poll.
    """
    material = {
        "route_posture": (snapshot.get("route") or {}).get("posture"),
        "authentication_posture": (snapshot.get("authentication") or {}).get("posture"),
        "capabilities": snapshot.get("capabilities"),
        "anchors": {
            name: {
                "found": a.get("found"),
                "selector_hint": a.get("selector_hint"),
                "matches_expectation": a.get("matches_expectation"),
            }
            for name, a in sorted((snapshot.get("anchors") or {}).items())
        },
        "controls": sorted(
            [
                f"{key}|{c.get('classification')}|{c.get('region')}"
                for key, c in (snapshot.get("controls") or {}).items()
                if c.get("visible")
            ]
        ),
    }
    raw = json.dumps(material, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


# --------------------------------------------------------------------------- #
# Diff
# --------------------------------------------------------------------------- #
def diff_snapshots(before: JsonDict, after: JsonDict) -> JsonDict:
    """Structural diff of two surface snapshots."""
    b_controls = before.get("controls") or {}
    a_controls = after.get("controls") or {}
    b_anchors = before.get("anchors") or {}
    a_anchors = after.get("anchors") or {}
    b_caps = before.get("capabilities") or {}
    a_caps = after.get("capabilities") or {}
    b_auth = (before.get("authentication") or {}).get("posture")
    a_auth = (after.get("authentication") or {}).get("posture")

    added = [a_controls[k] for k in sorted(set(a_controls) - set(b_controls))]
    removed = [b_controls[k] for k in sorted(set(b_controls) - set(a_controls))]

    changed: list[JsonDict] = []
    for key in sorted(set(a_controls) & set(b_controls)):
        before_c, after_c = b_controls[key], a_controls[key]
        deltas = {
            field: {"before": before_c.get(field), "after": after_c.get(field)}
            for field in ("classification", "region", "visible", "disabled", "selector_hint", "aria_label", "test_id")
            if before_c.get(field) != after_c.get(field)
        }
        if deltas:
            changed.append({"key": key, "changes": deltas})

    anchor_changes: list[JsonDict] = []
    for name in sorted(set(b_anchors) | set(a_anchors)):
        before_a = b_anchors.get(name, {})
        after_a = a_anchors.get(name, {})
        deltas = {
            field: {"before": before_a.get(field), "after": after_a.get(field)}
            for field in ("found", "selector_hint", "matches_expectation")
            if before_a.get(field) != after_a.get(field)
        }
        if deltas:
            anchor_changes.append({"anchor": name, "changes": deltas})

    capability_changes = [
        {"capability": name, "before": b_caps.get(name), "after": a_caps.get(name)}
        for name in sorted(set(b_caps) | set(a_caps))
        if b_caps.get(name) != a_caps.get(name)
    ]
    authentication_change = (
        {"before": b_auth, "after": a_auth}
        if b_auth != a_auth
        else None
    )

    return {
        "schema": "glasstty-surface-diff/v1",
        "generated_at": utcnow(),
        "before_fingerprint": before.get("fingerprint"),
        "after_fingerprint": after.get("fingerprint"),
        "identical": before.get("fingerprint") == after.get("fingerprint"),
        "route_changed": (before.get("route") or {}).get("posture") != (after.get("route") or {}).get("posture"),
        "authentication_change": authentication_change,
        "capability_changes": capability_changes,
        "anchor_changes": anchor_changes,
        "controls_added": added,
        "controls_removed": removed,
        "controls_changed": changed,
        "counts": {
            "controls_added": len(added),
            "controls_removed": len(removed),
            "controls_changed": len(changed),
            "anchor_changes": len(anchor_changes),
            "capability_changes": len(capability_changes),
            "authentication_changes": int(authentication_change is not None),
        },
    }


# --------------------------------------------------------------------------- #
# Repair proposals
# --------------------------------------------------------------------------- #
def _score_replacement(control: JsonDict, anchor: str) -> float:
    """How plausible is this live control as a replacement for a broken anchor?

    Returns -1 for anything that is *disqualified outright*. This matters more
    than the ranking: an earlier version of this function happily proposed
    `send -> #prompt-textarea` — the text editor itself — because it was an
    unknown, visible thing sitting in the composer. A repair engine that can tell
    the adapter to click the text box is worse than no repair engine at all.
    """
    classification = control.get("classification")
    signals = " ".join(
        str(control.get(field) or "").lower()
        for field in ("aria_label", "title", "text", "test_id", "id")
    )

    if anchor == "send":
        # 1. It must actually be a clickable control. A div, a textarea, or the
        #    composer itself can never be the send button, however well it scores.
        button_like = (
            control.get("tag") in ("button", "a")
            or control.get("role_attr") == "button"
            or control.get("type_attr") == "submit"
        )
        if not button_like:
            return -1.0

        # 2. Anything we positively identified as some OTHER role is disqualified,
        #    not merely penalised. Enumerating the bad roles (as an earlier version
        #    did) means every new control ChatGPT ships is a fresh hole: the live
        #    2026-07-11 composer contains an effort pill that no blocklist knew
        #    about, and it sailed straight through. Invert the rule instead — only
        #    a confirmed send, or an honest unknown, may stand in for send.
        if classification not in ("send", "unknown"):
            return -1.0
        if any(term in signals for term in ("add files", "attach", "upload", "photo", "dictate", "microphone")):
            return -1.0

        score = 0.0
        if classification == "send":
            score += 0.6          # positively identified as send
        elif classification == "unknown":
            score += 0.2          # a candidate worth showing a human, never enough to auto-apply
        if "send" in signals:
            score += 0.3
        if control.get("type_attr") == "submit":
            score += 0.2
        if control.get("region") == "composer":
            score += 0.15
        if control.get("disabled"):
            score -= 0.2
        return round(score, 3)

    # Non-send anchors: only a positively classified control is a candidate.
    hints = ANCHOR_ROLE_HINTS.get(anchor, [])
    if classification not in hints or classification == "unknown":
        return -1.0
    score = 0.6
    if control.get("region") == "composer":
        score += 0.2
    if control.get("disabled"):
        score -= 0.2
    return round(score, 3)


# A repair is only auto-applied when the candidate was POSITIVELY identified as
# the role it is replacing. An 'unknown' control is surfaced for a human to look
# at (and can be forced with --force), but GlassTTY will not start clicking
# something it cannot name.
CONFIDENT_THRESHOLD = 0.6


def propose_repairs(snapshot: JsonDict, *, top_n: int = 3) -> list[JsonDict]:
    """For each broken/suspicious anchor, rank live controls that could replace it."""
    proposals: list[JsonDict] = []
    controls = list((snapshot.get("controls") or {}).values())
    capabilities = snapshot.get("capabilities") or {}
    composer = snapshot.get("composer") or {}

    # Send is hidden, not broken, whenever the composer is empty — so there is
    # nothing to repair and offering to repair it is just noise. Nothing erodes
    # trust in a drift detector faster than it proposing fixes for healthy pages.
    send_merely_hidden = capabilities.get("submit_prompt") is None or (
        composer.get("present") and composer.get("empty")
    )

    for name, anchor in (snapshot.get("anchors") or {}).items():
        if name in TRANSIENT_ANCHORS:
            continue
        if name == "send" and send_merely_hidden and not anchor.get("found"):
            continue
        # Only anchors under contract (those with an expected selector) can be
        # "wrong"; the rest are observations, not obligations.
        if not anchor.get("expected_selector"):
            continue
        broken = not anchor.get("found")
        substituted = bool(anchor.get("found")) and not anchor.get("matches_expectation")
        if not (broken or substituted):
            continue

        ranked = sorted(
            (
                {
                    "selector_hint": control.get("selector_hint"),
                    "key": control.get("key"),
                    "classification": control.get("classification"),
                    "region": control.get("region"),
                    "aria_label": control.get("aria_label"),
                    "test_id": control.get("test_id"),
                    "id": control.get("id"),
                    "confidence": _score_replacement(control, name),
                }
                for control in controls
                if control.get("visible")
            ),
            key=lambda row: row["confidence"],
            reverse=True,
        )
        candidates = [row for row in ranked if row["confidence"] > 0][:top_n]
        best = candidates[0] if candidates else None
        # Confident == "we positively identified the replacement", not merely
        # "it outscored the others". A field of bad options still has a winner.
        suggested = _suggest_selector(best) if best else None
        confident = bool(
            best
            and best["confidence"] >= CONFIDENT_THRESHOLD
            and best["classification"] != "unknown"
            # No durable selector => nothing worth persisting, however sure we are
            # about *which node* it is right now.
            and suggested is not None
        )

        proposals.append({
            "anchor": name,
            "problem": "missing" if broken else "resolved-to-unexpected-selector",
            "observed_selector": anchor.get("selector_hint"),
            "expected_selector": anchor.get("expected_selector"),
            "candidates": candidates,
            "suggested_selector": suggested,
            "confident": confident,
        })
    return proposals


def _suggest_selector(candidate: JsonDict) -> str | None:
    """Build the most durable selector we can from a candidate's identity.

    Order matters and so do the exclusions: a volatile framework id is the most
    *specific* thing on the node and the least *durable*. Preferring it — as an
    earlier version of this function did — produces an override that works once.
    """
    identifier = candidate.get("id")
    if identifier and not is_volatile_id(identifier):
        return f"#{identifier}"
    if candidate.get("test_id"):
        return f'[data-testid="{candidate["test_id"]}"]'
    if candidate.get("aria_label"):
        return f'[aria-label="{candidate["aria_label"]}"]'
    hint = candidate.get("selector_hint")
    return hint if is_stable_selector(hint) else None


# --------------------------------------------------------------------------- #
# Triage
# --------------------------------------------------------------------------- #
def triage(snapshot: JsonDict, *, baseline: JsonDict | None = None, failure: JsonDict | None = None) -> JsonDict:
    """Turn a snapshot (optionally vs a baseline, optionally around a failure)
    into an operator-facing diagnosis: what broke, what it breaks, what to do."""
    findings: list[JsonDict] = []
    capabilities = snapshot.get("capabilities") or {}
    authentication = snapshot.get("authentication") or {}

    # 1a. UNKNOWN capabilities. `None` means "cannot be determined right now",
    #     which is a different thing from "broken" and must never be reported as
    #     damage. The canonical case: send is not rendered until the composer has
    #     text, so an empty-composer probe simply cannot see it.
    for capability, value in capabilities.items():
        if value is not None:
            continue
        findings.append({
            "kind": "capability-unknown",
            "severity": "info",
            "capability": capability,
            "why": "cannot be determined from an idle page; re-probe with `--probe-with-draft` for a definitive reading",
        })

    # 1b. Lost capabilities — the direct "your command is broken" signal.
    for capability, lost in ((name, value is False) for name, value in capabilities.items()):
        if not lost or capability in TRANSIENT_CAPABILITIES:
            continue
        impact = CAPABILITY_IMPACT.get(capability, {})
        finding = {
            "kind": "capability-lost",
            "severity": impact.get("severity", "warn"),
            "capability": capability,
            "breaks_commands": impact.get("breaks", []),
            "why": impact.get("why", "a GlassTTY action depends on this"),
            "anchor": impact.get("anchor"),
        }
        if capability == "attach_files" and authentication.get("posture") == "anonymous":
            finding.update({
                "cause": "authentication-required",
                "why": "ChatGPT is logged out; file upload requires an authenticated browser session",
            })
        findings.append(finding)

    # 2. Anchors that resolved to something other than what the adapter expects.
    #    This is the silent-substitution case and it is the dangerous one: the
    #    command still "works", it just clicks the wrong thing.
    for name, anchor in (snapshot.get("anchors") or {}).items():
        if anchor.get("found") and anchor.get("expected_selector") and not anchor.get("matches_expectation"):
            findings.append({
                "kind": "anchor-substituted",
                "severity": "critical",
                "anchor": name,
                "observed": anchor.get("selector_hint"),
                "expected": anchor.get("expected_selector"),
                "why": "the adapter is about to act on a node it did not expect; this is how a wrong click happens",
            })

    # 3. Oddities from the probe (unknown composer controls, dialogs, banners).
    for oddity in snapshot.get("oddities") or []:
        if oddity.get("kind") in {"missing-anchor", "unexpected-anchor-selector"}:
            continue  # already covered above, do not double-report
        findings.append({
            "kind": f"oddity:{oddity.get('kind')}",
            "severity": oddity.get("severity", "info"),
            "summary": oddity.get("summary"),
            "region": oddity.get("region"),
            "control": oddity.get("control"),
        })

    # 4. Drift against the last known-good surface.
    delta: JsonDict | None = None
    if baseline is not None:
        delta = diff_snapshots(baseline, snapshot)
        if not delta["identical"]:
            for change in delta["capability_changes"]:
                # True -> None is "we can no longer see it", not "it broke".
                if change["after"] is None:
                    continue
                capability = change["capability"]
                if capability in TRANSIENT_CAPABILITIES:
                    continue
                if change["before"] and not change["after"]:
                    impact = CAPABILITY_IMPACT.get(capability, {})
                    findings.append({
                        "kind": "regression",
                        "severity": impact.get("severity", "warn"),
                        "summary": f"capability '{capability}' worked in the baseline and does not now",
                        "capability": capability,
                    })
            for control in delta["controls_added"]:
                # A *recognised* new control is already covered by the anchor findings.
                # An unrecognised one is the real oddity: it is how a new picker,
                # a new mode toggle, or a new decoy send button first appears.
                if (
                    control.get("region") == "composer"
                    and control.get("visible")
                    and control.get("classification") == "unknown"
                ):
                    findings.append({
                        "kind": "new-composer-control",
                        "severity": "warn",
                        "summary": f"a control appeared in the composer since the baseline: {control.get('selector_hint')}",
                        "control": control,
                    })

    repairs = propose_repairs(snapshot)

    severities = [f.get("severity") for f in findings]
    if "critical" in severities:
        verdict = "surface-drift-blocking"
    elif "degraded" in severities:
        verdict = "surface-drift-degraded"
    elif findings:
        verdict = "surface-drift-cosmetic"
    else:
        verdict = "surface-ok"

    report: JsonDict = {
        "schema": "glasstty-surface-triage/v1",
        "generated_at": utcnow(),
        "verdict": verdict,
        "url": snapshot.get("url"),
        "route": snapshot.get("route"),
        "authentication": authentication,
        "fingerprint": snapshot.get("fingerprint"),
        "baseline_fingerprint": baseline.get("fingerprint") if baseline else None,
        "findings": findings,
        "repairs": repairs,
        "diff": delta,
        "next_actions": _next_actions(verdict, findings, repairs),
    }
    if failure is not None:
        report["failure_context"] = {
            "settle_reason": failure.get("settle_reason"),
            "error": failure.get("error"),
            "detection": failure.get("detection"),
            "submitted": failure.get("submitted"),
        }
        report["likely_cause"] = _correlate_failure(failure, findings)
    return report


def _correlate_failure(failure: JsonDict, findings: list[JsonDict]) -> str:
    """Tie the observed turn failure to the observed surface damage.

    This is the sentence the operator actually wants: not "something changed",
    but "your submit did nothing *because* the send button is now X".
    """
    reason = failure.get("settle_reason")
    criticals = [f for f in findings if f.get("severity") == "critical"]

    if reason == "error" and not failure.get("submitted"):
        for finding in criticals:
            if finding.get("anchor") == "send" or finding.get("capability") == "submit_prompt":
                return "submit was refused because the send control no longer matches the expected surface"
            if finding.get("anchor") == "composer" or finding.get("capability") == "write_prompt":
                return "the prompt could not be written because the composer was not found"
        return "submit was refused, but the surface probe found no critical anchor damage; check route posture"

    if reason == "no-generation-detected":
        if any(f.get("kind") == "oddity:dialog" for f in findings):
            return "the click likely landed on a modal dialog that was covering the composer"
        if any(f.get("kind") == "oddity:banner" for f in findings):
            return "an alert/banner is present — this is often a rate limit or an error notice suppressing generation"
        if any(f.get("anchor") == "send" for f in criticals):
            return "the click landed on a control that is not the real send button"
        return "submit reported success but nothing generated; the send control may be a decoy"

    if reason == "timeout":
        if any(f.get("capability") == "detect_generation" for f in findings):
            return "the generation lifecycle is unreadable, so the engine could not tell when the answer finished"
        return "the answer never settled; the model may still have been thinking (try --max-wait)"

    if reason == "no-output-change":
        return "no new assistant text appeared; the transcript selector may have moved"

    return "no confident correlation; inspect findings"


def _next_actions(verdict: str, findings: list[JsonDict], repairs: list[JsonDict]) -> list[str]:
    actions: list[str] = []
    if verdict == "surface-ok":
        return ["no action needed"]

    for repair in repairs:
        if repair.get("confident") and repair.get("suggested_selector"):
            actions.append(
                f"apply repair: anchor '{repair['anchor']}' → {repair['suggested_selector']} "
                f"(glassttyd surface-repair --apply)"
            )
        elif repair.get("candidates"):
            actions.append(
                f"review candidates for anchor '{repair['anchor']}' "
                f"(glassttyd surface-triage --pretty) — no candidate was confident enough to auto-apply"
            )
        else:
            actions.append(f"anchor '{repair['anchor']}' is missing and no replacement was found; the page may not be a chat route")

    if any(f.get("kind") == "capability-unknown" for f in findings):
        actions.append("re-run with `--probe-with-draft` — the send control is not rendered on an empty composer")
    if any(f.get("cause") == "authentication-required" for f in findings):
        actions.append("log in to ChatGPT in this browser profile, then re-probe before using attachments")
    if any(f.get("kind") == "oddity:dialog" for f in findings):
        actions.append("a modal is open — dismiss it and re-probe")
    if any(f.get("kind") == "new-composer-control" for f in findings):
        actions.append("a new composer control appeared — add it to the role atlas in extension/src/adapters/surface-probe.ts")
    if not actions:
        actions.append("drift is cosmetic; record a new baseline with `glassttyd surface-snapshot --promote`")
    return actions


# --------------------------------------------------------------------------- #
# History store
# --------------------------------------------------------------------------- #
@dataclass
class SurfaceStore:
    """Timestamped snapshot history, plus a promoted 'known-good' baseline.

    History is the whole point: a single contract tells you the UI is different;
    a history tells you *when* it changed and *what changed with it*.
    """

    root: Path

    def __post_init__(self) -> None:
        self.snapshots_dir = self.root / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.baseline_path = self.root / "baseline.json"

    def save(self, snapshot: JsonDict) -> Path:
        stamp = snapshot.get("stored_at", utcnow()).replace(":", "").replace("-", "")
        fp = snapshot.get("fingerprint", "nofp")
        path = self.snapshots_dir / f"{stamp}-{fp}.json"
        path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def promote(self, snapshot: JsonDict) -> Path:
        self.baseline_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return self.baseline_path

    def baseline(self) -> JsonDict | None:
        if not self.baseline_path.exists():
            return None
        return json.loads(self.baseline_path.read_text(encoding="utf-8"))

    def history(self) -> list[Path]:
        return sorted(self.snapshots_dir.glob("*.json"))

    def latest(self) -> JsonDict | None:
        files = self.history()
        if not files:
            return None
        return json.loads(files[-1].read_text(encoding="utf-8"))

    def timeline(self) -> list[JsonDict]:
        """One row per snapshot, collapsing runs of identical fingerprints.

        This is what makes the UI's evolution legible: you see the moments it
        actually changed, not one row per poll.
        """
        rows: list[JsonDict] = []
        last_fp: str | None = None
        for path in self.history():
            snap = json.loads(path.read_text(encoding="utf-8"))
            fp = snap.get("fingerprint")
            changed = fp != last_fp
            rows.append({
                "path": str(path),
                "stored_at": snap.get("stored_at"),
                "fingerprint": fp,
                "changed": changed,
                "label": snap.get("label"),
                "route": (snap.get("route") or {}).get("posture"),
                "capabilities_lost": [k for k, v in (snap.get("capabilities") or {}).items() if v is False],
                "oddities": len(snap.get("oddities") or []),
            })
            last_fp = fp
        return rows
