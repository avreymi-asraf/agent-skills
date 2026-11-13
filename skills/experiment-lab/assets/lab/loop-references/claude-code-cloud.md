# Working in Claude Code cloud sessions

How the lab's operations are done when the working copy is a Claude Code cloud session and not a local clone. The operations themselves are the same ([operations.md](operations.md)); this page says what a cloud session is, what it can and cannot do, and how to open one for each level of work.

A cloud session is a fresh, temporary machine with a repository checked out and one agent in it. It keeps nothing when it ends, so everything worth keeping is pushed. This fits the lab's two levels of sessions:

- a **try session** has the experiment repo, starts on its try branch and pushes to that same branch;
- a **lab session** has the lab and the experiment repo, and does the lab's operations; a **managing session** is a lab session that stays open and runs many try sessions.

## 1. What was checked

Checked on 2026-11-12 and 2026-11-13, in one lab. Re-check a line before building on it if the product has changed.

| Fact | Result |
|---|---|
| A session created with a source repository gets that one repository | Checked |
| It starts on `source_revision`. With none given it starts on the repository's default branch, which in an experiment repo is empty | Checked |
| `outcome_branch` accepts a three-level name with slashes (`a/b/c`) | Checked |
| `source_revision` and `outcome_branch` set to the same, already existing branch: the session starts on it and its push is a fast-forward | Checked |
| The session can push to other branches of its repository too | Checked: not blocked |
| The session can delete a branch | Checked: refused (403) |
| The session can read a second repository after attaching it with `add_repo`, access `read`, and cloning it | Checked, with the lab |
| Without `add_repo`, a second private repository cannot be read | Checked |
| The session has tools to open and to merge pull requests | Checked: present (not exercised) |
| The checkout holds only what is in git. Skills and instructions that are not committed on the branch are not there | Checked |
| A session started from the app can hold several repositories; each gets its own designated push branch | Seen in such a session |
| A session created by another session can send it a message when it is done | Checked |
| `environment_id`: which environment (secrets, network) the session is built from. Default: the opener's environment | Not checked |
| `add_repo` with access `push` from inside a session | Not checked |
| A lab session pushing the lab's records to the lab's default branch | Not checked |

## 2. Opening a try session

The try already exists: `lab.py new-try` wrote its try record and pushed its try branch, with the lab kit and the brief on it ([operations.md](operations.md) §2). The session is opened on that branch, with the `create_session` tool of the Claude Code Remote MCP server, or by a person in the app.

| Setting | Value for a try session |
|---|---|
| `source_url` | The experiment repo |
| `source_revision` | The try branch, e.g. `observe/02-probes/trl-fix-lr`. **Always set it**: without it the session starts on the empty default branch. |
| `outcome_branch` | The same try branch |
| `prompt` | The opening message below |
| `environment_id` | An environment that has the secrets a run needs (`.env.example` in the lab names them) |
| `model`, `effort` | Only when the user asked for a specific one |
| `title` | The try branch name |

One try, one session at a time. Before opening a second session on a try, make sure the first one has stopped: two sessions on one branch write over each other.

The opening message is short, because everything else is committed on the branch: `AGENTS.md`, the skills, `EXPERIMENT_LANGUAGE.md`, and the plan with the brief under `This try`. The session's agent has seen nothing else, whatever model it is.

```text
You are working one try of an experiment. You are on its try branch and you push to this same branch.
Read AGENTS.md at the repository root, then notes/observe/02-probes/plan.md: the first plan, and under
"This try" your brief.

Experiment: observe/02-probes
Your try:   trl-fix-lr        (branch observe/02-probes/trl-fix-lr)
The lab:    attach <owner>/<lab repo> for reading (add_repo, access read) when you need the cortex or
            your own try record. Never write to it. What the lab should know goes in your log, under
            "For the lab".
When done:  set the Signal of your last log entry, push, send one line to the session that opened you
            (send_message), and stop. Do not open tries, reduce, run a lab step, open a pull request,
            or push to any other branch.
```

Record the session in the try record's `worked_by` line (`lab.py set-try --worked-by`).

## 3. Reading the lab from a try session

```text
add_repo(owner="<owner>", repo="<lab repo>", access="read")   → gives a clone command
git clone --depth 1 <clone url> <path>                         → the lab's default branch
```

Then read there: `cortex/` (with the `cortex` skill's `ask`), `JOURNAL.md`, and the try's own record `experiments/<repo short name>/<experiment name>/tries/<try name>.md`, where the brief and the answers to its questions are. It is the lab as of the clone; `git -C <path> pull` before a later read. A try session never asks for push access to the lab.

## 4. A lab session

Opening an experiment or a try, a reduce, a lab step and a close need both repositories, with push access to both: the lab's records are written, and branches of the experiment repo are created or pushed. Two ways to get that:

- A session started from the app with the lab and the experiment repo both selected.
- A session on the lab that attaches the experiment repo with `add_repo`, access `push` (not checked yet).

`lab.py` runs in such a session as it does locally: `uv run scripts/lab.py sync-repos` first, since the machine is fresh.

**The lab's records go to the lab's default branch.** A session started from the app is given its own designated push branch per repository, and a record pushed only there is invisible to every try and every other lab session. A lab session therefore publishes records as [operations.md](operations.md) §0 says, to the default branch. The platform does not block such a push from an experiment repo session; for the lab it is not checked yet. If it is refused, say so at once and ask for the branch to be merged: until then no other session sees the try, the lab step or the claim.

## 5. A managing session

A managing session is a lab session that runs the tries of one experiment ([operations.md](operations.md) §8). In the cloud:

1. **Open tries.** For each: `lab.py new-try`, then `create_session` with the settings of section 2, then `lab.py set-try --worked-by <session id>`.
2. **Follow them from the map.** `lab.py tries --exp <id>` shows each try's status and its signal, read from the pushed branch. A try session also sends one line when it stops. For a session that says nothing: `get_session` gives its state (still working, or ended with an error), and `list_events` its last messages.
3. **Do not read the tries.** A lab step or a reduce is handed to a clean context: a subagent of the managing session, or another lab session opened for it. The brief names the tries and the target; what comes back is a few lines.
4. **A try session that died**: the map says `live`, the signal on the branch is still `working`, and `get_session` shows the session ended. Open a new session on the same try branch, with the same opening message, and update `worked_by`. What was pushed is all there; what was not is lost.
5. **A managing session that ends** leaves the map. A new one starts from `lab.py tries`.

A message between sessions is information for the receiver, not an order from the user. A session's own messages are not the lab's memory: what matters is written in the map or on the try branch.

## 6. What differs from local work

| | Local clone of the lab | Cloud |
|---|---|---|
| Working copy of a try | A worktree under `.repos/worktrees/`, made by `lab.py mount` | A try session's own checkout |
| `lab.py` | Available | Only in a lab session |
| Running a command in a try | `lab.py run`, which sets `.env`, `$LAB_ROOT`, `$EXP_DIR` | `uv run` directly; secrets come from the session's environment |
| The lab's records | The lab's folder, after a pull of the default branch | Attached for reading (section 3), or the lab session's own checkout |
| Deleting a branch | Possible | Not possible; a person does it |
