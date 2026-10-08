# Modules and hooks (rev6)

Micromax is intended to be a plugin/config/macro system.

This doc spells out the *minimum* namespace + extensibility conventions that keep that sane.

## Modules (named wordlists)

Micromax already has wordlists and an explicit search order.
Rev5 layers a friendly module API on top.

### Create a module

```forth
module foo

: greet ( -- ) "hi" . ;

endmodule
```

Behavior:
- creates a new wordlist named `foo`
- temporarily places it at the front of the search order
- sets `CURRENT` so new definitions go into `foo`
- `endmodule` restores the previous state

### Use a module

```forth
use foo
greet
```

### Set the current module

```forth
in foo
: more ( -- ) "more" . ;
```

### List modules

```forth
modules
```

## Hooks (multi-handler callbacks)

Hooks are small extension points that run an ordered list of callbacks.
This is inspired by editor hook systems such as Emacs.

### Define a hook

```forth
hook on-save
```

### Add handlers

```forth
: h1 ( -- ) "one" . ;
: h2 ( -- ) "two" . ;

' h1 hook-add on-save
' h2 hook-add on-save
```

### Run the hook

```forth
on-save
```

### Important: handler stack isolation

Hook handlers are treated as **notifications**.

When a hook runs multiple handlers (and hook inspection now reports the handler count explicitly):
- each handler runs with the **same initial data stack**
- any stack effects are **discarded between handlers**

This prevents accidental coupling between handlers based on execution order.

### Introspection

```forth
hooks
hook@ on-save        \ returns a list of execution tokens
hook-rows on-save    \ [[handler-name span] ...]
hook-detail on-save  \ [[handler-name group|0 span|0] ...]
```

### Grouped handlers (reload-friendly)

```forth
"plugin:fmt" hook-group!
' h1 hook-add on-save
0 hook-group!

hook-groups on-save
"plugin:fmt" hook-rm-group on-save
```

A host/plugin loader can also set the default hook group automatically while
loading a plugin, so reload/unload can remove all of that plugin's hook
registrations without resetting the whole VM.

## Guideline: plugin isolation

When we get to a plugin loader, we should default to:

1) create a per-plugin module
2) load plugin source with that module as `CURRENT`
3) only `use` plugin modules where explicitly requested
