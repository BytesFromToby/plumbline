<!-- GENERATED from TERMS.md by `python tools/audit.py --write-terms` -- do not edit.
     This is walkthrough's slice of the Plumbline contract: the preamble plus every
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

## §3 — Marks written into the blueprint
<!-- audience: foreman, builder, inspector, walkthrough -->

| Token | Producer → Consumers | Meaning |
|---|---|---|
| `**Deviation:** [what changed and why]` | builder → inspector, foreman, walkthrough | A behavior-preserving change to *how* a step was done (§6). Logged under the step's checkbox. |
| `**Fix:** [item] — [what changed] (YYYY-MM-DD)` | builder (fix mode) → inspector | A repair logged under the affected slice. |
| `**STALE — spec changed YYYY-MM-DD**` | foreman → builder, inspector | Marks a slice whose spec basis changed on regeneration; the slice is rewritten, its prior stamp kept. |
| `✅ Inspector: PASS — YYYY-MM-DD HH:MM` | inspector → builder, foreman, inspector | Dated pass stamp on a slice or the final checkpoint. **Colon in the time** (`HH:MM`). |
| `❌ Inspector: FAIL — YYYY-MM-DD HH:MM — off spec: [criterion] — expected [x], observed [y]` | inspector → builder (fix mode) | Dated fail stamp; names the violated criterion + expected-vs-observed. A final fail appends `— see Plumbline/inspect/Inspect_[feature]_Final_[date]_[HH-MM].md`. |
| `- [x] **Fully inspected**` | inspector only | Ticked only when every `[inspect]` slice **and** the final sign-off passed. Never ticked by hand or while any item failed. |

These are the **only** writes inspector and builder make to the blueprint's structure; they record results, never change a step, Done-When, or scope.

---

## §4 — Status lines (the routing vocabulary)
<!-- audience: architect, foreman, builder, inspector, homeowner, walkthrough -->

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

## §7 — System invariants
<!-- audience: homeowner, walkthrough -->

Cross-skill guarantees the framework depends on. Each worker skill asserts its own invariants
in its own body; this registry is the auditor's oracle and the **orchestrators'** map of the
boundaries they sequence across — only they load it at runtime.

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
<!-- audience: scaffold, architect, foreman, builder, inspector, surveyor, homeowner, walkthrough -->

Every skill must agree byte-for-byte. `[feature]` is the feature's lowercase slug, identical across its spec, blueprint, and output files. Dates are `YYYY-MM-DD`.

**The tree splits in two.** `Planning/` holds **human intent** — the specs and reference the build is judged against. `Plumbline/` holds **everything the workflow generates** — blueprints, decision logs, and every skill's reports. Code lives wherever the stack puts it, outside both.

| Path / pattern | Owner | Notes |
|---|---|---|
| `Planning/specs/[feature]_spec.md` | architect | source of truth |
| `Planning/reference/` | architect | shared definitions specs cite (data models, constants) |
| `Plumbline/blueprints/[feature]_BP.md` | foreman | single-file blueprint |
| `Plumbline/blueprints/[feature]_BP_p-1.md`, `_p-2.md`, … | foreman | part files past 10 slices; **slice numbering is continuous across parts** (p-2 opens at Slice 11) |
| `Plumbline/decisions/[feature]_YYYY-MM-DD.md` | architect | decision log (append-only) |
| `Plumbline/architecture.md` | manual | as-built map; written only once modules need one |
| `Plumbline/inspect/Inspect_[feature]_Final_[YYYY-MM-DD]_[HH-MM].md` | inspector | final report; **`HH-MM` uses a hyphen** (filenames forbid `:`); the time suffix stops a re-inspection overwriting the failed one |
| `Plumbline/deviations/Deviations_[feature]_[YYYY-MM-DD]_[HH-MM].md` | builder | deviation rollup; written even when none ("None.") |
| `Plumbline/surveys/Survey_[YYYY-MM-DD]_[HH-MM].md` (or `Survey_[feature]_[YYYY-MM-DD]_[HH-MM].md`) | surveyor | dated drift report |
| `Plumbline/walkthrough/WalkthroughLog_[YYYY-MM-DD]_[HH-MM].md`, `Recommendations_[YYYY-MM-DD]_[HH-MM].md` | walkthrough | |
| `Plumbline/homeowner/HomeownerLog_[YYYY-MM-DD]_[HH-MM].md` | homeowner | run log |
| `CLAUDE.md` | scaffold (writes) / architect (fills) | the project contract (§9) |

**Every generated report under `Plumbline/` carries `_YYYY-MM-DD_HH-MM`** (hyphens) — so reruns sort by time and never overwrite a prior run. Blueprint **stamps** use `HH:MM` (colon — they are text, not filenames). The append-only decision log stays date-only (`[feature]_YYYY-MM-DD.md`).

---

## §10 — Contract & lifecycle terms
<!-- audience: scaffold, architect, inspector, homeowner, walkthrough -->

| Term | Definition |
|---|---|
| `CLAUDE.md` | The per-project contract scaffold writes and every skill reads: identity, stack, commands, change rules, folder map, Plumbline version stamp. |
| `[pending — architect]` | Placeholder scaffold leaves in `CLAUDE.md` for **Stack** and **Commands**. **architect** fills them when it writes the first spec — the one time architect writes to the contract. walkthrough must route an unfilled placeholder to Recommendations, **never fill it**. |
| `UI evidence tool` | A `CLAUDE.md` **Commands** line — `- UI evidence tool: <tool>` (e.g. `playwright (python)`) — that **architect** adds when the spec calls for a browser UI and **inspector** reads to choose its capture engine. Match the key exactly: inspector greps the literal `UI evidence tool` (no hyphen). |
| `History` mode | A `CLAUDE.md` field — `git` (**default**) or `none`. `git`: scaffold inits git, every change ends in a commit, history is the git log. `none`: no git; history is the dated artifact trail (`Plumbline/` — decisions, reports, and blueprint stamps) — a full audit trail, no per-file diffs, no manual changelog. scaffold sets it; the Change-rules terminal step and homeowner's closing file-list both branch on it. |
| **Quick Path / Full Path** | The change-rules in `CLAUDE.md`. Quick Path: no files added/removed/renamed (new *test* files excepted), no schema/core-logic change → edit, test, commit. Full Path: everything else → spec, code, test, inspect, decision doc, commit. |
| **Build mode / Maintain mode** | Build = idea → verified code (scaffold → architect → foreman → builder → inspector). Maintain = keep built code honest (surveyor, inspector, walkthrough). |
| **Orchestrator** | A skill that sequences others without reimplementing them: **homeowner** (build), **walkthrough** (maintain). |
