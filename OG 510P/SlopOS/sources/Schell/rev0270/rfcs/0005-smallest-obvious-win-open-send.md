# RFC 0005: Smallest obvious win — exact-artifact open/send with review and receipt

## Status

Proposed.

## Purpose

Name the smallest end-to-end Schell interaction that should feel obviously better than bash for a SlopOS-style reviewed action.

## Candidate interaction

**Select one exact artifact, request one exact open/send action, review it, approve it once, and receive a durable receipt.**

Examples:

- open one exact document with a chosen viewer through a mediated portal;
- send one exact artifact to a share / print / handoff destination;
- grant one-shot access to one exact object for one launch.

## Why this is the right first proving action

- It is visible and easy to understand.
- It is portal-shaped and authority-bearing.
- It has a clear denial story.
- It benefits from exact object identity.
- It benefits from receipts and replay.
- bash is weak here because ordinary shell flows usually rely on pathnames, ambient associations, or broad process launch.

## Required operator path

1. identify the exact artifact;
2. preview the proposed action;
3. show the narrow authority request and expected expiry;
4. approve or deny;
5. execute through an explicit mediation path;
6. leave behind a receipt block with replay / explain affordances.

## Non-goals

- no full scripting language proof;
- no full pipeline model proof;
- no host-language embedding;
- no terminal lock-in as correctness requirement.

## Admit when proven

This RFC should only be promoted after there is a tested prototype or crisp mock that shows ordinary users understand:

- what object is being acted upon,
- what authority is being requested,
- what happened,
- and how to inspect or repeat it safely.
