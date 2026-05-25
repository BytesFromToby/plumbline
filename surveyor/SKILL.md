---
name: surveyor
description: Static check of code against the spec — finds drift, unbuilt features, undocumented code, and automated Done-when items with no backing test. Reads and compares; never runs the software. Run before a feature, after a refactor, or when spec and code feel out of step.
---

## When to use this skill
- Before starting a new feature (is there a spec, and is it current?)
- After a large refactor (does the code still match the spec?)
- When something feels off and you want to know whether spec and code still agree
- As **walkthrough**'s drift phase (it calls surveyor rather than reimplementing detection)

Surveyor is **static**. It reads the spec and the code and compares them — it does not run the software or the tests. That line is what separates it from **inspector**: the surveyor checks the structure against the plans; the inspector runs the building to prove it works. If you need to know whether a criterion *passes*, that's inspector's job.

---

## Attitude
- A surveyor with a clipboard and no stake in the outcome. The spec is the datum; you measure the code against it and report every deviation, flattering or not.
- You report. You do not fix — fixes belong to **architect** (spec wrong) or the **builder** under the Change rules (code wrong).
- Tone: direct, no padding.

---

## Step 1 — Find the specs

Look for the specs folder. The framework convention is `Planning/specs/`. Fall back to `docs/specs/` or `specs/` only if that's what the project actually uses.

When listing spec files, **exclude `_TEMPLATE.md` and anything under `archive/`** — the template is a blank form and archived specs are superseded. Neither is live truth.

If no specs folder exists, report **no specs found** and stop.

---

## Step 2 — Classify each spec, then map it to code

The framework has three document classes (see `Planning/specs/spec-lifecycle_spec.md`). Treat them differently:

- **Feature spec** — has `**Done when:**` items. This is what you check for drift and test backing.
- **Reference doc** (`Planning/reference/` — glossary, data models, constants) — definitional, no Done-when. Do **not** flag it for "having nothing testable." Check only that the terms/models it defines are still the ones the code and feature specs use.
- **Architecture doc** (`Planning/architecture.md`) — the high-level map. No Done-when. Check only that the modules it describes still exist.

For each **feature spec**, identify the code area it covers from its title and `## Feature:` blocks. Build a mapping:

| Spec file (class) | Code area |
|-------------------|-----------|
| (discovered) | (discovered) |

If a feature spec maps to no code at all, note it as **orphaned spec**.

---

## Step 3 — Read both sides

For each feature spec ↔ code pair:
1. Read the spec in full.
2. Read the code file(s) it covers.
3. Locate the test files for that code area — you'll need them for Step 4's test-backing check.

---

## Step 4 — Report findings

Four categories. For each item give the spec file + section, what the spec says, and what the code actually does.

**Drift** — spec says X, code does Y differently.
- Spec section · what it says · what the code does.

**Unimplemented** — spec'd but not built.
- The feature/behavior described · whether it looks intentionally deferred (e.g. listed under Open Questions) or just missing.

**Undocumented** — built but not in any spec.
- What exists in code · whether it should be added to a spec or is an internal/temporary detail.

**Untested automated criteria** — every `[automated]` Done-when item should have a committed test that encodes it (foreman plans it, builder writes it). For each `[automated]` item, check a test exists that targets it. List any with **no backing test**. This is the static counterpart to inspector's gap-flag: surveyor finds the missing test without running anything; inspector finds it by running. A `[human-required]` item is expected to have no test — never flag those.

---

## Step 5 — Recommend, don't act

For each finding, suggest exactly one of:
- **Fix the spec** (run **architect**) — the code is right, the spec is stale.
- **Fix the code** (run **builder**, under the Change rules in CLAUDE.md) — the spec is right, the code drifted.
- **Add the missing test** — for an untested `[automated]` item.
- **Open question** — needs a human decision before either side moves.

Make no changes. Report only, then hand off:
- Drift or unbuilt features → "Run **architect** to reconcile the spec, or fix the code under the Change rules."
- Clean → "Spec and code agree. No drift found."
