# Reliance lineage receipt page: audience envelope, freshness, and recall boundary interface spec

## Purpose

This receipt tells the next operator exactly what was published, to whom, with what safe sentence, and what later invalidated or superseded it.

## Required fields

- reliance charter id
- source certification id
- source proof ids
- audience class
- packet variant
- safe published sentence
- explicit exclusions carried
- freshness window carried
- delivery channel
- acknowledgement class reached
- live-link or snapshot class
- superseding charter if any
- recall boundary
- blocked stronger sentence

## Receipt footer sentence

Use:

> On [time], [safe sentence] was published to [audience] via [channel] as a [packet class]. It remained safe through [freshness / trigger] and was [superseded/recalled/retired] by [event]. The blocked stronger sentence stayed: [sentence].

## Hard rules

- the receipt must survive even after the packet is superseded
- a recalled packet still needs lineage, not silent disappearance
- the receipt must preserve whether recipients only received, acknowledged, or accepted custody
- the receipt must preserve whether the packet was live-linked or detached snapshot
- the receipt must tell the next operator what weaker sentence old packet holders may still believe unless recall is confirmed
