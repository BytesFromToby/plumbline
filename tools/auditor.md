# Contract audit (auditor) — keep the skills coherent with TERMS

**Internal maintenance, not an end-user skill.** This is how a maintainer keeps Plumbline's own
skills and agents in agreement with `TERMS.md`. It is the *semantic* half of the hybrid auditor;
`tools/audit.py` is the mechanical half (deterministic, CI-able, cannot hallucinate). Run this
after changing any skill, agent, or `TERMS.md`, and before a release.

## Step 1 — Mechanical pass (must be green first)

Run `python tools/audit.py`. It checks frontmatter validity, each skill's
`${CLAUDE_PLUGIN_ROOT}/terms/<skill>.md` load-line, `${CLAUDE_PLUGIN_ROOT}` reference
resolvability, skill-name resolution, and that the generated `terms/` slices are fresh against
`TERMS.md`. Exit 0 = clean. Fix every finding before going on — they are unambiguous, so there is
nothing to judge.

**After any edit to `TERMS.md`** (content or an `<!-- audience: ... -->` line), regenerate the
runtime slices with `python tools/audit.py --write-terms` and commit them with the change — the
audit stays red until you do. Never edit a `terms/*.md` slice by hand; they are generated output.

## Step 2 — Semantic pass (judgment, against TERMS as the oracle)

Read `TERMS.md` and every `skills/*/SKILL.md` + `agents/*.md`. For each check below, a finding is
"the skills and the contract disagree" — TERMS is the datum, not the code.

- **Producer/consumer agreement.** For every token in TERMS that carries a producer → consumers
  mapping, confirm the producer emits it in TERMS's *exact* form and each consumer parses that same
  form. Canonical check: architect writes `**Done when:**` with `[automated]` / `[human-required]`
  exactly as foreman, builder, inspector, and surveyor read them. A shape or spelling mismatch is a
  finding even when each side is internally consistent.
- **Registry completeness.** Find tokens, status lines, or path patterns that appear in two or more
  skills but are **absent from TERMS** — new contract surface that drifted in unregistered. Each is
  either added to TERMS or removed.
- **Prose drift.** The same concept spelled differently across skills (the `[inspect]` trigger-list
  class) — these pass the script but should be unified to TERMS's canonical wording.
- **Stale oracle.** Does any TERMS definition no longer match what the skills actually do? The
  contract can rot too, and a definition that lies is worse than a missing one.

## Step 3 — Triage each finding

- **Auto** — local and mechanical (a token typo, a dangling in-file reference): fix in place.
- **Guard** — relational cause, local fix (a consumer assumes a shape it never validates): add the
  boundary stop in the consumer. The foreman/inspector untagged-criteria guards are the model.
- **Decision** — a true contract choice (the canonical shape, where a definition lives, or a real
  producer/consumer conflict): do not edit unilaterally; write it up and route to a human.

Apply Auto and Guard; list Decision items for review.

## Step 4 — Close

Re-run `python tools/audit.py` to confirm the mechanical pass is still green, and record the
semantic findings plus what was applied. When skills and TERMS disagree, fix one deliberately —
never silently.
