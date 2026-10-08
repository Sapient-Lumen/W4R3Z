"""A mock ChatGPT tab that speaks the real GlassTTY broker protocol.

This lets you exercise the whole commandline conversation stack —
``glassttyd ask`` / ``chat`` / ``run`` and the :class:`ConversationEngine` —
with **no browser, no extension, and no network**. It stands up a real
:class:`~glassttyd.broker.BrokerServer` on the normal daemon socket and plays the
role that the extension + content script + ChatGPT adapter would play in a live
session, including a simulated streaming generation lifecycle.

Run it standalone::

    glassttyd mock-tab            # in one terminal
    glassttyd ask "hello there"   # in another

Or embed it in tests::

    with MockChatGPTTab(socket_path) as tab:
        engine = ConversationEngine(BrokerClient(socket_path))
        result = engine.send("hello")

Prompt markers understood by the default responder:
    ``[[continue]]``  -> answer arrives in two parts (needs a Continue click)
    ``[[stall]]``     -> submit succeeds but no generation ever starts
    ``[[error]]``     -> submit is refused
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .broker import BrokerServer

JsonDict = dict[str, Any]

STREAMING = "streaming-or-stoppable"
NEEDS_CONTINUE = "needs-continue"
SETTLED = "settled-or-idle"
MAX_ACTIVE_ATTACH_TRANSFERS = 4
ATTACH_CHUNK_BYTES = 384 * 1024
MAX_ATTACH_CHUNKS = 4096
MAX_ATTACHMENT_BYTES = 512 * 1024 * 1024
MAX_ATTACH_CHUNK_BASE64 = 4 * ((ATTACH_CHUNK_BYTES + 2) // 3)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class _Frame:
    state: str          # streaming | needs-continue | settled
    text: str           # visible latest-assistant text at this frame


@dataclass
class _Generation:
    frames: list[_Frame]
    index: int = 0

    @property
    def current(self) -> _Frame:
        return self.frames[min(self.index, len(self.frames) - 1)]

    @property
    def at_end(self) -> bool:
        return self.index >= len(self.frames) - 1

    def advance_if_streaming(self) -> None:
        if self.current.state == STREAMING and not self.at_end:
            self.index += 1

    def advance_past_continue(self) -> bool:
        if self.current.state == NEEDS_CONTINUE and not self.at_end:
            self.index += 1
            return True
        return False


Responder = Callable[[str, int], "MockReply"]


@dataclass
class MockReply:
    """A scripted reply. ``parts`` are streamed; >1 part inserts a continue gate."""

    parts: list[str]
    stall: bool = False   # submit ok, but nothing generates
    refuse: bool = False  # submit refused outright


def default_responder(prompt: str, turn_index: int) -> MockReply:
    head = (prompt.strip().splitlines() or [""])[0][:80]
    if "[[error]]" in prompt:
        return MockReply(parts=[], refuse=True)
    if "[[stall]]" in prompt:
        return MockReply(parts=[], stall=True)
    if "[[continue]]" in prompt or "[[long]]" in prompt:
        return MockReply(parts=[
            f"MOCK REPLY #{turn_index} (part 1) to: {head}",
            f"MOCK REPLY #{turn_index} (part 2 / continued) to: {head}",
        ])
    return MockReply(parts=[f"MOCK REPLY #{turn_index} to: {head}"])


def _frames_for(reply: MockReply, previous_text: str) -> list[_Frame]:
    """Turn a scripted reply into a frame timeline the engine can poll through."""
    frames: list[_Frame] = []
    accumulated = ""
    for part_i, part in enumerate(reply.parts):
        if part_i > 0:
            # gate before each continuation part
            frames.append(_Frame(NEEDS_CONTINUE, accumulated))
        accumulated = (accumulated + ("\n\n" if accumulated else "") + part).strip()
        # a couple of streaming frames per part so the engine observes "start"
        half = max(1, len(part) // 2)
        partial = (accumulated[: len(accumulated) - len(part) + half]).strip() or accumulated
        frames.append(_Frame(STREAMING, partial))
        frames.append(_Frame(STREAMING, accumulated))
    frames.append(_Frame(SETTLED, accumulated))
    return frames


# --------------------------------------------------------------------------- #
# Drift scenarios
#
# The point of the surface wing is to survive a UI that changes without warning.
# You cannot test that by waiting for OpenAI to ship a change. So the mock can
# *become* a drifted ChatGPT on demand: rename the send button, hide the
# composer, throw up a modal, add an unrecognised control next to send.
#
# Each scenario changes both what the probe SEES and how the tab BEHAVES, so a
# diagnosis is graded against a real failure, not a fake one.
# --------------------------------------------------------------------------- #
DRIFT_SCENARIOS = {
    'none': 'a healthy, known-good surface',
    'send-renamed': 'the send button keeps working but its id/testid changed (the adapter no longer recognises it)',
    'send-removed': 'the send control is gone entirely; submit must refuse',
    'composer-removed': 'the prompt editor is gone; nothing can be written',
    'nag-dialog': 'a modal dialog covers the page; submit appears to work but nothing generates',
    'rate-limit-banner': 'an alert banner is present and generation never starts',
    'new-composer-control': 'an unrecognised new control appears in the composer (a new picker, say)',
    'no-generation-signal': 'the page stops reporting a generation lifecycle; the engine must fall back',
    'decoy-send': 'the real send is gone and an "Add files" control sits where send used to be',
    'no-file-input': 'the composer has no <input type=file>; attachments are impossible',
    'silent-upload-failure': 'the file input accepts the bytes but no attachment chip ever renders',
    'sticky-attachment-chip': 'the attachment renders but remains after the file input is cleared',
    'consumed-file-input': 'the page consumed input.files but a staged attachment chip remains',
    'volatile-ids': 'every control id is framework-generated (radix-*) and changes each load',
}


def _control(key, *, selector, tag='button', id=None, test_id=None, aria=None,
             text=None, region='composer', visible=True, disabled=False,
             classification='unknown', evidence=None, type_attr=None):
    return {
        'key': key,
        'selector_hint': selector,
        'tag': tag,
        'id': id,
        'test_id': test_id,
        'aria_label': aria,
        'title': None,
        'text': text,
        'role_attr': None,
        'type_attr': type_attr,
        'disabled': disabled,
        'visible': visible,
        'region': region,
        'classification': classification,
        'evidence': evidence or [],
    }


def _anchor(name, *, found, selector=None, expected=None, matches=True):
    return {
        'name': name,
        'found': found,
        'selector_hint': selector,
        'expected_selector': expected,
        'matches_expectation': bool(found and expected and matches),
        'detail': {},
    }


def build_mock_probe(drift: str, *, url: str, composer_text: str = '', attached_files: int = 0) -> JsonDict:
    """Produce a probe report shaped exactly like the extension's, under `drift`.

    Composer emptiness is modelled faithfully: like the real ChatGPT, the mock does
    not render a send button until the composer has text. Any tool that treats that
    as drift will fail this mock, which is the point.
    """
    controls: list[JsonDict] = []
    oddities: list[JsonDict] = []

    composer_present = drift != 'composer-removed'
    composer_empty = len(composer_text.strip()) == 0
    volatile = drift == 'volatile-ids'
    file_input_present = drift != 'no-file-input'

    send_exists = drift not in ('send-removed', 'decoy-send')
    send_recognised = drift not in ('send-renamed',)
    # The real behaviour, straight from the live 2026-07-11 capture:
    # #composer-submit-button matched ZERO nodes on a healthy page with an empty composer.
    send_present = send_exists and not composer_empty

    if composer_present:
        controls.append(_control('id:prompt-textarea', selector='div#prompt-textarea', tag='div',
                                 id='prompt-textarea', aria='Chat with ChatGPT',
                                 classification='composer', region='composer'))
    # The composer effort pill. Live report: a __composer-pill button whose id is
    # radix-_r_ds_ (volatile) and whose text is the tier, e.g. "Pro".
    controls.append(_control('text:pro', selector='button#radix-_r_ds_', id='radix-_r_ds_',
                             text='Pro', classification='effort-pill', region='composer'))
    for index in range(attached_files):
        # NOTE: this is a PLACEHOLDER shape. Nobody has captured a real ChatGPT
        # attachment chip yet. `glassttyd first-flight --learn-attachment` exists to
        # go and find out; when it does, replace this with the observed control and
        # add it to ROLE_ATLAS. Until then the mock is guessing, and it says so.
        controls.append(_control('testid:attachment-chip',
                                 selector=f'div[data-testid=attachment-chip-{index}]',
                                 test_id='attachment-chip', tag='div',
                                 text='package.zip', classification='attachment-chip', region='composer'))

    if send_present and send_recognised:
        controls.append(_control('id:composer-submit-button', selector='button#composer-submit-button',
                                 id='composer-submit-button', test_id='send-button', aria='Send prompt',
                                 classification='send', evidence=['id=composer-submit-button'], type_attr='submit'))
    elif send_present and not send_recognised:
        # Still a send button — but the adapter's expected selector no longer matches it.
        controls.append(_control('testid:composer-send-v2', selector='button[data-testid=composer-send-v2]',
                                 test_id='composer-send-v2', aria='Send message',
                                 classification='send', evidence=['term=send message'], type_attr='submit'))

    # The historical footgun, reproduced: a "+" control sitting where send was.
    controls.append(_control('id:composer-plus-btn', selector='button#composer-plus-btn',
                             id='composer-plus-btn', aria='Add files and more',
                             classification='attach', evidence=['id=composer-plus-btn']))

    if drift == 'new-composer-control':
        controls.append(_control('testid:composer-mode-picker', selector='button[data-testid=composer-mode-picker]',
                                 test_id='composer-mode-picker', aria='Thinking effort',
                                 classification='unknown', region='composer'))
        oddities.append({'kind': 'unknown-control', 'severity': 'warn', 'region': 'composer',
                         'summary': 'unclassified control in the composer: button[data-testid=composer-mode-picker]',
                         'control': controls[-1]})

    if drift == 'nag-dialog':
        controls.append(_control('text:got it', selector='button', text='Got it', region='dialog',
                                 classification='unknown'))
        oddities.append({'kind': 'dialog', 'severity': 'warn', 'region': 'dialog',
                         'summary': 'a modal dialog is open (1 control(s)); it may be intercepting clicks'})

    if drift == 'rate-limit-banner':
        controls.append(_control('text:upgrade', selector='button', text='Upgrade', region='banner',
                                 classification='account'))
        oddities.append({'kind': 'banner', 'severity': 'info', 'region': 'banner',
                         'summary': 'a live/alert region is present (1 control(s)); possible nag, error, or rate-limit notice'})

    anchors = [
        _anchor('composer', found=composer_present, selector='div#prompt-textarea' if composer_present else None,
                expected='#prompt-textarea', matches=composer_present),
        _anchor('send', found=send_present,
                selector=('button#composer-submit-button' if send_recognised else 'button[data-testid=composer-send-v2]') if send_present else None,
                expected='#composer-submit-button', matches=send_recognised),
        _anchor('generation_stop', found=False),
        _anchor('generation_continue', found=False),
        _anchor('latest_assistant_turn', found=True, selector='div[data-message-author-role=assistant]'),
        _anchor('latest_user_turn', found=True, selector='div[data-message-author-role=user]'),
    ]

    for item in anchors:
        if not item['found'] and item['name'] == 'send' and composer_present and composer_empty and send_exists:
            continue  # hidden because empty; already reported as info above
        if not item['found'] and item['name'] in ('composer', 'send'):
            oddities.append({'kind': 'missing-anchor', 'severity': 'critical', 'region': 'page',
                             'summary': f"anchor not found: {item['name']}", 'anchor': item['name']})
        elif item['found'] and item['expected_selector'] and not item['matches_expectation']:
            oddities.append({'kind': 'unexpected-anchor-selector', 'severity': 'critical', 'region': 'page',
                             'summary': f"anchor '{item['name']}' resolved to {item['selector_hint']}, "
                                        f"which does not match the expected selector {item['expected_selector']}",
                             'anchor': item['name']})

    if send_exists and composer_empty and composer_present:
        oddities.append({'kind': 'send-hidden-empty-composer', 'severity': 'info', 'region': 'composer',
                         'summary': 'no send control, but the composer is empty — ChatGPT only renders send once you type.',
                         'anchor': 'send'})

    submit_capability: bool | None
    if send_present and send_recognised:
        submit_capability = True
    elif composer_present and composer_empty and send_exists:
        submit_capability = None      # unknowable, NOT broken
    else:
        submit_capability = False

    capabilities = {
        'write_prompt': composer_present,
        'submit_prompt': submit_capability,
        'detect_generation': drift != 'no-generation-signal',
        'read_latest_output': True,
        'read_user_turn': True,
        'continue_generation': False,
        'attach_files': file_input_present,
    }

    return {
        'probe_version': 'rev0359-mock',
        'captured_at': _utc_now(),
        'url': url,
        'route': {'pathname': '/c/mock-conversation', 'posture': 'plain-chat'},
        'authentication': {
            'posture': 'authenticated',
            'login_control_present': False,
            'signup_control_present': False,
            'account_control_present': True,
        },
        'composer': {
            'present': composer_present,
            'empty': composer_empty,
            'text_length': len(composer_text.strip()),
            'file_input_present': file_input_present,
            'file_input_selector': 'input[type=file]' if file_input_present else None,
            'file_input_multiple': True,
            'attachment_chip_count': attached_files,
            'attached_file_count': attached_files,
        },
        'capabilities': capabilities,
        'anchors': anchors,
        'controls': controls,
        'oddities': oddities,
        'counts': {
            'controls': len(controls),
            'visible_controls': sum(1 for c in controls if c['visible']),
            'unknown_controls': sum(1 for c in controls if c['classification'] == 'unknown'),
            'oddities': len(oddities),
            'critical_oddities': sum(1 for o in oddities if o['severity'] == 'critical'),
        },
    }


class MockChatGPTTab:
    """Broker-backed emulation of a live ChatGPT tab."""

    def __init__(
        self,
        socket_path: Path,
        *,
        responder: Responder = default_responder,
        emit_generation: bool = True,
        drift: str = 'none',
        tab_id: int = 1,
        url: str = "https://chatgpt.com/c/mock-conversation",
        log: Callable[[str], None] | None = None,
    ) -> None:
        self.socket_path = Path(socket_path)
        self.responder = responder
        self.drift = drift
        if drift not in DRIFT_SCENARIOS:
            raise SystemExit(f"unknown drift scenario: {drift}. Known: {', '.join(sorted(DRIFT_SCENARIOS))}")
        # A drifted surface that cannot report its lifecycle also stops emitting it.
        self.emit_generation = emit_generation and drift != 'no-generation-signal'
        self.tab_id = tab_id
        self.url = url
        self._log = log or (lambda _m: None)

        self._lock = threading.Lock()
        self.composer = ""
        self.latest_output = ""
        self.turn_index = 0
        self.generation: _Generation | None = None
        self.transcript: list[JsonDict] = []
        self.overrides: JsonDict = {}
        self.transfers: dict[str, JsonDict] = {}
        self.attached: list[JsonDict] = []   # files currently in the composer

        self._server = BrokerServer(self.socket_path, self._emit_to_extension, self._status)

    # -- lifecycle --------------------------------------------------------- #
    def __enter__(self) -> "MockChatGPTTab":
        self.start()
        return self

    def __exit__(self, *_exc) -> None:
        self.stop()

    def start(self) -> None:
        self._server.start()
        self._log(f"[mock-tab] serving broker at {self.socket_path}")

    def stop(self) -> None:
        self._server.stop()

    # -- broker plumbing --------------------------------------------------- #
    def _status(self) -> JsonDict:
        return {
            "ok": True,
            "mock": True,
            "supportedTabs": [{"tabId": self.tab_id, "url": self.url, "adapter": "chatgpt"}],
            "selectedTargetTabId": self.tab_id,
        }

    def _emit_to_extension(self, message: JsonDict) -> None:
        """The broker forwards ``bridge.forward_to_active_tab`` here; we act as the tab."""
        if message.get("type") != "bridge.forward_to_active_tab":
            return
        request = message.get("payload", {}).get("request")
        if not isinstance(request, dict):
            return
        reply = self._handle_request(request)
        self._server.broadcast({"stream": "browser_event", "message": reply})

    def _reply_envelope(self, request: JsonDict, msg_type: str, payload: JsonDict) -> JsonDict:
        return {
            "version": "0.1",
            "request_id": request.get("request_id"),
            "type": msg_type,
            "timestamp": _utc_now(),
            "tab_id": self.tab_id,
            "payload": payload,
        }

    # -- the emulated content script -------------------------------------- #
    def _handle_request(self, request: JsonDict) -> JsonDict:
        rtype = request.get("type")
        payload = request.get("payload") if isinstance(request.get("payload"), dict) else {}
        with self._lock:
            if rtype == "prompt.read":
                return self._reply_envelope(request, rtype, {"text": self.composer, "adapter": "chatgpt", "url": self.url})

            if rtype == "prompt.write":
                if self.drift == 'composer-removed':
                    return self._reply_envelope(request, rtype, {
                        "ok": False, "adapter": "chatgpt", "readback": None,
                        "error": "composer not found", "url": self.url,
                    })
                self.composer = str(payload.get("text") or "")
                return self._reply_envelope(request, rtype, {
                    "ok": True, "adapter": "chatgpt", "readback": self.composer, "url": self.url,
                })

            if rtype == "prompt.submit":
                return self._reply_envelope(request, rtype, self._do_submit())

            if rtype == "prompt.continue":
                ok = self.generation is not None and self.generation.advance_past_continue()
                return self._reply_envelope(request, rtype, {
                    "ok": ok, "adapter": "chatgpt", "generation": self._generation_field(), "url": self.url,
                })

            if rtype in ("state.snapshot", "generation.state", "transcript.latest"):
                self._advance_generation()
                return self._reply_envelope(request, rtype, self._read_state(rtype))

            if rtype == "attach.begin":
                transfer_id = payload.get("transfer_id")
                size = payload.get("size")
                chunks = payload.get("chunks")
                valid = (
                    isinstance(transfer_id, str) and 0 < len(transfer_id) <= 128
                    and isinstance(payload.get("name"), str) and 0 < len(payload["name"]) <= 1024
                    and isinstance(size, int) and not isinstance(size, bool) and 0 < size <= MAX_ATTACHMENT_BYTES
                    and isinstance(chunks, int) and not isinstance(chunks, bool) and 0 < chunks <= MAX_ATTACH_CHUNKS
                    and chunks == (size + ATTACH_CHUNK_BYTES - 1) // ATTACH_CHUNK_BYTES
                )
                if not valid:
                    return self._reply_envelope(request, rtype, {
                        "ok": False,
                        "error": f"invalid attachment envelope (max {MAX_ATTACHMENT_BYTES} bytes / {MAX_ATTACH_CHUNKS} chunks)",
                    })
                if transfer_id in self.transfers:
                    return self._reply_envelope(request, rtype, {"ok": False, "error": "duplicate transfer_id"})
                if len(self.transfers) >= MAX_ACTIVE_ATTACH_TRANSFERS:
                    return self._reply_envelope(request, rtype, {
                        "ok": False,
                        "error": f"too many active attachment transfers (max {MAX_ACTIVE_ATTACH_TRANSFERS})",
                    })
                if self.drift == 'no-file-input':
                    return self._reply_envelope(request, rtype, {
                        "ok": False, "adapter": "chatgpt",
                        "error": 'no <input type="file"> found in the page', "url": self.url,
                    })
                keys_before = self._composer_keys()
                witness_before = self._attachment_witness(keys_before, "")
                input_files_before = witness_before["input_files"]
                known_chip_keys_before = self._attachment_witness([], "")["known_chip_keys"]
                expected_name_visible_before = self._attachment_witness(
                    keys_before, str(payload.get("name") or "")
                )["expected_name_visible"]
                self.transfers[transfer_id] = {
                    "name": payload.get("name"),
                    "size": int(payload.get("size") or 0),
                    "chunks": [None] * chunks,
                    "keys_before": keys_before,
                    "known_chip_keys_before": known_chip_keys_before,
                    "expected_name_visible_before": expected_name_visible_before,
                }
                return self._reply_envelope(request, rtype, {
                    "ok": True, "adapter": "chatgpt", "transfer_id": transfer_id,
                    "composer_keys_before": self.transfers[transfer_id]["keys_before"],
                    "input_files_before": input_files_before,
                    "known_chip_keys_before": known_chip_keys_before,
                    "expected_name_visible_before": expected_name_visible_before,
                    "url": self.url,
                })

            if rtype == "attach.chunk":
                transfer = self.transfers.get(str(payload.get("transfer_id")))
                if transfer is None:
                    return self._reply_envelope(request, rtype, {"ok": False, "error": "unknown transfer_id"})
                index = payload.get("index")
                if not isinstance(index, int) or isinstance(index, bool) or index < 0 or index >= len(transfer["chunks"]):
                    return self._reply_envelope(request, rtype, {
                        "ok": False,
                        "error": f"chunk index {index} is outside 0..{len(transfer['chunks']) - 1}",
                    })
                data = payload.get("data")
                if not isinstance(data, str) or not data or len(data) > MAX_ATTACH_CHUNK_BASE64:
                    return self._reply_envelope(request, rtype, {
                        "ok": False,
                        "error": f"invalid base64 chunk payload (max {MAX_ATTACH_CHUNK_BASE64} characters)",
                    })
                transfer["chunks"][index] = str(payload.get("data") or "")
                received = sum(1 for chunk in transfer["chunks"] if chunk is not None)
                return self._reply_envelope(request, rtype, {
                    "ok": True, "index": index, "received": received, "expected": len(transfer["chunks"]),
                })

            if rtype == "attach.commit":
                import base64
                import binascii
                transfer = self.transfers.pop(str(payload.get("transfer_id")), None)
                if transfer is None:
                    return self._reply_envelope(request, rtype, {"ok": False, "error": "unknown transfer_id"})
                if any(chunk is None for chunk in transfer["chunks"]):
                    return self._reply_envelope(request, rtype, {"ok": False, "error": "incomplete transfer"})
                try:
                    data = b"".join(base64.b64decode(chunk, validate=True) for chunk in transfer["chunks"])
                except (ValueError, binascii.Error) as exc:
                    return self._reply_envelope(request, rtype, {
                        "ok": False, "error": f"attachment decode failed: {exc}",
                    })
                if len(data) != transfer["size"]:
                    return self._reply_envelope(request, rtype, {
                        "ok": False,
                        "error": f"size mismatch after reassembly: got {len(data)}, expected {transfer['size']}",
                    })
                if len(data) == 0:
                    return self._reply_envelope(request, rtype, {
                        "ok": False, "error": f"refusing to attach zero-byte file: {transfer['name']}",
                    })

                files_before = len(self.attached)
                self.attached.append({"name": transfer["name"], "bytes": len(data)})
                # 'silent-upload-failure': the input takes the bytes, but the page
                # never renders a chip. This is the fileless-prompt trap, reproduced.
                if self.drift == 'silent-upload-failure':
                    self.attached.pop()
                witness = self._attachment_witness(
                    transfer["keys_before"],
                    str(transfer["name"] or ""),
                    bool(transfer["expected_name_visible_before"]),
                )
                return self._reply_envelope(request, rtype, {
                    "ok": True, "adapter": "chatgpt", "name": transfer["name"], "bytes": len(data),
                    "files_before": files_before, "files_after": len(self.attached),
                    "composer_keys_before": transfer["keys_before"],
                    "expected_name_visible_before": transfer["expected_name_visible_before"],
                    "witness": witness, "url": self.url,
                })

            if rtype == "attach.status":
                witness = self._attachment_witness(
                    list(payload.get("composer_keys_before") or []),
                    str(payload.get("expected_name") or ""),
                    bool(payload.get("expected_name_visible_before")),
                )
                return self._reply_envelope(request, rtype, {
                    "ok": True, "adapter": "chatgpt", "witness": witness, "url": self.url,
                })

            if rtype == "attach.abort":
                transfer_id = str(payload.get("transfer_id") or "")
                aborted = self.transfers.pop(transfer_id, None) is not None
                return self._reply_envelope(request, rtype, {
                    "ok": True, "aborted": aborted, "adapter": "chatgpt",
                })

            if rtype == "attach.clear":
                files_before = len(self.attached)
                if self.drift != 'sticky-attachment-chip':
                    self.attached.clear()
                witness = self._attachment_witness(
                    list(payload.get("composer_keys_before") or []),
                    str(payload.get("expected_name") or ""),
                    bool(payload.get("expected_name_visible_before")),
                )
                return self._reply_envelope(request, rtype, {
                    "ok": True, "adapter": "chatgpt", "inputs_seen": 1,
                    "files_before": files_before, "files_after": len(self.attached),
                    "witness": witness, "url": self.url,
                })

            if rtype == "prompt.stop":
                stopping = self.generation is not None and self.generation.current.state == STREAMING
                if stopping:
                    self.generation = None
                return self._reply_envelope(request, rtype, {"ok": stopping, "adapter": "chatgpt"})

            if rtype == "chat.new":
                self.transcript.clear()
                self.latest_output = ""
                self.generation = None
                self.attached.clear()
                self.composer = ""
                return self._reply_envelope(request, rtype, {"ok": True, "adapter": "chatgpt", "url": self.url})

            if rtype == "surface.overrides.set":
                requested = payload.get("overrides")
                self.overrides = dict(requested) if isinstance(requested, dict) else {}
                return self._reply_envelope(request, rtype, {
                    "ok": True, "adapter": "chatgpt", "overrides": self.overrides, "url": self.url,
                })

            if rtype == "surface.overrides.get":
                return self._reply_envelope(request, rtype, {
                    "ok": True, "adapter": "chatgpt", "overrides": self.overrides, "url": self.url,
                })

            if rtype == "surface.probe":
                probe = build_mock_probe(self.drift, url=self.url, composer_text=self.composer,
                                         attached_files=len(self.attached))
                return self._reply_envelope(request, rtype, {
                    "ok": True, "adapter": "chatgpt", "probe": probe, "url": self.url,
                })

            if rtype == "selection.read":
                return self._reply_envelope(request, rtype, {"text": None, "adapter": "chatgpt", "url": self.url})

            # Unknown types get a benign ok=false so the engine surfaces it clearly.
            return self._reply_envelope(request, "error.report", {
                "ok": False, "error": f"mock tab has no handler for {rtype}", "adapter": "chatgpt",
            })

    def _do_submit(self) -> JsonDict:
        # A drifted surface must FAIL like the real thing, not merely look wrong.
        # Behaviour is derived from the SAME capability map the probe reports, so
        # the mock can never look broken while secretly working (or vice versa) —
        # that inconsistency would let a wrong diagnosis pass its own test.
        probe = build_mock_probe(self.drift, url=self.url, composer_text=self.composer,
                                 attached_files=len(self.attached))
        caps = probe['capabilities']
        if not caps['write_prompt']:
            return {"ok": False, "adapter": "chatgpt", "error": "composer not found", "url": self.url}
        if not caps['submit_prompt'] and self._override_finds_send(probe):
            # A correct runtime override points the adapter at the real (renamed)
            # send control, so the click lands and the tab HEALS. This is the
            # end-to-end proof that a repair actually repairs something.
            caps = {**caps, 'submit_prompt': True}
        if not caps['submit_prompt']:
            # The adapter refuses to click a control it cannot positively identify
            # as send. That refusal is the feature, not the bug.
            return {"ok": False, "adapter": "chatgpt",
                    "error": "no send control matched the expected live surface", "url": self.url}

        prompt = self.composer.strip()
        if not prompt:
            return {"ok": False, "adapter": "chatgpt", "error": "empty composer", "url": self.url}
        reply = self.responder(prompt, self.turn_index + 1)
        if reply.refuse:
            return {"ok": False, "adapter": "chatgpt", "error": "mock refused submit", "url": self.url}
        self.turn_index += 1
        submitted = prompt
        self.composer = ""
        self.transcript.append({"role": "user", "text": submitted, "attachments": list(self.attached)})
        self.attached.clear()
        if reply.stall:
            self.generation = None  # nothing will ever change
            return {"ok": True, "adapter": "chatgpt", "submitted_prompt": submitted,
                    "prompt_after_submit": "", "url": self.url}
        if self.drift in ('nag-dialog', 'rate-limit-banner'):
            # The click landed, but a modal/banner swallowed it: the exact shape of
            # "submit said ok and nothing happened", which is the hardest real failure.
            self.generation = None
            return {"ok": True, "adapter": "chatgpt", "submitted_prompt": submitted,
                    "prompt_after_submit": "", "url": self.url}
        self.generation = _Generation(_frames_for(reply, self.latest_output))
        # prime the first visible frame immediately
        self.latest_output = self.generation.current.text
        return {"ok": True, "adapter": "chatgpt", "submitted_prompt": submitted,
                "composer_readback_before_submit": submitted, "prompt_after_submit": "", "url": self.url}

    def _composer_keys(self) -> list[str]:
        probe = build_mock_probe(self.drift, url=self.url, composer_text=self.composer,
                                 attached_files=len(self.attached))
        return [c['key'] for c in probe['controls'] if c['region'] == 'composer' and c['visible']]

    def _attachment_witness(
        self,
        keys_before: list[str],
        expected_name: str = "",
        expected_name_visible_before: bool = False,
    ) -> JsonDict:
        probe = build_mock_probe(self.drift, url=self.url, composer_text=self.composer,
                                 attached_files=len(self.attached))
        now = [c for c in probe['controls'] if c['region'] == 'composer' and c['visible']]
        remaining: dict[str, int] = {}
        for key in keys_before:
            remaining[key] = remaining.get(key, 0) + 1
        added = []
        for control in now:
            key = control['key']
            if remaining.get(key, 0) > 0:
                remaining[key] -= 1
            else:
                added.append(control)
        known_chip_keys = [c['key'] for c in added if c['classification'] == 'attachment-chip']
        expected_name_visible = bool(
            expected_name and (
                expected_name.casefold() in self.composer.casefold()
                or any(item.get('name') == expected_name for item in self.attached)
            )
        )
        expected_name_newly_visible = expected_name_visible and not expected_name_visible_before
        return {
            "input_files": 0 if self.drift == 'consumed-file-input' else len(self.attached),
            "added_keys": [c['key'] for c in added],
            # The real content script returns the full control descriptors so the
            # chip can be *identified*, not merely counted. The mock must too.
            "added_controls": added,
            "known_chip_keys": known_chip_keys,
            "expected_name_visible": expected_name_visible,
            "expected_name_newly_visible": expected_name_newly_visible,
            "chip_present": bool(known_chip_keys) or (bool(added) and expected_name_newly_visible),
        }

    def _override_finds_send(self, probe: JsonDict) -> bool:
        selector = self.overrides.get('send')
        if not selector:
            return False
        for control in probe['controls']:
            if control['classification'] != 'send' or not control['visible']:
                continue
            # The same identity forms the real adapter would resolve.
            forms = {
                f"#{control['id']}" if control['id'] else None,
                f"[data-testid=\"{control['test_id']}\"]" if control['test_id'] else None,
                f"[aria-label=\"{control['aria_label']}\"]" if control['aria_label'] else None,
                control['selector_hint'],
            }
            if selector in {form for form in forms if form}:
                return True
        return False

    def _advance_generation(self) -> None:
        gen = self.generation
        if gen is None:
            return
        self.latest_output = gen.current.text
        if gen.current.state == SETTLED:
            self.transcript_finalize()
            return
        gen.advance_if_streaming()
        self.latest_output = gen.current.text

    def transcript_finalize(self) -> None:
        if self.transcript and self.transcript[-1].get("role") == "assistant":
            self.transcript[-1]["text"] = self.latest_output
        else:
            self.transcript.append({"role": "assistant", "text": self.latest_output})

    def _generation_field(self) -> JsonDict | None:
        if not self.emit_generation:
            return None
        gen = self.generation
        state = gen.current.state if gen is not None else SETTLED
        return {
            "state": state,
            "stop_present": state == STREAMING,
            "continue_present": state == NEEDS_CONTINUE,
            "stop_selector": "#composer-submit-button" if state == STREAMING else None,
            "continue_selector": "button[data-testid=continue]" if state == NEEDS_CONTINUE else None,
        }

    def _read_state(self, rtype: str) -> JsonDict:
        witness = {
            "text": self.latest_output or None,
            "assistant_like": bool(self.latest_output),
            "author_role": "assistant" if self.latest_output else None,
            "selection_policy": "mock",
        }
        base: JsonDict = {
            "adapter": "chatgpt",
            "latest_output": self.latest_output,
            "latest_output_witness": witness,
            "generation": self._generation_field(),
            "url": self.url,
        }
        # Field-for-field fidelity with extension/src/content/main.ts:
        # `transcript.latest` replies under `text`; `state.snapshot` replies under
        # `latest_output`. The mock must not invent a shape the real page never
        # sends, or it stops being a valid test double.
        if rtype == "transcript.latest":
            base["text"] = self.latest_output or None
        if rtype == "state.snapshot":
            base["prompt"] = self.composer
            base["selection"] = None
        return base


def run_mock_tab(
    socket_path: Path,
    *,
    emit_generation: bool = True,
    drift: str = 'none',
    rules_path: Path | None = None,
    verbose: bool = True,
) -> int:
    """Blocking entry point used by ``glassttyd mock-tab``."""
    responder = default_responder
    if rules_path is not None:
        responder = _responder_from_rules(rules_path)

    def _log(msg: str) -> None:
        if verbose:
            print(msg, flush=True)

    tab = MockChatGPTTab(socket_path, responder=responder, emit_generation=emit_generation, drift=drift, log=_log)
    tab.start()
    if drift != 'none':
        _log(f"[mock-tab] DRIFT ACTIVE: {drift} — {DRIFT_SCENARIOS[drift]}")
    _log("[mock-tab] ready. Try: glassttyd ask \"hello\"   (Ctrl-C to stop)")
    _log(f"[mock-tab] generation lifecycle emitted: {emit_generation}")
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        _log("\n[mock-tab] stopping")
    finally:
        tab.stop()
    return 0


def _responder_from_rules(rules_path: Path) -> Responder:
    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    if not isinstance(rules, list):
        raise SystemExit(f"mock rules file must be a JSON list of objects: {rules_path}")

    def responder(prompt: str, turn_index: int) -> MockReply:
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            needle = rule.get("contains")
            if isinstance(needle, str) and needle in prompt:
                reply = rule.get("reply", "")
                parts = reply if isinstance(reply, list) else [str(reply)]
                return MockReply(parts=[str(p) for p in parts], stall=bool(rule.get("stall")), refuse=bool(rule.get("refuse")))
        return default_responder(prompt, turn_index)

    return responder
