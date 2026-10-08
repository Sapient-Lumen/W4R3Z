from vhk.core.models import I3WindowSelector
from vhk.i3.tree import find_first


def test_find_first_window_by_class_and_workspace():
    tree = {
        "type": "root",
        "nodes": [
            {
                "type": "output",
                "name": "HDMI-0",
                "nodes": [
                    {
                        "type": "workspace",
                        "name": "1",
                        "nodes": [
                            {
                                "type": "con",
                                "id": 123,
                                "name": "MyApp",
                                "urgent": False,
                                "focused": True,
                                "window_properties": {"class": "MyClass", "instance": "myinst", "title": "MyApp"},
                                "nodes": [],
                                "floating_nodes": [],
                            }
                        ],
                        "floating_nodes": [],
                    }
                ],
                "floating_nodes": [],
            }
        ],
        "floating_nodes": [],
    }

    sel = I3WindowSelector.model_validate({"class": "MyClass", "workspace": "1"})
    m = find_first(tree, sel)
    assert m is not None
    assert m.node["id"] == 123
    assert m.workspace == "1"


def test_find_first_title_regex():
    tree = {
        "type": "root",
        "nodes": [
            {
                "type": "workspace",
                "name": "2",
                "nodes": [
                    {
                        "type": "con",
                        "id": 77,
                        "name": "Firefox — Docs",
                        "window_properties": {"class": "firefox", "instance": "Navigator", "title": "Firefox — Docs"},
                        "nodes": [],
                        "floating_nodes": [],
                    }
                ],
                "floating_nodes": [],
            }
        ],
        "floating_nodes": [],
    }

    sel = I3WindowSelector(title="Firefox.*Docs", title_regex=True)
    m = find_first(tree, sel)
    assert m is not None
    assert m.node["id"] == 77
