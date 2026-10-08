# Official voter-information document-upload surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes workable when the public must attach a document, image, scan, or camera-captured file before the current answer/help lane can continue.

## Inventory and review scope

- Identify the critical public-answer routes that depend on document upload, image attachment, or camera capture before revealing the next answer/help lane.
- Distinguish this from general form publication, generic field-entry review, document-download review, and verification-code review.
- Re-check routes whose success depends on mobile camera capture, front/back images, multiple files, or large document uploads.

## Artifact expectations and chooser posture

- Say whether the route accepts PDF, image, or another specific file type.
- State whether one file, multiple files, front/back images, or a combined document are expected.
- Make practical file-size or count limits visible before failure.
- Do not rely on picker hints alone to explain what the office needs.

## Camera capture, retry, and predictable behavior

- If camera capture is offered, keep an ordinary existing-file path available when practical.
- Do not make permission success or live camera access the hidden prerequisite for reaching the route.
- Distinguish wrong type, too-many, too-large, permission-denied, interrupted-transfer, and server-rejection states.
- Preserve safely preservable state across ordinary upload retry instead of forcing a full restart by default.

## Accessibility and help

- Test the upload lane in project context on mobile, at zoom, with keyboard navigation, and with screen readers.
- Ensure instructions, errors, and retry/help cues remain visible and announced meaningfully.
- Keep a plainly visible first-party help or alternate recovery lane available when upload itself is the weak link.

## Evidence posture

- Preserve only route labels, reviewed upload paths, file-type/size/count review state, camera-capture posture review state, upload-error/retry review state, and last review time.
- Do not preserve real voter documents, real IDs, affidavit images, live camera captures, EXIF metadata, full upload logs tied to named voters, or exhaustive session replay when bounded policy reconstruction is sufficient.
