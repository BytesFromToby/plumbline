# Plumbline — a spec-driven workflow of AI-agent skills

*A plumb line is the builder's reference of truth — the vertical everything is checked against. Here, the spec is that line.*

## Description

A small set of skills that take a feature from idea to *verified, working* code through five single-responsibility stages. Each stage is run by an AI agent. The stages never call each other — they coordinate through files and folders, so any stage can run on its own, and the spec stays the single source of truth from the first interview to the final sign-off.

This repo is as much about *how it's designed* as what it does. The interesting part isn't the skills — it's the seams between them, and the choices about what each stage is and isn't allowed to do.

## Current Status

This is built for a solo developer's own projects, and it's been run end-to-end on real features — spec through signed-off code — not just designed on paper. It's deliberately strongest on *reliability* and *repeatability*; the lighter-weight path for very small features is still being tuned, and the machinery for restructuring a spec once a project gets large is specified but intentionally not yet built. It grows when a real project makes a gap hurt — not before.

---

## The lifecycle

```
scaffold ──▶ architect ──▶ foreman ──▶ builder ──▶ inspector
 (once)       (spec)       (blueprint)   (code)      (proof)
                                          ▲             │
                                          └──── fix ◀───┘
```

| Stage | Owns | Produces |
|-------|------|----------|
| **scaffold** | Bootstrapping a project (run once) | Folder conventions, a `CLAUDE.md` contract, a spec template |
| **architect** | Defining *what* to build | `Planning/specs/[feature]_spec.md` with inline acceptance criteria, a decision log |
| **foreman** | Planning *how* to build it | `Planning/blueprints/[feature]_BP.md` — slices of ordered steps |
| **builder** | Writing the code | Code + tests, executed one slice at a time, with a deviation log |
| **inspector** | Proving it works | An evidence report; a dated PASS/FAIL stamp on the blueprint |

Each stage hands off through the filesystem. The user approves between stages — the agent does the work, the human stays the judge.

---

## Principles

- **The spec is the spine.** `architect` writes it, `builder` checks its work against it, `inspector` verifies the running software against it. The blueprint in the middle is a disposable plan; the spec is truth at both ends *and* in the middle.
- **Evidence over assertion.** "Done" means *shown* to work. `inspector` runs the software and captures output — a bare "PASS" is not evidence.
- **Independence is structural, not promised.** `inspector` runs with fresh eyes — ideally as a separate agent that never saw the build — so "no stake in the outcome" is enforced by isolation, not by good intentions.
- **Convention-coupled, not call-coupled.** Skills share documented file contracts (the `CLAUDE.md` declarations + folder layout), never direct calls. They're sequenced by data dependency, not by a hard-wired chain.
- **Proportional ceremony.** A one-line fix doesn't get a decision doc; a schema change does. `architect` sizes its interview to the work; the **Change rules** in each project's `CLAUDE.md` give trivia a Quick Path and reserve the Full Path for features and schema.
- **Gates must earn their place.** Every stop, check, and document exists to catch a specific failure. The ones that don't get cut — this framework has been pruned as hard as it's been built.

**Design priorities, in order:** *repeatable > reliable > easy > fast.* When they conflict, the higher one wins — a reliability gain is worth a small speed cost, and consistency across runs beats either.

---

## The "Done when" contract

Acceptance criteria live *inline in the spec*, attached to each feature — not in a separate checklist that drifts. Each is observable and tagged:

```
**Done when:**
- `POST /login` with valid creds → 200 + a session cookie; bad creds → 401   `[automated]`
- the dashboard's 4 KPI cards sit above the fold at 1280px                    `[human-required]`
```

- `[automated]` — `foreman` plans a committed test that encodes it; `builder` writes that test; `inspector` runs it. "Automated" means *there is a test*, not "the agent improvised a check."
- `[human-required]` — `inspector` captures evidence (e.g. a screenshot) but never grades it; the human signs it off.

---

## How the stages stay honest

- **`builder` reads the spec, not just the blueprint.** If a step contradicts the spec, it stops rather than faithfully building the wrong thing — closing the "telephone game" between plan and intent.
- **`builder` stops cleanly when stuck.** Clear rules: don't improvise a different approach, don't retry forever, never run a destructive action on the blueprint's say-so alone, and leave the codebase in a known state when you stop.
- **Deviations are an audit trail, not a blocker.** When the build diverges from the plan in a behavior-preserving way, it's logged inline and rolled up to `output/deviations/` — visible at the end whether or not inspection runs.
- **`inspector` may stamp a result but never edit criteria.** It can record `✅ PASS — <date>` on the blueprint; it cannot touch a step, a Done-when, or the spec to make something pass.

---

## Folder conventions

| Path | Holds |
|------|-------|
| `Planning/specs/[feature]_spec.md` | Specs — the source of truth |
| `Planning/specs/archive/` | Superseded spec versions |
| `Planning/blueprints/[feature]_BP.md` | Per-feature build plans |
| `Planning/decisions/` | Decision logs |
| `Planning/reference/` | Glossary, data models — created only when a project grows large enough to need them |
| `docs/changelog/` | Changelog |
| `output/inspect/` | Inspector reports + evidence |
| `output/deviations/` | Builder deviation rollups |

Nothing empty is pre-created. Folders appear when a stage first writes to them.

---

## The CLAUDE.md contract

`scaffold` writes these declarations into each project; every skill reads them:

- **Test command** — how tests run.
- **Run/demo command** — how to launch the thing so behaviour is *visible*. `inspector` depends on this being real.
- **UI evidence tool** (web stacks only) — how `inspector` drives the UI and captures screenshots.
- **Spec/blueprint naming** — so every stage finds the same files.
- **Change rules** — the Quick Path / Full Path for any code change, and who owns the changelog and decision docs. This is doctrine every skill reads, not a skill you invoke.

---

## Supporting skills (run when useful, not every cycle)

- **`surveyor`** — a static spec-vs-code drift report. Reads and compares, never runs the software (that's `inspector`'s job). Cheap; catches divergence after a refactor, and flags `[automated]` Done-when items with no backing test.
- **`walkthrough`** — an autonomous maintenance pass over a whole project, fenced to safe (Quick-Path) changes and routing anything bigger to a reviewed recommendations list. Delegates drift detection to `surveyor`.

The order-of-operations for any single change isn't a skill — it lives as the **Change rules** in each project's `CLAUDE.md` (Quick Path / Full Path), so every skill follows the same doctrine without one having to call another.

---

## License

[MIT](LICENSE) © 2026 BytesFromToby
