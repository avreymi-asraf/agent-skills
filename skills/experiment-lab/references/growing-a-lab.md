# Growing a lab

This is `grow-autonomy` in a lab's terms. The general skill is about any agent system; here the same method is given with a lab's parts, a lab's words and the failures labs usually show. Read it before changing how a lab works, and at every reject. It is enough for most changes. Go to the full `grow-autonomy` skill when the cut of the work between agents has to be redesigned, or when a new kind of task needs its information flow mapped from nothing.

## What grows

How hard a request the lab can take: from "fix this line in the cortex" to "find a direction and run it to a conclusion". There are no levels. Every request carries its own size, and a wide one can be followed by a tiny one in the same hour.

The far goal is in `cortex/purpose.md` §2, in the user's words. Every change is judged twice: does it fix today's request, and does it build something the far goal needs?

Two things decide whether a wide request comes back well: **the picture** each agent has of its piece, and **attention**, which information reaches which agent. In a lab both are made of a small number of parts, and every change lands in one of them.

## Who reads what

Three kinds of agents work in a lab, and each has a different picture:

| Agent | Has from the start | Gets only if |
|---|---|---|
| The one holding the request, at the lab root | `AGENTS.md`, the names of the skills | It loads the loop skill (the request is about an experiment); it opens `cortex/purpose.md`, `cortex/profile.md`, the system page |
| One working a try, in a try session | The lab kit on its try branch (the try `AGENTS.md`, the lab's skills), `EXPERIMENT_LANGUAGE.md`, its plan with the brief | It attaches the lab for reading: the cortex, the journal, its own try record. The lab's `AGENTS.md` is not on its branch |
| A subagent | Its brief | The brief carries it. It sees no conversation, no file already read |

Most rejects on wide requests are found in the third row. The subagent did its piece correctly, and the reason for the piece never reached it.

What each part of the lab carries, and how it arrives, is the table in the skill's [What-carries-the-picture]; what each must hold is in [Parts](parts.md).

## Bringing a behavior in

The user wants the lab to work in a certain way: "every run should say in advance what would stop it early". The shallow way is one more sentence in `AGENTS.md`. The agent then complies where the sentence fits and misses everywhere else.

Ask instead what the behavior is for, who needs it, and which part of the lab carries that kind of thing:

| The behavior is about | It usually belongs in |
|---|---|
| Something to ask in every round | A field in the log template (`Run plan`, `For the lab`, `Signal`) |
| Something decided when an experiment opens | The plan template |
| Something settled when it closes | The postmortem template and the closing steps of the loop skill |
| What is worth writing to the lab's memory, and how far it is trusted | `cortex/profile.md` and the claim and findings templates |
| How code is written in an experiment repo | The system page (Experiment Language) |
| A mechanical step that keeps coming out wrong | `scripts/lab.py`: make the right path the easy one |
| What a word means | The vocabulary in `AGENTS.md`, once, with an example |
| Something the user wants always | "What always holds" in `AGENTS.md`, with its reason |
| What a subagent must be told | The attention section of `AGENTS.md` |

A field in a template is a behavior. A sentence is a hope. Then find what pulls the other way: an old experiment that agents read as an example, a `lab.py` help text, a line in the README. Examples outweigh prose, so they change too.

## When work is rejected

Open the entry in `.grow-autonomy/rejects.md` first, with the request and the reject in the user's own words. Then trace; do not fix yet.

A lab leaves an unusually good trail, because its agents write their decisions down. For the rejected decision, establish as fact:

- **The request,** worded as it was given, and how much it left to the lab.
- **Which agent decided:** the one holding the request, or a subagent. For a subagent, find the brief it was given.
- **What it had read by then.** The try's `plan.md` with its brief and its history (`git log -p -- notes/<experiment name>/plan.md` on the try branch), the round entries in `log.md` (`Run plan`, `Decided`, `For the lab`), the try record with its lab step records, the claims written from it (`cortex.py claims --from <experiment name>`), `cortex/log.md`, the postmortem, the experiment's diff against its base. When session transcripts exist, `audit-agent-context` with traces shows which files were opened and in what order.

Then name, in one sentence, what the agent believed that made its action look right. If you cannot, you are still looking at the symptom.

## The beliefs behind the usual failures

A wrong belief produces a family of mistakes; the one the user rejected only surfaced first. These are the families labs show most. Use the neighbors as the test of a fix: after the change, is each of them clearly wrong to an agent that read only the lab?

| The belief | What it produces (the reject, and its neighbors) | Where the root usually is |
|---|---|---|
| "An experiment is a test that passes or fails." | Closed as refuted after one failed run; a crash counted as a result; the plan never edited after day one; work stops dead at the stopping point | The vocabulary; a plan template that reads as a contract; a log template with no place for the kind of failure |
| "The job is to produce a number." | Evaluation on leaked data; the best seed reported; numbers from two evaluation versions compared; a threshold tuned on held-out data | `purpose.md` §3 is empty or generic; data rules missing from the system page |
| "This experiment is my codebase." | A private loader; a copied script per variant; a shared component forked; a diff that is mostly plumbing | The Experiment Language is not on the system page, or did not reach the subagent that wrote the code |
| "The cortex is where things get written down." | One experiment's settings in a findings page; a claim per sentence of a paper; a page per source. Or the opposite: a lesson everyone needs, left in a branch log | `cortex/profile.md` §1 does not carry the loop's test; the log template has no `Told the lab` line |
| "What is written in the cortex is known." | A paper's result presented as the lab's finding; a Banlist entry that rests on a quote; a plan built on a withdrawn claim; two contradicting results averaged into "mixed" | The anchor of a claim does not reach the page; the findings template has no `Rests on` line; nothing asks for a tension |
| "A new direction is the next item on the list." | Ten experiments on one knob; never reading outside the lab; never questioning the task itself | The far goal is unwritten; every Spark is a follow-up, because that is what the postmortem asks for |
| "Wide means finish." | No report of what was assumed; a direction chosen without crossing it with the cortex; a run that answers nothing left to burn GPU hours | `AGENTS.md` §1; nothing asks for a run plan |
| "The user has to approve." | Approval asked at every step of a wide request | A level, a mode or an "ask before" left somewhere in the content |

The fix goes where all the neighbors pass through, and it is often not text: a template field, a named split in a loader, a line the CLI prints. A good fix leaves no trace of the incident. Do not write the neighbors into the lab as rules; they measure the fix and stay out of the content.

## Where a lesson goes

A lab has more levels of memory than most systems, and each lesson belongs to one. The question is always for whom it is true (`grow-autonomy`, Levels-of-memory):

| True for | Written in |
|---|---|
| This try | `notes/<experiment name>/` on its try branch: `plan.md`, `log.md` |
| This experiment | The lab step record of the try that showed it, in the lab folder |
| The research: a different experiment should know it | The cortex: a claim, and the findings page or gap it changes |
| How this lab works | The lab's own files: `AGENTS.md`, its `experiment-lab-loop` skill, the templates, `cortex/profile.md`, `lab.py` |
| Any lab | The scaffold in this skill (`assets/lab/`), proposed to the user and changed here, not by re-copying over a living lab |
| Anyone who uses `cortex`, `grow-autonomy` or a run skill | The source of that skill, proposed to the user. The copy in the lab's `.agents/skills/` is not edited |
| The user, in every project | The user's own instructions |

The lab's `AGENTS.md` holds this as a few short lines (its last section), so that every agent asks the question before it finishes. When the same kind of lesson keeps landing at the wrong level, that is a reject like any other: find what the agent believed about where things go.

## Words that carry judgment here

"Experiment", "round", "conclusion", "finding", "refuted", "provisional", "baseline", "kept", "exhausted", "a new direction", "worth trying". Each has one meaning, written once in the vocabulary. The user may think in another language than the lab is written in (ניסוי comes out as experiment, trial or test, and each brings its own associations), so agree on cases and not on sentences:

- "The run crashed after one step. Is the experiment closed?"
- "A paper says this method collapses. Is that a finding of the lab?"
- "The number went up by 0.3 and the code doubled. Is that a good result?"

Before writing the answer into the lab, say back to the user, in their language, what an agent will do because of the text. They judge the consequence, not the English.

## The reject journal

`.grow-autonomy/rejects.md`, one entry per reject, opened before anything is fixed. Working agents do not read it and its entries never become rules.

```
## YYYY-MM-DD · <short name>

- Request: the user's words, verbatim, in their language. How much it left to the lab: one line.
- What the lab did: the part that was rejected. Experiment and round, if any. Which agent decided it.
- Reject: the user's words, verbatim.
- What the agent had: what had reached it by then (files, skill, brief), and what had not.
- Belief: one sentence.
- Root: why it believed that. Which part of the lab.
- Neighbors: two or three other mistakes the same root would produce.
- Change: what was changed and where (template, profile, CLI, vocabulary, brief).
- Check: how it was tested (a cold read, a borderline case, a run) and what happened.
```

"Root: unknown" is an honest entry. Before changing a part of the lab, read the entries for that part: they say which paragraphs are there because a root was once found. Read the whole journal from time to time for what returns, and tell the user which kinds of wide requests have stopped producing rejects. That is the evidence that the lab has grown.

## A worked case

**The request** (wide): "תמצא כיוון חדש לשיפור ה-recall ותריץ אותו עד מסקנה".

**What came back.** An experiment that raised the retrieval depth from 20 to 50, closed as `HYPOTHESIS_SUPPORTED` with +1.1 recall.

**The reject.** "זה לא כיוון חדש, זה אותו ניסוי כמו 0c עם מספר אחר."

**The plaster.** "IMPORTANT: a new direction must differ from previous experiments." The next wide request changes the chunk size.

**The trace.** The plan's "Crossed with what the lab knows" cites experiment `0c` and takes its Spark, "try a larger k". The agent read the gap map, the Sparks and the Banlist, as the loop asks. All four Sparks in the journal are follow-ups of the last two experiments. `purpose.md` §2 says "Not written yet".

**The belief.** "A new direction is the most promising open item on the lab's lists."

**The root.** Two things. Nothing in the lab says what the user counts as a direction, and the lists hold only increments, because the postmortem template asks for "the follow-up idea this experiment makes most worth trying". The agent chose well from what it was given.

**Neighbors.** It will keep turning the same knob; it will never read outside the lab; it will never ask whether recall on this question set is the right thing to measure.

**The change.** The user was asked with cases ("a different reranker: new direction? query rewriting? a different retrieval unit?") and the answer went into `purpose.md` in their words: a direction changes what the system does, not how hard it does it. The postmortem's Sparks section now asks for two: the follow-up, and one idea that leaves this line of work. Nothing was added to `AGENTS.md`.

**The check.** A fresh agent, given the same request, starts by investigating the oldest open gap from outside sources and proposes two ideas that touch different extension points. Asked for "a quick follow-up on 0c", it still does the increment: the fix did not fence off a reasonable request.
