---
name: new-pr
description: >
  Open or update pull requests and merge requests, including stacked changes.
  Check and commit the changes, write the description, and fix CI failures
  and review findings. Keep changes local when requested.
---

# New PR

Own the path from a scoped change to an open PR/MR with passing CI and handled
forge reviews. Retain responsibility for branch state, scope, evidence,
authorship, and bot-finding triage.

Start at the stage the task needs. For existing changes, inspect and verify
them without repeating planning or implementation. For an existing PR/MR,
resolve its head and base, then address the requested updates or watch CI.

When the user also requests local adversarial review, use the sibling
[Adversarial Review skill](../adversarial-review/SKILL.md) if installed, or the
user's chosen review workflow, before publishing. Carry its findings and
reviewed revision forward. Creating or watching a PR alone does not require
local reviewers.

Read [references/conventions.md](references/conventions.md)
before choosing branch names, PR structure, visual evidence, or attribution.
Read [references/forge-commands.md](references/forge-commands.md) before using
`gh` or `glab`. Resolve bundled script paths relative to this skill directory,
even when running commands from the target repository.

## Non-negotiable rules

- Read repository instructions and PR templates first. They outrank defaults
  in this skill.
- Pin the exact base before branching. Stacked PRs are common; never assume
  `main`.
- Preserve the user's publish gate. “Keep it local,” “status before push,” or
  “I will review before submit” means stop before push/opening the PR.
- Keep each PR independently understandable and as focused as practical.
  Separate mutually exclusive changes, optional product choices, and unrelated
  fixes. State stacking and merge-order dependencies explicitly.
- Use the user's established git identity. Do not create an AI-named branch,
  AI-authored commit, or AI `Co-authored-by` footer unless explicitly required
  by the user or repository.
- Treat a repository-required `Model: … | Harness: …` PR disclosure separately
  from commit authorship. Include it only when current repo instructions or
  recent accepted PRs require it. Use the **full model name** (including version
  and variant) and **full harness** (agent plus app or CLI surface). If the
  prompt does not reveal the exact model, inspect the active turn's runtime
  metadata before writing the trailer; do not infer it from a configured
  default. For multiple models or harnesses, join names with ` & ` in the same
  disclosure line. See
  [conventions](references/conventions.md#model-and-harness-disclosure).
- Never overwrite bot-managed PR-body blocks. Preserve their marker-delimited
  contents verbatim when editing the human-authored portion.
- Prefer rebasing the PR branch onto its intended base when bringing it up to
  date. After rewriting published commits, use `--force-with-lease`. An
  authorized PR update includes this push; no separate confirmation is needed.
  Preserve publish hold points and never use plain `--force`.
- Do not merge a PR, dismiss a human review, or close competing PRs unless the
  user explicitly asks.

## Stage 0: Resolve the workflow

Inspect without asking:

1. Repository root, instructions, PR/MR template, current branch, remotes, and
   working-tree status.
2. Forge and authenticated account.
3. Any existing PR for the current branch. When updating an existing PR, use
   its actual head branch; do not create a replacement branch.
4. The latest three to five accepted PRs/MRs by the user in the same repository
   plus recent local branch history. Derive title, branch, body, identity, and
   draft conventions from these.
5. Available focused checks and which clients/providers/surfaces apply.

Resolve four decisions:

- **Change and boundaries**: desired behavior, exclusions, and whether adjacent
  findings need separate issues/PRs.
- **Base**: exact local or remote ref. If the user named a parent PR, resolve
  that PR's head branch.
- **Publish gate**: proceed through PR creation, or stop locally for review.
- **Readiness**: ready PR, draft, or explicitly blocked/dependent PR.

Ask only for a decision that cannot be discovered safely. Do not re-ask facts
already supplied. When base is missing, offer the repo default, current branch,
and recently active stack bases with evidence.

For a feature, bug, or restoration, search open issues and PRs/MRs for the same
behavior before implementing. Report a likely duplicate or overlapping branch;
do not silently build a second version.

If the tree is dirty, classify every changed/untracked file. Include only
in-scope changes; isolate new work in a separate worktree when needed. Ask if
ownership or overlapping edits are ambiguous. Never stash, discard, absorb,
or move unrelated user work without approval.

## Stage 1: Plan independently

For a non-trivial change, use a read-only planning subagent when delegation is
available and would improve the plan. Otherwise plan directly. Give it only
the task, repo root, exact base, relevant repo instructions, and known
constraints. Require:

- minimal change and affected contracts/surfaces,
- files and responsibilities,
- edge cases and likely regressions,
- focused verification and user-visible evidence,
- any reason to split or stack the work.

Critique the plan yourself. Check that it honors repo architecture, multi-
surface/provider obligations, and the user's exclusions. Stop for user input
if the plan changes product direction or materially expands scope.

For an obvious one-file change, write the compact plan yourself.

## Stage 2: Establish the branch and implement

Inspect `git worktree list` first. Reuse the worktree owning an existing PR's
head. For new work, create a separate worktree when repository guidance,
parallel work, or unrelated changes call for isolation. Otherwise create the
branch in place. Preserve unrelated changes in their original worktree.

In T3 Code, keep the app's workspace binding correct. Inspect
`t3_worktree_status` and `t3_worktree_list`. To move this thread, use
`t3_worktree_handoff` as the last action of the turn, with a continuation prompt;
it cannot move a thread already attached to a worktree. For a user-requested
separate top-level thread, use `t3_thread_launch` with an explicit
`workspaceStrategy` and put the task in `message`. A local stack uses the
parent branch as `baseRef` with `startFromOrigin: false`. Discover and reuse
existing worktrees instead of duplicating them. A shell `cd` or worktree
creation does not update the app binding. Outside an app-managed workspace,
use the git commands below.

Resolve the base remote separately from the push remote; a fork's `origin`
need not own the upstream base. When creating a branch outside an app-managed
workspace, fetch and branch from the exact base:

```bash
git fetch <base-remote> <base>
git switch --no-track -c <head> <base-remote>/<base>
# Or, for a separate worktree:
git worktree add --no-track -b <head> <worktree-path> <base-remote>/<base>
```

For a local-only stack base, branch from the verified local commit instead.
Choose the branch name from same-repo history; do not impose a global prefix.

When updating an existing PR, fetch its actual base and head before rewriting
history. Inspect and incorporate any remote head commits missing locally,
then record the observed remote head SHA for the push lease. Rebase onto the
intended base instead of merging the base into the PR branch, unless the user
or repository requires a merge. For a stack whose parent was rewritten, use
`git rebase --onto <new-parent> <old-parent-sha>` to replay only this layer;
verify the old boundary before proceeding. Resolve conflicts, inspect the
resulting diff, and rerun affected checks before pushing. See
[forge commands](references/forge-commands.md#update-a-pr-branch).

Implement directly or delegate with the plan, branch, instructions, checks,
and explicit exclusions. When delegating, prefer T3 `delegate_task` when
available; use its live `orchestrator_capabilities` catalog for providers,
models, and options, track its `taskId`, and use native delegation as a
fallback. A separate child checkout uses `isolation: "worktree"`, which starts
from the parent's local commit and does not copy uncommitted work. Collect and
inspect the child's changes before committing them. Tell the child:

- implement and test the plan,
- preserve unrelated work,
- do not commit, push, open a PR, or alter PR text,
- report changed files, checks, evidence, and unresolved risks.

Read the load-bearing diff yourself. Compare against the exact base, inspect
untracked files, and verify that no test fixtures, signing changes, local
credentials, proof screenshots, or integration-only commits leaked in.

Run the smallest relevant test/lint/typecheck set. For user-visible changes,
exercise the actual affected clients and capture evidence before opening the
PR when repository instructions allow that environment. Do not substitute a
typecheck for behavior verification.

When a change affects mobile behavior, verify it in an iOS Simulator or Android
Emulator by default unless the user specifies otherwise. Cover the affected
platforms and form factors; a desktop browser's mobile viewport does not verify
the native app. In T3 Code, use `device_list` and `device_open`, then the exact
AgentDevice executable and target arguments returned by `device_open`. Follow
the repository's mobile verification workflow when available. Honor existing
authorization and report unavailable device access as a verification gap.

For screen recordings, read
[references/recording-evidence.md](references/recording-evidence.md). Rehearse
before recording, then run start, brief lead-in, scripted actions with bounded
waits, brief lead-out, and stop in one uninterrupted execution. Aim for about
one second at each end. Inspect the result after stopping; keep model/tool
round-trip pauses out of the recording.

## Stage 3: Prepare commits

Before committing:

```bash
git diff --stat <base>...HEAD
git diff --check
git status --short
git config user.name
git config user.email
```

Match the user's identity from repository history/config. If identity is
missing or conflicts with recent user-authored commits, stop and ask rather
than inventing it.

Use conventional commit subjects when repository history supports them:
`feat(scope): …`, `fix(scope): …`, and similar. Keep the subject imperative.
Split commits by coherent, reviewable concern—not by arbitrary file count.
Preserve upstream authorship when importing another person's commit.

Inspect final commit messages for unintended AI coauthor/generated footers.
Follow the user's and repository's attribution requirements. Do not rewrite
inherited base commits merely to sanitize a stacked PR; verify authorship of
the new commits.

If the publish gate is closed, stop here with the diff, checks, evidence, and
proposed PR metadata. Otherwise use a normal push for new branches and
fast-forward updates:

```bash
git push -u <push-remote> <head>
```

If the update rewrote published history, push with an explicit
`--force-with-lease=refs/heads/<head>:<expected-remote-head-sha>` using the SHA
recorded before the rewrite. A rejected lease requires inspecting the new
remote changes; do not simply refresh the lease and overwrite them.

## Stage 4: Open the PR/MR

Build the title and body from current same-repo examples. Default content:

- what changed,
- why it is needed or the failure mode,
- exact verification performed,
- issue closure and stack/merge ordering when applicable,
- before/after evidence for user-visible changes,
- known gaps, blockers, or intentionally deferred work.

For visual changes, use matched before/after captures: same surface, state,
theme, dimensions, and orientation. Keep proof images out of the code branch
unless they are official repository assets that the change makes stale.

Use a draft when the work is intentionally blocked, exploratory, dependent on
an unpublished prerequisite, or offered as one side of a product decision.
Do not assume drafts are the default.

Open against the exact chosen base. Immediately report the URL and
`base ← head`. If the PR is stacked, verify the forge shows only this layer's
diff and document its parent/merge order.

When T3 exposes `link_pull_request`, register the full URL immediately after
creating a PR or starting work on an existing one, including every stack layer
you work on. Before finishing, use `list_thread_pull_requests` and link any
missing PRs from this task. Report linking failures explicitly.

After bots have modified the body, never replace it from a stale local copy.
Fetch the current body and merge only the human-authored prefix with:

```bash
python3 scripts/preserve-bot-body.py \
  --current <current-body.md> \
  --authored <new-human-body.md> \
  --output <merged-body.md>
```

Then update from the merged file. Keep model/harness disclosure above bot
notes when the repo requires that disclosure.

## Stage 5: Babysit forge reviews and CI

Record the latest head SHA after every push. Watch checks, issue comments,
reviews, and inline review comments for that SHA. Derive the relevant checks
and review bots from the repository and PR.

On entry, read existing unresolved discussions and current failing checks;
then track new or updated activity after each push. Keep unresolved findings
in the queue even when their comments predate the latest push. CI status alone
does not cover bots that report through comments or PR-body summaries.

When a repository's review bots automatically resolve findings, let them
re-review the latest head and resolve their own findings after a fix. Do not
assume a finding is resolved just because a fix was pushed. If it remains open
after re-review, inspect the feedback and current code again. Follow repository
policy for bots that require manual resolution.

For each new bot or human finding:

1. Read the full thread and inspect the referenced code.
2. Decide whether it is real, already resolved, base-branch noise, or taste.
3. Fix real findings, run focused verification, commit, and push.
4. Reply only when authorized and useful; explain false positives with evidence.
   Leave fixed bot findings for automatic resolution. Resolve human review
   threads only when authorized.
5. Reset the watch baseline to the new head and wait for the latest checks.

In T3 Code, after handling existing comments and failures, call
`watch_pull_request` and end the turn. The app wakes this thread for new
activity; do not poll, sleep, or start another watcher. On a wake, inspect the
latest head and handle actionable activity. Call `unwatch_pull_request` before
handing the work back to the user. A delegated child must return the URL, head
SHA, and pending check/review state to its parent; it must not watch or poll.

Otherwise use the available wait/monitor mechanism. Continue until checks and
normal review bots pass for the latest head and actionable threads are handled.
Stay quiet when nothing changed. Treat applicable skipped/neutral checks
according to repository policy; pending, failed, cancelled, or unavailable
checks are not green. Fix relevant failures and restart the watch after a push.
If progress requires missing credentials, unavailable infrastructure, a user
decision, or another maintainer's action, report the specific blocker and
remaining work. Also stop if the user cancels or the PR is merged/closed.
Do not claim success based on checks or approvals from an earlier SHA.

## Final report

Return:

- PR/MR URL and `base ← head`,
- ready/draft/blocked state and dependencies,
- concise change summary,
- checks and visual/manual evidence,
- CI and forge-review results, plus local review results if separately requested,
- anything unverified, deferred, or awaiting a reviewer.

If the publish gate remained closed, replace the URL with the local branch,
commit(s), proposed title/body/base, and the exact next action awaiting the
user.

## Failure handling

- Wrong base or polluted stack: stop before push; rebuild the branch from the
  correct base and cherry-pick only intended commits.
- Push rejected or branch diverged: fetch and inspect the remote changes,
  incorporate them, and rebase as needed. Preserve others' commits and use a
  fresh explicit lease only after reconciliation; never bypass a rejection
  with plain `--force`.
- Scope balloons: stop and propose a split.
- Bot edits disappear from the body: restore the current marker-delimited bot
  blocks before any further PR-body update.
