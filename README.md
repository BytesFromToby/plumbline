# Plumbline — a spec-driven workflow of AI-agent skills

*To build a house well you follow the plans, double-check the work, and keep everything plumb. The plumb line is the builder's reference of truth — here, your spec is that line.*

## Description

A "trust, but verify" set of agent skills that build code in a trackable way — even reporting their own deviations as they go — for better, more accountable coding.

- **Agents build, you approve.** The work runs across five single-responsibility stages — first interview to signed-off code — and stops for your sign-off at each handoff.
- **No stage does the next one's job.** `inspector` can't edit the spec to pass a test; `builder` can't invent requirements. Those boundaries are what keep it honest.
- **Coordinated by files, not calls.** Stages never call each other, so any one runs on its own — and the spec stays the single source of truth end to end.
- **Inspectable, not trusted.** A deviation log records where the build left the plan; test evidence backs every "done."
- **Two modes.** The same conventions also power an autonomous maintenance loop that keeps a built project aligned to its spec over time.

*Built for a solo developer's real projects — and run end-to-end on real features, spec through signed-off code, not just designed on paper.*

---

## Two modes: build, then maintain

Plumbline runs in two directions. **Build** takes an idea to verified code through five forward stages. **Maintain** keeps an already-built project honest over time, on its own. The two share the same spec, the same file conventions, and one skill — `inspector` — that does duty in both.

### Build — idea to verified code

```
scaffold ──▶ architect ──▶ foreman ──▶ builder ──▶ inspector
 (once)       (spec)       (blueprint)   (code)      (proof)
                                          ▲             │
                                          └──── fix ◀───┘
```

| Stage | Owns | Produces |
|-------|------|----------|
| **scaffold** | Bootstrapping a greenfield project (run once) | The folder skeleton + a `CLAUDE.md` contract |
| **architect** | Defining *what* to build | `Planning/specs/[feature]_spec.md` with inline acceptance criteria, a decision log |
| **foreman** | Planning *how* to build it | `Planning/blueprints/[feature]_BP.md` — slices of ordered steps |
| **builder** | Writing the code | Code + tests, executed one slice at a time, with a deviation log |
| **inspector** | Proving it works | An evidence report; a dated PASS/FAIL stamp on the blueprint |

Each stage hands off through the filesystem. The user approves between stages — the agent does the work, the human stays the judge.

A project grows through stages — **experimental** (loose files, no git) → **useful** (git + structure) → **big** (split specs, reference tier, architecture doc). `scaffold` starts a project clean at the first stage; graduating it across the later boundaries — init git, split a monolith spec, extract the reference tier — is currently a **manual** step. (Automating those transitions in a dedicated skill is a planned addition, not part of this version.)

### Maintain — keep a built project honest

Once code exists, `walkthrough` is the autonomous counterpart to the build lifecycle: run it and walk away. It works a project end-to-end — baseline, drift, coverage, docs — applying only changes safe enough to make unattended and routing everything else to a list you approve. It doesn't reimplement the checks it needs; it calls the same skills the build mode uses.

```
walkthrough  ── one autonomous session, fenced to safe changes ──
   │
   ├─ calls ─▶ surveyor    static: spec-vs-code drift
   ├─ calls ─▶ inspector   runtime: proof against the Done-when items
   │
   ├─▶ Quick-Path fixes ........ applied in place, tests re-run after each
   └─▶ everything larger ....... a dated, prioritized Recommendations list
```

| Skill | Owns | Produces |
|-------|------|----------|
| **walkthrough** | An autonomous maintenance session (no check-ins, commits nothing) | Quick-Path fixes applied + `output/walkthrough/Recommendations_YYYY-MM-DD.md` |
| **surveyor** | Static spec-vs-code drift — reads and compares, never runs the software | A dated `output/surveys/Survey_YYYY-MM-DD.md` (written even when clean) |
| **inspector** | Runtime proof against the spec — *the same skill the build lifecycle ends on* | An evidence report in `output/inspect/` |

`surveyor` and `inspector` also run standalone — `surveyor` before a feature or after a refactor when you just want a drift report; `inspector` to sign off a single slice. `walkthrough` is the hands-off orchestration of both, fenced by the **Change rules** in `CLAUDE.md`: it applies Quick-Path fixes itself and never authors a decision doc or touches a schema unattended.

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

**`Planning/` = the living plan · `docs/` = the record & reference · `output/` = skill output.**

| Path | Holds |
|------|-------|
| `Planning/specs/[feature]_spec.md` | Specs — the source of truth |
| `Planning/reference/` | Shared definitions specs cite (data models, constants) |
| `Planning/blueprints/[feature]_BP.md` | Per-feature build plans |
| `docs/decisions/` | Decision logs (append-only) |
| `docs/changelog/` | Changelog — `local` history mode only |
| `docs/architecture.md` | The as-built system map — written once modules need one |
| `output/inspect/` | Inspector reports + evidence |
| `output/deviations/` | Builder deviation rollups |
| `output/surveys/` | Surveyor drift reports (`Survey_YYYY-MM-DD.md`) |
| `output/walkthrough/` | Walkthrough log + recommendations (`…_YYYY-MM-DD.md`) |

`scaffold` lays the full folder skeleton up front as guide-rails. **History mode:** a fresh
project starts `local` (history lives in `docs/changelog/` + `docs/decisions/`, no git); when it
proves useful, you flip it to `git` by hand — init the repo and shed the changelog (git becomes the history).

---

## The CLAUDE.md contract

`scaffold` writes a single `CLAUDE.md` contract into each project; every skill reads it. It carries:

- **Identity** — one line on what the project is and why.
- **Stack + Commands** — the test command and the run/demo command (must be *real* — `inspector` depends on it), plus a UI-evidence tool for web stacks.
- **History mode** — `local` (history in `docs/changelog/` + `docs/decisions/`) or `git` (git log is the history); flipping `local → git` is a manual step.
- **Where things live** — the folder map, so a reader or agent orients without spelunking.
- **Change rules** — the Quick Path / Full Path for any change. Branches on history mode (`local` adds a changelog entry, `git` commits). Doctrine every skill reads, not a skill you invoke.
- **How to work here** + the skills flow.

The spec *format* isn't copied into the contract — it's authoritative in `architect` (which writes specs), so there's no separate template to drift.

---

## Not a skill: the order of operations

The sequence for any *single* change isn't a stage you invoke — it lives as the **Change rules** in each project's `CLAUDE.md` (Quick Path for trivia, Full Path for features and schema). Every skill reads the same doctrine, so the workflow stays consistent without one skill ever having to call another.

---

## License

[MIT](LICENSE) © 2026 BytesFromToby
