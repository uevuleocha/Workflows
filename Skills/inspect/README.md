# Inspect — Adoption Guide

The general read, understand, verify, or audit workflow. Bare or neutral
Inspect requests use Mode C to read a target and establish working context
without grading it. Mode A verifies recently applied code; Mode B performs an
explicitly requested audit. Inspect also serves as the bounded runtime-evidence
reviewer for `ecosystem-calgo-greenlight`. It does not edit unless separately
authorized.

## Related skills

- `debug` — the escalation for full bug diagnosis; inspect stays a
  single-pass check.
- `green-light` — approval protocol if the inspection's suggested corrections
  should then be applied.
- `ecosystem-calgo-greenlight` — calls Inspect's bounded, read-only Ecosystem
  runtime-evidence profile after builds and permitted parameter gates.
