#!/usr/bin/env python3
"""Scan TeX sources for shell-escape, unsafe input primitives, and suspicious escaped-command drift."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

SUSPICIOUS_DOUBLED_COMMAND_RE = re.compile(r"(?<!\\)\\\\([A-Za-z]+)")
ALLOWED_DOUBLED_COMMANDS_AFTER_LINEBREAK = {"hline", "midrule", "bottomrule", "toprule", "cmidrule", "addlinespace"}
STRUCTURAL_ENVS = {"proof", "theorem", "lemma", "proposition", "corollary", "definition", "remark"}
BEGIN_STRUCTURAL_ENV_RE = re.compile(r"\\begin\{(" + "|".join(sorted(STRUCTURAL_ENVS)) + r")\}")
END_STRUCTURAL_ENV_RE = re.compile(r"\\end\{(" + "|".join(sorted(STRUCTURAL_ENVS)) + r")\}")
SECTIONING_COMMAND_RE = re.compile(r"\\(section|subsection|subsubsection|paragraph)\*?\{")

STALE_MATH_REGRESSION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "stale_mceq_one_sum_cross_destination_tv_bound",
        re.compile(r"\\TV\s*\(\s*\\mathcal\{L\}_d\s*,\s*\\mathcal\{L\}_\{d'\}\s*\)\s*\\;\s*\\le\s*\\;\s*\\sum_\{t=0\}\^\{T-1\}\s*\\eps_t"),
    ),
    (
        "stale_mucc_hypergeom_t_over_alpha_event_floor",
        re.compile(r"t'\s*:?=\s*\\lceil\s*t\s*/\s*\\alpha\s*\\rceil"),
    ),
    (
        "stale_mucc_hoeffding_log2_tail",
        re.compile(r"\\sqrt\s*\{\s*\\frac\s*\{\s*\\log_2\s*\(\s*1\s*/\s*\\beta\s*\)\s*\}\s*\{\s*2d\s*\}\s*\}"),
    ),
    (
        "stale_odds_epsdelta_exp_slack_bits",
        re.compile(r"\\delta_\{\\mathrm\{tot\}\}.*\\exp\s*\\Big\s*\(\s*\\sum_\{s<t\}\s*\\varepsilon_s\s*\\Big\s*\)"),
    ),
    (
        "stale_odds_epsdelta_prefix_slack_direction",
        re.compile(r"\\delta_\{\\mathrm\{tot\}\}.*2\^\{\\sum_\{s<t\}\\varepsilon_s\}"),
    ),
    (
        "stale_odds_epsdelta_proof_prefix_slack_direction",
        re.compile(r"\\sum_\{t<T\}\\delta_t\\,2\^\{\\sum_\{s<t\}\\varepsilon_s\}"),
    ),
    (
        "stale_odds_renyi_tail_exp_delta_bits",
        re.compile(r"\\delta\s*=\s*\\exp\s*\(\s*\(\\alpha-1\)\s*\(\\rho_\\alpha-\\varepsilon\)\s*\)"),
    ),
    (
        "stale_odds_bayes_factor_exp_bits",
        re.compile(r"B_\{i,t\}\s*=\s*\\exp\s*\(\s*L_i\(O_\{1:t\}\)\s*\)"),
    ),
    (
        "stale_odds_maxl_exp_bits",
        re.compile(r"log-moment\s+of\s+\$\\exp\(\\ell\(O\)\)\$"),
    ),
    (
        "stale_profiling_prefix_slack_direction",
        re.compile(r"\\sum_\{\\ell=1\}\^n\s*\\delta_\\ell\\,?\s*2\^\{\\sum_\{j<\\ell\}\\eta_j\}"),
    ),
    (
        "stale_receipt_rulebook_prefix_slack_direction",
        re.compile(r"\\sum_\{t=1\}\^n\s*\\delta_t\\,?\s*2\^\{\\sum_\{j<t\}\\eps_j\}"),
    ),
    (
        "stale_receipt_rulebook_separator_prefix_slack_direction",
        re.compile(r"\\rho\s*\+\s*\\sum_t\s*\\delta_t\\,?\s*2\^\{\\sum_\{j<t\}\\varepsilon_j\}"),
    ),
    (
        "stale_endpoint_bridge_natural_exp_moment_bits",
        re.compile(r"\\EE[^$]{0,80}\\exp\s*\(\s*\\ell\s*\(\s*Y\s*\)"),
    ),
    (
        "stale_endpoint_bridge_natural_exp_exact_guess_bits",
        re.compile(r"P_\{\\mathrm\{guess\}\}.*\\le\s*\\exp\s*\(\s*\\mathrm\{MaxL\}"),
    ),
    (
        "stale_bossfight_unmetered_stopping_times_phrase",
        re.compile(r"selecting\s+stopping\s+times\),\s+and\s+attempts\s+to\s+identify"),
    ),
    (
        "stale_bossfightc_materialized_verifier_packet_claim",
        re.compile(r"Exact public/on-request packet wiring[^\n]*concrete[^\n]*via\s+\\texttt\{bossfight\\_verifier\\_packet\}"),
    ),
    (
        "stale_bossfightc_four_plan_rows_claim",
        re.compile(r"(?:checked\s+four\s+pinned\s+\\texttt\{plan\\_id\}/\\texttt\{plan\\_spec\\_id\}\s+pairs|same\s+four\s+(?:maintained\s+)?\\texttt\{plans\\_checked\}\s+rows)"),
    ),
    (
        "stale_workedexample_nonconservative_float_budget_rows",
        re.compile(r"(?:0\.046533409961736785|0\.0563455069846569(?:64|7)|0\.2630344058337938|0\.2659045629259257)"),
    ),
    (
        "stale_workedexample_negative_proof_carrying_status",
        re.compile(r"(?:deterministic_closure_smoke_not_formal_proof_bundle|deterministic\\_closure\\_smoke\\_not\\_formal\\_proof\\_bundle)"),
    ),
    (
        "stale_workedexample_raw_log_endpoint_declared_input",
        re.compile(r"raw\s+transcendental/statistical\s+endpoint\s+derivations\s+remain\s+certificate\s+inputs|raw\s+transcendental\s+and\s+finite-sample\s+endpoint\s+derivations\s+remain\s+certificate\s+inputs"),
    ),
    (
        "stale_profiling_eta_rounded_underbound",
        re.compile(r"(?:eta(?:\\_)?bits\s*=\s*)?0\.821759"),
    ),
    (
        "stale_bossfightc_old_proof_status_without_profile_bundle",
        re.compile(r"formal(?:\\_|_)exact(?:\\_|_)rational(?:\\_|_)budget(?:\\_|_)closure(?:\\_|_)and(?:\\_|_)log(?:\\_|_)endpoint(?:\\_|_)derivations(?:\\_|_)present"),
    ),
    (
        "stale_profiling_cp_rounded_declared_input",
        re.compile(r"profiling\s+eta/delta\s+finite-sample\s+row\s+(?:is|remains)\s+(?:a\s+)?declared\s+(?:statistical\s+)?(?:input|certificate\s+input)"),
    ),
    (
        "stale_bossfightc_profile_outside_certificate_after_cp_bundle",
        re.compile(r"leaving\s+the\s+profiling\s+statistical\s+eta/delta\s+row\s+outside\s+the\s+formal\s+arithmetic\s+certificate"),
    ),
    (
        "stale_workedexample_profile_cert_without_fixedsample_lock",
        re.compile(r"profiling(?:\\_|_)statistical(?:\\_|_)derivation(?:\\_|_)bundle\}\s+now\s+proves\s+the\s+base\s+profiling\s+eta/delta\s+CP\+union-bound\s+envelope\s+by\s+exact\s+binomial-tail/log-ratio\s+checks\."),
    ),
]

RISK_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("shell_escape_write18", re.compile(r"\\(?:immediate\s*)?write18\b")),
    ("shellesc_package", re.compile(r"\\usepackage(?:\[[^\]]*\])?\{shellesc\}")),
    ("direct_openout", re.compile(r"\\openout\b")),
    ("direct_openin", re.compile(r"\\openin\b")),
    ("tex_read_primitive", re.compile(r"\\read\b")),
    ("pipe_input", re.compile(r"\\input\s*\|")),
    ("absolute_input", re.compile(r"\\(?:input|include|includegraphics|bibliography|addbibresource|lstinputlisting|verbatiminput)\s*(?:\[[^\]]*\])?\{\s*/")),
    ("url_input", re.compile(r"\\(?:input|include|includegraphics|bibliography|addbibresource|lstinputlisting|verbatiminput)\s*(?:\[[^\]]*\])?\{\s*(?:https?|file)://", re.IGNORECASE)),
]

NEGATIVE_CONTROL_CASES: list[dict[str, str]] = [
    {
        "id": "shell_escape_write18",
        "line": r"\immediate\write18{touch should_not_exist}",
        "expect_category": "shell_escape_write18",
    },
    {
        "id": "absolute_input",
        "line": r"\input{/outside/ambient-host-file.tex}",
        "expect_category": "absolute_input",
    },
    {
        "id": "doubled_latex_command",
        "line": r"This source-only release is a single \\LaTeX\ file.",
        "expect_category": "suspicious_doubled_command_escape",
        "expect_command": "LaTeX",
    },
    {
        "id": "doubled_texttt_command",
        "line": r"Internet-Draft, \\texttt{draft-example-00}, 2026.",
        "expect_category": "suspicious_doubled_command_escape",
        "expect_command": "texttt",
    },
    {
        "id": "doubled_math_relation",
        "line": r"A sufficient condition is $x\\ge 1$.",
        "expect_category": "suspicious_doubled_command_escape",
        "expect_command": "ge",
    },
    {
        "id": "doubled_emph_command",
        "line": r"The operator must repair this \\emph{before release}.",
        "expect_category": "suspicious_doubled_command_escape",
        "expect_command": "emph",
    },
    {
        "id": "section_inside_proof_like_environment",
        "line": r"\\begin{proof}\n\\subsection{This heading is accidentally inside the proof}\n\\end{proof}",
        "expect_category": "sectioning_inside_structural_environment",
    },
    {
        "id": "stale_mceq_one_sum_cross_destination_tv_bound",
        "line": r"\TV(\mathcal{L}_d,\mathcal{L}_{d'})\;\le\; \sum_{t=0}^{T-1} \eps_t.",
        "expect_category": "stale_mceq_one_sum_cross_destination_tv_bound",
    },
    {
        "id": "stale_mucc_hypergeom_t_over_alpha_event_floor",
        "line": r"where $t':=\lceil t/\alpha\rceil$ and therefore $\Pr[\mathrm{Hypergeom}(M,d,k_0)\ge t']\ge1-\beta$.",
        "expect_category": "stale_mucc_hypergeom_t_over_alpha_event_floor",
    },
    {
        "id": "stale_mucc_hoeffding_log2_tail",
        "line": r"$p\alpha \ge t/d + \sqrt{\frac{\log_2(1/\beta)}{2d}}$.",
        "expect_category": "stale_mucc_hoeffding_log2_tail",
    },
    {
        "id": "stale_odds_epsdelta_exp_slack_bits",
        "line": r"$\delta_{\mathrm{tot}}:=\sum_{t=1}^T \delta_t\,\exp\Big(\sum_{s<t}\varepsilon_s\Big)$.",
        "expect_category": "stale_odds_epsdelta_exp_slack_bits",
    },
    {
        "id": "stale_odds_epsdelta_prefix_slack_direction",
        "line": r"$\delta_{\mathrm{tot}}:=\sum_{t=1}^T \delta_t\,2^{\sum_{s<t}\varepsilon_s}$.",
        "expect_category": "stale_odds_epsdelta_prefix_slack_direction",
    },
    {
        "id": "stale_odds_epsdelta_proof_prefix_slack_direction",
        "line": r"This yields $\sum_{t<T}\delta_t\,2^{\sum_{s<t}\varepsilon_s}$ in the induction step.",
        "expect_category": "stale_odds_epsdelta_proof_prefix_slack_direction",
    },
    {
        "id": "stale_odds_renyi_tail_exp_delta_bits",
        "line": r"Equivalently, with $\delta=\exp((\alpha-1)(\rho_\alpha-\varepsilon))$, the odds inflation exceeds $\varepsilon$.",
        "expect_category": "stale_odds_renyi_tail_exp_delta_bits",
    },
    {
        "id": "stale_odds_bayes_factor_exp_bits",
        "line": r"The per-identity Bayes factor process $B_{i,t}=\exp(L_i(O_{1:t}))$ is a nonnegative martingale.",
        "expect_category": "stale_odds_bayes_factor_exp_bits",
    },
    {
        "id": "stale_odds_maxl_exp_bits",
        "line": r"Maximal leakage is the log-moment of $\exp(\ell(O))$ in this bit-valued paper.",
        "expect_category": "stale_odds_maxl_exp_bits",
    },
    {
        "id": "stale_profiling_prefix_slack_direction",
        "line": r"$(\eta_\star,\delta_\star)=(\sum_{\ell=1}^n\eta_\ell,\sum_{\ell=1}^n\delta_\ell\,2^{\sum_{j<\ell}\eta_j})$.",
        "expect_category": "stale_profiling_prefix_slack_direction",
    },
    {
        "id": "stale_receipt_rulebook_prefix_slack_direction",
        "line": r"$P_k(A)\le 2^{\sum_{t=1}^n\eps_t}P(A)+\sum_{t=1}^n\delta_t\,2^{\sum_{j<t}\eps_j}$.",
        "expect_category": "stale_receipt_rulebook_prefix_slack_direction",
    },
    {
        "id": "stale_receipt_rulebook_separator_prefix_slack_direction",
        "line": r"$(\sum_t\varepsilon_t,\ \rho + \sum_t \delta_t\,2^{\sum_{j<t}\varepsilon_j})$ under the one-vs-mixture semantics.",
        "expect_category": "stale_receipt_rulebook_separator_prefix_slack_direction",
    },
    {
        "id": "stale_endpoint_bridge_natural_exp_moment_bits",
        "line": r"$\EE_P[\exp(\ell(Y))]=\sum_y P(y)\max_s P_s(y)/P(y)$ in a bit-valued endpoint bridge.",
        "expect_category": "stale_endpoint_bridge_natural_exp_moment_bits",
    },
    {
        "id": "stale_endpoint_bridge_natural_exp_exact_guess_bits",
        "line": r"$P_{\mathrm{guess}}(S\mid Y)\le \exp(\mathrm{MaxL}(S\to Y))\cdot \max_s\pi(s)$ in a bit-valued endpoint bridge.",
        "expect_category": "stale_endpoint_bridge_natural_exp_exact_guess_bits",
    },
    {
        "id": "stale_bossfight_unmetered_stopping_times_phrase",
        "line": r"possibly adaptively (choosing queries, inducing retries, or selecting stopping times), and attempts to identify C.",
        "expect_category": "stale_bossfight_unmetered_stopping_times_phrase",
    },
    {
        "id": "stale_bossfightc_materialized_verifier_packet_claim",
        "line": r"Exact public/on-request packet wiring for one exported verifier-bundle card is now concrete in the maintained worked example via \texttt{bossfight\_verifier\_packet}.",
        "expect_category": "stale_bossfightc_materialized_verifier_packet_claim",
    },
    {
        "id": "stale_bossfightc_four_plan_rows_claim",
        "line": r"the maintained verifier report checked four pinned \texttt{plan\_id}/\texttt{plan\_spec\_id} pairs and recomputed the published rows",
        "expect_category": "stale_bossfightc_four_plan_rows_claim",
    },
    {
        "id": "stale_workedexample_nonconservative_float_budget_rows",
        "line": r"Recomputed rows include \texttt{fallback\_contact\_bits\_per\_lookup=0.046533409961736785}.",
        "expect_category": "stale_workedexample_nonconservative_float_budget_rows",
    },
    {
        "id": "stale_workedexample_negative_proof_carrying_status",
        "line": r"The row still says \texttt{proof\_carrying\_status=deterministic\_closure\_smoke\_not\_formal\_proof\_bundle}.",
        "expect_category": "stale_workedexample_negative_proof_carrying_status",
    },
    {
        "id": "stale_workedexample_raw_log_endpoint_declared_input",
        "line": r"The verifier status says raw transcendental/statistical endpoint derivations remain certificate inputs in this cut.",
        "expect_category": "stale_workedexample_raw_log_endpoint_declared_input",
    },
    {
        "id": "stale_profiling_eta_rounded_underbound",
        "line": r"The worked receipt still reports eta_bits=0.821759 for the profiling equalization row.",
        "expect_category": "stale_profiling_eta_rounded_underbound",
    },
    {
        "id": "stale_bossfightc_old_proof_status_without_profile_bundle",
        "line": r"The verifier contract still says proof_carrying_status=formal_exact_rational_budget_closure_and_log_endpoint_derivations_present.",
        "expect_category": "stale_bossfightc_old_proof_status_without_profile_bundle",
    },
    {
        "id": "stale_profiling_cp_rounded_declared_input",
        "line": r"The profiling eta/delta finite-sample row remains a declared statistical input in this cut.",
        "expect_category": "stale_profiling_cp_rounded_declared_input",
    },
    {
        "id": "stale_bossfightc_profile_outside_certificate_after_cp_bundle",
        "line": r"The current worked-example cut is a smoke row while leaving the profiling statistical eta/delta row outside the formal arithmetic certificate.",
        "expect_category": "stale_bossfightc_profile_outside_certificate_after_cp_bundle",
    },
    {
        "id": "stale_workedexample_profile_cert_without_fixedsample_lock",
        "line": r"while \nolinkurl{profiling_statistical_derivation_bundle} now proves the base profiling eta/delta CP+union-bound envelope by exact binomial-tail/log-ratio checks.",
        "expect_category": "stale_workedexample_profile_cert_without_fixedsample_lock",
    },
]


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def strip_comments(line: str) -> str:
    out: list[str] = []
    escaped = False
    for char in line:
        if char == "%" and not escaped:
            break
        out.append(char)
        escaped = char == "\\" and not escaped
        if char != "\\":
            escaped = False
    return "".join(out)


def doubled_command_escape_allowed(line: str, command: str) -> bool:
    """Return True only for the intentional doubled-backslash contexts in this archive.

    A literal ``\\`` followed immediately by letters often means that a source
    accidentally doubled the command introducer, e.g. ``\\texttt`` or
    ``\\emph``.  The main legitimate cases here are title/date linebreaks and
    table-row rule commands after a row break.
    """
    compact = line.strip()
    if "\\title{" in compact or "\\date{" in compact:
        return True
    if command in ALLOWED_DOUBLED_COMMANDS_AFTER_LINEBREAK:
        return True
    return False


def findings_for_line(rel: str, line_no: int, raw_line: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    line = strip_comments(raw_line)
    if not line.strip():
        return findings
    for name, pattern in [*RISK_PATTERNS, *STALE_MATH_REGRESSION_PATTERNS]:
        if pattern.search(line):
            findings.append({"path": rel, "line": line_no, "category": name, "excerpt": " ".join(line.strip().split())[:160]})
    for match in SUSPICIOUS_DOUBLED_COMMAND_RE.finditer(line):
        command = match.group(1)
        if doubled_command_escape_allowed(line, command):
            continue
        findings.append({
            "path": rel,
            "line": line_no,
            "category": "suspicious_doubled_command_escape",
            "command": command,
            "excerpt": " ".join(line.strip().split())[:160],
        })
    return findings



def structural_findings_for_text(rel: str, text: str) -> list[dict[str, Any]]:
    r"""Find sectioning commands accidentally nested inside proof-like environments.

    LaTeX will often compile a misplaced ``\subsection`` inside ``proof`` or
    ``remark`` without failing.  For release review that is worse than a hard
    compile error: a theorem proof may silently absorb unrelated paper sections.
    This scanner is intentionally conservative for this archive and fails on any
    section/paragraph command while a proof-like structural environment is open.
    """
    findings: list[dict[str, Any]] = []
    stack: list[dict[str, int | str]] = []
    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = strip_comments(raw_line)
        if not line.strip():
            continue
        for match in BEGIN_STRUCTURAL_ENV_RE.finditer(line):
            stack.append({"env": match.group(1), "line": line_no})
        section_match = SECTIONING_COMMAND_RE.search(line)
        if section_match and stack:
            top = stack[-1]
            findings.append({
                "path": rel,
                "line": line_no,
                "category": "sectioning_inside_structural_environment",
                "command": section_match.group(1),
                "open_environment": top.get("env"),
                "open_environment_line": top.get("line"),
                "excerpt": " ".join(line.strip().split())[:160],
            })
        for match in END_STRUCTURAL_ENV_RE.finditer(line):
            env = match.group(1)
            if stack and stack[-1]["env"] == env:
                stack.pop()
                continue
            for idx in range(len(stack) - 1, -1, -1):
                if stack[idx]["env"] == env:
                    del stack[idx:]
                    break
    return findings


def negative_control_results() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in NEGATIVE_CONTROL_CASES:
        rel = f"<negative-control:{case['id']}>"
        hits = []
        for line_no, line in enumerate(case["line"].splitlines(), start=1):
            hits.extend(findings_for_line(rel, line_no, line))
        hits.extend(structural_findings_for_text(rel, case["line"]))
        expect_category = case["expect_category"]
        expect_command = case.get("expect_command")
        category_hits = [hit for hit in hits if hit.get("category") == expect_category]
        if expect_command:
            matched = any(hit.get("command") == expect_command for hit in category_hits)
        else:
            matched = bool(category_hits)
        rows.append({
            "id": case["id"],
            "status": "pass" if matched else "fail",
            "expect_category": expect_category,
            "expect_command": expect_command,
            "observed_categories": sorted({str(hit.get("category")) for hit in hits}),
            "observed_commands": sorted({str(hit.get("command")) for hit in hits if hit.get("command")}),
        })
    return rows


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    findings: list[dict[str, Any]] = []
    tex_files = sorted(root.rglob("*.tex"), key=lambda p: p.relative_to(root).as_posix())
    scanned_line_count = 0
    for path in tex_files:
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_no, raw_line in enumerate(text.splitlines(), start=1):
            if strip_comments(raw_line).strip():
                scanned_line_count += 1
            findings.extend(findings_for_line(rel, line_no, raw_line))
        findings.extend(structural_findings_for_text(rel, text))

    category_counts: dict[str, int] = {}
    for item in findings:
        category = str(item["category"])
        category_counts[category] = category_counts.get(category, 0) + 1

    negative_controls = negative_control_results()
    negative_control_failures = [row for row in negative_controls if row["status"] != "pass"]
    checks_failed = len(findings) + len(negative_control_failures)
    summary = {
        "checks_failed": checks_failed,
        "tex_file_count": len(tex_files),
        "scanned_line_count": scanned_line_count,
        "finding_count": len(findings),
        "category_counts": category_counts,
        "negative_control_count": len(negative_controls),
        "negative_control_failed_count": len(negative_control_failures),
    }
    return {
        "status": "pass" if checks_failed == 0 else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "checked_root": ".",
        "policy": {
            "scope": "All shipped .tex files, including series, published, auxiliary, and freeze-packet TeX snapshots.",
            "comment_handling": "Line comments are stripped before pattern matching so documented examples do not create false shell-escape findings.",
            "risk_categories": [name for name, _ in RISK_PATTERNS] + [name for name, _ in STALE_MATH_REGRESSION_PATTERNS] + ["suspicious_doubled_command_escape", "sectioning_inside_structural_environment"],
            "negative_control_policy": "Synthetic hazardous TeX lines must trigger the same detectors used for shipped sources.",
        },
        "findings": findings[:100],
        "negative_controls": negative_controls,
        "summary": summary,
        "fail_closed_rule": "If a TeX source-safety finding appears or a negative control is missed, default to no publication and remove, explicitly redesign the risky source primitive, repair suspicious doubled TeX command escapes, close proof-like environments before sectioning commands, or repair stale known mathematical regression text before compiling or shipping it.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
