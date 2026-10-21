---
name: adversarial-review
description: >
  When requested, use for adversarial review of a branch, a stacked diff, or
  local changes before publication.
---

# Adversarial Review

Find concrete defects in local changes and independently verify them. Run the
review without requiring a pushed branch or an existing PR. A request to
review produces findings; a request to review and fix also authorizes scoped
local corrections. Publication belongs to the separate New PR workflow.

## Select models

Discover the available reviewer providers and models first. In T3 Code, call
`orchestrator_capabilities` and use its live composer catalog, including custom
models and provider-instance constraints. Tool names may have an MCP prefix,
such as `mcp__t3_code__orchestrator_capabilities`. The native subagent model
list is not the full T3 catalog.

Default to interactive model selection. Before launching reviewers, use the
harness's **Question tool** (`AskUserQuestion`, `request_user_input`, or its
available equivalent) to ask together:

- Which current OpenAI model should the Codex reviewer use?
- Which current Anthropic model should the Claude reviewer use?

Offer choices from the current provider catalogs when available and allow a
custom model name. Do not present remembered model names as a current catalog.
If no Question tool is available, ask the same questions in the conversation.
Inspect the review target while waiting, but wait for model choices before
launching reviewers. A missing answer does not select full-auto mode.

If the user already supplied either model, ask only for the missing choice.
Keep the selections for follow-up review rounds in this task unless the user
changes them; do not ask again on every round.

When the user explicitly requests **full-auto** (for example,
`Use $adversarial-review in full-auto mode`), skip the model questions and use:

- **OpenAI: Astra**, through Codex.
- **Anthropic: Fable 5.1**, through Claude Code.

Explicit model choices override the full-auto defaults. Full-auto controls
model selection only; review-only, fix, commit, and publish scope still comes
from the user's request. Retain the configured Codex effort and use `xhigh`
for the Anthropic reviewer unless the user specifies another effort. If the
selected model does not support that effort, report the incompatibility
rather than silently lowering it.

## Establish the review target

Read repository instructions, then inspect the current branch, worktree,
status, and relevant local refs. Resolve the base from the user's request,
known PR metadata, or verified branch ancestry. Ask if materially different
bases remain plausible; do not assume `main` or treat the tracking branch as
the PR base. For a stack, review only the layer above the intended parent.

Record the base SHA, head SHA, and merge-base SHA. Review the branch's committed
changes with `git diff <merge-base-sha> <head-sha>` and inspect its commit log.
Use pinned SHAs so a moving base or head cannot silently change the target.

Inspect staged, unstaged, and untracked files separately. If the user asks for
the current local work, include the relevant edits and untracked source files
in addition to committed changes. If the request targets committed changes
only, exclude those edits and report that boundary. Never commit or stash user
work merely to make review easier.

Both reviewers must see the same code. Use a stable checkout while they read;
if other work is active, give them a temporary snapshot outside the worktree
containing the selected commits and local changes, with repository instructions
and enough source context to inspect callers. Verify that the snapshot matches
the selected diff. If the target changes during review, identify what changed
and review it before claiming coverage of the final state.

## Run two independent reviewers

Start fresh reviewers in parallel:

1. **Codex:** use a fresh Codex instance or Codex subagent with the selected
   OpenAI model and effort.
2. **Claude:** use a fresh Claude instance with the selected Anthropic model
   and effort.

Set the model and effort through actual launch parameters, not only through
the prompt.

### Prefer T3 child tasks

When T3 orchestration is available, use `delegate_task` as the primary launch
path for both reviewers, including same-provider work, subject to higher-level
harness instructions. Read its current schema before calling it.

- Select each `target.providerInstanceId` and `target.model` from
  `orchestrator_capabilities`; check `canRunChildTask`, cross-provider support,
  and constraints. Do not assume the provider instance ID equals its driver.
- Set effort and other requested settings in `target.options` using that
  model's advertised descriptors. For example, Codex may expose
  `reasoningEffort` and Claude `effort`. Preserve applicable configured options;
  inheritance applies only to the same provider instance and model. Pass
  selected settings explicitly for other targets. Never translate an
  unsupported effort to a lower value or put launch settings only in prose.
- Use `role: "review"`, a self-contained `task` prompt, and a distinct
  `clientRequestId` for each reviewer and round. Reuse that ID only when
  retrying the same launch. Retain the returned `taskId`; check the returned
  provider instance, model, and options against the selection.
- The default shared checkout includes local edits. Use it only while the
  target is stable, or point both reviewers at the verified snapshot. Use
  `isolation: "worktree"` only for a committed target: T3 starts from the
  parent's local commit, runs project setup, and does not copy uncommitted
  edits. Inspect the pinned comparison there; never assume the base is `main`.
- Launch both tasks before awaiting either result. Prefer `mode: "async"` for
  long reviews. Completion wakes the parent; end the current turn while waiting
  rather than polling or launching watchers. Resume consolidation when results
  arrive. Use `task_status` when a result is needed during active work, and
  `task_cancel` for an abandoned or duplicate task. A wait timeout does not
  cancel work; retain the original task ID.
- Treat `workState: "waiting_for_children"` as unfinished. Read blocking
  questions through the pending-request tools in `childThreadId` or relay them
  to the user. Pending approval records do not grant authority to approve.

`childThreadId` is backing storage, not a replacement for the task handle.
Use a new `delegate_task` call for every independent re-review round. Include
the original brief, the revised target, prior findings, their dispositions,
and unresolved objections. Do not start another review by sending to the old
child thread. `create_threads` and `t3_thread_launch` create ordinary top-level
conversations; use them only when the user explicitly requests separate
threads, never as a substitute for reviewers.

If T3 tools are absent from an initial catalog scan, make one bounded direct
attempt at `mcp__t3_code__orchestrator_capabilities` before falling back.

### Native and CLI fallback

Outside T3, or when its delegation is unavailable for the selected target,
use native delegation if it supports the selected provider, model, and actual
launch settings. Otherwise use the provider CLI after checking its installed
help. Do not launch a duplicate reviewer after an uncertain T3 response;
reconcile the existing task first. Two same-provider subagents do not fulfill
the Codex-plus-Claude requirement.

Keep prompts and outputs outside the repository. Resolve the actual model IDs
from the live catalog or verified provider configuration, including full-auto
defaults. Use an alias only if it is verified to select the intended model; a
floating alias is not a version pin. Never silently substitute another model
or effort. If a reviewer is unavailable, complete the available review,
disclose the missing coverage, and do not claim that both reviews passed.

Give each reviewer only the repo/snapshot location, pinned comparison, local
edits included, desired behavior, constraints, and repository instructions.
Do not pass implementation reasoning, expected findings, or the other
reviewer's conclusions before both return.

Use a prompt shaped like this, filling in the actual target and scope:

> Review the changes from <merge-base SHA> to <head SHA> in <repo/snapshot>,
> including <specified local edits, or none>. Desired behavior: <task>.
> Inspect the diff, surrounding code, callers, contracts, and relevant tests.
> Look for concrete correctness bugs, regressions, missing edge cases,
> performance problems, and violations of repository constraints. Trace each
> suspected issue to a reachable failure scenario and distinguish new defects
> from pre-existing behavior. Use focused read-only checks where useful.
> Report each actionable finding with severity, file:line, trigger, impact,
> and supporting evidence. Say "no findings" if none survive verification;
> list coverage gaps separately. Review only: do not edit tracked files,
> commit, push, post comments, or start more reviewers.

Track each reviewer task/process through its supported completion mechanism.
Do not claim the review is complete with results uncollected; a T3 turn may
end while awaiting automatic delivery. Record actual model/effort exposed by the
harness; do not rely on a model's self-identification in prose.

## Verify and consolidate findings

Deduplicate the results and inspect every proposed finding yourself. Trace
the failure through actual callers and dependencies. Use a targeted test or
reproduction when it resolves uncertainty. Agreement between reviewers is
useful evidence, but not proof; a single verified finding is enough to act.

For each finding, determine whether it is:

- **Confirmed:** supported by the code and a reachable failure scenario.
- **Unconfirmed:** plausible but missing evidence; state what remains unknown.
- **Rejected or pre-existing:** explain why the changed code is not responsible,
  the scenario is unreachable, or the suggestion is only preference.

Prioritize confirmed findings by impact. Avoid speculative hardening, stylistic
rewrites, and unrelated cleanup. State convention violations only when there
is a concrete repository requirement or consequence.

## Fix and re-review when requested

For a review-only request, return the verified findings and stop. When local
fixes are authorized, apply confirmed corrections, add meaningful regression
coverage where appropriate, and run the affected checks. Preserve unrelated
changes. Leave fixes local unless the user separately authorized committing
or publishing them.

After corrections, record the new head and/or working-tree diff and run at
least one fresh independent reviewer over the resulting changes. Keep the
same model requirements for whichever reviewer runs again. Check both the
original failure and regressions introduced by the fix. Repeat while new
confirmed in-scope defects remain; ask for direction if a finding requires a
product decision or scope expansion.

## Report and handoff

Lead with confirmed findings, ordered by severity, or "No confirmed findings."
For each, include file:line, the triggering condition, impact, and evidence.
Briefly record rejected findings and reasons when useful to avoid repeat work.

Include the reviewed base/head SHAs, scope of local edits, actual reviewers,
checks performed, and missing coverage. If fixes were authorized, distinguish
fixed findings from remaining ones and identify the state that was re-reviewed.
A review report is evidence about that state, not a guarantee of correctness.

When the user requested both review and a PR, pass this report and the verified
revision to [New PR](../new-pr/SKILL.md) when installed, or continue through the
user's existing PR workflow. That workflow owns commits, pushes, PR/MR
descriptions, and subsequent CI/forge bot follow-up. Do not launch or require
it for a standalone local review.
