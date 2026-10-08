"""Static witnesses for identity ownership and cross-thread boundaries."""
from __future__ import annotations

import ast
import os
from pathlib import Path


SOURCE = Path(os.environ["NICOTINE_SOURCE_ROOT"])


def text(relative: str) -> str:
    return (SOURCE / relative).read_text(encoding="utf-8")


def function_source(relative: str, class_name: str, function_name: str) -> str:
    source = text(relative)
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == function_name:
                    segment = ast.get_source_segment(source, item)
                    assert segment is not None
                    return segment
    raise AssertionError(f"missing {class_name}.{function_name}")


def test_search_token_is_core_registry_key_and_wire_token():
    source = text("pynicotine/search.py")
    assert "self.searches[token] = search = SearchRequest(" in source
    assert "self.add_allowed_token(token)" in function_source(
        "pynicotine/search.py", "Search", "send_search_request"
    )
    assert "UserSearch(username, search.token" in source


def test_gui_page_and_notification_identity_are_token_keyed():
    source = text("pynicotine/gtkgui/search.py")
    assert "self.pages[token] = page = Search(" in source
    assert "self.token = token" in source
    assert "str(self.token), self.text" in source


def test_search_again_reuses_page_token_without_clear():
    source = function_source("pynicotine/gtkgui/search.py", "Search", "on_search_again")
    assert "core.search.send_search_request(self.token)" in source
    assert "clear_model" not in source


def test_result_page_deduplicates_username_until_clear():
    response = function_source("pynicotine/gtkgui/search.py", "Search", "file_search_response")
    clear = function_source("pynicotine/gtkgui/search.py", "Search", "clear_model")
    assert "if user in self.users:" in response
    assert "self.users.clear()" in clear


def test_main_emit_is_synchronous_but_network_events_are_queued():
    events_source = text("pynicotine/events.py")
    emit = function_source("pynicotine/events.py", "Events", "emit")
    emit_main = function_source("pynicotine/events.py", "Events", "emit_main_thread")
    assert "function(*args, **kwargs)" in emit
    assert "self._thread_events.put_nowait" in emit_main
    assert "Called by the main loop 10 times per second" in events_source


def test_network_queue_silently_ignores_messages_while_disabled():
    queue_source = function_source("pynicotine/slskproto.py", "NetworkThread", "_queue_network_message")
    assert "if self._should_process_queue:" in queue_source
    assert "self._message_queue.put_nowait(msg)" in queue_source
    assert "else" not in queue_source


def test_allowed_response_controls_share_network_queue_with_server_messages():
    core_source = text("pynicotine/core.py")
    assert core_source.count('events.emit("queue-network-message", message)') >= 2
    protocol = text("pynicotine/slskproto.py")
    assert "elif msg_class is AddAllowedResponse:" in protocol
    assert "elif msg_class is RemoveAllowedResponse:" in protocol


def test_search_result_token_gate_precedes_full_decompression():
    source = function_source(
        "pynicotine/slskmessages.py", "FileSearchResponse", "parse_network_message"
    )
    gate = source.index("if self.token not in self.allowed_responses:")
    full = source.index("max_uncompressed_size")
    # The constant is declared before the gate, so use the second decompression
    # call as the full-message boundary.
    full_decompress = source.rindex("decompressor.decompress")
    assert gate < full_decompress
    assert "return" in source[gate:full_decompress]


def test_retry_at_display_cap_retires_token_before_page_processing():
    source = function_source(
        "pynicotine/gtkgui/search.py", "Searches", "file_search_response"
    )
    cap = source.index("if page.num_results_found >=")
    retire = source.index("core.search.remove_allowed_token(msg.token)")
    dispatch = source.index("page.file_search_response(msg)")
    assert cap < retire < dispatch


def test_disconnect_clears_pending_queue_and_response_admission():
    source = text("pynicotine/slskproto.py")
    disable = function_source("pynicotine/slskproto.py", "NetworkThread", "_disable_message_queue")
    clear = function_source("pynicotine/slskproto.py", "NetworkThread", "_clear_message_queue")
    disconnect = function_source("pynicotine/slskproto.py", "NetworkThread", "_server_disconnect")
    assert "self._clear_message_queue()" in disable
    assert "self._message_queue.get_nowait()" in clear
    assert "self._allowed_message_responses.clear()" in disconnect
    assert source.index("def _disable_message_queue") < source.index("def _server_disconnect")
