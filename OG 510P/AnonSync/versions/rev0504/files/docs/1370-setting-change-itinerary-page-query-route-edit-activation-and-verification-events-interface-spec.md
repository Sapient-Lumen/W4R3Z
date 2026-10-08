# Setting-change itinerary page — query, route, edit, activation, and verification events

## Purpose

This page keeps settings truth chronological.
It exists so the product can explain how an operator went from a vague query to a concrete route, an actual mutation, an activation event, and a verification result.

## Required event classes

### 1) Query / alias resolution

Examples:

- operator searched `priority`
- operator searched `LAN only`
- operator clicked a warning card
- product resolved aliases to one canonical setting object

### 2) Route selection

Examples:

- global desktop route chosen
- selected share-specific route instead of global default
- mobile share details chosen
- config-file route chosen because runtime surface was witness-only
- service route chosen instead of user-session route

### 3) Edit commit

Examples:

- toggle changed
- numeric value changed
- `sync.conf` written
- share override created
- share override detached back to inheritance

### 4) Activation event

Examples:

- active immediately
- active after rescan
- active after app restart
- active after service restart
- active on next startup / clean world

### 5) Verification event

Examples:

- same-surface confirmation
- route-specific proof
- behavior witness
- proof still incomplete because stronger witness missing

## Timeline output rules

- Every event must say whether it changed **identity**, **route**, **scope**, **authority**, or **activation** truth.
- Every event must say whether the stronger sentence widened, narrowed, or remained blocked.
- Every route-selection event must say what false-friend route was rejected.
- Every edit event must say whether it changed a default, an override, or only a startup-owned future state.

## Final itinerary sentence

The page must end with one summary sentence in this shape:

> `Current settings answer is the result of <latest governing event>; stronger sentence <...> remains blocked because <...>.`
