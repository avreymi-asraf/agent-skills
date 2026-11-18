# Research vault starter

Copy this directory to create a new local dossier vault (includes `AGENTS.md`):

```bash
cp -R skills/politics-investigator/assets/research-vault research-vault
cp -R research-vault/affairs/_TEMPLATE research-vault/affairs/<affair-slug>
```

Replace `<affair-slug>` with a lowercase kebab-case identifier, then remove `affairs/_TEMPLATE` when the vault is initialized.

The vault is tracked in Git on `main`. Update `INDEX.md` alongside dossier changes, commit, and push immediately.
