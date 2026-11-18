# Research vault starter

Copy `AGENTS.md` to the project root and this directory to `research-vault/`:

```bash
cp skills/politics-investigator/assets/AGENTS.md AGENTS.md
cp -R skills/politics-investigator/assets/research-vault research-vault
cp -R research-vault/affairs/_TEMPLATE research-vault/affairs/<affair-slug>
```

Replace `<affair-slug>` with a lowercase kebab-case identifier, then remove `affairs/_TEMPLATE` when the vault is initialized.

The project is tracked in Git on `main`. Update `INDEX.md` alongside dossier changes, commit, and push immediately.
