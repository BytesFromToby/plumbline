---
name: contractor
description: Runs the full build pipeline end-to-end — scaffold, spec, blueprint, build-til-green, independent sign-off, and how-to-run. Stops once for spec approval; everything else flows. The build-mode counterpart to walkthrough.
version: 1.0
---

## When to use this skill
When you want to take an idea to verified code in one pass, without hand-walking each stage.
Run `/contractor`, answer the architect's interview, approve the spec — then walk away while it builds, tests, and proves the result.

This is the **general contractor**: it sequences the same single-responsibility skills you'd run by hand (architect → foreman → builder → inspector), coordinating the job so you don't have to dispatch each trade yourself. It does not reimplement any of them — it calls them.

**Not for maintenance.** To keep an *already-built* project aligned to its spec, use `walkthrough`.

---

## The one gate

Build mode is all high-stakes generative work, so it keeps exactly one human gate — the one where a wrong turn is expensive and cheap to correct: **the spec.** You approve the spec before any code is planned or written. Everything downstream (blueprint, build, test, inspect, how-to-run) flows without check-ins.

That gate is non-negotiable because the spec is the spine — `architect`'s value comes from interviewing *you*, not from expanding a one-line idea. A weak spec poisons every stage after it.

---

## Setup

Identify before starting:
1. **Project root** — the folder being built in.
2. **Greenfield or existing?** — is there a `Planning/` structure and a `CLAUDE.md`? Greenfield (neither present) runs Phase 1; an existing project skips it and treats this as a new feature.
3. **Test command** and **run/demo command** — from `CLAUDE.md` if it exists (Phase 1 establishes them otherwise).

---

## Rules
- **Stop only where the framework requires it.** Two inherent human touchpoints — the architect interview and the spec-approval gate — plus the forced halts below. Nothing else asks permission.
- **Forced halts (surface and stop, never improvise around):**
  - `architect` leaves unresolved **Open Questions** — they must be answered before `foreman` runs.
  - `builder` hits a **Stuck** — blueprint contradicts spec, a destructive/irreversible action, or three failed fix attempts on a test. Report exactly where, leave the codebase in a known state, wait for input.
  - `foreman` wants to **split** a blueprint (>10 slices) — that's a scope call; surface it.
- **Spec is truth.** Carry the spec into every stage; if a stage's output contradicts it, stop.
- **Inspector runs with fresh eyes — always as a separate subagent.** The pipeline built the code; it cannot also be the one to prove it. Spawn `inspector` in a fresh session so "no stake in the outcome" stays structural. The pipeline never grades its own work.
- **Spend capability where it pays.** `builder` may run on an economy model — the blueprint's fine grain is what makes that safe (see `Builder grade:` in `CLAUDE.md`). `inspector` must spawn on a capable model: judging evidence and test fidelity is where capability pays, and it's the last line of defense — never the place to save money.
- **Build-til-green is `builder`'s per-slice test run**, not a self-graded check. `builder` runs the test command after each step and at each slice checkpoint; the suite must be green before the next slice.
- **Follow the project's Change rules** (the Quick/Full Path in `CLAUDE.md`). Don't commit unless the user asked or the project's history mode calls for it; leave changes reviewable.

---

## Execution Order

### Phase 1 — Scaffold (greenfield only)
Skip entirely if `Planning/` and `CLAUDE.md` already exist.
- Run **scaffold**: lays the convention skeleton and writes the `CLAUDE.md` contract. It will ask for the test command and run/demo command if it can't infer them — those must be real, because `inspector` depends on the run/demo command.

### Phase 2 — Spec  ⟵ THE GATE
- Run **architect**: it interviews you (sized to the work), writes `Planning/specs/[feature]_spec.md` and the decision log, and runs its size check.
- **Stop here.** Hand the user the spec path and ask them to review it. Do not proceed to Phase 3 until they approve.
- If the spec has **Open Questions**, they must be resolved (re-run architect or have the user answer) before continuing — `foreman` will refuse a spec with open questions anyway.

### Phase 3 — Blueprint
- Run **foreman** against the approved spec: produces `Planning/blueprints/[feature]_BP.md` — slices of ordered steps, with a committed test planned for every `[automated]` Done-when item.
- If foreman flags a **split** (>10 slices), surface it and let the user decide before building.

### Phase 4 — Build til green
- Run **builder** on Slice 1, then continue slice by slice through the final slice — *this is the automation the pipeline adds*: you don't re-dispatch builder per slice.
- After each slice, builder has run the test command; confirm green before the next slice.
- **On a slice flagged `[inspect]`** (schema, auth, destructive ops, cross-module seams — foreman tags these), spawn `inspector` for a mid-slice check before continuing; unflagged slices flow on green tests alone.
- **On any builder Stuck, halt** (see forced halts). Do not skip the slice, swap the approach, or retry past three attempts.
- On the final slice, builder rolls every deviation up into `output/deviations/Deviations_[feature]_[date].md`. Carry that path forward.

### Phase 5 — Independent sign-off
- **Spawn `inspector` as a separate subagent** for final feature sign-off — feature: [feature], scope: final. It reads the spec's Done-when items, runs the committed tests (driving the software where no test exists), captures evidence, stamps the blueprint, and writes `output/inspect/Inspect_[feature]_Final_[date].md`.
- If inspector reports **FAIL**, route back: run **builder in fix mode** with the inspection report — the failure items are its step list, governed by the same stuck/deviation rules — then re-spawn inspector. Do not edit criteria to make it pass.
- `[human-required]` items come back as `needs-human` — collect them for the final report; never grade them.

### Phase 6 — How to run
- Read the run/demo command from `CLAUDE.md` and tell the user exactly how to launch the thing themselves, plus the test command. This is the "see it work" close — concrete commands, not a description.

---

## Final report

When the run completes (or halts), tell the user:
- **Spec:** `Planning/specs/[feature]_spec.md`
- **Blueprint:** `Planning/blueprints/[feature]_BP.md` (with inspector's PASS/FAIL stamp)
- **Deviations:** `output/deviations/Deviations_[feature]_[date].md` ([N] logged / none)
- **Inspection:** `output/inspect/Inspect_[feature]_Final_[date].md` — [X] passed · [Y] failed · [Z] need human sign-off
- **Human sign-off items:** list them — these are yours to verify.
- **How to run it:** the run/demo command and the test command, verbatim.

If the pipeline halted early, say which phase, why, and what input it needs to resume.
