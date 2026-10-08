# ChatGPT visible screenshot capture

Rev0340 keeps screenshot capture and adds a safer transfer path: the side panel can capture a local visible-tab PNG, embed it in the assembled proof JSON, and download the proof JSON instead of relying on clipboard transfer.

## Operator flow

1. Select the supported ChatGPT tab in the side panel.
2. Run `Write checkpoint + capture`.
3. Run `Check live gate`.
4. Activate the ChatGPT tab if it is not the visible active tab.
5. Run `Capture visible screenshot`.
6. Run `Submit checkpoint (gated)`.
7. After ChatGPT settles on `/c/...`, run `Read latest + capture`.
8. Run `Download proof JSON` as the primary transfer path. `Copy proof JSON` remains a fallback.
9. Move or point the downloaded JSON at the live finalizer input path.
10. Run `glassttyd proof-finalize-pack --input <downloaded-json> --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack --require-live --clean --pretty`.

The screenshot is local evidence only. Publication/support use still requires the privacy redaction review artifact.

## Safety posture

The screenshot button refuses to capture when no supported ChatGPT tab is selected, when the selected URL is not `https://chatgpt.com/`, or when the selected tab is not the active visible tab in its window. This avoids silently capturing the wrong surface.

## Transfer posture

The side-panel preview redacts embedded PNG data URLs so the UI remains usable after screenshot capture. The downloaded JSON remains complete and still carries the embedded screenshot for `proof-finalize-pack`. Use `Download screenshot PNG` only as a convenience copy for human review; the JSON is the canonical proof transfer artifact.
