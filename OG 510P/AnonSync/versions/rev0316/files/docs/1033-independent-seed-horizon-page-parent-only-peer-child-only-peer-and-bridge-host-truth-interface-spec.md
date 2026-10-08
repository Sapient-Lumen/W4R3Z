# Independent seed horizon page — parent-only peer, child-only peer, and bridge-host truth

## Purpose

Make the actual seeding graph visible when overlapping subjects create different audience horizons.

This page exists to answer:

- `who can actually serve bytes to whom right now?`
- `which paths are direct and which require a bridge?`
- `what claim about availability is safe today?`

## Required sections

### 1. Horizon header

Must show:

- subject pair / overlap id
- evaluated time
- proof freshness
- current bridge requirement (`none`, `optional`, `required`, `unknown`)

### 2. Peer-class graph

Must show at minimum nodes for:

- parent-only peers
- child-only peers
- both-subject peers

Edges must distinguish:

- direct seed path
- carried path through bridge
- no path
- path unknown / degraded

### 3. Availability claims

Must show separately:

- child availability to child-only peers
- child availability to parent-only peers
- parent availability to child-only peers
- whether any claim depends on one specific bridge host or one bridge cohort

### 4. Failure consequences

Must show:

- what breaks if all bridge hosts disappear
- what survives if parent-only peers remain online
- what survives if child-only peers remain online
- which stale beliefs must be invalidated immediately

### 5. Claim ceiling

Must show:

- strongest safe sentence
- blocked stronger sentence
- confidence level
