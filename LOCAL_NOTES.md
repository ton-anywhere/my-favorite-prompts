# Local workspace notes

## Superpowers custom commits

Keep `superpowers/main` aligned with upstream and maintain personal changes as a
small stack of commits on the local-only `local-custom` branch. A fork is not
needed.

Create the branch and apply the custom commits once:

```bash
git -C superpowers fetch --prune origin
git -C superpowers switch -c local-custom origin/main
git -C superpowers cherry-pick <commit-1> <commit-2>
```

Update it when upstream changes:

```bash
git -C superpowers fetch --prune origin
git -C superpowers switch local-custom
git -C superpowers rebase origin/main
```

Do not reset or reclone `superpowers/` during routine updates; that would lose
the local patch stack. The parent repository's `bootstrap.sh` fetches upstream
refs for Superpowers and Matt Pocock without rebasing local patches. Run the
rebase commands above manually.

## Third-party checkouts with local patches

Use the same local-patch pattern for any upstream checkout that contains
personal changes.

- Keep `main` aligned with `origin/main`.
- Keep personal changes on the local-only `local-custom` branch.
- Create `local-custom` from `origin/main` before adding personal changes.
- Update the checkout with `fetch --prune origin`, then rebase `local-custom`
  onto `origin/main`.
- Resolve rebase conflicts manually. Do not replace the checkout or discard
  the personal patch stack.
- Keep path customizations in the upstream checkout's local commits. Do not
  duplicate those changes as copied skills in the parent repository.

The Matt Pocock checkout follows this pattern. Its path-customized `handoff`,
`prototype`, and `wizard` skills belong in `mattpocock-skills` on
`local-custom`. The parent `bootstrap.sh` should link those skills from that
checkout after the local patch stack is updated.

Update Matt Pocock's checkout with:

```bash
git -C mattpocock-skills fetch --prune origin
git -C mattpocock-skills switch local-custom
git -C mattpocock-skills rebase origin/main
```
