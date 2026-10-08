from __future__ import annotations

from vhk.system.display import (
    parse_gnome_displayconfig_getcurrentstate,
    parse_kscreen_doctor_outputs,
    parse_wlr_randr_json,
    parse_wlr_randr_outputs,
)


def test_parse_gnome_displayconfig_basic() -> None:
    # Minimal `gdbus call ... GetCurrentState`-style output.
    text = (
        "(uint32 7, "
        "[(('eDP-1', 'V', 'P', 'S'), "
        "  [('mode1', 1920, 1080, 60.0, 1.0, [1.0, 2.0], {'is-current': <true>})], "
        "  {'is-builtin': <true>})], "
        "[(0, 0, 1.0, uint32 0, true, [('eDP-1', 'V', 'P', 'S')], @a{sv} {})], "
        "{'layout-mode': <uint32 2>})"
    )

    size = parse_gnome_displayconfig_getcurrentstate(text)
    assert size is not None
    assert size.width == 1920
    assert size.height == 1080
    assert size.backend == "gnome-displayconfig"


def test_parse_gnome_displayconfig_scaled_logical() -> None:
    # scale=2 and logical layout => width/height divided by scale.
    text = (
        "(uint32 7, "
        "[(('eDP-1', 'V', 'P', 'S'), "
        "  [('mode1', 1920, 1080, 60.0, 2.0, [1.0, 2.0], {'is-current': <true>})], "
        "  {})], "
        "[(0, 0, 2.0, uint32 0, true, [('eDP-1', 'V', 'P', 'S')], @a{sv} {})], "
        "{'layout-mode': <uint32 2>})"
    )

    size = parse_gnome_displayconfig_getcurrentstate(text)
    assert size is not None
    assert size.width == 960
    assert size.height == 540


def test_parse_gnome_displayconfig_transform_swap() -> None:
    # transform=1 (90 degrees) swaps w/h.
    text = (
        "(uint32 7, "
        "[(('eDP-1', 'V', 'P', 'S'), "
        "  [('mode1', 1920, 1080, 60.0, 1.0, [1.0, 2.0], {'is-current': <true>})], "
        "  {})], "
        "[(0, 0, 1.0, uint32 1, true, [('eDP-1', 'V', 'P', 'S')], @a{sv} {})], "
        "{'layout-mode': <uint32 2>})"
    )

    size = parse_gnome_displayconfig_getcurrentstate(text)
    assert size is not None
    assert size.width == 1080
    assert size.height == 1920


def test_parse_kscreen_doctor_outputs_geometry() -> None:
    out = """
Output: 1
  Name: DP-1
  Enabled: true
  Geometry: 0,0 2560x1440
Output: 2
  Name: HDMI-1
  Enabled: true
  Geometry: 2560,0 1920x1080
"""

    size = parse_kscreen_doctor_outputs(out)
    assert size is not None
    assert size.width == 2560 + 1920
    assert size.height == 1440
    assert size.backend == "kscreen-doctor"



def test_parse_wlr_randr_plain_outputs() -> None:
    out = """
DP-1 "Test (DP-1)"
  Enabled: yes
  Modes:
    2560x1440 px, 59.950000 Hz (preferred, current)
  Position: 0,0
  Transform: normal
  Scale: 1.000000
HDMI-A-1 "Test (HDMI-A-1)"
  Enabled: yes
  Modes:
    1920x1080 px, 60.000000 Hz (current)
  Position: 2560,0
  Transform: normal
  Scale: 1.000000
"""

    size = parse_wlr_randr_outputs(out)
    assert size is not None
    assert size.width == 2560 + 1920
    assert size.height == 1440
    assert size.backend == "wlr-randr"


def test_parse_wlr_randr_negative_positions_bbox() -> None:
    out = """
DP-1 "Left"
  Enabled: yes
  Modes:
    1920x1080 px, 60.000000 Hz (current)
  Position: -1920,0
  Transform: normal
  Scale: 1.000000
HDMI-A-1 "Right"
  Enabled: yes
  Modes:
    1920x1080 px, 60.000000 Hz (current)
  Position: 0,0
  Transform: normal
  Scale: 1.000000
"""

    size = parse_wlr_randr_outputs(out)
    assert size is not None
    assert size.width == 3840
    assert size.height == 1080


def test_parse_wlr_randr_json_scaled_and_transform() -> None:
    # Portrait transform swaps w/h. scale divides for logical size.
    js = """
[
  {
    "name": "eDP-1",
    "enabled": true,
    "position": {"x": 0, "y": 0},
    "current_mode": {"width": 1920, "height": 1080},
    "scale": 2.0,
    "transform": 1
  }
]
"""

    size = parse_wlr_randr_json(js)
    assert size is not None
    # mode 1920x1080, portrait => 1080x1920, scale 2 => 540x960
    assert size.width == 540
    assert size.height == 960
