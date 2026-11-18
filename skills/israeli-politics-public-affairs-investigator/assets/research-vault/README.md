# Research vault starter

Copy this directory to create a new local dossier vault:

```bash
cp -R skills/israeli-politics-public-affairs-investigator/assets/research-vault research-vault
cp -R research-vault/affairs/_TEMPLATE research-vault/affairs/<affair-slug>
```

Replace `<affair-slug>` with a lowercase kebab-case identifier, then remove `affairs/_TEMPLATE` when the vault is initialized.

The vault is intentionally local and Git-tracked. Store full source text and visual artifacts in the dossier, and update `INDEX.md` in the same commit as the dossier.
