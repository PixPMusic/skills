# PR/MR conventions

Discover conventions in the target repository. These fallbacks carry no
assumptions about a particular owner, organization, forge, or branch prefix.

## Decision precedence

1. Explicit instructions in the current user request.
2. Repository instructions, contribution guidelines, and PR/MR templates.
3. Recent accepted PRs/MRs by the user in that repository.
4. The defaults below.

Read three to five relevant accepted changes, the current git identity, recent
branch history, and the remote layout. Use that evidence to choose the base,
branch name, title, commit style, description, and draft state. Do not carry
conventions from another repository into this one.

## Branches and commits

- Resolve the exact base, including the intended parent of a stack. Neither
  the default branch nor a branch's tracking ref proves the PR base.
- Choose branch names from current repository guidance and history. There is
  no required username or global prefix.
- Use the user's configured git identity, verified against their recent
  commits. If identity is missing or conflicting, ask rather than invent it.
- Match the repository's title and commit style. Use conventional commits
  when the repository uses them; choose a scope that describes the affected
  component. Split commits by coherent behavior.
- Keep AI attribution out of new commit authorship and footers unless the user
  or repository explicitly requires it. Preserve upstream authorship when
  importing existing commits.
- Honor local-only and pre-push hold points. Draft status should reflect the
  user's request, repository convention, or a real blocker or dependency.
- Prefer rebase when updating a PR branch from its base. Use
  `--force-with-lease` when the rebase rewrites published commits, within the
  existing authorization to publish updates. Follow an explicit user or
  repository requirement to merge instead.

## Description

For a small change, lead with the problem and resulting behavior, followed by
verification. Use the repository's template when provided. A compact fallback:

```markdown
## Summary

Explain the problem and what changes for users.

## Verification

- Checks actually performed and their results.
```

Add issue links, stack dependencies and merge order, visual evidence, or known
gaps when they help a reviewer assess the change. Omit empty sections. Keep
alternative product choices and unrelated fixes out of the same PR unless the
user requests that scope.

## Visual evidence and bot content

Capture before and after in the same state, theme, dimensions, and orientation.
Cover the affected surfaces. Use a short recording when timing or motion is
part of the change; see [recording-evidence.md](recording-evidence.md).

Keep proof assets outside the code branch unless they are official tracked
assets that the change makes stale. Upload evidence through the repository's
established workflow. Avoid private data, incidental overlays, and misleading
captures; provide descriptive alt text.

Read the current PR body before editing. Preserve bot-managed marker blocks
verbatim. The bundled helper recognizes Cursor and Macroscope markers; inspect
for other bots and preserve those blocks too. Review bot names and checks come
from the repository, not from this skill.

## Model and harness disclosure

Include disclosure only when the user or current repository convention asks
for it. Match the required format. If none is specified, use:

```text
Model: <full model name> | Harness: <agent and app or CLI surface>
```

Use the actual contributing model's version and variant. Effort is a separate
setting. A configured default does not prove which model ran a particular
turn. Prefer exposed runtime metadata; if necessary, read only the matching
session's turn metadata. Do not search unrelated conversations or attribute a
previous turn when the current one has not been recorded.

In T3 Code, use the current turn's runtime metadata and returned child-task
model/options. Verify the contributing run when selection may have changed.
The agent and app/CLI context determine the harness; a model ID alone does
not. State any unverified detail instead of guessing. When crediting multiple
models or harnesses, join their verified names with ` & ` in one disclosure
line unless the repository requires another format.
