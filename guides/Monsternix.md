# Monsternix

## A system configuration that remembers how to be changed

Monsternix is carried here as one [configuration.nix](../configuration.nix). Its subject is larger than a collection of NixOS options: how a person and successive human or language-model collaborators can change a computer without losing the distinction between a request, a proposal, a measured result and an accepted system.

The opening constitution is worth reading as prose. It treats continuity and clarity as practical systems requirements. A later worker should inherit the reasons for a boundary, the failures already encountered and the questions still open, rather than only inheriting code.

## Where to start

The source has three major marked regions:

1. **Constitution and office protocol** (`00.00`): read the opening letter, the first loop, the epistemic protocol and the constitutional laws. These explain what the artifact is trying to preserve when ownership of the work changes hands.
2. **Portable Foundation system and adapter boundary** (`10.00`): read this to distinguish the portable reference module from a particular bootable machine. The supplied Foundation is not a complete physical-system configuration until an explicit machine adapter supplies what is missing.
3. **Source-carried predecessor-supervised transaction and evidence protocol** (`90.00`): this is the operational machinery behind checking, observing and accepting an exact candidate. Approach it after understanding the earlier distinction between generated text and an accepted system.

These region names and identifiers are searchable in the [original file](../configuration.nix). The suffix is not the whole story: the artifact has a directly executable Bash entrance as well as its Nix interpretation. Treat it as software, not as an inert snippet to paste casually into another configuration.

## What gives the design its character

The proposed editing loop passes complete source, not disconnected fragments. The accepted supervisor checks a candidate as data; the human reviews bounded evidence; promotion is supposed to refer to the exact tested closure rather than rebuilding whatever mutable text happens to be present later.

The constitution names six kinds of statement that should not blur together: the operator’s present request, inherited intent, measured fact, inference, proposal and unknown. This is a useful way to read the entire artifact. A confident explanatory paragraph and an observation of a particular running system do different jobs.

The exit matters as much as the entrance. The design includes ejection to ordinary NixOS and a separate return to the portable Foundation core. Those are claims about the operator retaining a way out, not merely about making onboarding convenient. They remain implementation claims to test against exact source and an appropriate machine.

## Portable in which sense?

The source explicitly treats portability as several levels: readable text, an executable entrance, Nix evaluation and a real NixOS transaction. Passing one does not prove the next. The direct entrance describes Linux, a trusted Bash 4-or-newer interpreter, compatible sed and the relevant launcher behavior; successful reading in a browser says nothing about boot or activation on a particular host.

Likewise, source-carried or externally recorded evidence is not automatically local measurement or present permission. The source’s historical dialogues and commands explain a design; they do not authorize changes to the reader’s computer.

## Optional and experimental machinery

The file also carries mechanisms that are intentionally source-visible without being universally active. The constitution calls some of this *semipermanent flavor*: components with named activation gates, evidence surfaces and ejection behavior.

The supplied source includes experimental vault and encrypted keystroke-journal facilities. Their presence must not be mistaken for a recommendation to enable them or consent to capture input. Read their gates, privacy consequences and experimental qualifications in the source before any use. This introduction does not activate them.

## Current W4R3Z copy

The [3 October 2026 update receipt](../updates/2026-10-03.json) identifies the supplied bytes. That intake performed bounded source review, not NixOS activation. This editorial pass examined the constitution, marked organization, adapter distinction and selected source declarations. It did not build a closure, test ejection, approve a machine adapter or make the source’s qualification labels into an independent W4R3Z certification.

h0p3 intends continued development. The portable file remains the current entry point; future updates should keep source identity, operator-facing explanation and measured checks distinct. Existing source notices and component terms remain applicable.

*Reading and orientation by Lumen, 8 October 2026.*

[Living software](../LIVING-SOFTWARE.md) · [Catalog](../CATALOG.md) · [W4R3Z](../README.md)
