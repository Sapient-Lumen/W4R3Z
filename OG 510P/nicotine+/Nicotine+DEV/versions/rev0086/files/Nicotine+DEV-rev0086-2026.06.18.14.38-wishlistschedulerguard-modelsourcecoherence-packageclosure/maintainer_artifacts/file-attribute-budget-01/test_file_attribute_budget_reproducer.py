# SPDX-License-Identifier: GPL-3.0-or-later
"""Current-behavior witness for FILE-ATTRIBUTE-BUDGET-01 / U-199."""

import zlib

import pytest


def _pack_string(slsk, text):
    return slsk.FileListMessage.pack_string(text)


def _pack_uint8(slsk, value):
    return slsk.FileListMessage.pack_uint8(value)


def _pack_uint32(slsk, value):
    return slsk.FileListMessage.pack_uint32(value)


def _pack_uint64(slsk, value):
    return slsk.FileListMessage.pack_uint64(value)


def _inflate_attribute_pairs(slsk, *, filler_count=11, final_bitrate=320):
    """Return >valid-attribute-count pairs with the useful attribute at the end."""
    bitrate_attr = slsk.FileAttribute.BITRATE
    pairs = []

    for index in range(filler_count):
        # ENCODER is known as a protocol file attribute code but is not retained
        # by the current Nicotine+ parser, so it is a safe filler. Vary the value
        # to avoid collapsing the test into one duplicate-key dictionary case.
        pairs.append((slsk.FileAttribute.ENCODER, index + 1))

    pairs.append((bitrate_attr, final_bitrate))
    return pairs


def _pack_file_record(slsk, *, virtual_path="Music/needle.mp3", size=123456, attrs=None):
    if attrs is None:
        attrs = _inflate_attribute_pairs(slsk)

    msg = bytearray()
    msg += _pack_uint8(slsk, 1)
    msg += _pack_string(slsk, virtual_path)
    msg += _pack_uint64(slsk, size)
    msg += _pack_uint32(slsk, 0)  # obsolete extension length
    msg += _pack_uint32(slsk, len(attrs))

    for attrnum, attr in attrs:
        msg += _pack_uint32(slsk, attrnum)
        msg += _pack_uint32(slsk, attr)

    return msg


def _new_message(cls, compressed_payload):
    try:
        return cls(msg_content=compressed_payload)
    except TypeError:
        return cls()


def _parse(instance, compressed_payload):
    try:
        return instance.parse_network_message(compressed_payload)
    except TypeError:
        return instance.parse_network_message()


def _attribute_dict(attrs):
    if hasattr(attrs, "as_dict"):
        return attrs.as_dict()
    return attrs


def _assert_final_bitrate_survived(slsk, attrs, expected=320):
    assert _attribute_dict(attrs).get(slsk.FileAttribute.BITRATE) == expected


def test_search_result_parser_walks_peer_supplied_attribute_count_beyond_known_file_attribute_budget():
    import pynicotine.slskmessages as slsk

    token = 0x199001
    payload = bytearray()
    payload += _pack_string(slsk, "peer_user")
    payload += _pack_uint32(slsk, token)
    payload += _pack_uint32(slsk, 1)
    payload += _pack_file_record(slsk)
    payload += slsk.FileListMessage.pack_bool(True)
    payload += _pack_uint32(slsk, 1000)
    payload += _pack_uint32(slsk, 0)
    payload += _pack_uint32(slsk, 0)
    compressed_payload = zlib.compress(bytes(payload))

    msg = _new_message(slsk.FileSearchResponse, compressed_payload)

    if hasattr(slsk, "SEARCH_TOKENS_ALLOWED"):
        slsk.SEARCH_TOKENS_ALLOWED.add(token)
    if hasattr(msg, "allowed_responses"):
        msg.allowed_responses.add(token)

    _parse(msg, compressed_payload)

    assert len(msg.list) == 1
    _assert_final_bitrate_survived(slsk, msg.list[0][4])


def test_shared_file_list_parser_walks_peer_supplied_attribute_count_beyond_known_file_attribute_budget():
    import pynicotine.slskmessages as slsk

    payload = bytearray()
    payload += _pack_uint32(slsk, 1)              # folder count
    payload += _pack_string(slsk, "Music")
    payload += _pack_uint32(slsk, 1)              # file count
    payload += _pack_file_record(slsk)
    compressed_payload = zlib.compress(bytes(payload))

    msg = _new_message(slsk.SharedFileListResponse, compressed_payload)
    _parse(msg, compressed_payload)

    assert len(msg.list) == 1
    _directory, files = msg.list[0]
    assert len(files) == 1
    _assert_final_bitrate_survived(slsk, files[0][4])


def test_folder_contents_parser_walks_peer_supplied_attribute_count_beyond_known_file_attribute_budget():
    import pynicotine.slskmessages as slsk

    directory = "Music"
    peer_username = "peer_user"
    token = 0x199002
    payload = bytearray()
    payload += _pack_uint32(slsk, token)
    payload += _pack_string(slsk, directory)
    payload += _pack_uint32(slsk, 1)              # returned folder count
    payload += _pack_string(slsk, directory)
    payload += _pack_uint32(slsk, 1)              # file count
    payload += _pack_file_record(slsk)
    compressed_payload = zlib.compress(bytes(payload))

    msg = _new_message(slsk.FolderContentsResponse, compressed_payload)

    if hasattr(msg, "username"):
        msg.username = peer_username
    if hasattr(msg, "allowed_responses"):
        msg.allowed_responses.add(peer_username + directory)

    _parse(msg, compressed_payload)

    assert directory in msg.list
    assert len(msg.list[directory]) == 1
    _assert_final_bitrate_survived(slsk, msg.list[directory][0][4])
