# Spec: Spec Document Lifecycle (grow-then-split)

A project's specification starts as a single document and splits into a structured tier only when it grows past a threshold. Small projects stay simple (one file). Big projects get structure — per-feature specs, a shared reference tier, and an architecture doc — but only when size makes that structure earn its place, never pre-built. This defines the two document classes, the size trigger, and what the split produces.

## Scope
- Does: define how the project spec grows from one file and splits on a size trigger; define two document classes (feature spec vs reference doc) and the architecture doc; say where the new tiers live and who triggers the split.
- Does NOT: change the `**Done when:**` format or tags; change foreman/builder/inspector behavior; auto-split without a human-reviewed examination; apply to projects that never cross the threshold (they keep one spec file forever).

---

## Reference: Document classes

This section is definitional — no Done-when. (It is itself an example of a reference section living beside feature sections.)

- **Feature spec** — describes a behavior. Carries `**Done when:**` items. Testable. Lives in `Planning/specs/`.
- **Reference doc** — shared truth that feature specs cite: glossary/terms, data models, constants/formulas. No Done-when (definitions don't pass or fail). Lives in `Planning/reference/`.
- **Architecture doc** — the map: how features/modules relate, the high-level shape. Not testable, not a glossary. Lives at `Planning/architecture.md` (promote to `Planning/architecture/` folder only if it itself grows too big).

The framework today models only the feature spec. This spec adds the other two as recognized classes.

---

## Feature: Single project spec at start

A new project has exactly one spec file: `Planning/specs/[project]_spec.md`. It holds the one-paragraph project description plus one `## Feature:` block per feature. `architect` appends feature blocks to this single file as features are defined. No per-feature files, no reference tier, no architecture doc yet.

- Input: a new (scaffolded) project; `architect` runs to define features.
- Output: one growing spec file under `Planning/specs/`.

**Done when:**
- A freshly scaffolded project that has run `architect` once has exactly one `*.md` file in `Planning/specs/` (excluding `_TEMPLATE.md` and `archive/`)  `[automated]`
- That file contains every defined feature as a `## Feature:` block with its own `**Done when:**`  `[automated]`
- No `Planning/reference/` or `Planning/architecture.md` exists until the threshold is crossed  `[automated]`

---

## Feature: Size flag (owned by architect)

`architect` is the only skill that detects size and raises the flag. At the end of a run (Step 5 in `architect/skill.md`), it measures what it just wrote and, if over threshold, **warns the user and asks** — it never restructures. Scaffold is explicitly NOT involved. The restructure execution is deferred to a later, separate mechanism (TBD owner — see Open Questions).

Triggers (tunable): the project spec exceeds **6 `## Feature:` blocks OR ~500 lines**, OR any single `## Feature:` block exceeds **~150 lines** (a bloated single feature counts too).

The decision is the user's, framed by *forecast not size*: "near done / staying small" → drop it; "big project / will keep growing" → record a one-line **Pending: restructure** note in the decision log. Nothing acts on that note yet; it's a breadcrumb for the deferred mechanism.

- Input: a just-written/grown spec; `architect` finishing a run.
- Output: either nothing (under threshold or user says near-done), or a printed warning + question + an optional `Pending: restructure` note in the decision log.

**Done when:**
- A project spec with 7+ feature blocks makes `architect` print a size warning naming what tripped  `[automated]`
- A single feature over ~150 lines also trips the warning, even if the whole-spec count is low  `[automated]`
- The warning asks the forecast question (near-done vs big project) rather than asserting a split  `[human-required]`
- "Big project" answer leaves a `Pending: restructure` line in the decision log; "near done" leaves nothing  `[human-required]`
- A spec under all thresholds produces no warning  `[automated]`

---

## Feature: The examination (split + extract)

The examination is a reviewed restructure. With user sign-off, it does three things, each independently skippable:

1. **Split features** — each `## Feature:` block moves to its own `Planning/specs/[feature]_spec.md`. The original monolith is copied to `Planning/specs/archive/[project]_spec_YYYY-MM-DD.md`, then removed from the live folder.
2. **Extract shared terms** — domain vocabulary repeated across features moves to `Planning/reference/glossary.md`; feature specs reference the term instead of redefining it.
3. **Extract data models** — shared entities move to `Planning/reference/data-models.md`; feature specs cite them.

It also offers to create `Planning/architecture.md` describing how the now-split features relate. `Planning/reference/` and the architecture doc are created lazily here — never by `scaffold`.

- Input: a triggered examination with user approval for which of the three actions to take.
- Output: per-feature spec files; a reference tier (as needed); an archived monolith; optionally an architecture doc.

**Done when:**
- After a split, each former `## Feature:` block exists as its own file in `Planning/specs/`  `[automated]`
- The pre-split monolith exists in `Planning/specs/archive/` with a dated name and is gone from the live folder  `[automated]`
- Extracted terms appear in `Planning/reference/glossary.md` and are no longer redefined inline in the feature specs  `[human-required]`
- `Planning/reference/` and `Planning/architecture.md` exist only after an examination that chose to create them  `[automated]`
- Cross-references between the split specs resolve (no spec points at a section that no longer exists)  `[human-required]`

---

## Folder conventions (additions)

| Folder/file | Holds | Created by |
|---|---|---|
| `Planning/reference/` | glossary, data models, constants — reference docs | examination, lazily |
| `Planning/architecture.md` | the high-level map | examination, lazily |

Existing folders (`specs/`, `specs/archive/`, `blueprints/`, `decisions/`, `docs/changelog/`, `output/`) are unchanged.

---

## Resolved

- **Detection/flag owner:** `architect`, at end of run. Scaffold is NOT involved (new-project-only).
- **Architect's role:** warn + ask only. Never splits specs.
- **Decision basis:** user's forecast (near-done vs big project), not the raw line count.
- **Feature-level bloat counts** too, not just whole-spec size.
- **README:** deprecated — not authoritative; do not reconcile against it.

## Open Questions (deferred — "restructuring later")

- **Who *performs* the restructure.** Not scaffold, not architect. A new dedicated skill, or a mode of an existing one? This is the disruptive part (shattering the source of truth) and is intentionally unbuilt for now.
- **Dangling references after a split.** Decision logs and blueprints written against the monolith point at a file that's been archived/split. Does the restructure rewrite those references, or just flag them?
- **The `Pending: restructure` breadcrumb has no consumer yet.** Architect writes it; nothing reads it. Acceptable while deferred, but the future restructure mechanism must look for it.
- **Size metric value.** 6 features / ~500 lines / ~150 lines-per-feature are guesses. Consider making them per-project settings in the contract.
- **`architecture.md` file vs folder.** Start as one file, promote to a folder when big, or start as a folder? city_sim grew a `Planning/architecture/` folder ad hoc.
