---
name: experiment-lab
description: Build and maintain a research lab repository - an autonomous system that runs experiments in external experiment repos, with a cortex (its knowledge base of the field: claims anchored to outside sources and to experiments, and topic pages on top), a journal (the path of the research), a map of the tries each experiment is worked through, and a small CLI, all serving one loop (find a direction, open an experiment, work tries in rounds, reduce them, tell the lab through lab steps, conclude). Use when the user wants to create a new lab, rebuild one, add an experiment repo to it, change how the lab works, or find out why it is not serving the experiment loop. Ships a scaffold (AGENTS.md, the lab's own experiment-lab-loop skill, templates, lab.py). Not for running an experiment inside an existing lab - the lab's own AGENTS.md and its experiment-lab-loop skill direct that work.
---

<experiment-lab>

# Experiment lab

A research lab is a repository that holds the knowledge and the tools for experiments on other repositories (the experiment repos). An experiment there is one idea, worked through tries (each a branch of the experiment repo, worked in rounds of implement, run, analyze) until there is a conclusion. The lab exists so that this work compounds: what one experiment learns is where the next one starts.

This skill is for the person or agent who **builds or changes** such a lab. It is not read while an experiment runs. A lab that is built well directs its own agents: its `AGENTS.md` gives the picture, its own `experiment-lab-loop` skill describes the loop, its templates and its CLI carry the rest. If an agent inside the lab would have to come back here to know what to do, the lab is missing something, and the fix goes into the lab.

- **[The-autonomy-we-build-for]**: what the lab must be able to do, and the test every part is held to. Read this first.
- **[One-code-language-per-repo]**: the shared code language and shared components of an experiment repo. The part of a lab that decides whether its experiments add up. Read this second.
- **[What-the-loop-needs]**: the other ideas the design follows from.
- **[What-carries-the-picture]**: the parts of a lab, and how each reaches an agent.
- **[Create-a-lab]**: from an empty folder to a lab ready for its first experiment.
- **[Change-a-lab]**: adding an experiment repo, changing a behavior, handling a reject.
- **[Check-a-lab]**: finding out whether the lab serves the loop.
- **[Scripts-and-scaffold]**, **[References]**, **[Example]**.

Companion skills: `grow-autonomy` is the method behind this skill (how to change what agents understand, at the root); use it for every change and every reject. [Growing a lab](references/growing-a-lab.md) is that method in a lab's own terms. `cortex` is the skill the lab's knowledge base is built with: the lab is one cortex, and its `cortex/profile.md` says what is particular to it. `manage-skills` when editing the lab's skills.

</experiment-lab>

<The-autonomy-we-build-for>

The user wants to hand this lab requests of any size, at any moment, in any order: "fix this line in the cortex", "analyze the last run", "think of a new direction and run it to a conclusion". The last kind is the point. The lab is built so that a wide request comes back done well, with nobody watching the steps.

What that takes:

- **The request sets how far to go.** The lab has no automation level, no stages, no "human-in-the-loop mode". Nothing in its content says "ask before planning" or "the agent only implements": such a line describes one request and contradicts the next. A limit the user wants always (nothing is merged into an experiment repo's default branch) is a rule of the lab, written once with its reason.
- **The loop is semantic.** Whether a round taught something, whether a lesson matters to others, whether the idea is exhausted: these are judgments, and the agent makes them. No tool gates them. An experiment can spend many rounds in implementation and analysis before there is anything to conclude, and the lab must make that normal, not a violation.
- **The lab is whole wherever it is cloned.** A wide request may run in a cloud session that has nothing but the repo. Instructions, skills and tools live in the lab, and work that matters is pushed.
- **Tools serve the loop.** The CLI does the mechanical steps (ids and names, branches, the map of tries, running a command with the right environment, recording a result) so the correct path is the easy one. It decides nothing and blocks nothing.
- **The far goal is written down.** An agent holding a wide task has to choose a direction and decide when to stop. It can only judge those against what the lab is for and the hardest thing the user hopes to hand it one day.

The test for every part of a lab, and for every change to one: **does this help an agent that holds a wide request decide well without coming back to the user?** A part that adds a gate, a signature or an approval step fails it. A part that gives the agent a reason, a place to write, or an easier correct path passes.

Wide requests fail quietly. On a small request the user sees every mistake; on a wide one nobody reads every step. So the lab also asks for an honest report at the end of a wide request: what was decided along the way, what was assumed, what was not checked.

</The-autonomy-we-build-for>

<One-code-language-per-repo>

All experiments on one experiment repo are written in one shared code language and built from the same shared components. The lab calls this the repo's **Experiment Language**. It is the first thing to get right in a lab and the first thing to protect when changing one, because everything the lab promises rests on it.

**What it is.** For one experiment repo, recorded once on its system page:

- the mental model: what a run is, what an idea is allowed to change, what stays as it is;
- the vocabulary: one name per concept, used in code, plans, logs and the cortex alike;
- the **shared components** every experiment uses and none reimplements: loading and splitting data, the run entry point and its config object, the runner that sends a run to a machine and brings the results back, the tools for watching and analyzing a run, the evaluation;
- the **extension points**: the few named places where an idea goes in;
- the shape of what a run leaves behind (folder, file names, key names).

**Why the lab cannot work without it.**

- *Results can be attributed.* When two experiments share everything except the idea, a difference between them is about the idea. When each brings its own loader, loop and metrics code, a difference is about nothing in particular.
- *Experiments can be read.* Someone who understood experiment `0a` opens `0b` and sees only what changed. On a wide request nobody reads every step, so this is how the user, and the next agent, can check the work at all.
- *Tools carry over.* The observation and analysis tools written for one experiment work on the next, so each round is cheaper than the last and rounds can be compared.
- *Knowledge carries over.* A finding in the cortex is stated in the shared terms, so it applies to the next experiment without translation.
- *An agent can start.* A fresh agent with a new idea does not design a codebase. It finds the extension point and writes the idea.

Without it, the lab is a pile of unrelated branches, and no cortex or journal turns them into research that compounds.

**How it works in practice.**

- An idea goes in at an extension point. A variant is a config value or a flag, not a copied script.
- A shared component is used as it is. If it is wrong or too narrow, it is fixed as a shared component, the plan says so, and every later experiment inherits the fix. It is never forked into the experiment.
- Something new that more than this experiment will need (a metric, a plot, a data view) is written as a shared component, in the shared style, and added to the system page when the experiment is kept.
- The language itself changes only when that change is the idea of an experiment. Then the plan says so, and the system page is updated at close.
- When an idea does not fit the language, that is a finding, not an obstacle to code around. Stop and decide: either changing the language is the idea, or that change is its own experiment first.
- The test at any moment: read the experiment's diff against its base. It should read as the idea and nothing else.

**How a lab carries it** (so that no agent has to remember it):

- the system page holds it, with a table of shared components and a list of extension points;
- `AGENTS.md` states it first among the things that always hold, with the reason;
- the plan template asks which components and extension points the experiment uses, what stays fixed, and what it adds to the shared set;
- the postmortem template asks what happened to the language;
- a kept try branch carries the code and `EXPERIMENT_LANGUAGE.md`, and later experiments start from it (`new-exp --base`);
- a subagent's brief includes it, because a subagent that never saw the system page will write its own loader.

For a new or empty experiment repo, the language does not exist yet. The first experiment creates it ([Create-a-lab] step 5), and it deserves the care of a design that many experiments will live in.

</One-code-language-per-repo>

<What-the-loop-needs>

Four more ideas shape the rest. Each was learned from a lab that had it wrong; the mistake is noted so it can be recognized.

1. **An experiment is a line of inquiry, not a single gated test.** One idea, as many rounds as it takes. So the plan is a living page, rewritten in place as rounds teach something, and it carries a stopping point in free text that marks a moment to decide, not an automatic stop. *The mistake:* a signed plan, scope lists and guard/verify commands that check an experiment once. Agents then stop after one failed run, refuse to touch the plan, and invent their own folders for the rounds the design had no place for.

2. **How far to go comes with the request.** See [The-autonomy-we-build-for]. *The mistake:* a lab-wide level in an always-loaded file. Agents then ask for approval at each step of a wide request, or redesign the lab when asked to rename a function.

3. **An experiment has two memories, for two readers.** The working memory of each try (plan, log, run files) lives next to the code, on the try branch in the experiment repo, for whoever continues or reduces *this* try. What it tells the lab (the lab step records, cortex, journal, postmortem) is for whoever does a *different* experiment and will never open that branch. The question that separates them: would someone working on a different idea do their work differently if they knew this? *The mistake:* one kind of memory. Either every round's settings land in the cortex and bury what matters, or a lesson everyone needs stays in a branch nobody opens.

5. **The lab says which tries exist, and several tries become one by a reduce.** An idea is usually worked through several tries side by side, and most of them should end. So a try is opened through the lab, which records it in the experiment's map of tries; (one file per experiment, one short line per try); it is live while its line says so; and it ends when a reduce takes its code or its lessons into another try, or a lab step records what it showed. The start branch of an experiment is only a template, and the experiment's conclusion is the aggregation of the lab step records of its tries. *The mistake:* letting git say what is done. "Merged into main" then stands for "finished", an abandoned branch can never be finished, code lands on a branch nobody ran, and what a dropped try taught is lost with it.

6. **Two levels of sessions.** A try session works one try and sees only its branch. A lab session does the rest (open, reduce, lab step, close) and is the one that connects tries and experiments; when there are many tries, one long-running lab session manages them from the map and never loads their content. *The mistake:* one agent that both works a try and judges it against its siblings, or a manager that reads every log and has no attention left for the decision.

4. **The cortex is the lab's knowledge base of its field; the journal is the path of the research.** Research advances on everything that is known, and most of that was found by someone else: papers, documentation, data, other fields, a discussion. So the cortex gathers it as widely as it can, at any time, with no gap or experiment having to ask first, and the lab's own experiments enter it as one kind of source among the others, with no higher rank. Every claim is one sentence with an anchor that says where it comes from and how to check it: the words of a source, or an experiment round with its commit. topic pages are written per topic on top of claims of every anchor and rewritten freely. The journal is a different thing: what the lab did and decided, growing like a tree in the direction of the research. *The mistake:* a cortex that is the lab's memory of its experiments, where outside knowledge enters only when a gap asks for it and counts as a mere hypothesis. Agents then stop reading, the cortex knows only what the lab already tried, and every direction is a follow-up of the last experiment. The opposite mistake stays one: a page that presents a source's result as something the lab saw.

Some things are **this lab's own decisions**, and the skill only keeps a place for them: how a try is measured in a lab step and how cheap that has to be, what counts as a good result, where heavy runs go, which data may leave the machine. The scaffold ships a working default for the evaluation (one script in the experiment repo, its version recorded with every number). Keep it, change it or replace it according to what this lab measures; do not treat it as part of the method.

</What-the-loop-needs>

<What-carries-the-picture>

An agent acts on what reaches its context, and most of a repo never does. So each piece of the picture is placed by how it arrives.

| Part | Arrives | Carries |
|---|---|---|
| `AGENTS.md` | Always | What the lab is, how far to go, its structure, the glossary (every term, one concept one name; the only copy), the few things that always hold with their reasons, how to brief a subagent, where what was learned is written. Short. No procedure. |
| `cortex/purpose.md` | Pointed to from `AGENTS.md` for any task with a choice of direction | What the lab is for, the far goal, how results are judged here |
| `experiment-lab-loop` skill, inside the lab | When the task is about an experiment | The loop, written once: direction, opening, tries and rounds, reduce, what to tell the lab, lab step, managing many tries, closing. Its references: the system guide, each operation step by step, cloud sessions, the evaluation, the commands |
| Templates (`plan.md`, `log.md`, `tries.md`, `lab-steps.md`, `postmortem.md`) | When an experiment or a try is opened, at a lab step, at close | The behaviors themselves: a stopping point section, a "For the lab" line and a signal per round, a lab step record that names its commit, a line per provisional claim. A template outweighs a sentence. |
| `scripts/lab.py` | When used | The mechanical steps, so names, folders and environments come out right without being remembered |
| System page per experiment repo (`cortex/systems/`) | When working on that repo | The Experiment Language: shared components, extension points, vocabulary. Also data rules and known limits |
| `JOURNAL.md` | When choosing a direction | The path of the research: what was tried and concluded, what is best, what is next, what not to repeat |
| The rest of the cortex | When choosing a direction, and whenever something about the field has to be known | What is known about the field, from any source: topic pages on top of claims, each claim anchored to an outside source or to an experiment round |
| `cortex/profile.md` | Before any write to the cortex | What this cortex is for, its layout, what each kind of anchor earns here, when claims are written and settled, what a review checks |
| `cortex` skill, copied into the lab | When the task is on the lab's knowledge base | The operations: add a source, investigate a gap from outside, answer from what the lab knows, review. The forms of a claim and a page. A script that checks anchors and links |
| `.grow-autonomy/rejects.md` | Never, for working agents | The record of rejects, for the user and whoever maintains the lab |

Two rules follow. **Say each thing once**: the loop only in the lab's loop skill, a term only in the vocabulary, a rule only where it holds; a second copy drifts and the agent gets both. **What an agent would not know to look for must be given**: an agent asks "how do I open an experiment" by itself, and never asks "may this data leave the machine".

What each part must hold, and what goes wrong when it does not: [Parts](references/parts.md).

</What-carries-the-picture>

<Create-a-lab>

1. **Ask what only the user knows**, before writing anything, in their language and with concrete cases:
   - What is being researched, and on which experiment repos?
   - The far goal: the hardest thing they want to hand this lab one day. If they cannot say yet, record that; do not invent one.
   - What a good result is here, and how it is measured.
   - Where heavy runs go, and any data rules.
2. **Scaffold:**
   ```bash
   uv run <this-skill>/scripts/new_lab.py <lab-folder> --name "<lab name>"
   ```
   It copies the scaffold and prints the `{{FILL: ...}}` slots.
3. **Fill the slots** from the user's answers, in their terms. A slot the user has not answered stays visibly open ("Not written yet"), never filled with a guess. Turning a rough answer into fluent text adds meaning the user did not state; say back what an agent will take from the text and let them judge that.
4. **Register the first experiment repo** in `repos.yaml`, then `uv run scripts/lab.py init` and `sync-repos`.
5. **Write the repo's system page** from `cortex/systems/_TEMPLATE.md`. If the repo is new or empty, the Experiment Language does not exist yet: say so on the page. The first experiment on that repo then has one job: connect the pipeline end to end (data in, one short run, results back) and build the shared components every later experiment reuses, including the tools for watching a run. Its claim is narrow ("the pipeline is connected"), its numbers are not a baseline, and its Sparks are usually the first real task and the first evaluation. The system page template carries this case into the lab, and `lab.py` names a target that has no system page, so a target added later by the lab's own agents is onboarded the same way.
6. **Check the companion skills.** `new_lab.py` copies the skills the lab's content names (`cortex`, `grow-autonomy`, `code-as-tools`) into the lab when they are installed next to this skill, and says so when they are not. Install those, and the skills for where runs go, into the lab's own folders, not the user's home ([Running anywhere](references/running-anywhere.md)).
7. **Check it** ([Check-a-lab]) before the first wide request, and commit.

The scaffold is a starting point. After step 2 the lab's files are its own and will diverge from the scaffold as the lab learns; that is intended.

</Create-a-lab>

<Change-a-lab>

Every change to a lab is a change to what its agents understand, so it goes through `grow-autonomy`: find what the agent believed, change that where it lives, and record a reject in `.grow-autonomy/rejects.md` when there was one. [Growing a lab](references/growing-a-lab.md) walks that method through a lab's own parts and words; read it before the first change.

- **Change the part that carries the thing** ([What-carries-the-picture]). A behavior that agents keep missing usually belongs in a template or in the CLI, not in one more sentence of `AGENTS.md`.
- **Keep one copy.** When a behavior changes, find every place the old one is written or shown: `AGENTS.md`, the loop skill, `cortex/profile.md`, the templates, `lab.py` help texts, the README, old experiments agents read as examples.
- **Edit the lab, not this skill.** The lab's loop skill and `AGENTS.md` are the lab's own. Do not re-copy the scaffold over them to "update": that erases what the lab learned. Bring a general lesson back to the scaffold separately, if it holds for any lab. The `cortex` skill in the lab is an installed copy of the general skill: what is particular to this lab's cortex goes in `cortex/profile.md` and the templates beside it, not into the copy.
- **A new experiment repo:** an entry in `repos.yaml` with its own `short_name`, a system page with its Experiment Language, and a line in `cortex/index.md` (the comment in `repos.yaml` says the same to a lab agent that adds one). A later stage of the research is a new target, not a new lab.
- **A new stage in the loop, or a new tool:** hold it to the test in [The-autonomy-we-build-for] first.

</Change-a-lab>

<Check-a-lab>

A lab is checked by reading it the way its agents do, not by reading it as its author.

- **No open slots:** `grep -rn "{{FILL" --include=*.md .` is empty, or each remaining slot says honestly that the user has not answered.
- **Cold read:** a fresh agent, given only the lab and a request worded as the user would word it, says what the task is for, how far it will go, and what it will read first.
- **A small and a wide request:** the small one stays small; the wide one is carried through and ends with an honest report.
- **The CLI on a scratch experiment repo:** every command runs from a fresh clone.

The full pass, and the signs that show which part is failing: [Checking](references/checking.md). `audit-agent-context`, when installed, finds contradictions and stale text across the lab's content.

</Check-a-lab>

<Scripts-and-scaffold>

- `uv run scripts/new_lab.py <destination> --name "<lab name>"`: creates a lab from the scaffold and copies into it the skills its content names (`cortex`, `grow-autonomy`, `code-as-tools`). Never overwrites an existing file, so it is safe on a partly built lab. Prints the open slots.
- `assets/lab/`: the scaffold. `AGENTS.md` (the lab's `AGENTS.md`: structure, the glossary of every term, what always holds), `loop-skill.md` and `loop-references/` (become the lab's own `experiment-lab-loop` skill and its references), `README.md`, `JOURNAL.md`, `repos.yaml`, `pyproject.toml`, `cortex/` (profile, purpose, gap map, index, log, and the templates for a claim, a topic page, a source note and a system page), `experiments/_TEMPLATE/` (plan and log for the start branch, the map of tries, the lab step records, postmortem and results for the lab folder), and `scripts/lab.py`. Read a part here when deciding what a lab's own version should hold; edit it only to change what every new lab starts with.
- `assets/lab/scripts/lab.py`, in the lab as `uv run scripts/lab.py <command>`: `init`, `sync-repos`, `context-pack`, `check-drift`, `new-exp`, `mount-exp`, `run`, `evaluate`, `record-verdict`, `cleanup-worktree`. Standard library only. It does not yet have the commands for tries that the loop skill's `references/commands.md` describes (`new-try`, `tries`, `inbox`, `set-try`, `mount`, `evaluate --try`), nor the new experiment names: until it does, `commands.md` describes what it has to do.

Python in a lab is `uv` only: `uv run`, `uv add`, `uv sync`. No `pip install`, no bare `python`, no hand-made virtual environment, in the lab or in an experiment repo. One tool means a fresh clone on any machine reaches the same environment with one command.

</Scripts-and-scaffold>

<References>

- [Parts](references/parts.md): each part of a lab, what it must hold, and the failure that shows when it does not. Read it when creating a lab or deciding where a change belongs.
- [Checking](references/checking.md): the pass that tests whether a lab serves the loop. Read it before the first wide request and after any change of structure.
- [Growing a lab](references/growing-a-lab.md): `grow-autonomy` in a lab's terms: where a reject is traced, the words that carry judgment here, the beliefs behind the usual failures, and the reject journal. Read it before any change to how a lab works, and at every reject.
- [Running anywhere](references/running-anywhere.md): what makes a lab work from a fresh clone in a cloud session as well as on a laptop: skills in the repo, secrets, git access, what must be pushed. Read it when creating a lab and when a session elsewhere cannot continue the work.

</References>

<Example>

A user asks: "build me a lab for my retrieval research; in the end I want to give it a question and get back a tested answer."

1. **Ask.** Experiment repo: `rag-core`. Far goal, in their words: the lab picks a weakness of the retriever, tries ideas against it and tells them which one to ship. Good result: recall on their held-out question set, cheap enough to run in every round. Runs: one local GPU. Data: the question set never leaves the machine.
2. **Scaffold** with `new_lab.py`, fill `purpose.md` and the three slots at the end of `AGENTS.md` from those answers, register `rag-core` with `short_name: rag`.
3. **System page.** `rag-core` has code already, so the Experiment Language is written from it. Shared components: the indexer, the question loader, the run entry point with its config, the recall report. Extension points: the retriever and the reranker, behind their existing interfaces. An idea changes one of those two and nothing else.
4. **Check.** A fresh agent given "see if query rewriting helps" explains it will open an experiment, cross the idea with the gap map and Banlist, and work in rounds until the plan's stopping point. Given "fix the typo in the gap map", it fixes the typo and stops. The CLI runs on a scratch clone.
5. **Two weeks later, a reject.** The lab closed an experiment as refuted after one run that crashed on a full disk. This is not fixed with "IMPORTANT: never refute after a crash". `grow-autonomy`: the agent believed a failed run is a result. The rule about technical failures was in `AGENTS.md`, but the log template had no place to say which kind of failure a round was. The template gets it, the reject is recorded, and nothing is added to `AGENTS.md`.

</Example>
