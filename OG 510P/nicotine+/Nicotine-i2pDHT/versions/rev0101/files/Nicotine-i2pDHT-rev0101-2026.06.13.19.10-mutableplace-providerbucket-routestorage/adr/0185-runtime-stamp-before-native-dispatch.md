# ADR 0185 — Runtime stamp before native dispatch

Accepted for rev0083.

A native artifact that passed parity and ABI checks may still drift at runtime. Object digest, source digest, compiler flags, fallback seal, and selection bits must be carried in a previous-linked runtime stamp before dispatch.
