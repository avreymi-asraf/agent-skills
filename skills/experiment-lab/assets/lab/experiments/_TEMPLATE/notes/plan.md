---
exp_name: <exp-name>
title: "<title>"
date: YYYY-MM-DD
target_repo: <target-repo>
base_branch: <base-branch>
exp_branch: <exp-name>/main
linked_gaps: []      # e.g. G11 from cortex/gap_map.md
inspired_by: []      # e.g. SPARK-03 from JOURNAL.md
data_source: "<repo>@<ref>:<path>"  # e.g. data-repo@main:data/samples/v1 (never a local path)
---
# Plan: `<exp-name>` — <title>

> This page is the **current** best description of how to realise the idea. On the start branch it is the first plan, written when the experiment is opened. Every try carries it, with its brief in section 5, and rewrites its own copy in place after every round that teaches something. The history is in `log.md`, next to this file.

## 1. The Idea
* **Idea:** [What we want to try, in one or two sentences. This part is stable: if it has to be replaced, close the experiment and open a new one.]
* **Why it is worth trying:** [The gap or Spark it answers, and how it serves `cortex/purpose.md`.]
* **Crossed with what the lab knows:** [Findings, claims, tensions, earlier experiments and Banlist entries that bear on it, and what they change. Say for each where it comes from: an outside source, or an experiment of the lab; and whether its conditions match this experiment's.]
* **Alternatives considered:** [Other directions that were weighed and why this one was chosen. For one that is worth an experiment of its own: the `SPARK-nn` it was given in `JOURNAL.md`.]

## 2. What We Know and How We Will Do It
[The realisation, as exact as present knowledge allows and no more. May start high-level. Name the files, extension points and settings once they are known.]

* **Experiment Language** (from `EXPERIMENT_LANGUAGE.md` at the repo root):
  * **Extension point:** [Where the idea goes in.]
  * **Shared components used as they are:** [Data, run entry and config, runner, observation and analysis tools, evaluation.]
  * **What stays fixed for every try:** [The data and split, and the measurement competing tries will be compared on, so that a difference can be attributed to the idea.]
  * **Added to or changed in the shared set:** [None | the new component or the fix, and why every later experiment should inherit it. If the Experiment Language itself is what changes, say that this is the idea.]

## 3. Open Questions
* [What the tries have to find out.]

## 4. Stopping Point
[Free text. What result would be enough. What would make it not worth continuing: a budget of GPU hours or rounds, a sign that the idea is exhausted. Reaching it is the moment to decide, with a reason, whether to conclude or go on.]

## 5. This Try
[Empty on the start branch. `new-try` writes the try's brief here: what to try and what makes this try different from its siblings, whether it competes or cooperates with which tries, how far to go, when to stop and flag. Whoever works the try adds how it will do it and its own open questions.]
