## Activation timeline page

### Purpose
Show the chronology from **intent edit** to **real activation** without hiding intermediate debt.

### Event grammar
- **Intent authored** — the user or system changed a file, setting, or service parameter.
- **Disk state written** — the changed bytes are durably present on disk.
- **Reread opportunity opened** — watcher/rescan boundary where hot adoption could happen.
- **Process restart** — the local runtime stops and starts again.
- **Service restart** — the governing service world stops and starts again.
- **Cache-burn sequence** — remembered peer/route state is explicitly expired or invalidated.
- **Successor cutover** — a replacement runtime/package/world begins governing the subject.
- **Observed behavioral proof** — the new policy is witnessed in real behavior.

### Timeline rules
- The page must always show the earliest event where the stronger sentence became legal.
- If disk state and behavioral proof diverge, the page favors behavioral truth over file-edit optimism.
- If an old cache can survive the visible restart, the timeline must keep that debt visible instead of stamping the change `done`.
