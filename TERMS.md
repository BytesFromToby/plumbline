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
- **Referencing.** A skill that depends on a term reads this file from the plugin root
  (`${CLAUDE_PLUGIN_ROOT}/TERMS.md` once packaged as a plugin). A skill that cannot load it
  should stop and report, never guess the contract.

---

## §1 — Spec tokens

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

## §2 — Blueprint tokens

Producer: **foreman** · Consumers: **builder, inspector**

Blueprint: `Planning/blueprints/[feature]_BP.md`, or part files past 10 slices (§8).

| Token | Meaning |
|---|---|
| `**Scope:**` | One-sentence slice scope — what the codebase can do once the slice is done. |
| `**Build:**` | What a step implements: exact file paths and identifiers, no guessing. |
| `**Test:**` | The runnable check for a step — the project's *real* test command (from `CLAUDE.md`). |
| `**Done When:**` | A step's observable pass condition. **Capital `When`.** Step-level — distinct from the spec's `**Done when:**` (§1). |
| `**Stuck If:**` | The condition under which a step requires human input. |
| `- [ ] Complete` | A step's checkbox. builder flips `[ ]` → `[x]`. |
| `[inspect]` | Slice-heading flag marking inspection is due (§5 for the trigger list). |
| `- [ ] **Fully inspected**` | Blueprint-level completion box. **Only inspector ticks it** (§3). |

---

## §3 — Marks written into the blueprint

| Token | Producer → Consumers | Meaning |
|---|---|---|
| `**Deviation:** [what changed and why]` | builder → inspector, foreman, walkthrough | A behavior-preserving change to *how* a step was done (§6). Logged under the step's checkbox. |
| `**Fix:** [item] — [what changed] (YYYY-MM-DD)` | builder (fix mode) → inspector | A repair logged under the affected slice. |
| `**STALE — spec changed YYYY-MM-DD**` | foreman → builder, inspector | Marks a slice whose spec basis changed on regeneration; the slice is rewritten, its prior stamp kept. |
| `✅ Inspector: PASS — YYYY-MM-DD HH:MM` | inspector → builder, foreman, inspector | Dated pass stamp on a slice or the final checkpoint. **Colon in the time** (`HH:MM`). |
| `❌ Inspector: FAIL — YYYY-MM-DD HH:MM — off spec: [criterion] — expected [x], observed [y]` | inspector → builder (fix mode) | Dated fail stamp; names the violated criterion + expected-vs-observed. A final fail appends `— see output/inspect/Inspect_[feature]_Final_[date]_[HH-MM].md`. |
| `- [x] **Fully inspected**` | inspector only | Ticked only when every `[inspect]` slice **and** the final sign-off passed. Never ticked by hand or while any item failed. |

These are the **only** writes inspector and builder make to the blueprint's structure; they record results, never change a step, Done-When, or scope.

---

## §4 — Status lines (the routing vocabulary)

Producer: each skill (last line of its report) · Consumers: **homeowner, walkthrough, the human caller**

Orchestrators route on the **exact** string. A rename here silently mis-routes a run.

| Skill | Status line | Routes to |
|---|---|---|
| architect | `READY` | proceed (foreman) |
| architect | `READY · ASSUMPTIONS: N` | proceed; assumptions non-blocking, surfaced to human |
| architect | `OPEN_QUESTIONS: N` | **halt** — architect's only blocking status |
| architect | `+ SIZE_FLAGGED` | append to any status above; never blocks |
| foreman | `BLUEPRINT_READY` | proceed (builder) |
| foreman | `BLUEPRINT_BLOCKED: <reason>` | **halt** |
| builder | `SLICE_DONE: N` | continue to next slice (no inspection due; orchestrator-internal) |
| builder | `SLICE_DONE_INSPECT: N` | run inspector on slice N before continuing |
| builder | `BUILD_COMPLETE` | proceed to final sign-off |
| builder | `STUCK: [where/why]` | **halt** — codebase left in a known state |
| builder | `FIXES_COMPLETE` | re-inspect (fix mode only) |
| inspector | `PASS` | mid-slice clear → continue |
| inspector | `PASS · needs-human: Z` | final clear; Z human-required items owed (not a halt) |
| inspector | `FAIL: N` | → builder fix mode |
| inspector | `BLOCKED: [reason]` | **halt** — a precondition is missing; **never** route to fix mode |

`FAIL` vs `BLOCKED` must never be confused: `FAIL` has findings to repair (→ fix mode); `BLOCKED` has nothing to fix (→ halt for a human).

---

## §5 — Inspection model

| Term | Definition |
|---|---|
| **Inspection level** | Set by the caller; governs only where builder *stops for inspection* mid-build. Values: `full` (stop after every slice) · `flagged` (stop only at `[inspect]` slices — **the default**) · `none` (no mid-build stops). The **final sign-off always runs**, whatever the level. |
| **`[inspect]` trigger** | A slice is flagged `[inspect]` when it touches one of: **schema · auth/security · destructive operation · cross-module seam.** (Canonical wording — use this list verbatim.) |
| **Builder checkpoint** | End of an unflagged slice: tests green → continue. |
| **Inspection due** | End of an `[inspect]` slice under `full`/`flagged`: inspector runs before code stacks on it. |
| **Deferred inspection** | An `[inspect]` slice a `none` run skipped mid-build; the final inspector sweep inspects it. **No `[inspect]` slice ships uninspected.** |
| **Final sign-off** | The terminal inspection of the whole feature against the spec's `**Done when:**` items. Always independent, always runs. |
| **Fix mode / fix loop** | A `FAIL` routes to builder **fix mode** (the failure items become the step list; builder returns `FIXES_COMPLETE` or `STUCK`). The orchestrator re-inspects with a **fresh** inspector and bounds the retry (homeowner: **3 fix⇄inspect rounds per slice**, tunable); exceed → halt. |

---

## §6 — Shared decision tests

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

## §7 — System invariants

Cross-skill guarantees the framework depends on. Each is asserted in several skills; this is its home.

- **Spec is truth.** architect writes it; builder checks its work against it; inspector verifies the running software against it. Where code and spec disagree, fix one deliberately — no skill silently builds the wrong thing.
- **No read-ahead.** builder reads only its assigned slice (and the part file holding it), never later slices/parts. This invariant is what makes forward constraints sound.
- **Forward constraint.** A cross-slice (or cross-part) dependency foreman writes into the *earlier* step's `**Build:**` text, precisely because builder never reads ahead.
- **Committed test.** A test, kept beside the code, that *encodes* an `[automated]` Done-when item. foreman plans one per `[automated]` item; builder writes it; inspector runs it; surveyor checks it exists. An improvised check is not a committed test.
- **Fresh eyes / structural independence.** inspector verifies only from artifacts (spec, blueprint, run/demo command, running software), never from the build conversation — ideally a separate subagent. Orchestrators spawn inspector fresh; builder never grades its own work.
- **Convention-coupled, not call-coupled.** Single-responsibility skills never call each other; they share file contracts and are sequenced by data dependency. Only the orchestrators (homeowner, walkthrough) invoke skills, and only to sequence — they reimplement nothing.
- **No stage does the next one's job.** inspector can't edit the spec or a criterion to pass; builder can't invent requirements; surveyor and inspector never fix code.
- **Size flag.** A spec trips the flag past **6 features**, **~500 lines**, or any single feature **~150 lines** (tunable defaults). architect flags but **never splits**; restructure is a human decision. The flag never blocks a build.

---

## §8 — Paths & naming

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

| Class | Identified by | Has `**Done when:**`? |
|---|---|---|
| **Feature spec** | `**Done when:**` items | yes — checked for drift and test backing |
| **Reference doc** | lives in `Planning/reference/` | no — definitional; check only that its terms still match code/specs |
| **Architecture doc** | `docs/architecture.md` | no — check only that the modules it names still exist |

---

## §10 — Contract & lifecycle terms

| Term | Definition |
|---|---|
| `CLAUDE.md` | The per-project contract scaffold writes and every skill reads: identity, stack, commands, change rules, folder map, Plumbline version stamp. |
| `[pending — architect]` | Placeholder scaffold leaves in `CLAUDE.md` for **Stack** and **Commands**. **architect** fills them when it writes the first spec — the one time architect writes to the contract. walkthrough must route an unfilled placeholder to Recommendations, **never fill it**. |
| **Quick Path / Full Path** | The change-rules in `CLAUDE.md`. Quick Path: no files added/removed/renamed (new *test* files excepted), no schema/core-logic change → edit, test, commit. Full Path: everything else → spec, code, test, inspect, decision doc, commit. |
| **Build mode / Maintain mode** | Build = idea → verified code (scaffold → architect → foreman → builder → inspector). Maintain = keep built code honest (surveyor, inspector, walkthrough). |
| **Orchestrator** | A skill that sequences others without reimplementing them: **homeowner** (build), **walkthrough** (maintain). |
