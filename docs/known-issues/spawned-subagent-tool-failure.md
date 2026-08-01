# Bug: Plumbline worker agents fail when spawned as subagents (halt after one tool call / empty tool output)

**Status:** Resolved (verified 2026-08-01). `plumbline:scaffold` spawned as a real subagent (Agent tool, no orchestrator) against a fresh throwaway project completed the full skill — 20 tool calls, folder skeleton, `CLAUDE.md`, `.gitignore`, and a real `git init` + commit, all confirmed on disk. No halt-after-one-read, no empty tool output. The v1.0.1 lowercase→capitalized `tools:` casing fix (see below) appears to have been the actual cause; leaving this doc as a record in case it resurfaces on a different model/environment.
**Reported:** 2026-06-30
**Affects:** `scaffold`, `architect`, `foreman`, `builder`, `inspector` (all worker agents) when spawned as subagents — e.g. by the `homeowner` orchestrator, or directly via the Agent/Task tool.
**Does not affect:** the same skills invoked **inline** in the main session via the Skill tool; a **general-purpose** (non-Plumbline) subagent in the same environment.

## Summary

When a Plumbline worker agent is spawned as a subagent, it fails almost immediately — either returning empty output from its tool calls, or **halting silently after a single read call**. The identical skill logic works when run inline (Skill tool, main session), and a generic subagent in the same session works normally. This breaks the `homeowner` autonomous pipeline, whose entire model is delegating each stage to a fresh subagent.

## Environments (reproduced in both — not environment-specific)

1. Windows 11, Claude Code, plugin installed from a **local directory** marketplace.
2. Ubuntu Linux, Claude Code, plugin installed **fresh from GitHub** on a machine that never had Plumbline (`claude plugin marketplace add BytesFromToby/plumbline` → `install` → restart).

Reproduced 2–3× per agent across both.

## Symptoms observed

- **scaffold:** first spawn returned **0 tool uses** (pure no-op after emitting one line). On resume, the `Read` tool and Bash *read* commands (`cat`/`grep`/`find`) returned **empty** on valid paths, while Bash side-effects (`git init`, `mkdir`, writing files) succeeded. Worked around inside the agent via `powershell Get-Content`.
- **architect / foreman / inspector:** each **died silently after one read call** — made a single read, then halted with no further action or output.
- **general-purpose subagent (control):** given "read `SPEC.md`, report its first line," it returned the correct content in one clean tool use. Works.
- **inline skills (control):** running each skill's procedure inline via the Skill tool worked fully, including real Bash execution for verification (caught a `pytest` discrepancy).

## Isolation

| Path | Result |
|---|---|
| Generic subagent, trivial task | ✅ works |
| Plumbline skill, inline (Skill tool, main session) | ✅ works |
| Plumbline agent, spawned as a subagent | ❌ halts after ~one read / empty tool output |

→ Not a Claude Code subagent-layer bug (generic subagent is fine). Not the skill logic (inline is fine). The fault is specific to the **Plumbline agents when spawned as subagents**.

## Fix attempted — v1.0.1 (commit `23e9ffa`, tag `v1.0.1`)

All six agent frontmatters declared `tools:` with **lowercase** names (`tools: [read, write, bash]`) instead of the canonical capitalized `[Read, Write, Bash, …]`. Claude Code's `tools:` allowlist is case-sensitive, so a *restricted* agent whose names don't match may receive a broken/empty tool set — consistent with the generic agent (no restriction, all tools) being unaffected. v1.0.1 capitalized and right-sized each agent's tools per role.

**Not yet verified:** no spawned Plumbline subagent has been confirmed working *after* pulling v1.0.1 (`claude plugin marketplace update plumbline` + restart).

## Leading hypothesis if v1.0.1 does not resolve it

The "die after exactly one read" pattern matches each agent's **first instruction**: *"read and follow `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`."* If that self-read of the agent's own skill returns empty in a spawned-subagent context (e.g. `${CLAUDE_PLUGIN_ROOT}` not resolving, or the `Read` tool returning empty for that path when nested), the agent is left with no instructions and halts right there — after one read. The tool-name fix does not address this.

**Test:** in a spawned Plumbline subagent, does `${CLAUDE_PLUGIN_ROOT}` resolve, and does reading its own `SKILL.md` return content?

## Impact

`homeowner` cannot delegate stages to fresh subagents; the orchestrator must run each stage inline. Planning stages (`architect`, `foreman`, `builder`) are unaffected in substance, but running `inspector` inline forfeits its **fresh-eyes structural independence** — the final sign-off becomes self-assessed rather than independently verified, which is the framework's core guarantee.

## Workaround

Run the skills inline via the Skill tool. Safe for `architect`/`foreman`/`builder`; compromises `inspector`'s independence specifically. Inline retains full Bash execution for verification.

## Reproduction

1. Install: `claude plugin marketplace add BytesFromToby/plumbline` → `claude plugin install plumbline@plumbline` → restart.
2. Spawn a Plumbline worker as a subagent — e.g. `/homeowner <one-line brief>`, or the Agent/Task tool with `subagent_type: plumbline:scaffold` and a trivial task.
3. Observe: the agent halts after ~one read, or its tool output is empty.
4. Control: spawn a `general-purpose` subagent with the same trivial "read a file, report line 1" task → it works.
