from __future__ import annotations

"""Auditable core primitive registration table.

The primitive implementations remain in ``micromax.core`` so they can share
small helper closures, but the registration names/docs/effects live here.
This keeps duplicate definitions visible and makes ports easier to audit.
"""

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class PrimitiveEntry:
    name: str
    handler_name: str
    doc: str = ""
    effect: str = ""


CORE_PRIMITIVE_REGISTRY: tuple[PrimitiveEntry, ...] = (
    PrimitiveEntry('.', 'w_dot', doc='( x -- ) print top of stack'),
    PrimitiveEntry('cr', 'w_cr', doc='( -- ) newline'),
    PrimitiveEntry('emit', 'w_emit', doc='( n -- ) print character'),
    PrimitiveEntry('.s', 'w_dots', doc='( -- ) print stack'),
    PrimitiveEntry('callstack', 'w_callstack', doc='( -- xs ) return current callstack (debug)'),
    PrimitiveEntry('trace', 'w_callstack', doc='( -- xs ) alias for callstack'),
    PrimitiveEntry('words', 'w_words', doc='( -- ) list words in current search order'),
    PrimitiveEntry('words-list', 'w_words_list', doc='( -- names ) list word names in current search order'),
    PrimitiveEntry('words-rows', 'w_words_rows', doc='( -- rows ) list visible word rows [name kind effect doc wid wl]'),
    PrimitiveEntry('wid-words', 'w_wid_words', doc='( wid -- names ) list word names in a wordlist'),
    PrimitiveEntry('wid-word-rows', 'w_wid_word_rows', doc='( wid -- rows ) list word rows [name kind effect doc wid wl] in a wordlist'),
    PrimitiveEntry('wid-name', 'w_wid_name', doc='( wid -- s ) friendly wordlist name'),
    PrimitiveEntry('help', 'w_help', doc='( -- ) parse next name; show documentation'),
    PrimitiveEntry('where', 'w_where', doc='( -- ) parse next name; show defining wordlist'),
    PrimitiveEntry('order', 'w_order', doc='( -- ) print search order + current wordlist'),
    PrimitiveEntry('dup', 'w_dup', doc='', effect='( x -- x x )'),
    PrimitiveEntry('drop', 'w_drop', doc='', effect='( x -- )'),
    PrimitiveEntry('swap', 'w_swap', doc='', effect='( a b -- b a )'),
    PrimitiveEntry('over', 'w_over', doc='', effect='( a b -- a b a )'),
    PrimitiveEntry('rot', 'w_rot', doc='', effect='( a b c -- b c a )'),
    PrimitiveEntry('depth', 'w_depth', doc='', effect='( -- n )'),
    PrimitiveEntry('clear', 'w_clear', doc='', effect='( -- )'),
    PrimitiveEntry('pick', 'w_pick'),
    PrimitiveEntry('roll', 'w_roll'),
    PrimitiveEntry('>r', 'w_to_r', doc='( x -- ) move to return stack'),
    PrimitiveEntry('r>', 'w_r_from', doc='( -- x ) move from return stack'),
    PrimitiveEntry('r@', 'w_r_fetch', doc='( -- x ) copy top of return stack'),
    PrimitiveEntry('rdepth', 'w_rdepth', doc='( -- n ) return stack depth'),
    PrimitiveEntry('+', 'w_add', doc='checked signed-64-bit addition', effect='( a b -- n )'),
    PrimitiveEntry('-', 'w_sub', doc='checked signed-64-bit subtraction', effect='( a b -- n )'),
    PrimitiveEntry('*', 'w_mul', doc='checked signed-64-bit multiplication', effect='( a b -- n )'),
    PrimitiveEntry('/', 'w_div', doc='checked signed-64-bit floor division', effect='( a b -- n )'),
    PrimitiveEntry('mod', 'w_mod', doc='signed-64-bit remainder paired with floor division', effect='( a b -- n )'),
    PrimitiveEntry('=', 'w_eq', doc='', effect='( a b -- flag )'),
    PrimitiveEntry('<', 'w_lt', doc='', effect='( a b -- flag )'),
    PrimitiveEntry('>', 'w_gt', doc='', effect='( a b -- flag )'),
    PrimitiveEntry('0=', 'w_0eq', doc='', effect='( n -- flag )'),
    PrimitiveEntry('int?', 'w_int_q', doc='( x -- flag ) 1 if x is a portable signed-64-bit int'),
    PrimitiveEntry('str?', 'w_str_q', doc='( x -- flag ) 1 if x is a string'),
    PrimitiveEntry('list?', 'w_list_q', doc='( x -- flag ) 1 if x is a list'),
    PrimitiveEntry('quote?', 'w_quote_q', doc='( x -- flag ) 1 if x is a quotation'),
    PrimitiveEntry('xt?', 'w_xt_q', doc='( x -- flag ) 1 if x is an execution token'),
    PrimitiveEntry('s=', 'w_s_eq', doc='( a b -- flag ) typed string equality'),
    PrimitiveEntry('s<', 'w_s_lt', doc='( a b -- flag ) typed string less-than'),
    PrimitiveEntry('to-int', 'w_to_int', doc='( x -- n ) parse a portable signed-64-bit int'),
    PrimitiveEntry('to-str', 'w_to_str', doc='( x -- s ) convert to string'),
    PrimitiveEntry('call', 'w_call', doc='( ..a q -- ..b ) execute quotation (q: ..a -- ..b)'),
    PrimitiveEntry('execute', 'w_execute', doc='( ..a xt -- ..b ) execute xt'),
    PrimitiveEntry("'", 'w_tick', doc='( -- xt ) parse next name; push xt'),
    PrimitiveEntry('defer', 'w_defer', doc='( -- ) parse next name; define deferred word'),
    PrimitiveEntry('is', 'w_is', doc='( xt -- ) parse deferred name; set it'),
    PrimitiveEntry('defer@', 'w_defer_fetch', doc='( dw -- xt|0 ) get deferred xt'),
    PrimitiveEntry('defer!', 'w_defer_store', doc='( xt dw -- ) set deferred xt'),
    PrimitiveEntry('xt-name', 'w_xt_name', doc='( xt -- s ) name of execution token'),
    PrimitiveEntry('xt-kind', 'w_xt_kind', doc='( xt -- s ) kind string for xt (primitive|colon|quote|...)'),
    PrimitiveEntry('xt-effect', 'w_xt_effect', doc='( xt -- s ) stack-effect string for xt'),
    PrimitiveEntry('stackcheck!', 'w_stackcheck_store', doc='( n -- ) set dev stack effect checking (0 off, 1 warn, 2 error)'),
    PrimitiveEntry('stackcheck@', 'w_stackcheck_fetch', doc='( -- n ) current stackcheck mode (0/1/2)'),
    PrimitiveEntry('infer-effect', 'w_infer_effect', doc='( xt -- s|0 ) infer a closed stack effect for straight-line code'),
    PrimitiveEntry('check-effect', 'w_check_effect', doc='( xt -- flag ) 1 if declared effect matches inferred'),
    PrimitiveEntry('xt-doc', 'w_xt_doc', doc='( xt -- s ) documentation string for xt'),
    PrimitiveEntry('xt-src', 'w_xt_src', doc='( xt -- s ) source-ish representation for xt'),
    PrimitiveEntry('xt-src-rows', 'w_xt_src_rows', doc='( xt -- rows ) structured source rows [[text kind span|0] ...]'),
    PrimitiveEntry('xt-span', 'w_xt_span', doc='( xt -- span|0 ) source span as [file line col] (or 0)'),
    PrimitiveEntry('here-span', 'w_here_span', doc='( -- span|0 ) current execution span as [file line col] (or 0)'),
    PrimitiveEntry('if', 'w_if', doc='( ..a flag qtrue qfalse -- ..b ) runtime if (qtrue/qfalse: ..a -- ..b)'),
    PrimitiveEntry('when', 'w_when', doc='( ..a flag q -- ..b ) execute q if flag!=0 (q: ..a -- ..b)'),
    PrimitiveEntry('while', 'w_while', doc='( ..a qcond qbody -- ..b ) loop (qcond: ..a -- ..a flag, qbody: ..a -- ..a)'),
    PrimitiveEntry('catch', 'w_catch', doc='( ..a q -- ..b ior ) execute q; on error restore entry stack and push ior'),
    PrimitiveEntry('throw', 'w_throw', doc='( ior -- ) raise error if ior != 0'),
    PrimitiveEntry('last-error', 'w_last_error', doc='( -- s ) formatted last error string'),
    PrimitiveEntry('error', 'w_error', doc='( "msg" -- ) raise a VM error'),
    PrimitiveEntry('dict-version', 'w_dict_version', doc='( -- n ) dictionary/search-order version'),
    PrimitiveEntry('last-error.', 'w_last_error_dot', doc='( -- ) print last error'),
    PrimitiveEntry('set-budget', 'w_set_budget', doc='( n -- ) set base step budget (-1 clears base)'),
    PrimitiveEntry('budget', 'w_budget', doc='( -- n depth ) inspect script budgets'),
    PrimitiveEntry('with-budget', 'w_with_budget', doc='( ..a n q -- ..b ) execute q with extra budget'),
    PrimitiveEntry('wordlist', 'w_wordlist', doc='( -- wid ) create a new wordlist'),
    PrimitiveEntry('set-current', 'w_set_current', doc='( wid -- ) set CURRENT wordlist'),
    PrimitiveEntry('get-current', 'w_get_current', doc='( -- wid ) get CURRENT wordlist'),
    PrimitiveEntry('set-order', 'w_set_order', doc='( wid_n ... wid_1 n -- ) set search order'),
    PrimitiveEntry('get-order', 'w_get_order', doc='( -- wid_n ... wid_1 n ) get search order'),
    PrimitiveEntry('only', 'w_only', doc='( -- ) set search order to FORTH only'),
    PrimitiveEntry('also', 'w_also', doc='( -- ) duplicate top of search order'),
    PrimitiveEntry('previous', 'w_previous', doc='( -- ) drop top of search order'),
    PrimitiveEntry('definitions', 'w_definitions', doc='( -- ) set CURRENT to top of search order'),
    PrimitiveEntry('constant', 'w_constant', doc='( x -- ) parse next name; define constant word'),
    PrimitiveEntry('variable', 'w_variable', doc='( -- ) parse next name; define variable word'),
    PrimitiveEntry('@', 'w_fetch', doc='( cell -- x ) fetch'),
    PrimitiveEntry('!', 'w_store', doc='( x cell -- ) store'),
    PrimitiveEntry('hostcall', 'w_hostcall', doc='( "name" -- ... ) call allowlisted host function'),
    PrimitiveEntry('host.api-version', 'w_host_api_version', doc='( -- s ) host API version string'),
    PrimitiveEntry('host.feature?', 'w_host_feature_q', doc='( "feat" -- flag ) 1 if host feature is available'),
    PrimitiveEntry('host.features', 'w_host_features', doc='( -- list ) list known host features'),
    PrimitiveEntry('send', 'w_send', doc='( "name" -- ) execute word by name (pairs with .name sugar)'),
    PrimitiveEntry('responds?', 'w_responds_q', doc='( "name" -- flag ) 1 if word exists'),
    PrimitiveEntry('find', 'w_find', doc='( "name" -- xt|0 ) find a word by string name (0 if missing)'),
    PrimitiveEntry('locals', 'w_locals', doc='( -- ) print current locals frame (debug)'),
    PrimitiveEntry('local@', 'w_local_fetch', doc='( -- x ) parse name; fetch local value'),
    PrimitiveEntry('local?', 'w_local_q', doc='( -- x flag ) parse name; check local'),
    PrimitiveEntry('local!', 'w_local_store', doc='( x -- ) parse name; store into locals'),
    PrimitiveEntry('unlocal', 'w_unlocal', doc='( -- ) parse name; remove from locals'),
    PrimitiveEntry('locals-clear', 'w_locals_clear', doc='( -- ) clear session locals'),
    PrimitiveEntry('see', 'w_see', doc='( -- ) parse next name; print definition'),
    PrimitiveEntry('compile', 'w_compile', doc='( xt -- xt ) compile quotation/colonword to tier-2 bytecode'),
    PrimitiveEntry('compiled?', 'w_compiled_q', doc='( xt -- flag ) 1 if xt has tier-2 bytecode'),
    PrimitiveEntry('disasm', 'w_disasm', doc='( xt -- ) disassemble compiled code (if any)'),
    PrimitiveEntry('disasm-rows', 'w_disasm_rows', doc='( xt -- rows|0 ) structured disassembly rows'),
    PrimitiveEntry('bytecode-json', 'w_bytecode_json', doc='( xt -- s ) serialize tier-2 bytecode as JSON'),
    PrimitiveEntry('bytecode-load-json', 'w_bytecode_load_json', doc='( s -- q ) parse bytecode JSON into a quotation'),
    PrimitiveEntry('map', 'w_map', doc='( -- map ) create an empty map'),
    PrimitiveEntry('map?', 'w_map_q', doc='( x -- flag ) 1 if x is a map'),
    PrimitiveEntry('m@', 'w_m_fetch', doc='( key map -- val|0 ) fetch (0 if missing)'),
    PrimitiveEntry('m?', 'w_m_has', doc='( key map -- flag ) 1 if key exists'),
    PrimitiveEntry('m!', 'w_m_store', doc='( val key map -- map ) store (mutates)'),
    PrimitiveEntry('m-del', 'w_m_del', doc='( key map -- map ) delete key (mutates)'),
    PrimitiveEntry('m-keys', 'w_m_keys', doc='( map -- keys ) sorted keys'),
    PrimitiveEntry('m-items', 'w_m_items', doc='( map -- items ) [[key val]...] sorted'),
    PrimitiveEntry('m-merge', 'w_m_merge', doc='( src dst -- dst ) merge (mutates dst)'),
    PrimitiveEntry('list', 'w_list', doc='( -- list ) create an empty list'),
    PrimitiveEntry('push', 'w_push', doc='( x list -- list ) append'),
    PrimitiveEntry('pop', 'w_pop', doc='( list -- x list ) pop last'),
    PrimitiveEntry('len', 'w_len', doc='( list -- n ) length'),
    PrimitiveEntry('nth', 'w_nth', doc='( n list -- x ) index'),
    PrimitiveEntry('set-nth', 'w_set_nth', doc='( x n list -- list ) store'),
    PrimitiveEntry('clone', 'w_clone', doc="( x -- x' ) shallow clone lists/dicts"),
    PrimitiveEntry('hook', 'w_hook', doc='( -- ) parse next name; define a hook'),
    PrimitiveEntry('hook-add', 'w_hook_add', doc='( xt -- ) parse hook name; add handler'),
    PrimitiveEntry('hook-rm', 'w_hook_remove', doc='( xt -- ) parse hook name; remove handler'),
    PrimitiveEntry('hook-clear', 'w_hook_clear', doc='( -- ) parse hook name; remove all'),
    PrimitiveEntry('hook@', 'w_hook_fetch', doc='( -- list ) parse hook name; get handlers'),
    PrimitiveEntry('hook-rows', 'w_hook_rows', doc='( -- rows ) parse hook name; get handler names + spans'),
    PrimitiveEntry('hook-detail', 'w_hook_detail', doc='( -- rows ) parse hook name; get handler names + groups + spans'),
    PrimitiveEntry('hook-groups', 'w_hook_groups', doc='( -- groups ) parse hook name; list handler groups'),
    PrimitiveEntry('hook-rm-group', 'w_hook_remove_group', doc='( group -- n ) parse hook name; remove grouped handlers'),
    PrimitiveEntry('hook-group!', 'w_hook_group_store', doc='( group|0 -- ) set default hook registration group'),
    PrimitiveEntry('hook-group@', 'w_hook_group_fetch', doc='( -- group|0 ) current default hook registration group'),
    PrimitiveEntry('hooks', 'w_hooks', doc='( -- ) list hooks'),
    PrimitiveEntry('module', 'w_module', doc='( -- ) parse name; create+enter module'),
    PrimitiveEntry('endmodule', 'w_endmodule', doc='( -- ) leave last module'),
    PrimitiveEntry('use', 'w_use', doc='( -- ) parse module; add to search order'),
    PrimitiveEntry('in', 'w_in', doc='( -- ) parse module; set CURRENT'),
    PrimitiveEntry('modules', 'w_modules', doc='( -- ) list known modules'),
    PrimitiveEntry('include', 'w_include', doc='( "path" -- ) load and eval file'),
    PrimitiveEntry('require', 'w_require', doc='( "path" -- ) load file once (absolute path)'),
    PrimitiveEntry('reload', 'w_reload', doc='( "path" -- ) force reload file'),
    PrimitiveEntry('unrequire', 'w_unrequire', doc='( "path" -- ) forget required file'),
    PrimitiveEntry('bye', 'w_bye', doc='( -- ) exit'),
)


def define_core_primitives(vm: Any, handlers: Mapping[str, Any], *, wid: int | None = None) -> None:
    """Define all core primitives listed in ``CORE_PRIMITIVE_REGISTRY``.

    ``handlers`` is normally ``locals()`` from ``install_core_words``.
    Resolve every handler before defining any primitive so a refactor typo
    fails atomically rather than partially changing a VM dictionary.
    """

    resolved: list[tuple[PrimitiveEntry, Any]] = []
    missing: list[str] = []
    for entry in CORE_PRIMITIVE_REGISTRY:
        fn = handlers.get(entry.handler_name)
        if not callable(fn):
            missing.append(f"{entry.name}->{entry.handler_name}")
            continue
        resolved.append((entry, fn))
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"missing core primitive handler(s): {joined}")
    for entry, fn in resolved:
        vm.define_primitive(entry.name, fn, doc=entry.doc, wid=wid, effect=entry.effect)


def core_primitive_names() -> tuple[str, ...]:
    """Return core primitive names in registration order."""

    return tuple(entry.name for entry in CORE_PRIMITIVE_REGISTRY)
