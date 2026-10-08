from __future__ import annotations

from micromax import VM


def test_require_resolves_relative_to_calling_file(tmp_path) -> None:
    lib = tmp_path / 'lib'
    lib.mkdir()
    util = lib / 'util.mx'
    util.write_text(': util "u" ;\n', encoding='utf-8')

    main = tmp_path / 'main.mx'
    main.write_text('"lib/util.mx" require\n', encoding='utf-8')

    vm = VM()
    vm.eval(main.read_text(encoding='utf-8'), filename=str(main))

    vm.eval('util', filename='<test>')
    assert vm.stack.pop() == 'u'


def test_require_resolves_via_micromax_path(monkeypatch, tmp_path) -> None:
    lib = tmp_path / 'mylib'
    lib.mkdir()
    util = lib / 'util.mx'
    util.write_text(': u2 "ok" ;\n', encoding='utf-8')

    monkeypatch.setenv('MICROMAX_PATH', str(lib))

    vm = VM()
    vm.eval('"util.mx" require', filename='<repl>')

    vm.eval('u2', filename='<test>')
    assert vm.stack.pop() == 'ok'


def test_require_resolves_via_host_load_paths(tmp_path) -> None:
    lib = tmp_path / 'hostlib'
    lib.mkdir()
    util = lib / 'h.mx'
    util.write_text(': h "h" ;\n', encoding='utf-8')

    vm = VM()
    vm.load_paths.append(str(lib))
    vm.eval('"h.mx" require', filename='<repl>')

    vm.eval('h', filename='<test>')
    assert vm.stack.pop() == 'h'
