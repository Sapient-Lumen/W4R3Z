#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_STYLE = """
  <style>
    body { font-family: system-ui, sans-serif; max-width: 60rem; margin: 2rem auto; padding: 0 1rem; }
    textarea, input:not([type='button']):not([type='submit']), [contenteditable='true'] { width: 100%; min-height: 3rem; box-sizing: border-box; border: 1px solid #999; border-radius: 10px; padding: 0.75rem; }
    article { border: 1px solid #bbb; border-radius: 12px; padding: 1rem; margin-top: 1rem; }
    .thread article + article { margin-top: 0.75rem; }
    dialog { width: min(42rem, 100%); border-radius: 16px; border: 1px solid #bbb; }
    fieldset { border-radius: 12px; padding: 1rem; }
  </style>
"""


def page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>{title}</title>
    {BASE_STYLE}
  </head>
  <body>
    {body}
  </body>
</html>
"""


PAGES = {
    "/": page(
        "GlassTTY Fixture Lab",
        """
    <h1 data-glasstty-role=\"meta-generator\">fixture-lab</h1>
    <p>Local deterministic page for GlassTTY adapter and content-script testing.</p>
    <textarea data-glasstty-role=\"prompt\">hello from fixture lab</textarea>
    <button data-glasstty-role=\"submit\" type=\"button\" onclick=\"document.querySelector('[data-glasstty-role=latest-output]').textContent = document.querySelector('[data-glasstty-role=prompt]').value\">Send</button>
    <article data-glasstty-role=\"latest-output\">fixture-lab response placeholder</article>
    """,
    ),
    "/contenteditable": page(
        "GlassTTY Fixture Lab — contenteditable",
        """
    <h1 data-glasstty-role=\"meta-generator\">fixture-lab-contenteditable</h1>
    <p>Use this page to test contenteditable prompt composition.</p>
    <div data-glasstty-role=\"prompt\" contenteditable=\"true\">hello from contenteditable lab</div>
    <button data-glasstty-role=\"submit\" type=\"button\" onclick=\"document.querySelector('[data-glasstty-role=latest-output]').textContent = document.querySelector('[data-glasstty-role=prompt]').textContent\">Send</button>
    <article data-glasstty-role=\"latest-output\">contenteditable placeholder</article>
    """,
    ),
    "/thread": page(
        "GlassTTY Fixture Lab — thread",
        """
    <h1 data-glasstty-role=\"meta-generator\">fixture-lab-thread</h1>
    <p>Multiple outputs emulate a threaded chat surface.</p>
    <textarea data-glasstty-role=\"prompt\">draft in thread fixture</textarea>
    <button data-glasstty-role=\"submit\" type=\"button\" onclick=\"document.querySelector('[data-glasstty-role=latest-output]').textContent = 'echo: ' + document.querySelector('[data-glasstty-role=prompt]').value\">Send</button>
    <section class=\"thread\">
      <article>older assistant response one</article>
      <article>older assistant response two</article>
      <article data-glasstty-role=\"latest-output\">newest assistant response in thread fixture</article>
    </section>
    """,
    ),
    "/long": page(
        "GlassTTY Fixture Lab — long output",
        """
    <h1 data-glasstty-role=\"meta-generator\">fixture-lab-long</h1>
    <p>Long-output page for transcript extraction and fixture capture.</p>
    <textarea data-glasstty-role=\"prompt\">summarize the log</textarea>
    <button data-glasstty-role=\"submit\" type=\"button\" onclick=\"document.querySelector('[data-glasstty-role=latest-output]').textContent = document.querySelector('[data-glasstty-role=prompt]').value + '\\n\\n' + document.querySelector('[data-glasstty-role=latest-output]').textContent\">Append</button>
    <article data-glasstty-role=\"latest-output\">This is a deterministic but fairly long output block used for GlassTTY transcript extraction tests. It contains repeated phrases so fixture indexing has something real to summarize. This is a deterministic but fairly long output block used for GlassTTY transcript extraction tests. It contains repeated phrases so fixture indexing has something real to summarize.</article>
    """,
    ),
    "/dialog-form": page(
        "GlassTTY Fixture Lab — dialog form",
        """
    <h1 data-glasstty-role=\"meta-generator\">fixture-lab-dialog-form</h1>
    <p>Dialog-scoped fixture for repeated controls and modal form planning.</p>
    <button type=\"button\">Save</button>
    <dialog open aria-label=\"Profile settings\">
      <form method=\"dialog\" name=\"Profile settings\">
        <fieldset>
          <legend>Composer</legend>
          <label for=\"dialog-prompt\">Message</label>
          <textarea id=\"dialog-prompt\" data-glasstty-role=\"prompt\">Draft inside dialog</textarea>
        </fieldset>
        <menu>
          <button type=\"button\">Cancel</button>
          <button data-glasstty-role=\"submit\" type=\"button\" onclick=\"document.querySelector('[data-glasstty-role=latest-output]').textContent = document.querySelector('[data-glasstty-role=prompt]').value\">Save</button>
        </menu>
      </form>
    </dialog>
    <article data-glasstty-role=\"latest-output\">Dialog saved state</article>
    """,
    ),
    "/iframe-compose": page(
        "GlassTTY Fixture Lab — iframe compose",
        """
    <h1 data-glasstty-role=\"meta-generator\">fixture-lab-iframe-compose</h1>
    <form name=\"Embedded composer\" action=\"/iframe-compose/save\" method=\"post\">
      <fieldset>
        <legend>Embedded card</legend>
        <label for=\"iframe-prompt\">Card number</label>
        <input id=\"iframe-prompt\" name=\"cardNumber\" data-glasstty-role=\"prompt\" value=\"4242424242424242\" />
        <button data-glasstty-role=\"submit\" type=\"button\" onclick=\"document.querySelector('[data-glasstty-role=latest-output]').textContent = 'Saved ' + document.querySelector('[data-glasstty-role=prompt]').value.slice(-4)\">Save card</button>
      </fieldset>
    </form>
    <article data-glasstty-role=\"latest-output\">Saved 4242</article>
    """,
    ),
    "/iframe-shell": page(
        "GlassTTY Fixture Lab — iframe shell",
        """
    <h1 data-glasstty-role=\"meta-generator\">fixture-lab-iframe-shell</h1>
    <p>Outer page for frame inventory and frame title/name testing.</p>
    <iframe id=\"billing-frame\" name=\"billing-frame\" title=\"Billing details\" src=\"/iframe-compose\" style=\"width:100%; min-height:24rem; border:1px solid #bbb; border-radius:12px;\"></iframe>
    """,
    ),
    "/iframe-split-compose": page(
        "GlassTTY Fixture Lab — iframe split compose",
        """
    <h1 data-glasstty-role="meta-generator">fixture-lab-iframe-split-compose</h1>
    <form name="Embedded split composer" action="/iframe-split-compose/save" method="post">
      <fieldset>
        <legend>Embedded draft composer</legend>
        <label for="split-iframe-prompt">Draft note</label>
        <textarea id="split-iframe-prompt" data-glasstty-role="prompt">Need billing follow-up</textarea>
        <button data-glasstty-role="submit" type="button">Queue follow-up</button>
      </fieldset>
    </form>
    <p>This frame intentionally has no latest-output node so output scope stays on the parent page.</p>
    """,
    ),
    "/iframe-split-shell": page(
        "GlassTTY Fixture Lab — iframe split shell",
        """
    <h1 data-glasstty-role="meta-generator">fixture-lab-iframe-split-shell</h1>
    <p>Input and submit live inside the iframe; status output stays in the top-level page.</p>
    <article data-glasstty-role="latest-output">Top-level billing summary is current</article>
    <iframe id="billing-split-frame" name="billing-split-frame" title="Billing draft frame" src="/iframe-split-compose" style="width:100%; min-height:24rem; border:1px solid #bbb; border-radius:12px;"></iframe>
    """,
    ),
    "/iframe-nested-compose": page(
        "GlassTTY Fixture Lab — iframe nested compose",
        """
    <h1 data-glasstty-role="meta-generator">fixture-lab-iframe-nested-compose</h1>
    <form name="Nested billing details" action="/iframe-nested-compose/save" method="post">
      <fieldset>
        <legend>Nested card editor</legend>
        <label for="nested-card-number">Card number</label>
        <input id="nested-card-number" name="cardNumber" data-glasstty-role="prompt" value="5555444433331111" />
        <button data-glasstty-role="submit" type="button" onclick="document.querySelector('[data-glasstty-role=latest-output]').textContent = 'Nested saved ' + document.querySelector('[data-glasstty-role=prompt]').value.slice(-4)">Save nested card</button>
      </fieldset>
    </form>
    <article data-glasstty-role="latest-output">Nested saved 1111</article>
    """,
    ),
    "/iframe-nested-middle": page(
        "GlassTTY Fixture Lab — iframe nested middle",
        """
    <h1 data-glasstty-role="meta-generator">fixture-lab-iframe-nested-middle</h1>
    <p>Intermediate frame for nested frame-locator planning.</p>
    <iframe id="card-frame" name="card-frame" title="Card editor frame" src="/iframe-nested-compose" style="width:100%; min-height:22rem; border:1px solid #bbb; border-radius:12px;"></iframe>
    """,
    ),
    "/iframe-nested-shell": page(
        "GlassTTY Fixture Lab — iframe nested shell",
        """
    <h1 data-glasstty-role="meta-generator">fixture-lab-iframe-nested-shell</h1>
    <p>Top-level outer page for nested iframe capture and frame-path planning.</p>
    <iframe id="settings-frame" name="settings-frame" title="Settings shell" src="/iframe-nested-middle" style="width:100%; min-height:26rem; border:1px solid #bbb; border-radius:12px;"></iframe>
    """,
    ),
    "/iframe-partial-compose": page(
        "GlassTTY Fixture Lab — iframe partial compose",
        """
    <h1 data-glasstty-role="meta-generator">fixture-lab-iframe-partial-compose</h1>
    <form name="Partial billing composer" action="/iframe-partial-compose/save" method="post">
      <fieldset>
        <legend>Accessible billing draft</legend>
        <label for="partial-iframe-prompt">Billing note</label>
        <textarea id="partial-iframe-prompt" data-glasstty-role="prompt">Accessible draft note</textarea>
        <button data-glasstty-role="submit" type="button" onclick="document.querySelector('[data-glasstty-role=latest-output]').textContent = 'Saved accessible draft'">Save accessible draft</button>
      </fieldset>
    </form>
    <article data-glasstty-role="latest-output">Saved accessible draft</article>
    """,
    ),
    "/iframe-partial-shell": page(
        "GlassTTY Fixture Lab — iframe partial shell",
        """
    <h1 data-glasstty-role="meta-generator">fixture-lab-iframe-partial-shell</h1>
    <p>One iframe stays same-origin and accessible; the sibling iframe is sandboxed without <code>allow-same-origin</code> to model partial frame capture.</p>
    <iframe id="accessible-frame" name="accessible-frame" title="Accessible billing frame" src="/iframe-partial-compose" style="width:100%; min-height:22rem; border:1px solid #bbb; border-radius:12px;"></iframe>
    <iframe id="partner-frame" name="partner-frame" title="Partner billing widget" sandbox="allow-scripts" srcdoc='<!doctype html><html lang="en"><body><h1>Partner widget</h1><form><label for="partner-note">Partner note</label><textarea id="partner-note">Blocked partner draft</textarea><button type="button">Send partner note</button></form></body></html>' style="width:100%; min-height:12rem; border:1px dashed #bbb; border-radius:12px; margin-top:1rem;"></iframe>
    """,
    ),
}

MANIFEST = {
    "name": "fixture-lab",
    "default_url": "http://127.0.0.1:8765/",
    "pages": sorted(PAGES.keys()),
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path == "/manifest.json":
            data = json.dumps(MANIFEST, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        target = self.path if self.path in PAGES else "/index.html" if self.path == "/index.html" else self.path.rstrip("/")
        if target == "":
            target = "/"
        if target in PAGES:
            data = PAGES[target].encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_error(404)

    def log_message(self, fmt: str, *args):
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the GlassTTY local fixture lab server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"fixture-lab serving on http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
