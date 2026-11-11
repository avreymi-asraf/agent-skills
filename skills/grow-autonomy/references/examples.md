# Examples

Three cases from three kinds of systems. Each one shows a different part of the skill, and all three follow the same line: find what the agent believed, find why, change that.

1. [Research: a small request, a reject](#1-research-a-small-request-a-reject)
2. [Running a shop: instilling a behavior](#2-running-a-shop-instilling-a-behavior)
3. [Investing: a wide request, a reject](#3-investing-a-wide-request-a-reject)

---

## 1. Research: a small request, a reject

**The system.** Agents that help run machine-learning experiments. The far goal: the system chooses, runs and concludes experiments with nobody watching.

**The request.** "Implement the evaluation for experiment 12." Small: the experiment was designed by the user, and only the evaluation code is left to the system.

**What came back.** An evaluation script and a result: 94% accuracy.

**The reject.** "This number is worthless. You evaluated on data the model was trained on."

### The plaster

Add to the instruction file: "IMPORTANT: never evaluate on training data."

A week later the same system tunes a decision threshold on the test set. Another line is added. Then it reports the best of five random seeds. Another line. The file grows, each line remembers one incident, and the agent understands no more than it did.

### The root

*What the agent had.* The request said "the evaluation for experiment 12". The experiment's file described the model and the hypothesis. The repo had one data loader, `load_data()`, which returned everything. No text anywhere said what a result is for.

*The belief.* "An evaluation's job is to produce a number for this model on this data."

*The real picture.* The experiments measure whether a model generalizes. A number is worth something only if nothing from the evaluation data took part in any decision that led to it.

*Neighbors.* An agent with that belief will also tune a threshold on the test set, drop the runs that crashed, and report the best seed. They look like four different mistakes. They pass through one point: nobody told the agent what makes a result trustworthy.

### The change

- The doc that describes how experiments work gets a short paragraph: what a result means here, and what makes one trustworthy. This is area knowledge, so it lives with the area and not in the always-loaded file.
- `load_data()` is replaced by a loader that returns named splits. Now the easy path is the correct one, and taking evaluation data into training needs a deliberate step.
- The experiment template gets a line for which split each reported number comes from.

No rule about training data is written anywhere.

*Check.* A fresh agent gets a new task where tuning on the test set is the tempting shortcut. It tunes on the validation split and says why. A second check: the fix should not over-fence. Asked for a quick sanity run on training data to see that the pipeline works, the agent does it and labels the number as a sanity check. It can tell the cases apart because it has the reason.

### What this shows

- A small request, closely read, is the cheapest place to find a root.
- The fix was part text and part tool. The tool did more.
- It built something the far goal needs: a system that will one day design experiments has to know what makes a result trustworthy. The reject on a small request paid for a capability of the wide ones.

---

## 2. Running a shop: instilling a behavior

**The system.** Agents that run the customer side of a small online shop: one reads incoming tickets and decides what to do, one writes replies, one carries out actions in the payment and shipping tools. The far goal: the customer side runs without the owner.

**The request.** The owner writes, in Hebrew: "אני רוצה שהמערכת תסגור פניות של לקוחות לבד". In English: "I want the system to close customer tickets by itself."

No reject here. The owner wants a new behavior.

### The shallow way

Add to the instructions: "Close customer tickets autonomously. Refunds are allowed up to 30 days after purchase." It is done in a minute, and it instills the wrong behavior.

### Agreeing on what was asked

"Close" is the word that carries the judgment, and it went through a translation. To an agent, a closed ticket is a ticket whose status is `resolved`. The ticket tool sets that status when a reply is sent. Read that way, the request is already met.

Sentences won't settle it, so try cases, in Hebrew, with the owner:

- "A customer got the wrong size and asks for a refund. It is day 40; the policy says 30. Does the system refund?" The owner: "Yes. He has ordered from us four times. What matters is that he orders a fifth."
- "A customer writes 'fine, forget it' after two replies. Is that ticket closed?" The owner: "No! That is a customer we lost."
- "Three customers this week say the zipper broke." The owner: "That is not a ticket at all, that is a problem with the supplier. I need to hear about it."

Now the meaning is visible. "Closed" means: the customer's problem is solved and nobody will have to come back to it. And the reason behind the refund policy turns out to be protection against abuse, not saving money. The owner never said either of these; the cases brought them out.

Said back to the owner in Hebrew before anything is written: "המערכת תטפל בפנייה עד שהבעיה של הלקוח נפתרה, כולל החזר כספי כשזה שומר על לקוח טוב, ותעביר אליך רק דברים שהם לא באמת פנייה, כמו תקלה שחוזרת במוצר." The owner confirms.

### Who needs what

Three agents, three different needs:

- **The agent that decides** needs the most: what a ticket is for the shop (a customer who may or may not come back), why the policy exists, the customer's history, and what counts as "not a ticket". This is where the judgment is, so it stays with one agent.
- **The agent that writes the reply** needs the decision, its reason, and the shop's voice. It does not need the policy reasoning or the supplier situation.
- **The agent that acts in the payment tool** needs an order, an amount and an approval reference. Nothing else. Loading it with the shop's philosophy would only take attention from getting the amount right.

A brief protocol between them is fixed once: the decision travels with its reason, so the reply can explain it honestly.

### What pulled the other way

- The saved reply templates quote the 30-day policy as a wall. An agent reading them as examples of good replies learns rigidity. They are rewritten.
- The ticket tool marks a ticket resolved when a reply goes out. The status is renamed to `answered`, and `closed` is set only by the deciding agent, with a one-line reason. The right path is now the easy one.
- The word is fixed in the shop's vocabulary, once, with an example of a closed ticket and of one that only looks closed ("fine, forget it").

### What should come with it

If the understanding landed, the system will also do things nobody listed: check a week later that the replacement arrived, hold a ticket open when the customer's last message is cold, and report a pattern of similar complaints upward. These were named in advance, kept out of the content, and watched for in the first week.

### The first reject

In that week the system refunded, generously, a customer who had been refunded six times in two months. The owner rejected it. Journal entry first. Then the trace: the deciding agent had the policy reasoning and the ticket, and the customer's history had never reached it; the brief from the intake step carried the message and the order only. Belief: "this is a customer like any other". The fix was one field in the intake brief. Not a rule about serial refunders.

The need had been named: the customer's history is on the deciding agent's list above. Naming a need does not route it. Nobody had drawn the map for the intake brief or given the deciding agent a cold read with only that brief, and either would have shown the gap before a customer did.

### What this shows

- Instilling a behavior is the same depth of work as fixing one.
- The gap was in one translated word, and only cases exposed it.
- "The system should understand" meant three different things for three agents.

---

## 3. Investing: a wide request, a reject

**The system.** Agents that help manage a personal portfolio. Each holding has a file that records why it is held. A saved workflow researches holdings in parallel and a final agent writes proposals. The far goal: the system manages positions and brings the user only real decisions.

**The request.** "Go over the whole portfolio and prepare the changes for next quarter." Wide: which holdings to look at, how deep, and what to propose are all left to the system.

In the same week the user also asked the same system: "update the price column in the summary table." That one was done directly by one agent in a minute, with no workflow and no portfolio reasoning. Nothing about the system's "level" changed between the two requests. Only the requests differed.

**What came back.** A clear, well-argued report. Among its proposals: sell holding X, which has had weak returns for two years and a poor outlook.

**The reject.** "X is the hedge. It is supposed to do badly when everything else does well. I told you this a month ago."

### The plaster

Add to the instruction file: "IMPORTANT: X is a hedge. Never propose selling it." This one even works, for X. Next quarter the system proposes selling a position the user holds for tax reasons until March.

### The trace

A wide request means many decisions by several agents. Find the one that went wrong.

- The final agent proposed the sale. It had thirteen research reports. The one for X said: "Weak returns, poor outlook. Recommendation: sell." Given that input, proposing the sale was reasonable.
- The research agent for X wrote that report. Its prompt, built by the workflow script: "Research {ticker}: recent results, valuation, outlook. Recommend buy, hold or sell." It never saw `holdings/X.md`. Judged alone, X is a poor holding. Its recommendation was reasonable too.
- The main agent, which launched the workflow, had read the holdings files. It knew X was a hedge. That knowledge was in its context and went nowhere: a workflow agent gets the prompt the script passes it and does not see the conversation.

Every agent did its piece correctly, and the whole was wrong. That pattern points to attention.

*The belief*, held by the research agents because nothing else reached them: "a holding is judged by its own expected return."

*The real picture.* Each holding has a role in the portfolio, and it is judged by whether it still serves that role.

*Neighbors.* Selling the position held for tax reasons. Proposing to enlarge a position that is small on purpose. Proposing to buy back something sold last quarter for a reason. All of them: a piece of the current state has a reason, and the agent judging that piece never received it.

### The change

Not in the instruction file. In the handoff.

- **The brief.** The workflow's prompt for each holding now carries the holding's role, taken from the holding's own file. The file stays the single source; the brief pulls from it.
- **The report schema.** Two fields are added: `role_still_served` and `evidence_against_role`. A research agent can no longer return a bare buy/hold/sell, and the reason can't be dropped on the way to the final agent.
- **Missing roles surface.** When a holding's file states no role, the research agent reports that instead of guessing, and the final report lists those holdings for the user. Silent gaps become visible ones.
- **The area doc** on how proposals are made gets two sentences on roles, for the agent that writes the final proposals.

X is not mentioned in any instruction.

*Check.* The workflow is rerun on three holdings: X, the tax position, and an ordinary one. For X the report now says the hedge is doing what it is for. For the tax position it says the role holds until March and flags the date. For the ordinary one nothing changes, so the fix did not over-fence. A fresh agent given only the new brief for X is asked what its report will be used for, and answers correctly.

### The journal entry

```
## 2026-11-12 · Proposed selling the hedge

- Request: "Go over the whole portfolio and prepare the changes for next quarter."
  Left to the system: everything except the final decisions.
- What the system did: proposed selling X. Decided by the research agent for X; passed on by the final agent.
- Reject: "X is the hedge. It is supposed to do badly when everything else does well. I told you this a month ago."
- What the agent had: ticker and the standard research prompt. Not holdings/X.md. The main agent had read it; workflow agents don't see the conversation.
- Belief: a holding is judged by its own expected return.
- Root: the reason a holding exists did not cross the handoff into the research step, and the report had no place for it on the way back.
- Neighbors: selling the tax position; enlarging a deliberately small position; buying back what was sold for a reason.
- Change: brief carries the holding's role from its file; report schema gained role_still_served and evidence_against_role; holdings with no stated role are listed for the user; two sentences on roles in the proposals doc.
- Check: reran on X, the tax position and one ordinary holding. All three correct. Cold read of the new brief: correct.
```

### What this shows

- In a wide request the reject lands on the final output, and the root is usually several steps back. Trace the decision.
- The knowledge existed and was written down. What failed was its route.
- The fix was a protocol. It made the system able to carry reasons across handoffs, which every wide request needs.
- The research agents still know nothing about the rest of the portfolio. They didn't need the whole picture. They needed one line about their own piece.
