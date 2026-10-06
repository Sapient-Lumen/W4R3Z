# RFC-0147: Printing portal

Status: **Draft**  
Last updated: 2026-02-24

## Problem

Printing is often implemented with ambient spooler/device access, enabling data exfiltration and messy, non-auditable policy.

## Proposal

Add an optional **Printing portal** lane modeled as:

1) Prepare: broker mediates settings/destination selection → `ui.print.grant`
2) Submit: app submits payload (or artifact digest) under the grant
3) Receipt: `ui.print.receipt` records what happened

## Policy

- deny by default for hardened profiles
- allow “export to PDF” separately from “physical printer”
- integrate with redaction transforms for sensitive documents

## References

- XDG Print portal: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Print.html
