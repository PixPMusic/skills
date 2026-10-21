# Forge command reference

Read repository instructions and resolve remotes before using these commands.
Use temp body files rather than shell-embedded Markdown. Check the installed
CLI's help when flags differ from these examples. Run bundled scripts using
their absolute skill-directory path when the working directory is the target
repository.

## GitHub (`gh`)

### Resolve context and current conventions

```bash
gh auth status
gh repo view --json nameWithOwner,defaultBranchRef
gh pr status
gh pr list --state open --author @me --limit 10 \
  --json number,title,headRefName,baseRefName,isDraft,url
gh search prs --author @me --repo <owner/repo> --sort updated --limit 5 \
  --json number,title,url,state,updatedAt
```

For an existing PR, resolve its real head before changing branches:

```bash
gh pr view <number-or-url> \
  --json url,headRefName,baseRefName,headRefOid,isDraft,body,reviews,comments,statusCheckRollup
```

### Search for overlap

```bash
gh search prs "<terms>" --repo <owner/repo> --state open --limit 20
gh issue list --repo <owner/repo> --state open --search "<terms>" --limit 20
```

### Create

```bash
gh pr create \
  --repo <owner/repo> \
  --base <base> \
  --head <head> \
  --title "feat(scope): ..." \
  --body-file <body.md> \
  [--draft]
```

For a fork-to-upstream PR, pass `--repo <upstream-owner/repo>` and an explicit
`--head <fork-owner>:<branch>` when `gh` cannot infer it safely.

### Watch the latest head

In T3 Code, handle existing feedback first, then prefer `watch_pull_request`
and end the turn. Do not also run a CLI watcher. Use these reads to inspect
feedback or as a fallback when app-managed monitoring is unavailable:

```bash
gh pr view <number> --repo <owner/repo> \
  --json headRefOid,updatedAt,reviews,comments,statusCheckRollup
gh pr checks <number> --repo <owner/repo> --watch
gh api repos/<owner>/<repo>/pulls/<number>/comments
gh api repos/<owner>/<repo>/issues/<number>/comments
gh api repos/<owner>/<repo>/pulls/<number>/reviews
```

Read unresolved discussions on entry, then filter new review/comment activity
after the last pushed SHA/time. Carry unresolved findings forward across
pushes. A successful check suite on an older SHA is not completion; check
inline comments and bot summaries as well as CI status.

### Safely update a bot-edited body

Fetch the current body, write the new human-authored prefix separately, then
preserve the bot blocks:

```bash
gh pr view <number> --repo <owner/repo> --json body --jq .body > <current.md>
python3 scripts/preserve-bot-body.py \
  --current <current.md> \
  --authored <authored.md> \
  --output <merged.md>
gh pr edit <number> --repo <owner/repo> --body-file <merged.md>
```

The helper recognizes `CURSOR_SUMMARY` and Macroscope's pull request summary
markers. Inspect the body for other bot delimiters and preserve those too;
never delete or regenerate their contents.

## GitLab (`glab`)

Derive the host from the target repository's remote and authenticated account.
When outside a matching checkout, set it explicitly; replace the example host:

```bash
GITLAB_HOST=gitlab.example.com glab auth status
```

### Resolve context and current conventions

```bash
glab repo view
glab mr list --author=@me --all
glab mr view <iid>
```

API fallback:

```bash
GITLAB_HOST=gitlab.example.com glab api \
  "projects/<url-encoded-project>/merge_requests/<iid>"
```

### Search for overlap

```bash
glab mr list --state opened --search "<terms>"
glab issue list --state opened --search "<terms>"
```

### Create

```bash
glab mr create \
  --target-branch <base> \
  --source-branch <head> \
  --title "feat(scope): ..." \
  --description-file <body.md> \
  [--draft]
```

If the installed `glab` lacks `--description-file`, load the already prepared
file with the least lossy supported mechanism; do not hand-escape Markdown.

### Watch

```bash
glab mr view <iid>
glab ci status
GITLAB_HOST=gitlab.example.com glab api \
  "projects/<project-id>/merge_requests/<iid>/discussions"
GITLAB_HOST=gitlab.example.com glab api \
  "projects/<project-id>/merge_requests/<iid>/pipelines"
```

## Update a PR branch

Use the PR's actual head and base, resolving the base and push remotes
separately. Fetch both, inspect and incorporate remote head commits missing
locally, and record the observed head SHA before rebasing:

```bash
git fetch <base-remote> <base>
git fetch <push-remote> refs/heads/<head>
git rev-parse FETCH_HEAD
git rebase <base-remote>/<base>
```

For a local stack base, use the verified local parent instead. If that parent
was rewritten, replay only this layer with
`git rebase --onto <new-parent> <old-parent-sha>`.

After resolving conflicts, reviewing the diff, and running affected checks,
push rewritten published history using the recorded remote head SHA:

```bash
git push --force-with-lease=refs/heads/<head>:<expected-remote-head-sha> \
  <push-remote> HEAD:refs/heads/<head>
```

Use normal pushes when published history was not rewritten. If the lease is
rejected, inspect and reconcile the new remote commits before trying again.
Do not merely update the expected SHA to make the push succeed.

## Shared safeguards

- Never print or persist forge tokens.
- Never infer the PR base from the default branch when the user named a parent
  PR or active stack.
- Prefer rebase over merging the base into a PR branch, then use an explicit
  `--force-with-lease` for rewritten published history. An authorized update
  includes this push; respect publish hold points and never use plain `--force`.
- Report the URL immediately after creation, then continue reviewing.
