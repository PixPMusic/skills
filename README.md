# Agent skills

Reusable skills for reviewing changes and preparing pull requests.

- [adversarial-review](SKILLS/adversarial-review/SKILL.md): Review local changes
  with independent Codex and Claude reviewers, verify findings, and fix them
  when requested. Prefers T3 Code delegation when available.
- [new-pr](SKILLS/new-pr/SKILL.md): Prepare, open, or update a PR/MR and handle
  CI and review feedback. Prefers rebase and `--force-with-lease` when updating
  published history.

## Install with Vercel Skills

Use Vercel's Skills installer to add these to your agent:

```sh
npx skills add https://github.com/PixPMusic/skills
```

Follow the prompts to choose skills and target agents. Installation is scoped
to the current project by default. Add `--global` to make the skills available
across your projects:

```sh
npx skills add https://github.com/PixPMusic/skills --global
```

To install just one skill:

```sh
npx skills add https://github.com/PixPMusic/skills --skill adversarial-review
npx skills add https://github.com/PixPMusic/skills --skill new-pr
```

To install both for Codex and Claude Code explicitly:

```sh
npx skills add https://github.com/PixPMusic/skills --skill '*' --agent codex claude-code
```

## Use

Ask your agent to use the installed skill. For example:

```text
Use $adversarial-review to review this branch against main. Keep it review-only.

Use $adversarial-review to review and fix my local changes. Leave them uncommitted.

Use $new-pr to open a PR for these changes against main and watch CI and reviews.
```

Replace `main` with your intended base, including a parent branch for stacked
PRs. Adversarial review needs access to both Codex and Claude reviewers; it asks
which models to use unless you already supplied them or requested full-auto.
Both skills follow the target repository's instructions and conventions.

## List and update

```sh
# See what this repository provides without installing.
npx skills add https://github.com/PixPMusic/skills --list

# Check installed skills for updates, then update them.
npx skills check
npx skills update
```

See the [Vercel Skills CLI reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)
for more options.
