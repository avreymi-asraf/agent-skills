# `lab.py` commands

All commands run from the lab root as `uv run scripts/lab.py <command>`, from a checkout of the lab's default branch. They exist only in the lab; a try session never needs them.

`--exp` takes the id (`02`) or the full experiment name (`observe/02-probes`). `--try` takes a try name.

"Publishes" below means: commits the lab's change, pulls with rebase, and pushes to the lab's default branch, retrying when the push is rejected. A command that publishes fails, and creates no branch, when the id or the try name it wanted was taken meanwhile.

| Command | Does | Does not |
|---|---|---|
| `init` | Creates `.repos/` and the cortex folders in a fresh lab or clone | |
| `sync-repos [--repo <name>]` | Clones or fetches the repos in `repos.yaml` into `.repos/clones/`; names an experiment repo that has no system page | Write the page |
| `context-pack` | Compiles `cortex/query_pack.md` from the purpose, the gap map, the journal and the cortex index. A part that does not fit is cut at a line marked **[CUT]** | Choose a direction, replace reading the sources |
| `check-drift` | Reports system pages whose monitored code changed since their `Fingerprint` | Update any page |
| `new-exp --repo <r> --name <idea>/<sub-idea> [--base <branch>] [--title <t>] [--id <hh>]` | Gives the id; writes the lab folder and the journal row (`OPEN`) and publishes them; then creates the start branch from the base in a local worktree, with the lab kit and the notes (first plan template, empty log) | Write the first plan, commit or push the start branch |
| `new-try --exp <id> --name <try name> (--brief <text> \| --brief-file <file>) [--base <branch>]` | Writes the try record (status `live`, base, brief) and publishes it; then creates the try branch from the base (default: the start branch), commits the current lab kit and the brief into the plan's `This try` section, and pushes the try branch | Start a session; work the try |
| `mount --exp <id> --try <try name>` | Creates the local worktree of a try from its pushed branch | |
| `tries [--exp <id>] [--all]` | Prints the map: per live try its status, its signal and last commit date as read from its branch, who works it, and its last lab step. Flags a live try whose branch is missing. With `--all`, also the tries that left the map and into what | Change anything |
| `inbox --exp <id> --try <try name>` | Prints the try's signal and the notes to the lab in its log added after the commit its last lab step read | Write the cortex or the try record |
| `set-try --exp <id> --try <try name> [--status merged\|dropped\|live --into <try name>] [--worked-by <who>]` | Changes a try record's header lines and publishes | Write the `Reduced` section or a lab step record |
| `run --exp <id> --try <try name> -- '<command>'` | Runs a command in the try's local worktree with `.env`, `$LAB_ROOT` and `$EXP_DIR` set; output is shown as it comes | Record anything |
| `evaluate --exp <id> --try <try name> [--commit <sha>] [--eval-from <branch>] [--timeout <sec>]` | Writes `patch.diff`, then runs `evaluate.py` on that commit of the try and writes `evaluate.log` and `metrics.json` into the lab step's files folder ([evaluation.md](evaluation.md)) | Write the lab step record, compare with the baseline |
| `record-verdict --exp <id> --verdict <V> --kept <try name\|none> --metric-delta "<d>" --summary "<s>"` | Sets the verdict and the kept try in `results.json`, completes the experiment's row in the matrix, sets every try still `live` to `closed`, and publishes | Update Frontier, Sparks or the Banlist; write the postmortem |
| `cleanup-worktree --exp <id> --try <try name>` | Removes a local worktree | Delete a branch, a try record or the lab folder |

`new-exp`, `evaluate` and `record-verdict` each add a line to `cortex/log.md`.

The plans, the logs, the lab step records, the cortex and the journal's Frontier, Sparks and Banlist are written by hand. They carry judgment, so no command writes them.

What `lab.py` must hold to, so that the map stays the truth:

- A try exists only if it has a try record. `new-try` is the only way a try branch is created, also for the new try of a reduce.
- The lab's record is published before the branch is created, never after.
- `tries` and `inbox` read branches; they never decide a try's status from git ancestry or from a branch existing.
