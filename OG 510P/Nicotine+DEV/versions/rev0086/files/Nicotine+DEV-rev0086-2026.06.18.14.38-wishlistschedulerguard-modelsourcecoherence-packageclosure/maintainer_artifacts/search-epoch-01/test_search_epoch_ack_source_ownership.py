"""Static witnesses for the queue-to-network ownership boundary.

These assertions bind the research model to the bundled master proxy. They do
not claim that a local ownership acknowledgement proves socket serialization,
remote receipt, or a response.
"""
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
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == function_name:
                segment = ast.get_source_segment(source, item)
                assert segment is not None
                return segment
    raise AssertionError(f"missing {class_name}.{function_name}")


def test_queue_acceptance_has_no_success_or_rejection_result():
    source = function_source(
        "pynicotine/slskproto.py", "NetworkThread", "_queue_network_message"
    )
    assert "if self._should_process_queue:" in source
    assert "self._message_queue.put_nowait(msg)" in source
    assert "return" not in source
    assert "else" not in source


def test_queue_drain_hands_a_list_to_outgoing_processing():
    source = function_source(
        "pynicotine/slskproto.py", "NetworkThread", "_process_queue_messages"
    )
    assert "msgs.append(self._message_queue.get_nowait())" in source
    assert "self._process_outgoing_messages(msgs)" in source


def test_outgoing_processing_can_drop_after_queue_acceptance():
    source = function_source(
        "pynicotine/slskproto.py", "NetworkThread", "_process_outgoing_messages"
    )
    assert "if not self._should_process_queue:" in source
    assert "if not self._is_outgoing_server_message_permitted(msg):" in source
    assert source.count("return") >= 2
    assert "Cannot send the message over the closed connection" in source
    assert "continue" in source


def test_allowed_response_controls_are_applied_in_network_thread():
    source = function_source(
        "pynicotine/slskproto.py", "NetworkThread", "_process_internal_messages"
    )
    assert "elif msg_class is AddAllowedResponse:" in source
    assert "self._allowed_message_responses[msg.msg_class].add(msg.response_id)" in source
    assert "elif msg_class is RemoveAllowedResponse:" in source
    assert "self._allowed_message_responses[msg.msg_class].discard(msg.response_id)" in source


def test_current_internal_controls_have_no_composite_epoch_message():
    source = function_source(
        "pynicotine/slskproto.py", "NetworkThread", "_process_internal_messages"
    )
    assert "SearchEpoch" not in source
    assert "EpochApplied" not in source
    assert "transaction_id" not in source


def test_network_loop_processes_commands_before_ready_sockets():
    source = function_source("pynicotine/slskproto.py", "NetworkThread", "_loop")
    queue_index = source.index("self._process_queue_messages()")
    sockets_index = source.index("self._process_ready_sockets(current_time)")
    assert queue_index < sockets_index


def test_disconnect_disables_and_clears_queue_before_main_event():
    source = function_source(
        "pynicotine/slskproto.py", "NetworkThread", "_server_disconnect"
    )
    disable_index = source.index("self._disable_message_queue()")
    clear_admission_index = source.index("self._allowed_message_responses.clear()")
    event_index = source.index('events.emit_main_thread(\n            "server-disconnect"')
    assert disable_index < clear_admission_index < event_index


def test_queue_disable_discards_accepted_commands():
    disable = function_source(
        "pynicotine/slskproto.py", "NetworkThread", "_disable_message_queue"
    )
    clear = function_source(
        "pynicotine/slskproto.py", "NetworkThread", "_clear_message_queue"
    )
    assert "self._should_process_queue = False" in disable
    assert "self._clear_message_queue()" in disable
    assert "self._message_queue.get_nowait()" in clear


def test_main_thread_events_are_fifo_batched_not_immediate_callbacks():
    emit_main = function_source("pynicotine/events.py", "Events", "emit_main_thread")
    process = function_source("pynicotine/events.py", "Events", "process_thread_events")
    assert "self._thread_events.put_nowait" in emit_main
    assert "event_list.append(self._thread_events.get_nowait())" in process
    assert "for event in event_list:" in process
    assert "self.emit(event.event_name" in process


def test_event_callbacks_do_not_return_acknowledgements_to_emitters():
    emit = function_source("pynicotine/events.py", "Events", "emit")
    assert "function(*args, **kwargs)" in emit
    assert "return function" not in emit
    assert "results.append" not in emit


def test_send_search_request_publishes_admission_before_requests():
    source = function_source("pynicotine/search.py", "Search", "send_search_request")
    admission_index = source.index("self.add_allowed_token(token)")
    first_send_index = min(
        source.index("self._send_global_search_request(search)"),
        source.index("self._send_rooms_search_request(search)"),
        source.index("self._send_buddies_search_request(search)"),
        source.index("self._send_peer_search_request(search)"),
    )
    assert admission_index < first_send_index


def test_disconnect_does_not_republish_existing_search_admissions_on_login():
    disconnect = function_source("pynicotine/search.py", "Search", "_server_disconnect")
    login = function_source("pynicotine/search.py", "Search", "_server_login")
    assert "self.searches.clear()" not in disconnect
    assert "add_allowed_token" not in login
    assert "send_search_request" not in login


def test_no_current_search_epoch_applied_event_name():
    source = text("pynicotine/events.py")
    assert '"search-epoch-applied"' not in source
    assert '"search-epoch-rejected"' not in source


def test_server_search_output_packs_then_appends_to_network_output_buffer():
    source = function_source(
        "pynicotine/slskproto.py", "NetworkThread", "_process_server_output"
    )
    pack_index = source.index("msg_content = self._pack_network_message(msg)")
    append_index = source.index("out_buffer += msg_content")
    write_interest_index = source.index("selectors.EVENT_WRITE")
    assert pack_index < append_index < write_interest_index


def test_server_output_silently_returns_when_packing_fails():
    source = function_source(
        "pynicotine/slskproto.py", "NetworkThread", "_process_server_output"
    )
    assert "if msg_content is None:" in source
    assert "return" in source[source.index("if msg_content is None:"):]
    assert "return True" not in source
    assert "return False" not in source


def test_existing_outgoing_batch_has_no_per_message_success_accounting():
    source = function_source(
        "pynicotine/slskproto.py", "NetworkThread", "_process_outgoing_messages"
    )
    assert "process_func(conn, msg)" in source
    assert "if process_func(conn, msg)" not in source
    assert "results.append" not in source


def test_search_close_retires_parser_admission_through_network_queue():
    remove = function_source("pynicotine/search.py", "Search", "remove_search")
    retire = function_source("pynicotine/search.py", "Search", "remove_allowed_token")
    assert remove.index("self.remove_allowed_token(token)") < remove.index(
        "search = self.searches.get(token)"
    )
    assert "core.send_message_to_network_thread" in retire
    assert "RemoveAllowedResponse" in retire
