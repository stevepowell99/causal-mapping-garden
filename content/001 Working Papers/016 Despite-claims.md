---
tags: paper
date: 2026-01-24
---
## "Despite" coding

### The problem: countervailing conditions that “failed”

Narratives often contain claims of the form:

> “E happened despite Z.”

Examples:

- “The heavy rains made the river levels rise, **despite** the prevention and clearance work.”
- “**Despite** me reminding him multiple times, he missed the train.”

In ordinary language, the “despite” clause does two things at once:

1. It signals that **Z was expected to prevent or reduce E** (a countervailing influence).
2. It asserts that **E happened anyway** (so Z was insufficient, absent, overridden, or ineffective in that case).

If we only code the main causal claim (e.g. `Heavy rains -> River levels rose`), we lose potentially important information about attempted mitigations, resistance, barriers, or protective factors.

But it is also usually wrong to code the “despite” clause as an ordinary positive causal link, e.g. `Prevention work -> River levels rose`, because that flips the intended meaning on its head.

### The convention: a “despite” link type (or tag)

We therefore treat “despite” as a **link type**, not a different semantics for `->`.

A minimal encoding is:

- **Main link** (ordinary): `X -> E`
- **Despite link** (typed/tagged): `Z -despite-> E`

Equivalently (in a plain links table), keep the same `Cause` and `Effect` columns but add either:

- a `link_type` column with values like `normal` vs `despite`, or
- a `link_tags` column containing a tag like `#despite`.

The key idea is that `-despite->` does **not** mean “Z caused E”. It means:

> “Z was presented as a countervailing influence against E, in virtue of its causal power to work against E, but E occurred anyway.”

### What can we do with “despite” links?

Because the distinction is explicit in the links table, we can decide—per analysis—how to treat these links:

- **Visualise** them distinctly (different colour/line style), so the map shows “tensions” rather than silently dropping them or misreading them.
- **Filter**: show only `despite` links to see what people present as failed protections / resistances / mitigations.
- **Compare**: for similar outcomes, do some sources describe Z as effective (ordinary preventive claim, e.g. `Z -> ~E`) while others describe “despite” failures (`Z -despite-> E`)? That contrast can be analytically important.
- **Count separately**: include them in evidence tallies only under a separate counter (e.g. `Despite_Citation_Count`) so you don’t accidentally inflate evidence for “Z causes E”.

### Worked example

Text:

> “The heavy rains made the river levels rise, despite the prevention and clearance work.”

Coding:

- `Heavy rains -> River levels rose`
- `Prevention and clearance work -despite-> River levels rose`

This preserves the main mechanism while also storing the claim that a mitigation was present but insufficient.

### Optional background: force dynamics (why “despite” is cognitively natural)

Leonard Talmy’s “force dynamics” treats many causal expressions as patterned talk about forces: an **Agonist** with a tendency (towards motion/rest) and an **Antagonist** that counters it. “Despite” is a canonical force-dynamics marker: it signals a countervailing force that failed to stop the outcome.

You do not need this theory to use `-despite->` coding; it is only a helpful explanation of why “despite” claims feel different from ordinary causal claims, and why it can be worth capturing them explicitly.

## Hard cases (brief notes)

- **“Despite” + opposites**: should `Z -despite-> E` be treated as evidence for `Z -> ~E`? Usually no; treat it as its own link type, or at most as weaker evidence depending on your analysis goal.
- **Bipolar concepts**: some pairs (employment/unemployment) have high cosine similarity (similar contexts) but are "opposite" in ordinary talk. This is why sentiment often becomes relevant when doing AI-assisted clustering/aggregation.

### 4.1 Force Dynamics: Agonists and Antagonists in Latent Space

Leonard Talmy’s theory of **Force Dynamics** posits that human causal understanding is rooted in the interplay of forces: an **Agonist** (the entity with a tendency towards motion or rest) and an **Antagonist** (the opposing force).   

- _Linguistic Patterns:_ "The ball kept rolling despite the grass" (Agonist: Ball; Antagonist: Grass). "He let the book fall" (Removal of Antagonist).
    
- _LLM Evaluation:_ Recent studies  have tested LLMs on translating and explaining these force-dynamic constructions.   
    
    - **Findings:** GPT-4 demonstrates a sophisticated grasp of these concepts. When translating "He let the greatcoat fall" into languages like Finnish or Croatian, the model correctly selects verbs that convey "cessation of impingement" (allowing) rather than "onset of causation" (pushing).   
        
    - **Implication:** This suggests that LLMs have acquired a **schematic semantic structure** of causality. They do not merely predict words; they map the _roles_ of entities in a physical interaction. However, this capability degrades in abstract social contexts. For example, in the sentence "Being at odds with her father made her uncomfortable," models sometimes misidentify the Agonist/Antagonist relationship, struggling to map "emotional force" as accurately as "physical force".   
 

![Untitled](img/💖 Sentiment f2b956db7932466d894f98ea81fbee94--Untitled 1.png)



**
This causal map reveals how **T1: The Disillusioned**, **T2: The Pragmatists**, and **T3: The Loyalists** experience the research environment differently. By applying a chi-square test ($p < .05$) to compensate for varying group sizes, several "hotspots" emerge where specific nodes (factors) and causal links are mentioned significantly more (▲) or less (▼) than expected.

### Tribal Narrative of Significant Divergence

The **T2: The Pragmatists** dominate the map's narrative of resilience and advancement. They are the only group to significantly mention the link between **"good guidance"** and **"applying active coping strategies"** (▲). Their pragmatic nature is further highlighted by their significant focus on the **"high performance pressure"** node (▲), which they directly link to **"mental health decline."** However, they balance this by identifying a **"positive and supportive work environment"** as a significant driver of **"growth"** (▲). Ultimately, they are the primary group fueling the transition from **"growth"** to **"high career optimism"** (▲).

In contrast, **T1: The Disillusioned** are defined by a narrative of stagnation. While they experience growth, they show a **significant lack of mentions** connecting that **"growth"** to **"high career optimism"** (▼). For this tribe, the link between personal development and a bright future is statistically broken.

Finally, **T3: The Loyalists** anchor their experience in community. Their significant contribution to the map is the node of **"supportive colleague behavior"** (▲), which they link directly to **"growth."** For the Loyalists, horizontal support from peers is the statistically significant engine of their professional evolution.