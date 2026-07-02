# The contract audit system

How Plumbline keeps a multi-skill agent framework coherent — and a pattern you can lift into
any project where several independently-loaded prompt files must agree on shared conventions.

## The problem it solves

Skills are read **cold**: a fresh agent loads one file with none of the context the author had.
Any convention shared between two files — a status string one skill emits and another routes on,
a heading one writes and another greps for — will eventually be spelled two ways, and the chain
breaks *silently*: no error, just a mis-route or a missed match. Prose review doesn't catch it,
because each file is internally consistent.

## The three layers

| Layer | File(s) | Catches | Runs |
|---|---|---|---|
| **Contract** | `TERMS.md` → generated `terms/<skill>.md` slices | nothing itself — it's the datum | read by each skill at runtime |
| **Mechanical audit** | `audit.py` | everything with a single right answer | CI, every push |
| **Semantic audit** | `auditor.md` | producer/consumer disagreements a script can't judge | by hand (an LLM pass), after edits and before releases |

### 1. TERMS.md — one contract, audience-tagged, sliced per consumer

Every token, status line, path pattern, and invariant shared by two or more skills lives in one
file, in numbered sections. Each section carries an `<!-- audience: skill, skill -->` line naming
who is bound by it.

Skills don't read the whole contract at runtime — `audit.py --write-terms` generates
`terms/<skill>.md`, the preamble plus only that skill's sections. This matters when an
orchestrator spawns many subagents per run: each spawn pays to load its contract, so scoping the
slice cuts a fixed per-spawn token cost (roughly in half here) without weakening the drift-guard.
The slices are **committed generated output**: never hand-edited, always reproducible from
TERMS.md, and the audit fails while they're stale — so a slice cannot silently diverge from the
contract it was cut from.

### 2. audit.py — deterministic, CI-able, cannot hallucinate

Stdlib-only Python; exit 0 = clean, 1 = findings. Checks only things with one right answer:

1. **Frontmatter** — parseable YAML with `name` + `description`, and no unquoted colon-space
   (the YAML break that silently drops *all* frontmatter at runtime).
2. **Contract load** — every skill loads its `terms/<skill>.md` slice.
3. **Resolvable references** — every `${CLAUDE_PLUGIN_ROOT}/<path>` points at a real file.
4. **Skill-name resolution** — every `run/spawn **name**` invocation names a real skill.
5. **Slice freshness** — every `terms/*.md` byte-matches what TERMS.md generates; missing,
   stale, and orphaned slices are findings.

Two modes: `python tools/audit.py` verifies (what CI runs — see
`.github/workflows/audit.yml`); `python tools/audit.py --write-terms` regenerates the slices
first, then verifies. Run the latter after any TERMS.md edit and commit the slices with it.

### 3. auditor.md — the judgment pass

The runbook for what a script can't decide: does the producer of a token emit it in exactly the
form every consumer parses? Has new contract surface drifted in unregistered? Has TERMS itself
gone stale against what the skills actually do? Findings triage into **Auto** (fix in place),
**Guard** (add a boundary check in the consumer), and **Decision** (a real contract choice —
route to a human, never edit unilaterally).

## The maintenance loop

```
edit a skill / agent / TERMS.md
        │
        ▼
python tools/audit.py --write-terms     ← regenerates slices, runs all checks
        │
        ▼
semantic pass per auditor.md            ← after meaningful contract changes
        │
        ▼
commit (source + regenerated slices together)
        │
        ▼
CI re-runs audit.py                     ← a forgotten regeneration fails the push
```

Runtime never generates anything — slices are static files by the time an agent reads them, so
there's no Python dependency and no failure mode at spawn time. Freshness is settled at commit
time, deterministically.

## Porting this to a new project

The pattern is three files plus a CI step; almost everything project-specific is a constant.

1. **Copy** `audit.py`, `auditor.md`, and the workflow file. Start `TERMS.md` from the section
   skeleton (numbered `## §N` sections, each with an audience line and a producer → consumers
   note).
2. **Adapt the constants** at the top of `audit.py`: the repo layout globs (`skills/*/SKILL.md`,
   `agents/*.md`), the reference prefix (`${CLAUDE_PLUGIN_ROOT}` — yours may be a plain relative
   path), and the section-heading regex if you don't use `## §N`.
3. **Point each skill at its slice** — a short "read your contract slice first; stop if you
   can't load it" block at the top.
4. **Decide the audiences honestly.** A section goes to a skill only if that skill *acts on it
   at runtime*. Conventions a skill already restates in its own body don't need to be in its
   slice — the audit, not the runtime read, is what keeps restatements honest.
5. **Wire CI** to run `python tools/audit.py` on push.

Rules that keep the system trustworthy, in any project:

- **The contract is the datum.** When a skill and TERMS disagree, TERMS wins and the skill is
  the thing to fix — deliberately, never silently.
- **Generated means generated.** Nobody edits a slice; the header says so and the audit enforces
  it.
- **Mechanical before semantic.** Don't spend judgment on what a script settles for free.
- **Every check earns its place.** Each one exists because that failure actually happened or
  demonstrably would. Don't port checks you can't name a failure for.
