# rev0288 cube deep audit

## Finding

The cube has become strong at preventing local artifacts from laundering source truth. The next failure mode is not premature acceptance inside the packet chain; it is losing momentum after a bounded dispatch has already named a due/recheck date.

## Audit result

The post-readout action artifact had a due/recheck date, but the router treated the dispatch as a permanent terminal stop. That avoided false closure, but it also let the owner-held action lane become unobservable. A due date that does not drive any executable gate is a hidden backlog item.

## Refactor

`rev0288` adds a post-readout recheck recorder and guard. The router now has three states after dispatch:

1. before due date: wait and perform only the owner-held action outside the archive;
2. on or after due date: record a bounded recheck;
3. after recheck: either stop with no new owner context or route actual new context through `owner-field-next CSV=...`.

## Waste removed

This replaces a likely future memo with a dated, hash-checked command. It also prevents the archive from using a recheck artifact as the owner packet itself. The cube remains large, but this change reduces dependence on operator memory at one of the last action seams.
