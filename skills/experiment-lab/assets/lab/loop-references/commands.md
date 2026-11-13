# `lab.py` commands

All commands run from the lab root as `uv run scripts/lab.py <command>`, from a checkout of the lab's default branch. They exist only in the lab; a try session never needs them.

`--exp` takes the id (`02`) or the full experiment name (`02-probes`). `--try` takes a try name.

"Publishes" below means: commits the lab's change, pulls with rebase, and pushes to the lab's default branch, retrying when the push is rejected. A command that publishes first brings the lab up to date, and it fails, takes its commit back and creates no branch when the id or the try name it wanted was taken meanwhile. Records written by hand and not committed yet are committed first, in a commit of their own, and published with it; so what a command takes back is only what it wrote. In a lab with no remote, or with `--no-publish` before the command, the record is committed and not pushed, and the command says so. Publishing pushes this checkout's commits to the lab's default branch: on another branch that holds commits of its own, every publishing command refuses.

| Command | Does | Does not |
|---|---|---|
| `init` | Creates `.repos/` and the cortex folders in a fresh lab or clone | |
| `sync-repos [--repo <name>]` | Clones or fetches the repos in `repos.yaml` into `.repos/clones/`; names an experiment repo that has no system page | Write the page |
| `publish -m "<what changed>"` | Publishes every change in `experiments/`, `cortex/` and `JOURNAL.md`: what was written by hand in a lab step, a reduce, a close or a cortex edit | Touch anything else in the lab (skills, `lab.py`, templates) |
| `context-pack` | Compiles `cortex/query_pack.md` from the purpose, the gap map, the journal and the cortex index. A part that does not fit is cut at a line marked **[CUT]** | Choose a direction, replace reading the sources |
| `check-drift` | Reports system pages whose monitored code changed since their `Fingerprint` | Update any page |
| `new-exp --repo <r> --name <idea> [--base <branch>] [--title <t>] [--id <hh>]` | Gives the id; writes the lab folder and the journal row (`OPEN`) and publishes them; then creates the start branch from the base in a local worktree, and writes the experiment template on it: the lab's `start-branch/` folder (the try `AGENTS.md`, with the experiment name and the lab commit filled in; `notes/` as `notes/<experiment name>/`: first plan template, empty log), `CLAUDE.md` and `GEMINI.md` pointing to `AGENTS.md`, and the lab's `.agents/skills/` with their `.claude/skills/` links. When the base has no `EXPERIMENT_LANGUAGE.md`, it adds the form of one. On an empty experiment repo the start branch is the repo's first branch. It notes every file of the repo's own that the lab kit replaced | Write the first plan, commit or push the start branch |
| `new-try --exp <id> --name <try name> --comment "<at most 100 characters>" (--brief <text> \| --brief-file <file>) [--base <try name or branch>]` | Adds the try's line to `tries.md` (try branch, `live`, the comment) and publishes it; then creates the try branch from the base (default: the start branch), commits the base and the brief into the plan's `This Try` section, and pushes the try branch. It copies no template: the lab kit and the notes come with the base. With `--base <try name>` the plan comes from that try, and its `This Try` section is replaced by the new brief | Start a session; work the try |
| `mount --exp <id> --try <try name>` | Creates the local worktree of a try from its pushed branch. `--try main` mounts the start branch, for writing the first plan in a fresh clone | Mount a try that has no line in the map |
| `tries [--exp <id>] [--all]` | Prints the map: per live try its status, its signal and last commit date as read from its branch, its comment, and its last lab step (from `lab-steps.md`). Flags a live try whose branch is missing. With `--all`, also the tries that ended, and into what | Change anything |
| `inbox --exp <id> --try <try name>` | Prints the try's signal and the notes to the lab in its log added after the commit its last lab step read | Write the cortex or a lab step record |
| `set-try --exp <id> --try <try name> [--status merged\|dropped\|live] [--into <try name>] [--comment "<at most 100 characters>"]` | Changes the try's line in `tries.md` and publishes. Refuses once the experiment is closed | Write a lab step record or the log entry of a reduce |
| `run --exp <id> --try <try name> -- '<command>'` | Runs a command in a live try's local worktree with `.env`, `$LAB_ROOT` and `$EXP_DIR` set; output is shown as it comes | Record anything |
| `evaluate --exp <id> --try <try name> [--commit <sha>] [--eval-from <branch>] [--timeout <sec>]` | Writes `patch.diff`, then runs `evaluate.py` on that commit of the try and writes `evaluate.log` and `metrics.json` into the lab step's files folder `steps/<try name>-<short commit>/` ([evaluation.md](evaluation.md)). The evaluation runs in a temporary worktree at that commit, never in a working copy someone works in | Write the lab step record, compare with the baseline, publish |
| `record-verdict --exp <id> --verdict <V> --kept <try name\|none> --metric-delta "<d>" --summary "<s>"` | Sets the verdict and the kept try in `results.json`, completes the experiment's row in the matrix, sets every try still `live` to `closed`, and publishes. Refuses an experiment that is already closed | Update Frontier, Sparks or the Banlist; write the postmortem |
| `cleanup-worktree --exp <id> --try <try name> [--force]` | Removes a local worktree; refuses when it holds work that is not pushed, unless `--force` | Delete a branch, a line of the map or the lab folder |

`new-exp`, `evaluate` and `record-verdict` each add a line to `cortex/log.md`.

The plans, the logs, the lab step records, the cortex and the journal's Frontier, Sparks and Banlist are written by hand. They carry judgment, so no command writes them.

What `lab.py` must hold to, so that the map stays the truth:

- A try exists only if it has a line in `tries.md`. A comment longer than 100 characters is refused. `new-try` is the only way a try branch is created, also for the new try of a reduce.
- The lab's record is published before the branch is created, never after. So a command that stops between the two leaves a record with no branch, and it is finished, not undone: run the same `new-try` again (it sees a `live` line with no branch and creates the branch), or `mount --exp <id> --try main` for a start branch (it creates it from the recorded base).
- `tries` and `inbox` read branches; they never decide a try's status from git ancestry or from a branch existing.
