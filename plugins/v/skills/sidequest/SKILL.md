---
name: sidequest
description: Pause the current task to do unrelated work, then resume exactly where you left off. Requires the atlas plugin (uses its note skill for the handoff).
disable-model-invocation: true
argument-hint: "[start <tangent> | resume | abandon]"
---

A **sidequest** is a task-stack push: pause the **main task**, do the **tangent**, pop back. One sidequest open at a time — resume or abandon the current one before starting another.

The tangent's own mechanics (splitting a branch, fixing a flaky test, filing a ticket) are never this skill's job — reach for whichever skill already owns that. `sidequest` only brackets it: write the handoff, isolate if it's code, and hand control back.

## Start

1. **Write the handoff** via the `atlas` plugin's `note` skill (this skill requires `atlas@vforge` installed alongside `v@vforge`): an artifact at `ai/_misc/<ticket-or-slug>/YYYY-MM-DD-sidequest-handoff.md`, `status: open`. Capture, in the artifact:
   - the main task: what it is, what's done, what's left
   - current git state: branch, HEAD sha, dirty files
   - the tangent: what it is, why it's happening now, its own done-criterion
   - `note`'s existing ticket-or-slug rule applies unchanged — no ticket, use a kebab-slug of the main task.
2. **Isolate if the tangent is code-shaped** (it'll touch files, run commands, or need its own branch): `EnterWorktree`. Invoking this skill is the explicit "work in a worktree" instruction its own guardrail requires — don't ask the user to say the word again. Default base ref (`fresh`, off the default branch) is correct for the stated PR-extraction case; only reach for `head` if the tangent must branch from the current dirty work itself.
3. **State the tangent's done-criterion out loud** before starting — checkable, not vague ("PR opened and CI green", not "extraction looks done").
4. Do the tangent, using whichever domain skill fits.

## Resume

Done when the tangent's own criterion from step 3 is met, or the user says to stop early.

1. Finish the tangent's own wrap-up (push, open PR, etc.) — that skill's job, not this one's.
2. `ExitWorktree`: `keep` if anything unpushed or unmerged is worth preserving, `remove` once the outcome lives safely elsewhere (a pushed branch, an opened PR). Confirm before discarding uncommitted changes.
3. Flip the handoff artifact's `status` to `resumed` (in place — an administrative field, not a content revision; no new `-vN`).
4. Restate the main task from the handoff — what was done, what's next — and continue it.

## Abandon

Same as resume steps 2–3, but flip `status` to `abandoned` instead of `resumed`, and skip the tangent's wrap-up.
