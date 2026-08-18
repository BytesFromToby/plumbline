# Examples

## `mdtoc` — a real Homeowner run

`mdtoc/` is a complete, **signed-off** project that Plumbline's `homeowner` orchestrator built end-to-end from a one-line brief, unattended — `scaffold → architect → foreman → builder → inspector`. It's kept here as proof the framework runs on real work, not just on paper.

**The brief:** *a CLI that generates a table of contents from a Markdown file's headings.*

**Worth opening, to see the audit trail the process leaves:**
- `mdtoc/Planning/specs/mdtoc_spec.md` — the spec `architect` expanded from the brief: 16 observable, tagged `[automated]` Done-when criteria, plus a `## Assumptions` list of 9 low-surprise defaults it surfaced instead of silently guessing.
- `mdtoc/Plumbline/blueprints/mdtoc_BP.md` — `foreman`'s blueprint, with the `builder`'s steps checked off and the `inspector`'s **`✅ Inspector: PASS` stamps** — Slice 5 (`--insert`, flagged `[inspect]` as a destructive op) inspected mid-build, the final sign-off stamped, and `Fully inspected` ticked.
- `mdtoc/Plumbline/inspect/` — the inspector's final evidence report (per-criterion pass + test-fidelity judgment).
- `mdtoc/Plumbline/deviations/` — the deviation rollup (none this run).
- `mdtoc/mdtoc/` + `mdtoc/tests/` — the result: a working tool, **19 passing tests**.

Built 2026-06-28 under Plumbline v1.0. (This run also surfaced — and led to fixing — a real gap: in git mode the autonomous pipeline wasn't committing the build after scaffold. `homeowner` now commits the signed-off result.)
