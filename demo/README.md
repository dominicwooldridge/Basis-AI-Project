## Basis Multi-Agent Demo

What This Demo Does
Imagine a solar developer wants to build a 100-megawatt solar farm in Kern County, California. Before they commit to the project, they need to know: how much of a tax credit will the federal government give them under the Inflation Reduction Act, and what is that credit worth in dollars?

This demo answers that question automatically using AI.

The problem it solves
The IRA tax credit calculation is not a simple lookup. The final credit rate depends on several layered rules:

Does the developer pay workers prevailing wages? That unlocks a 5x multiplier.
Is the project site in a designated "energy community" — a region that historically depended on coal or fossil fuels? That adds another 10%.
Stack those together and you get a final credit rate. Multiply that by the project's construction cost and you get a dollar figure.
A human analyst would need to know all of those rules, look up whether Kern County qualifies as an energy community, do the math, and write up a summary. This demo automates that entire process.

How the AI does it
Instead of one giant AI model trying to do everything at once, the demo uses four agents — think of them as a small team of specialists, each with one job.

A manager (the Orchestrator) receives the project details and hands the work down the line. It never does any analysis itself — it just runs the team.

The first specialist, the Credit Agent, looks at whether the developer has checked the prevailing wage and apprenticeship boxes and determines the base tax credit rate. In this case: yes on both, so the rate is 30%.

That result gets handed to the second specialist, the Adder Agent. Its only job is to check whether the project site qualifies for bonus credits. It looks up Kern County and confirms it's a designated coal closure community — so an extra 10% gets added, bringing the stacked rate to 40%.

That result goes to the third specialist, the Summary Agent. It takes everything — the 40% rate, the $120M construction cost — computes the credit value ($48M), and writes a plain-English paragraph explaining the result to the developer.

What you see when it runs

=== Basis Multi-Agent Demo ===

[1/3] CreditAgent running...
  Base ITC rate: 30% (PWA compliant)

[2/3] AdderAgent running...
  Energy community: YES — Kern County qualifies
  Stacked credit rate: 40%

[3/3] SummaryAgent running...
  [plain English summary]

=== Result ===
  Credit value: $48.0M on $120M project
  Stacked rate: 40%
Each line appears as that agent finishes — you're watching the pipeline execute in real time.

Why build it this way
The reason to use multiple agents instead of one is the same reason a firm has departments instead of one person doing everything. Each agent is narrow, testable, and replaceable. If the energy community rules change, you update one agent. If you want to add a domestic content bonus check, you add one agent. The manager doesn't need to know — it just passes results down the chain.