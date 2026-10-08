#!/usr/bin/env python3
"""Build a one-file offline disclosed-reader kit for P0002-D010.

The generated HTML contains the disclosure, exact poem body, response form, and
client-side JSON download. It makes no network request and collects no identity.
The returned JSON is intentionally compatible with tools/record_reader_response.py.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import zipfile
from pathlib import Path

FIXED_DT = (1980, 1, 1, 0, 0, 0)
TARGET = "P0002-D010"
CANDIDATE = "CAND-P0002-D010-001"
SOURCE_DRAFT = Path("poems/P0002/draft_010.md")
KIT_DIR = Path("anthology/candidates/P0002-D010_field_kit")
HTML_NAME = "P0002-D010_field_test.html"
README_NAME = "README.md"
MANIFEST_NAME = "FIELD_KIT_MANIFEST.json"
ZIP_PATH = Path("anthology/candidates/P0002-D010_field_kit.zip")
SIDE_PATH = Path("anthology/candidates/P0002-D010_field_kit.zip.sha256")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def extract_title_and_body(raw: str) -> tuple[str, str]:
    if "## Poem" not in raw or "## Disclosure" not in raw:
        raise ValueError("D010 must contain ## Poem and ## Disclosure sections")
    title = raw.splitlines()[0].lstrip("# ").strip()
    body = raw.split("## Poem", 1)[1].split("## Disclosure", 1)[0].strip("\n")
    if not title or not body:
        raise ValueError("D010 title/body extraction failed")
    return title, body


def render_html(title: str, body: str, revision: str) -> str:
    poem = html.escape(body)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(TARGET)} disclosed reader field test</title>
<style>
:root {{ color-scheme: light dark; font-family: ui-serif, Georgia, serif; line-height: 1.5; }}
body {{ max-width: 52rem; margin: 0 auto; padding: 2rem 1rem 5rem; }}
header, section, form {{ margin-block: 2rem; }}
.notice {{ border: 2px solid currentColor; padding: 1rem 1.2rem; }}
.poem {{ white-space: pre-wrap; font-size: 1.08rem; padding: 1.25rem; border-left: .25rem solid currentColor; }}
fieldset {{ margin-block: 1.25rem; padding: 1rem; }}
label {{ display: block; margin-block: .8rem; }}
textarea {{ width: 100%; min-height: 5rem; box-sizing: border-box; }}
select, button {{ font: inherit; padding: .45rem .65rem; }}
button {{ margin-right: .5rem; cursor: pointer; }}
small {{ display: block; margin-top: .35rem; }}
#status {{ font-family: ui-monospace, monospace; white-space: pre-wrap; }}
</style>
</head>
<body>
<header>
<h1>{html.escape(title)}</h1>
<p><strong>Reader field test for {TARGET}</strong> · package {html.escape(revision)}</p>
</header>

<section class="notice" aria-labelledby="disclosure-heading">
<h2 id="disclosure-heading">Disclosure before reading</h2>
<p>This poem was machine-drafted from disclosed NOAA tide-station and benchmark material. It is an internal candidate, not an admitted or evidence-ready poem. A local attempt to obtain a current water-level value failed, so the poem claims no live reading.</p>
<p>Please read the poem before opening any source packet, evaluator note, or other project material. Do not provide your name, contact information, location, demographics, employer, biography, or other identifying details.</p>
</section>

<section aria-labelledby="poem-heading">
<h2 id="poem-heading">Poem</h2>
<div class="poem">{poem}</div>
</section>

<form id="reader-form">
<h2>First response</h2>
<p>Answer from this reading only. The downloaded file contains your answers but no identity or browser metadata.</p>

<fieldset>
<legend>Reading boundary</legend>
<label><input type="checkbox" id="disclosure_seen_before_poem" required> I saw the machine/source/runtime disclosure before the poem.</label>
<label><input type="checkbox" id="source_packet_opened_before_first_response"> I opened a source packet or project notes before this response.</label>
<label><input type="checkbox" id="boundary_acknowledged" required> I understand this is non-identifying local editorial feedback, not admission, evidence, or research proof.</label>
</fieldset>

<label>Keep, reject, or uncertain?
<select id="keep_reject_uncertain" required>
<option value="">Choose one</option>
<option value="keep">Keep</option>
<option value="reject">Reject</option>
<option value="uncertain">Uncertain</option>
</select>
</label>

<label>Strongest line or phrase
<textarea id="strongest_line_or_phrase" required minlength="2"></textarea>
</label>

<label>Weakest line or phrase
<textarea id="weakest_line_or_phrase" required minlength="2"></textarea>
</label>

<label>How did the disclosure affect the reading?
<select id="disclosure_delta" required>
<option value="">Choose one</option>
<option value="improved">Improved it</option>
<option value="weakened">Weakened it</option>
<option value="confounded">Confounded it</option>
<option value="merely_explained">Merely explained it</option>
<option value="other">Other</option>
</select>
</label>

<fieldset>
<legend>Does the poem body work without the source packet?</legend>
<label><input type="radio" name="body_works_without_source_packet" value="true" required> Yes</label>
<label><input type="radio" name="body_works_without_source_packet" value="false" required> No</label>
</fieldset>

<label>Where, if anywhere, is documentation doing work the poem should do?
<textarea id="documentation_doing_poem_work" required minlength="2"></textarea>
</label>

<label>Give one concrete revision instruction, even if your instruction is “leave it alone.”
<textarea id="revision_instruction" required minlength="2"></textarea>
</label>

<p>
<button type="submit">Validate and download JSON</button>
<button type="button" id="preview">Preview JSON</button>
</p>
<output id="status" aria-live="polite"></output>
</form>

<script>
(() => {{
  'use strict';
  const form = document.getElementById('reader-form');
  const status = document.getElementById('status');
  const value = id => document.getElementById(id).value.trim();
  const checked = id => document.getElementById(id).checked;

  function payload() {{
    const bodyChoice = form.querySelector('input[name="body_works_without_source_packet"]:checked');
    if (!bodyChoice) throw new Error('Choose whether the poem body works without the source packet.');
    return {{
      disclosure_seen_before_poem: checked('disclosure_seen_before_poem'),
      source_packet_opened_before_first_response: checked('source_packet_opened_before_first_response'),
      boundary_acknowledged: checked('boundary_acknowledged'),
      keep_reject_uncertain: value('keep_reject_uncertain'),
      strongest_line_or_phrase: value('strongest_line_or_phrase'),
      weakest_line_or_phrase: value('weakest_line_or_phrase'),
      disclosure_delta: value('disclosure_delta'),
      body_works_without_source_packet: bodyChoice.value === 'true',
      documentation_doing_poem_work: value('documentation_doing_poem_work'),
      revision_instruction: value('revision_instruction'),
      quality_claims: []
    }};
  }}

  function validate() {{
    if (!form.reportValidity()) throw new Error('Complete every required field.');
    const data = payload();
    if (data.boundary_acknowledged !== true) throw new Error('Boundary acknowledgement must be checked.');
    return data;
  }}

  document.getElementById('preview').addEventListener('click', () => {{
    try {{ status.textContent = JSON.stringify(validate(), null, 2); }}
    catch (err) {{ status.textContent = err.message; }}
  }});

  form.addEventListener('submit', event => {{
    event.preventDefault();
    try {{
      const json = JSON.stringify(validate(), null, 2) + '\\n';
      const blob = new Blob([json], {{type: 'application/json'}});
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.href = url;
      link.download = 'P0002-D010-reader-response.json';
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      status.textContent = 'Downloaded P0002-D010-reader-response.json. Return that file to the project operator.';
    }} catch (err) {{ status.textContent = err.message; }}
  }});
}})();
</script>
</body>
</html>
'''


def render_readme(revision: str) -> str:
    return f'''# P0002-D010 offline disclosed-reader field kit — {revision}

Give the reader only `{HTML_NAME}`. It contains the disclosure, exact poem body, response form, and an offline JSON-download action.

Reader procedure:

1. Open the HTML file in a browser with no other cube materials supplied.
2. Read the disclosure and poem, complete every field, and click **Validate and download JSON**.
3. Return `P0002-D010-reader-response.json` to the operator. Do not add personal identifiers.

Operator procedure:

```bash
python tools/record_reader_response.py --root . --input P0002-D010-reader-response.json --dry-run
python tools/record_reader_response.py --root . --input P0002-D010-reader-response.json
```

Append only after the dry run succeeds. The intake tool assigns provenance fields, rejects personal-data keys and likely contact strings, rejects blanks and duplicate response fingerprints, and keeps the result as local editorial pressure only.

This kit contains no source packet, evaluator rubric, analytics, remote assets, network calls, or pre-filled response. Kit readiness is not a reader response, admission, evidence status, publication clearance, or proof of poem quality.
'''


def build(root: Path) -> dict:
    state = load_json(root / "STATE.json")
    revision = str(state.get("revision"))
    timestamp = state.get("updated_at") or state.get("timestamp")
    turn = state.get("turn", {}).get("last_completed")
    current_head = state.get("current_head")

    source = root / SOURCE_DRAFT
    title, body = extract_title_and_body(source.read_text(encoding="utf-8"))
    kit = root / KIT_DIR
    kit.mkdir(parents=True, exist_ok=True)

    html_path = kit / HTML_NAME
    readme_path = kit / README_NAME
    html_path.write_text(render_html(title, body, revision), encoding="utf-8")
    readme_path.write_text(render_readme(revision), encoding="utf-8")

    payload_entries = []
    for name in (HTML_NAME, README_NAME):
        p = kit / name
        payload_entries.append({"path": name, "size": p.stat().st_size, "sha256": sha256_file(p)})

    manifest = {
        "schema": "llmpoetry-offline-reader-field-kit-v1",
        "revision": revision,
        "created_at": timestamp,
        "created_turn": turn,
        "target_draft": TARGET,
        "target_draft_path": SOURCE_DRAFT.as_posix(),
        "target_draft_sha256": sha256_file(source),
        "candidate_id": CANDIDATE,
        "global_current_head": current_head,
        "status": "offline_disclosed_reader_field_kit_built_not_run",
        "entrypoint": HTML_NAME,
        "response_filename": "P0002-D010-reader-response.json",
        "intake_tool": "tools/record_reader_response.py",
        "response_log": "anthology/candidates/P0002-D010_reader_responses.json",
        "network_requests": False,
        "remote_assets": False,
        "collects_identity": False,
        "contains_source_packet": False,
        "contains_evaluator_rubric": False,
        "contains_prefilled_response": False,
        "files": payload_entries,
        "zip_path": ZIP_PATH.as_posix(),
        "sidecar_path": SIDE_PATH.as_posix(),
        "non_claim": "Field-kit readiness is not a reader response, admission, evidence status, publication clearance, or poem-quality proof."
    }
    manifest_path = kit / MANIFEST_NAME
    write_json(manifest_path, manifest)

    zip_path = root / ZIP_PATH
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for name in (HTML_NAME, README_NAME, MANIFEST_NAME):
            p = kit / name
            info = zipfile.ZipInfo(name, FIXED_DT)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, p.read_bytes())

    side = root / SIDE_PATH
    digest = sha256_file(zip_path)
    side.write_text(f"{digest}  {ZIP_PATH.name}\n", encoding="utf-8")
    return {
        "ok": True,
        "revision": revision,
        "target_draft": TARGET,
        "entrypoint": (KIT_DIR / HTML_NAME).as_posix(),
        "zip": ZIP_PATH.as_posix(),
        "sidecar": SIDE_PATH.as_posix(),
        "zip_sha256": digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build offline P0002-D010 reader field kit")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    print(json.dumps(build(Path(args.root)), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
