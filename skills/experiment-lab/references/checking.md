# Checking that a lab serves the loop

Run this before the first wide request, after any change of structure (a part moved, a skill split, a new target), and when rejects pile up without a clear source. It reads the lab as its agents do. Most of it is heavy reading with a small result, so the cold reads are good work for subagents.

## 1. Static

- `grep -rn "{{FILL" --include=*.md .` : no slot is left, or each one states plainly that the user has not answered yet.
- No level words in the content: search for "level", "mode", "approval", "human-in-the-loop", "ask before". A hit is either a rule the user wants always (then it has a reason next to it) or a leftover.
- One copy of the loop: `AGENTS.md` points to the loop skill and does not restate it. The README does not restate it either.
- One name per concept: the vocabulary in `AGENTS.md` matches the words used in the loop skill, the templates and `lab.py --help`.
- No absolute or machine-specific path in any tracked file.
- One entry point: `AGENTS.md`. The README, the journal and the wiki index do not each claim to be the page to read first.
- Every pointer leads to content. A line that says "read X before writing code" where X is a list of empty headings teaches agents to skip pointers.
- No example content that looks real: a sample gap, Spark, experiment row or target repo left from a template will be picked up and worked on.
- Nothing an agent needs lives outside the repo ([Running anywhere](running-anywhere.md)).
- What the docs say a command does is what it does. Read `lab.py`, do not trust the table.

## 2. Cold read

Start a fresh agent in the lab with a request worded as the user words it and nothing explained on the side. Before it works, ask open questions:

- What is this task for?
- How far will you go, and where will you stop?
- What will you read first?
- What are you unsure about?

Use at least three requests: a tiny one ("fix this wiki line"), a middle one ("analyze the last round of experiment 0a"), and a wide one ("find a direction and run it to a conclusion"). Compare the answers with what the user means. Keep the questions open: "will you ask for approval?" hands over the thing being tested.

Ask the same agent to explain "experiment", "plan" and "conclusion" in its own words, and what it would do in two borderline cases:

- A run crashed on the first step. Is the idea refuted?
- A round showed that a data field leaks the label. Where does that get written, and when?

Bring the answers to the user: is this what you meant?

## 3. A run

Let an agent carry a real, small experiment on a scratch target, then read the transcript for the flow and not for the result: which files it opened and in what order, what it looked for and did not find, where it guessed, whether it loaded the loop skill, what it wrote in the log and what it told the lab.

Then check a wide request ends with a report that names what was decided, assumed and not checked.

## 4. The CLI from a fresh clone

Clone the lab into an empty folder and run every command against a scratch target repo: `init`, `sync-repos`, `new-exp`, `run`, `evaluate` (with a missing, a failing and a valid evaluation), `record-verdict`, `cleanup-worktree`, `mount-exp`. A lab that only works on the machine it was built on cannot take a wide request in a cloud session.

## 5. Housekeeping

A lab that has run for a while collects leftovers that later agents read as state: worktrees of closed experiments, target branches that are no experiment, Sparks that were done, experiments opened and never closed. List them for the user with what each is; remove only what the user confirms. The wiki's own upkeep is the `review-wiki` pass.

## Signs, and the part they point to

| What is seen | Likely root | Part |
|---|---|---|
| The agent asks for approval at each step of a wide request | A level or a pause is written somewhere, or nothing says the request sets how far to go | `AGENTS.md` |
| The agent starts an experiment when asked for a small fix | The loop sits in the always-loaded file | `AGENTS.md`, loop skill |
| An experiment is closed as refuted after one failed run | "Experiment" reads as a single test; the log has no place for the kind of failure | Vocabulary, log template |
| The plan is never edited after the first round | The plan reads as a contract | Vocabulary, plan template |
| Agents invent folders or files for their rounds | The templates have no home for what a round produces | Templates, `lab.py new-exp` |
| The wiki fills with one experiment's settings | The two readers are not separated | Loop skill: what to tell the lab |
| A lesson everyone needed is found only in a branch log | Same root, other direction; or the round entry has no "Told the lab" line | Log template |
| Each experiment has its own layout and names | No Experiment Language, or it is not on the system page | System page |
| Frontier, Sparks or Banlist are stale | The docs say a command updates them | `lab.py` docs, closing steps |
| The agent picks a direction that serves nothing | The far goal is missing, or is template text | `purpose.md` |
| A subagent did its piece correctly and the whole is wrong | The brief dropped the reason | `AGENTS.md` attention section |
| Runs are started and only read when they finish; GPU time is spent on runs that answer nothing | Nothing asks for a run plan before the run, or the target has no tools for watching one | Log template, system page (Observation) |
| A cloud session cannot continue an experiment | Something was not pushed, or a path is machine-specific | What always holds; `mount-exp` |

When a sign appears after a real request the user rejected, it is a reject: open an entry in `.grow-autonomy/rejects.md` first, then follow `grow-autonomy` to the root. Do not fix signs one by one; several usually share a root.
