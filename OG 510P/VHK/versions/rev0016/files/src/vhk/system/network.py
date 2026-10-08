from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class HttpResponse:
    status: int
    reason: str
    headers: dict[str, str]
    body: bytes
    url: str

    @property
    def text(self) -> str:
        charset = "utf-8"
        content_type = self.headers.get("content-type", "")
        for part in content_type.split(";"):
            part = part.strip()
            if part.lower().startswith("charset="):
                charset = part.split("=", 1)[1].strip() or charset
                break
        try:
            return self.body.decode(charset, errors="replace")
        except LookupError:
            return self.body.decode("utf-8", errors="replace")

    def json(self) -> Any:
        return json.loads(self.text)



def http_request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    body: str | bytes | None = None,
    json_body: Any = None,
    timeout_ms: int = 30_000,
    allow_error_status: bool = False,
) -> HttpResponse:
    """Make a one-shot HTTP request using urllib.

    This intentionally mirrors the sessionless/simple-request shape used by many
    automation/test tools: a single request that returns a response object users
    can inspect without having to set up a session first.
    """

    url2 = str(url)
    if params:
        parsed = urllib.parse.urlsplit(url2)
        query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        for k, v in params.items():
            if isinstance(v, (list, tuple)):
                for item in v:
                    query.append((str(k), str(item)))
            else:
                query.append((str(k), str(v)))
        url2 = urllib.parse.urlunsplit(parsed._replace(query=urllib.parse.urlencode(query, doseq=True)))

    hdrs = {str(k): str(v) for k, v in (headers or {}).items()}
    data: bytes | None = None
    if json_body is not None:
        data = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
        if not any(k.lower() == "content-type" for k in hdrs):
            hdrs["Content-Type"] = "application/json; charset=utf-8"
    elif body is not None:
        data = body.encode("utf-8") if isinstance(body, str) else bytes(body)

    req = urllib.request.Request(url2, data=data, headers=hdrs, method=method.upper())
    timeout_s = max(0.001, float(timeout_ms) / 1000.0)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return HttpResponse(
                status=int(resp.status),
                reason=str(resp.reason),
                headers={str(k).lower(): str(v) for k, v in resp.headers.items()},
                body=resp.read(),
                url=str(resp.geturl()),
            )
    except urllib.error.HTTPError as e:
        response = HttpResponse(
            status=int(e.code),
            reason=str(e.reason),
            headers={str(k).lower(): str(v) for k, v in e.headers.items()},
            body=e.read(),
            url=str(e.geturl()),
        )
        if allow_error_status:
            return response
        raise RuntimeError(f"HTTP {response.status} {response.reason}: {response.url}")



def download_file(
    url: str,
    path: str | Path,
    *,
    headers: dict[str, str] | None = None,
    timeout_ms: int = 30_000,
    create_parents: bool = True,
    overwrite: bool = True,
) -> Path:
    response = http_request("GET", url, headers=headers, timeout_ms=timeout_ms)
    p = Path(path).expanduser()
    if p.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {p}")
    if create_parents:
        p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(response.body)
    return p
