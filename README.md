# my-favorite-prompts

Personal AI workspace for prompts, agents, and skills.

## Layout

- `prompts/` for reusable prompt fragments
- `agents/` for agent definitions
- `skills/` for local Codex skills
- `agents-skills/` for generated links to local and third-party skills
- `metaprompt/` for prompts that generate prompts
- [`superpowers/`](https://github.com/obra/superpowers) for the upstream Superpowers checkout
- [`lambdatest-agent-skills/`](https://github.com/LambdaTest/agent-skills) for the upstream LambdaTest agent skills checkout
- [`impeccable/`](https://github.com/pbakaus/impeccable) for the upstream Impeccable checkout
- [`steipete-agent-scripts/`](https://github.com/steipete/agent-scripts) for the upstream agent scripts checkout

## Setup

Bootstrap the managed upstream checkouts and skill links with:

```bash
./bootstrap.sh
```

1. This clones or updates the managed upstream directories
2. Links local and selected third-party skills into `agents-skills/`
3. Links `agents-skills/` into `~/.agents/skills`
4. Exposes custom OpenCode skills in `~/.opencode/skills`.

Bootstrap currently installs all Superpowers skills, LambdaTest's
`rspec-skill`, and Impeccable's agent skill. It clones Steipete's checkout for
future use but does not install its skills yet.

## Updating Upstreams

Update the upstream checkouts with:

```bash
git -C superpowers pull --ff-only origin main
git -C lambdatest-agent-skills pull --ff-only origin main
git -C impeccable pull --ff-only origin main
git -C steipete-agent-scripts pull --ff-only origin main
```

If you add or rename local skills, keep them under `skills/<name>/SKILL.md`.
The generated `agents-skills/` directory is created by `bootstrap.sh` and is
ignored by Git.
