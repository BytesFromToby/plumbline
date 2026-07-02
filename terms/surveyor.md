<!-- GENERATED from TERMS.md by `python tools/audit.py --write-terms` -- do not edit.
     This is surveyor's slice of the Plumbline contract: the preamble plus every
     section whose audience line names it. TERMS.md is the source of truth. -->

# Plumbline TERMS — the cross-skill contract

**Version:** v1.0 (tracks the skill suite version)

Single source of truth for every term, token, and status string shared by more than one
Plumbline skill. One skill **produces** a token; one or more others **consume** it. When
producer and consumer disagree on the exact string, the chain breaks silently — this file
keeps them identical.

**Rules of use**
- **Tokens are literal.** Reproduce them verbatim — exact case, punctuation, spacing.
  `**Done when:**` (spec) and `**Done When:**` (blueprint step) are *different* tokens.
- **This file wins.** Where a skill's prose describes a token differently than defined here,
  this file is canonical and the skill is the thing to fix.
- **Cross-skill only.** A term used inside one skill stays in that skill. This is a registry to
  match against, not a narrative — see the README for what each skill *does*.
- **Referencing.** At runtime each skill reads its **generated slice** of this contract —
  `terms/<skill>.md` under the plugin root, holding only the sections whose
  `<!-- audience: ... -->` line names that skill. Regenerate the slices with
  `python tools/audit.py --write-terms`; the audit fails while they are stale, so a slice
  can never silently drift from this file. A skill that cannot load its slice must stop
  and report, never guess the contract.

---

## §1 — Spec tokens
<!-- audience: architect, foreman, builder, inspector, surveyor, homeowner -->

Producer: **architect** · Consumers: **foreman, builder, inspector, surveyor, homeowner**

The spec (`Planning/specs/[feature]_spec.md`) is the source of truth. These strings are read literally.

| Token | Meaning |
|---|---|
| `**Done when:**` | Heading above a feature's acceptance criteria. **Lowercase `when`.** Distinct from the blueprint step's `**Done When:**` (§2). |
| `[automated]` | Tag on a Done-when item: a committed test judges it. Means *a test exists*, not an improvised check. |
| `[human-required]` | Tag on a Done-when item: only a person can judge it. inspector captures evidence but never grades it. |
| `## Scope` | Section with a `Does:` line and at least one hard `Does NOT:` line. |
| `## Feature: [Name]` | One block per feature; every block must carry a `**Done when:**` section. |
| `## Assumptions` | Low-surprise, cheap-to-change defaults made where a brief was silent. **Non-blocking.** Omitted when none. |
| `## Open Questions` | A genuine fork that could not be safely defaulted. **Blocking** (§6). Omitted when none. |

Every Done-when line carries **exactly one** tag — `[automated]` or `[human-required]`. No untagged criteria.

---

## §6 — Shared decision tests
<!-- audience: architect, foreman, builder, inspector, surveyor, homeowner, walkthrough -->

Decision rules more than one skill applies. The **test** is the contract — keep it identical everywhere.

- **Assumption vs Open Question** — architect sorts; homeowner re-checks.
  Test: *if this default turns out wrong, is it a cheap edit or a partial rebuild / architecture fork?*
  Cheap & low-surprise → **Assumption** (`## Assumptions`, non-blocking). Rebuild or fork → **Open Question** (`## Open Questions`, blocks). **When unsure, treat it as an Open Question.**

- **Deviation vs Stuck** — builder applies; inspector/walkthrough read the trail.
  Test: did the change alter only *how* a step was written (name, location, tactic), or *what* it does (behavior, interface, signature, approach)?
  How → **Deviation** (log it, keep going). What → **Stuck** (stop and report). The step's Done-When is the arbiter: if it still passes the same way, it was a deviation.

- **Test fidelity** — inspector judges; surveyor's static counterpart; foreman plans for it.
  Test: *would this test fail if the criterion were violated?* No → the criterion is **unproven**, however green the run — a finding routed to builder, never a pass. Recorded `fidelity: ok` or `fidelity: weak — [reason]`.

---

## §8 — Paths & naming
<!-- audience: scaffold, architect, foreman, builder, inspector, surveyor, homeowner, walkthrough -->

Every skill must agree byte-for-byte. `[feature]` is the feature's lowercase slug, identical across its spec, blueprint, and output files. Dates are `YYYY-MM-DD`.

| Path / pattern | Owner | Notes |
|---|---|---|
| `Planning/specs/[feature]_spec.md` | architect | source of truth |
| `Planning/reference/` | architect | shared definitions specs cite (data models, constants) |
| `Planning/blueprints/[feature]_BP.md` | foreman | single-file blueprint |
| `Planning/blueprints/[feature]_BP_p-1.md`, `_p-2.md`, … | foreman | part files past 10 slices; **slice numbering is continuous across parts** (p-2 opens at Slice 11) |
| `docs/decisions/[feature]_YYYY-MM-DD.md` | architect | decision log (append-only) |
| `docs/architecture.md` | manual | as-built map; written only once modules need one |
| `output/inspect/Inspect_[feature]_Final_[YYYY-MM-DD]_[HH-MM].md` | inspector | final report; **`HH-MM` uses a hyphen** (filenames forbid `:`); the time suffix stops a re-inspection overwriting the failed one |
| `output/deviations/Deviations_[feature]_[YYYY-MM-DD]_[HH-MM].md` | builder | deviation rollup; written even when none ("None.") |
| `output/surveys/Survey_[YYYY-MM-DD]_[HH-MM].md` (or `Survey_[feature]_[YYYY-MM-DD]_[HH-MM].md`) | surveyor | dated drift report |
| `output/walkthrough/WalkthroughLog_[YYYY-MM-DD]_[HH-MM].md`, `Recommendations_[YYYY-MM-DD]_[HH-MM].md` | walkthrough | |
| `output/homeowner/HomeownerLog_[YYYY-MM-DD]_[HH-MM].md` | homeowner | run log |
| `CLAUDE.md` | scaffold (writes) / architect (fills) | the project contract (§9) |

**Every generated file under `output/` carries `_YYYY-MM-DD_HH-MM`** (hyphens) — so reruns sort by time and never overwrite a prior run. Blueprint **stamps** use `HH:MM` (colon — they are text, not filenames). The append-only decision log stays date-only (`[feature]_YYYY-MM-DD.md`).

---

## §9 — Document classes (surveyor)
<!-- audience: surveyor -->

| Class | Identified by | Has `**Done when:**`? |
|---|---|---|
| **Feature spec** | `**Done when:**` items | yes — checked for drift and test backing |
| **Reference doc** | lives in `Planning/reference/` | no — definitional; check only that its terms still match code/specs |
| **Architecture doc** | `docs/architecture.md` | no — check only that the modules it names still exist |
