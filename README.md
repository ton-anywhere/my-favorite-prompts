# my-favorite-prompts

Personal AI workspace for prompts, agents, and skills.

## Layout

- `prompts/` for reusable prompt fragments
- `agents/` for agent definitions
- `skills/` for Codex skills
- `superpowers/` for a separate upstream Superpowers checkout

## Superpowers setup

Bootstrap everything with:

```bash
./bootstrap.sh
```

Update Superpowers later with:

```bash
git -C superpowers pull --ff-only origin main
```

If you add or rename local skills, keep them under `skills/<name>/SKILL.md`.
`skills/superpowers` is reserved for the upstream Superpowers checkout.
