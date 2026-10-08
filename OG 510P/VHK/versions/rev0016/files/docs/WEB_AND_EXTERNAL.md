# Web / external integration helpers

VHK now includes a small set of "don't make me shell out for this" steps for
common desktop-automation glue:

- `OpenUrl(url)` — open a URL (or file target) with the desktop default handler
  via `xdg-open`
- `ComposeEmail(...)` — open the preferred mail composer via `xdg-email`
- `PasteClipboard(selection)` — paste CLIPBOARD (`Ctrl+V`) or PRIMARY
  (`Shift+Insert`)
- `HttpRequest(...)` — make a one-shot HTTP request and store status/headers/body
- `DownloadFile(...)` — fetch a URL directly to a project-relative path
- `WaitForNewFile(...)` — wait until a fresh file matching a glob appears in a
  directory

## Why these exist

Real macro tools routinely include small but high-leverage glue like opening
URLs, editing files, clipboard actions, and data/network helpers. The goal is to
let users build practical workflows without wrapping every external integration in
`RunShell`.

## Example

```yaml
name: fetch_release_notes
steps:
  - type: HttpRequest
    method: GET
    url: https://example.com/api/releases/latest
    out_json: release
  - type: WriteFile
    path: data/release_notes.txt
    text: "${release.notes}"
  - type: OpenUrl
    url: "${release.html_url}"
```

## Notes

- `HttpRequest` is intentionally sessionless/simple. It is aimed at quick glue
  and API calls inside a macro, not at becoming a full browser automation stack.
- `ComposeEmail` prefills a composer; it does **not** send mail automatically.
- `WaitForNewFile` is useful after browser-driven downloads when the final file
  name is not known ahead of time.
