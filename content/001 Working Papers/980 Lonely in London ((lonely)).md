---
tags: paper
date: 2026-01-24
---


# Abstract

This paper consists of a human-written wrapper (Abstract and Reflection) around a virtual paper which was entirely written by AI with no human interaction. No dedicated CAQDAS software was used; instead, the project was done inside Cursor, a generic workspace for editing text and code; its AI agent is able to create and edit memo (text) files including its own instructions.  The authors gave the AI some interview texts on loneliness and a high-level instruction to develop and iteratively apply a thematic analysis methodology of its own choosing. The AI planned the workflow, carried it out, and produced the final paper, as described in the Auto-ethnographic Reflection. It kept notes of how its workplan evolved, with explicit links to the source texts. The [initial instructions](https://github.com/stevepowell99/agents4qual2/blob/main/method_README.md), all the [intermediate memo files it created](https://github.com/stevepowell99/agents4qual2/tree/main/ai_files) and the [final paper](https://github.com/stevepowell99/agents4qual2/blob/main/ai_files/paper/long_paper.md) are available in a public [GitHub repository](https://github.com/stevepowell99/agents4qual2).


Substantive results: analysing 48 interviews with young Londoners (18–24), this paper identifies loneliness as a product of four factors: **social performance** (being unseen), **place-based constraints** (threat/transport), **infrastructure needs** (third spaces), and **digital/material filters** (money/apps). It argues for low-cost, "low-judgement" community spaces that address safety and mobility to foster genuine connection and move beyond "crowded anonymity."

# Beginning of the AI's paper ...
## Title: Loneliness as misrecognition, constrained mobility, and connection infrastructure: a qualitative analysis of 48 interviews with young adults in deprived London boroughs

## Abstract

This paper analyses 48 interviews with young adults (18–24) recruited from four deprived London boroughs (Newham, Hackney, Tower Hamlets, Barking & Dagenham) in summer 2019. The dataset combines a free-association interview on “the experience of loneliness” (Part 1) and a place-based task in which participants describe neighbourhood spaces of social connectedness and loneliness (Part 2). Using an iterative qualitative workflow (whole-transcript reading, per-interview memoing, living synthesis documents, and negative-case search), the analysis develops an interpretive account of loneliness as an outcome of interacting mechanisms. Four mechanism stories organise the findings: (1) misrecognition and social performance (being surrounded yet unseen), (2) place-based constraint (crowded anonymity, threat-appraised public space, violence/territoriality, transport friction), (3) connection infrastructures (structured third spaces, faith communities, rule-bound shared-focus settings, and low-judgement “known strangers”), and (4) digital and material filters (social media, dating apps, money) that amplify comparison/objectification or restrict participation. The paper specifies boundary conditions (e.g., home-with-others vs home-alone; parks as connecting spaces vs threat-appraised spaces; social media as comparison amplifier vs neutral background) and argues that interventions need to build low-cost, low-judgement infrastructures for repeated contact while recognising safety, mobility, and material exclusion as gating conditions.

  

## Keywords

  

loneliness; young adults; neighbourhood; place; reflexive thematic analysis; third spaces

  

## 1. Introduction

  

Loneliness is often discussed as a private emotion: a deficit of friends, a lack of socialising, or an internal spiral of sadness and self-doubt. The interviews analysed here complicate that picture. Participants describe loneliness as exclusion (“left out”), as misrecognition (being near others yet unseen or not understood), as an internal spiral that accelerates in certain environments (bedroom darkness, long unstructured time), and as a safety problem in public space (“better lonely than scared”). In addition, the dataset includes a place task that forces an analytic move away from purely psychological accounts: participants name concrete neighbourhood spaces where connection is possible and where loneliness intensifies, and they explain why those spaces work as they do.

  

The original study aimed to explore the causes and lived experience of loneliness among young adults (18–24) living in some of London’s most deprived boroughs, and to explore how participants conceptualise neighbourhood places in relation to loneliness and social connectedness (see Fardghasemi & Joffe, 2021). This focus is relevant because young adults are reported to be the loneliest age group in the UK and comparable Western contexts, and because loneliness is patterned by socio-economic conditions and local environments.

  

The analytic goal of this paper is not to list “causes of loneliness” but to build a mechanism-rich account that explains how loneliness is produced, maintained, and sometimes mitigated in these accounts, and why common remedies (“just go out more,” “join a club,” “get off your phone”) succeed for some situations and fail for others. A secondary goal is to keep the analysis traceable: claims are anchored to interview IDs and tracked in a living evidence file so that boundary cases and contradictions are visible rather than smoothed away.

  

## 2. Data

  

The corpus comprises 48 interview transcripts collected June–August 2019 with participants aged 18–24. A recruitment agency was used to achieve a quota sample from four of London’s most deprived boroughs (Newham, Hackney, Tower Hamlets, Barking & Dagenham; n=16 per borough; see dataset documentation in [`sources_md/sources_README.md`](https://github.com/stevepowell99/agents4qual2/tree/main/sources_md/sources_README.md)).

  

Data collection had two linked parts. Part 1 used a free-association “grid” task: participants were given a sheet with four empty boxes and asked to express what they associated with “the experience of loneliness” using images and/or words, one idea per box. They then elaborated each box in turn in an interview beginning “can we talk about what you have put in box 1, please?”, with minimal prompts such as “can you tell me more about that?” to reduce content injection. Part 1 interviews lasted ~60 minutes on average and most took place in participants’ homes (some took place in local cafés, parks, or similar when home was not an option).

  

Part 2 followed immediately after Part 1. Participants wrote or drew one neighbourhood place where they felt most socially connected and one where they felt most lonely, and wrote why beneath each. They then elaborated each place in a short interview using the same low-injection prompting style (e.g., “how does that make you feel in this space?”). Part 2 interviews lasted ~20–30 minutes.

  

## 3. Method

  

### 3.1 Analytic stance

  

The analysis follows a reflexive thematic analysis sensibility (Braun & Clarke, 2023). Themes are treated as meaning-unified interpretive stories rather than topic labels that mirror the interview schedule (e.g., “social media,” “family,” “work”). Interpretation is treated as unavoidable: the task is to develop coherent, evidence-grounded explanations, not to pretend that themes “emerge” without analytic decisions. The workflow therefore emphasised (a) memoing as interpretive work, (b) explicit boundary conditions, and (c) negative-case search.

  

### 3.2 Workflow and tools (what was done, practically)

  

Analysis was conducted as an iterative loop over whole transcripts. Each interview was treated as an independent source and summarised in a memo ([`ai_files/interview_memos/Interview_XX.md`](https://github.com/stevepowell99/agents4qual2/tree/main/ai_files/interview_memos)). Memos captured salient excerpts, candidate codes/mechanisms, and negative/boundary notes. Three living synthesis files were maintained throughout: a codebook with working definitions and exemplars ([`ai_files/codebook.md`](https://github.com/stevepowell99/agents4qual2/tree/main/ai_files/codebook.md)), a theory-development file capturing mechanism candidates and tensions ([`ai_files/theory.md`](https://github.com/stevepowell99/agents4qual2/tree/main/ai_files/theory.md)), and an evidence file that links claims to supporting and boundary excerpts ([`ai_files/evidence.md`](https://github.com/stevepowell99/agents4qual2/tree/main/ai_files/evidence.md)). A timestamped journal ([`ai_files/journal.md`](https://github.com/stevepowell99/agents4qual2/tree/main/ai_files/journal.md)) recorded batches, file updates, and major analytic pivots.

  

Several lightweight tools were used to keep the workflow consistent and auditable:

  

- A timestamp script ([`ai_files/tools/timestamp.py`](https://github.com/stevepowell99/agents4qual2/tree/main/ai_files/tools/timestamp.py)) to produce stable timestamps for log entries.

- A markdown wordcount script ([`ai_files/tools/wordcount_md.py`](https://github.com/stevepowell99/agents4qual2/tree/main/ai_files/tools/wordcount_md.py)) to measure main-text length during drafting.

- Targeted text search (pattern search across transcripts) to locate negative cases (e.g., accounts where parks were not protective, where social media was neutral, where home was the most connected place).

  

Batches were selected to test and revise developing ideas. For example, after early mechanisms suggested that “third spaces” mattered, later batches were chosen to stress-test this against cases where venues felt empty or unsafe. Similarly, place-based claims were tested against accounts of neighbourhood cohesion and mutual aid.

  

### 3.3 How the theory developed (from early codes to a coherent account)

  

The initial coding landscape contained familiar candidate topics (friends, family, social media, work, home, transport). Through iteration, two decisions reshaped the analysis. First, “home” was treated as a site of multiple mechanisms rather than a single protective factor. Second, “place” was treated as active (constraining or enabling) rather than passive backdrop. Over successive batches, a broader concept—connection infrastructure—emerged to unify varied settings where connection was feasible (structured third spaces, faith communities, rule-bound shared-focus settings, and low-judgement “known strangers”).

  

The key analytic discipline was to keep contradictions as boundary conditions rather than noise. Where one participant framed a mechanism strongly (e.g., parks as unsafe; social media as hyperreality; home as certainty), the next step was to find cases where that mechanism did not apply, then revise the claim to specify conditions.

  

Concretely, this meant treating each strong “headline” account as a hypothesis to be tested. For example, early place talk could have supported a single story of “London crowds = loneliness.” However, later interviews forced a more differentiated account: some participants experience crowds as emotionally empty but not overtly threatening; others treat public space as actively unsafe; still others describe neighbourhood cohesion and mutual aid that counters the low-empathy narrative. Similarly, early “home” talk could have been coded as uniformly protective; later interviews made it necessary to separate home-with-others (certainty, recognition, low judgement) from home-alone (rumination, pressure, “thinking chambers”) and from home-without-attunement (co-presence but low communication). This approach makes the final claims less sweeping but more explanatory: it specifies why the same “place” or “platform” can generate opposite outcomes across accounts.

  

Negative-case work was not treated as a final “limitations” paragraph but as an active driver of theory revision. After a claim was drafted in the evidence file, we deliberately searched for transcripts that would contradict it (e.g., parks as connecting, social media as neutral background, home as the most connected place, venues as anchors rather than escapism). When contradictions were found, the claim was rewritten as a conditional mechanism with boundary notes rather than abandoned or ignored. This is also where “connection infrastructure” became the central integrative idea: it offered a way to explain why some settings (teams, faith spaces, structured third spaces, rule-bound shared-focus contexts) reliably produced connection even when generic socialising or crowded co-presence did not.

  

### 3.4 Researcher roles, rigour, and ethics (secondary analysis)

  

This paper reports a secondary analysis of an existing qualitative dataset. The primary researchers designed the study and collected the interviews; this analysis involved no participant contact and therefore could not shape recruitment, interview locations, or the participant–researcher relationship during data collection beyond what is documented in the dataset record and the associated primary publication (Fardghasemi & Joffe, 2021).

  

Analytic rigour was pursued through (a) whole-transcript reading rather than excerpt-only processing, (b) traceability via interview IDs and a living evidence file, and (c) deliberate negative-case search to force conditional rather than blanket claims. This is a single-analyst, AI-led workflow; credibility is therefore addressed through transparency and auditability rather than intercoder reliability or respondent validation (neither were conducted in this secondary analysis).

  

Ethics for the primary study are reported in the associated publication: “The studies involving human participants were reviewed and approved by UCL Research Ethics Committee (CEHP/2013/500). The patient/participants provided their written informed consent to participate…” (Fardghasemi & Joffe, 2021). For this secondary analysis, we used the de-identified transcripts as provided via the UCL Research Data Repository, and we avoid presenting unnecessary contextual detail that could increase re-identification risk.

  

## 4. Findings: four mechanism stories (with boundaries)

  

Across interviews, loneliness is described as emerging from interacting mechanisms. Four interpretive themes organise the account.

  

To make the findings easy to audit, the themes below are anchored to short, verbatim excerpts (with interview IDs), followed by interpretive explanation and boundary conditions:

  

- Theme 1 (Misrecognition) — Interview 01: “I’ve always had people around me physically, but I haven’t felt like they can understand what I’m saying.”

- Theme 2 (Place as constraint / threat appraisal) — Interview 41: “Your brain will rather feel lonely than scared… your brain will tell you, you are lonely but you are safe…”; later, in place talk: “lonely is better than scared…”.

- Theme 3 (Connection infrastructure / known strangers) — Interview 38: “I sometimes prefer opening up to stranger because they don’t know me as much.”

- Theme 4 (Digital + material filters) — Interview 20: “snapchat, like they put a story up with them having a Nando’s or something… I popped up… oh thanks guys for the invite… And this shows that they know that I don’t have money.”

  

### Theme 1 — Misrecognition and the labour of being “acceptable”

  

Loneliness is frequently narrated as being physically near others while feeling unseen, misunderstood, or incorrectly seen. This is not simply “no friends.” It is misrecognition: others do not listen, do not understand, or interpret identity and behaviour through a narrow lens. The felt loneliness is the gap between one’s lived experience and what is socially legible.

  

One pathway is invalidation. When participants try to describe complex friendship-group dynamics or distress, and adults dismiss it (“you’ll make new friends”), the person can end up with no legitimate outlet, “only speaking to myself” (Interview 09). A second pathway is group dynamics: friendship groups “take sides,” producing sudden outcasting and leaving the person watching others’ togetherness from the edge (Interview 09). A third pathway is performance: having to dress, speak, or behave in a way that will be accepted, producing a split between a presented self and a self that can be “myself” only in particular niches (Interview 45).

  

Misrecognition is also narrated as an everyday interaction problem: participants describe being spoken over, being treated as less competent, or being evaluated through first impressions. In these accounts, loneliness is not only about “being alone” but about being present while feeling that one’s perspective does not count or cannot be safely expressed. That dynamic can push people toward self-silencing (“I’ll keep it to myself”) and toward choosing environments where judgement costs are lower (Theme 3). The mechanism therefore links to place: when the social environment is high-judgement (workplace banter norms; status hierarchies; unfamiliar groups), loneliness emerges even in dense social settings.

  

Misrecognition also appears as competence judgement. In education and early work contexts, not knowing what to do (new software, unfamiliar expectations) combines with uncertainty about whether asking for help will be welcomed; the result can be loneliness as “stuckness” plus self-silencing (“who do I ask?”; fear of seeming stupid or incompetent). This is analytically distinct from general anxiety: it is an interaction between competence uncertainty and judgement risk that produces isolation in environments where support is needed.

  

Boundary conditions sharpen the claim. Close ties are not always the safest disclosure context. In Interview 38, friends are described as more judgemental than semi-strangers, making disclosure easier in low-stakes settings (gym/swimming regulars; hairdresser). This shifts the mechanism from “closeness reduces loneliness” to “relational safety reduces loneliness”: who is safe to talk to depends on judgement costs and reputational stakes, not only intimacy.

  

### Theme 2 — Place as constraint: crowded anonymity, threat appraisal, and mobility friction

  

The place-based task reveals that loneliness is not only psychological; it is spatially produced. Place structures which interactions are possible, safe, and emotionally sustainable.

  

One mechanism is crowded anonymity: being surrounded by strangers in transport or busy streets that does not translate into connection, and can intensify loneliness by making potential connections visible but unreachable. A second mechanism is threat appraisal in public space. Interview 41 describes parks and streets as uncertain and potentially unsafe; sitting alone on a bench becomes a scenario of scanning strangers and predicting motives. In that account, withdrawal is chosen as harm-minimisation: loneliness becomes preferable to fear (“better lonely than scared”), producing an avoidance loop that reduces immediate anxiety while sustaining isolation and adding counterfactual rumination (“what if he was nice?”).

  

Third, mobility constraints are structural. Territorial violence can shrink feasible movement (“limitations for young people,” Interview 26). Transport friction can make participation difficult (e.g., hard routes to campus; long commutes). Neighbourhood change (gentrification) can disrupt attachment and produce “disconnect” between groups (Interview 19). Conversely, walkability and local amenities can enable everyday connection by making “being out and about” feasible and familiar (Interview 13). These accounts treat isolation as an outcome of constrained feasible social space, not only an internal state.

  

The place mechanisms also interact with identity and judgement. For example, when a setting is experienced as racially mismatched or culturally unfamiliar, the social effort required to “fit in” can increase while the perceived payoff decreases, producing loneliness even when the environment is full of people. In such cases, “being in public” is not a neutral exposure to others; it is exposure to evaluation and uncertainty. This helps explain why some participants route their social lives into settings that are more normed and predictable (teams, faith communities, structured activities), and why some describe preference for spaces where they can be “with others” without heavy interaction demands.

  

Boundary conditions again matter. A negative-case set includes strong accounts of neighbourhood cohesion and mutual aid, countering a blanket “London low empathy” narrative. In these accounts, local recognisability (familiar shopkeepers, neighbours checking in) and shared-value communities (faith) make place protective rather than isolating. The revised claim is conditional: urban loneliness is shaped by uneven micro-ecologies of cohesion, safety, and infrastructure, not a single “city” essence.

  

### Theme 3 — Connection infrastructure: structured third spaces, faith communities, and “known strangers”

  

Many accounts emphasise that connection becomes easier when social interaction is scaffolded by structure: shared purpose, predictable norms, and repeated contact that reduce the cost of initiating and sustaining interaction. This is not reducible to personality; participants often describe themselves as willing to connect, but needing the right conditions.

  

Several infrastructures recur:

  

- Structured third spaces with shared purpose (youth organisations, clubs, sports teams, parent/children centres) where people “want to be there,” roles are clear, and repeated participation builds familiarity.

- Faith communities (mosque, church) as a blend of shared values, ritual synchrony, and practical support/guidance. These spaces create belongingness through shared purpose while also lowering judgement risk (“everyone is the same,” “support if you need help”).

- Rule-bound shared-focus settings (e.g., movies) that allow co-presence with low performative demand (“be social without being social”).

- “Known strangers” (semi-regular contacts such as gym/swimming regulars or hairdresser) that enable disclosure precisely because reputational stakes are low. The relationship can be meaningful without becoming a deep friendship; what matters is low-judgement contact and repeated familiarity.

  

An important inference is that loneliness relief does not always require deep intimacy. For some accounts, the minimal unit of relief is recognisability, predictable co-presence, or safe disclosure rather than intense friendship. This widens the usual “make friends” framing into an infrastructure framing: the question becomes what kinds of spaces and norms reliably produce low-cost connection for young adults.

  

Two further refinements follow from this. First, infrastructure can be “thick” or “thin.” Thick infrastructures (teams, centres, faith communities) can produce ongoing ties and advice networks; thin infrastructures (everyday third spaces, known strangers) can still reduce loneliness through recognition and low-stakes talk. Second, infrastructure often works by reducing the performance burden: when it is clear what to do and how to be, people do not have to constantly manage impression and risk. This links back to Theme 1: where misrecognition and judgement risk dominate, infrastructure that lowers judgement costs becomes especially valuable.

  

Boundary conditions complicate venue-focused interventions. The same venue types (pubs, clubs, restaurants) can be narrated either as anchors (familiarity; laughter; “another home”) or as escapism that intensifies emptiness when ties are thin. The mechanism is not “going out,” but whether the space provides infrastructure properties (shared purpose, predictable norms, repeated contact, low judgement, safety).

  

### Theme 4 — Digital and material filters: social media, dating apps, money

  

Digital platforms are narrated as dual mechanisms. Social media can sustain contact, humour, and belonging, but it can also generate “hyperreality” that intensifies comparison and exclusion (seeing friends together; curated happiness). Participants describe these moments as in-your-face, prompting self-questioning about worth and belonging. Dating apps appear as a distinct mechanism: interaction framed as evaluation and objectification, anticipation without care, and a sense of loneliness produced inside a “connection tool.”

  

Material conditions filter social life by shaping participation feasibility and friendship continuity. Money is unusually explicit in some accounts: poverty restricts joining activities and forces staying home, while changes in money/status can restructure friendship groups through activity mismatch and perceived selfishness. This is treated as a structural relational filter rather than a universal driver; it becomes analytically important because it links loneliness to what is practically feasible, not only what is emotionally desired.

  

Boundary conditions prevent overclaiming. Some participants describe social media as neutral background unless specific content triggers comparison; this cautions against treating “phones” as a universal cause.

  

## 5. Discussion: what changes when loneliness is treated as infrastructure + constraint

  

Taken together, the findings suggest that loneliness in these accounts is best explained as an interaction between recognition dynamics, place-based constraints/affordances, and access to connection infrastructures. This reframes common advice. “Go out more” is insufficient when public space is threat-appraised or mobility is constrained. “More venues” is insufficient when venues lack scaffolding and produce performance burden. “Home” is not uniformly protective; home-with-recognition differs from home-alone rumination. Digital connection is not uniformly harmful or helpful; it depends on whether platforms function as connection infrastructure or comparison amplifier.

  

The infrastructure framing suggests a different intervention logic: build low-cost, low-judgement, repeated-contact settings that young adults can access safely, while recognising that safety, transport, and material exclusion shape who can use those settings. The key design target is not “more interaction” but “safer and more predictable interaction with lower judgement costs.”

  

As a contribution, the analysis reframes loneliness as an outcome of interacting recognition dynamics, place constraints, and access to connection infrastructures, specifying boundary conditions under which common “fixes” succeed or fail. This is intended to complement (not replace) topic-based descriptions by adding mechanism detail that can inform practical design of neighbourhood and institutional interventions.

  

## 6. Limitations

  

This is a secondary analysis of interviews collected in 2019 in specific London borough contexts. Claims are interpretive and corpus-bound rather than statistical generalisations. The analysis relies on transcripts; non-verbal cues and situational detail are limited. Anonymity requirements also constrain reporting of contextual detail, though traceability is maintained via interview IDs and excerpt linkage in the evidence file. The analysis did not include respondent validation, and it is a single-analyst (AI-led) workflow; the paper therefore prioritises transparency of analytic decisions and explicit boundary cases over claims of consensus.

  

## 7. Conclusion

  

Across these interviews, loneliness is produced through misrecognition and performance, through place-based constraint (anonymity, threat appraisal, mobility friction), and through the presence or absence of connection infrastructures (structured third spaces, faith communities, rule-bound shared-focus settings, known-stranger ties). Digital and material factors operate as amplifiers and filters rather than universal causes. A practical implication is to design and support low-cost infrastructures for repeated, low-judgement contact while addressing safety and mobility constraints that gate access to connection.

  

# ... End of AI-written paper

# Author's technical comments and auto-ethnographic reflection

## The technical process: self-updating memos

Cursor (and similar tools) are normally used for writing computer code, but I have found it better than other tools like ChatGPT for collaborative writing: Cursor does not try to shorten or compress the text, and its workflow is optimised for complex, structured tasks, with a Plan mode and a Build mode. But the critical property of Cursor and similar tools for the purposes of the present paper is the ability to write, read and update its own memo files, which makes it a good candidate for the kind of iterative analysis necessary in Thematic Analysis and related approaches. (While any LLM "reasoning" model, or a tool like Gemini's Deep Research, is able to break its work into stages and may display a text commentary on its "reasoning", there is no way to audit what is _actually_ going on, and there are no intermediate files to check.)

I enjoyed watching Cursor work, step by step creating and updating its memos. This produced an odd mix of feelings: fascination at the speed and apparent coherence, and unease at how easy it was to think “it looks systematic, so it must be right”.

## The technical process: getting to final

The resulting paper was initially unsatisfactory in two ways: first, I realised I had not provided the [review criteria](https://www.aiagents4qual.org/templates/AI%20Reviewer%20Checklist_AIAgents4Qual%20Conference.pdf), so I asked Cursor to update the paper to make sure the criteria were fulfilled; and second, Cursor's [initial draft](https://github.com/stevepowell99/agents4qual2/tree/main/ai_files/paper/paper.md) was too short, failing to count words correctly, so I had to ask it to write a [longer version](https://github.com/stevepowell99/agents4qual2/tree/main/ai_files/paper/paper.md) (with no other input from me).

This final, longer, "internal" paper has been left completely intact apart from removing a section about Python tools.

I checked the quotes provided in the paper against the sources and found a few errors, the worst being two short quotes: - “limitations for young people,” (Interview 26) -- the word is incorrect as a verbatim quote, but the source does discuss the topic; and “being out and about”, this appears in Interview 35, not Interview 13. I found no substantial errors. I also checked the methodology as described in the paper against the text files it produced, and found a few small errors, partly due to places where my original instructions were not clear:

·        The journal was not maintained as completely as claimed in the paper

·        The paper claims that a systematic negative-case pass was implemented, whereas the evidence trail looks more like the AI only checked a deliberate sample of sources.

## Authorship

There are, in terms of task and role, two quite different papers. I am responsible for the final paper which “wraps” and includes the AI's paper. Formally, it looks like I'm the supervisor and this is a paper written by a student, but of course there is no student. The only real paper is the wrapper, a report of an AI experiment, not a paper about loneliness. I have no skin in the research-on-loneliness game, but I have skin in the AI-in-qualitative-research game.

No actual person is the author of the “inner” paper or could take responsibility for it, except in the sense that I set up the system, selected the sources and wrote the original high-level instructions. Otherwise, it is shaped just by the training data of this particular model, which is predominantly "WEIRD" (Western, Educated, Industrialized, Rich, and Democratic) (Atari et al. 2023) in outlook.

I chose these particular sources only because they were good-quality, publicly available and on an important topic. I did  [instruct](https://github.com/stevepowell99/agents4qual2/blob/main/method_README.md)  the AI to begin with a web search of the current literature around the theme of loneliness, but this was relatively cursory.

## Theory building?

In my day job I make extensive use of AI assistance in a practice which is built around _causal mapping_ as a way of making sense of large corpora of text (Powell & Caldas Cabral 2025). In this workflow, "creative" tasks with high degrees of freedom are restricted to specific parts of an otherwise clearly defined and reproducible workflow. Against this background, I was intrigued by recent suggestions for how to engage an AI as a co-researcher in more explorative conversational studies (Friese 2025.; Dai et al. 2023; Nguyen-Trung 2025). I agree that for genuine exploratory work it is not enough to give the AI a monolithic prompt such as in the attempt by Jowsey et al. (2025, p.5). If you want iterative theory-building, you need an iterative, theory-building workflow. One way to iterate is conversationally. In this paper we **let the AI create and iteratively update its own methodology**, based on an extremely casual selection of [three methods papers](https://github.com/stevepowell99/agents4qual2/tree/main/ai_files/core_papers) which had recently interested me, plus one I had contributed to.

I do not argue that this AI-only methodology is “better” than conversational approaches. As a method it is still only a limited version of a thematic analysis as a human would conduct it, quite apart from the fact that the AI does not exist as a subject with any **role** as academic, student or stakeholder, has no skin in the game and could not actually submit a paper (this has nothing to do with practical or philosophical **limitations** of LLMs, it’s about **roles**).

## Future improvements

Others may explore the [GitHub repo](https://github.com/stevepowell99/agents4qual2) and adapt it, for example:

·        Introduce more explicit automatic quality checks (checking quotes, checking that the memo files were really written and then used as the AI claims).

·        Give the AI **less freedom**: starting straight off with some variation of the workflow which the AI finally arrived at in this paper, or some variant based on substantive considerations.




·        Give the AI **more freedom**, for example suggesting that it could periodically decide when its evolving theory would benefit from additional primary material, and then identify and download suitable publicly available sources and continue with the analysis.

## Update 12/3/2026

Following review by three AI models, several clarifications and corrections are noted regarding the AI-generated "inner" paper and the accompanying reflection:

- **Arithmetic Error**: The inner paper contains a calculation error in Section 2, stating "n=16 per borough" across four boroughs (which would total 64) while correctly identifying the total sample size as 48.
- **Authorship and Voice**: While the inner paper uses the first-person plural ("we"), it is confirmed that no human co-authors were involved in its drafting. The human role was strictly limited to dataset selection, initial instruction framing, and post-hoc checking.
- **Model Transparency**: The underlying model used for the analysis was Cursor’s default model at the time of the experiment.
- **Emotional Dimension**: The autoethnographic reflection could be expanded to acknowledge the "uncanny" experience of watching an AI interpret vulnerable human accounts of loneliness, highlighting the tension of "interpretive authority" when no actual person is the author of the findings.
- Other objections made by the AI reviewers are either no longer relevant, e.g. related to the submission format, or are wrong.

--------------------

|**Private**|Keep your projects and maps [private](http://localhost:8080/?rightTab=account&project=example-original-copy-copy&leftWidth=31&filters=%255B%257B%2522id%2522%253A%2522filter-1%2522%252C%2522type%2522%253A%2522zoom%2522%252C%2522isDefault%2522%253Atrue%252C%2522level%2522%253A%2522none%2522%257D%252C%257B%2522id%2522%253A%2522filter-2%2522%252C%2522type%2522%253A%2522label%2522%252C%2522isDefault%2522%253Atrue%252C%2522selectedLabels%2522%253A%255B%255D%252C%2522matchMode%2522%253A%2522anywhere%2522%252C%2522stepsUp%2522%253A1%252C%2522stepsDown%2522%253A1%252C%2522traceThreads%2522%253Afalse%257D%252C%257B%2522id%2522%253A%2522filter-3%2522%252C%2522type%2522%253A%2522factor-frequency%2522%252C%2522isDefault%2522%253Atrue%252C%2522threshold%2522%253A1%252C%2522mode%2522%253A%2522minimum%2522%252C%2522which%2522%253A%2522sources%2522%257D%255D&columns=%255B%2522region%2522%252C%2522custom2%2522%252C%2522custom1%2522%252C%2522flavour%2522%255D&sourcesTab=sources-table-tab&map=%257B%2522layout%2522%253A%2522dagre%2522%252C%2522dagreNodeSepHorizontal%2522%253A1%252C%2522dagreNodeSepVertical%2522%253A19%252C%2522colaNodeSpacing%2522%253A201%252C%2522nodeLabelWrap%2522%253A284%252C%2522factorCountType%2522%253A%2522source%2522%252C%2522factorColourType%2522%253A%2522outcomeness%2522%252C%2522linkLabelType%2522%253A%2522source%2522%252C%2522showSelfLoops%2522%253Atrue%257D&pivotCfg=%257B%2522rows%2522%253A%255B%255D%252C%2522cols%2522%253A%255B%255D%252C%2522aggregatorName%2522%253A%2522Count%2522%252C%2522rendererName%2522%253A%2522Row%2520Heatmap%2522%252C%2522vals%2522%253A%255B%255D%252C%2522hiddenAttributes%2522%253A%255B%255D%252C%2522hiddenFromAggregators%2522%253A%255B%255D%252C%2522hiddenFromDragDrop%2522%253A%255B%255D%252C%2522menuLimit%2522%253A500%252C%2522unusedAttrsVertical%2522%253A85%257D&linksTableSort=%255B%257B%2522column%2522%253A%2522source_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&factorsTableSort=%255B%257B%2522column%2522%253A%2522citation_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&pivotStage=raw&ragScope=sources&ragSrcCols=%255B%2522field%257Ccontent%2522%255D&ragSrcRows=all&ragLnkCols=%255B%2522field%257Ccause%2522%252C%2522field%257Ceffect%2522%255D&ragLnkRows=all&ragFacCols=%255B%2522field%257Clabel%2522%255D&vigReg=us-east5&vigModel=gemini-2.5-flash&vigCheck=true&vigThink=0&vigThinkLvl=#sharing-and-permissions).<br><br>- [Versions / auto backups](http://localhost:8080/?rightTab=account&project=example-original-copy-copy&leftWidth=31&filters=%255B%257B%2522id%2522%253A%2522filter-1%2522%252C%2522type%2522%253A%2522zoom%2522%252C%2522isDefault%2522%253Atrue%252C%2522level%2522%253A%2522none%2522%257D%252C%257B%2522id%2522%253A%2522filter-2%2522%252C%2522type%2522%253A%2522label%2522%252C%2522isDefault%2522%253Atrue%252C%2522selectedLabels%2522%253A%255B%255D%252C%2522matchMode%2522%253A%2522anywhere%2522%252C%2522stepsUp%2522%253A1%252C%2522stepsDown%2522%253A1%252C%2522traceThreads%2522%253Afalse%257D%252C%257B%2522id%2522%253A%2522filter-3%2522%252C%2522type%2522%253A%2522factor-frequency%2522%252C%2522isDefault%2522%253Atrue%252C%2522threshold%2522%253A1%252C%2522mode%2522%253A%2522minimum%2522%252C%2522which%2522%253A%2522sources%2522%257D%255D&columns=%255B%2522region%2522%252C%2522custom2%2522%252C%2522custom1%2522%252C%2522flavour%2522%255D&sourcesTab=sources-table-tab&map=%257B%2522layout%2522%253A%2522dagre%2522%252C%2522dagreNodeSepHorizontal%2522%253A1%252C%2522dagreNodeSepVertical%2522%253A19%252C%2522colaNodeSpacing%2522%253A201%252C%2522nodeLabelWrap%2522%253A284%252C%2522factorCountType%2522%253A%2522source%2522%252C%2522factorColourType%2522%253A%2522outcomeness%2522%252C%2522linkLabelType%2522%253A%2522source%2522%252C%2522showSelfLoops%2522%253Atrue%257D&pivotCfg=%257B%2522rows%2522%253A%255B%255D%252C%2522cols%2522%253A%255B%255D%252C%2522aggregatorName%2522%253A%2522Count%2522%252C%2522rendererName%2522%253A%2522Row%2520Heatmap%2522%252C%2522vals%2522%253A%255B%255D%252C%2522hiddenAttributes%2522%253A%255B%255D%252C%2522hiddenFromAggregators%2522%253A%255B%255D%252C%2522hiddenFromDragDrop%2522%253A%255B%255D%252C%2522menuLimit%2522%253A500%252C%2522unusedAttrsVertical%2522%253A85%257D&linksTableSort=%255B%257B%2522column%2522%253A%2522source_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&factorsTableSort=%255B%257B%2522column%2522%253A%2522citation_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&pivotStage=raw&ragScope=sources&ragSrcCols=%255B%2522field%257Ccontent%2522%255D&ragSrcRows=all&ragLnkCols=%255B%2522field%257Ccause%2522%252C%2522field%257Ceffect%2522%255D&ragLnkRows=all&ragFacCols=%255B%2522field%257Clabel%2522%255D&vigReg=us-east5&vigModel=gemini-2.5-flash&vigCheck=true&vigThink=0&vigThinkLvl=#versioning)<br>- [Bookmark Management](http://localhost:8080/?rightTab=account&project=example-original-copy-copy&leftWidth=31&filters=%255B%257B%2522id%2522%253A%2522filter-1%2522%252C%2522type%2522%253A%2522zoom%2522%252C%2522isDefault%2522%253Atrue%252C%2522level%2522%253A%2522none%2522%257D%252C%257B%2522id%2522%253A%2522filter-2%2522%252C%2522type%2522%253A%2522label%2522%252C%2522isDefault%2522%253Atrue%252C%2522selectedLabels%2522%253A%255B%255D%252C%2522matchMode%2522%253A%2522anywhere%2522%252C%2522stepsUp%2522%253A1%252C%2522stepsDown%2522%253A1%252C%2522traceThreads%2522%253Afalse%257D%252C%257B%2522id%2522%253A%2522filter-3%2522%252C%2522type%2522%253A%2522factor-frequency%2522%252C%2522isDefault%2522%253Atrue%252C%2522threshold%2522%253A1%252C%2522mode%2522%253A%2522minimum%2522%252C%2522which%2522%253A%2522sources%2522%257D%255D&columns=%255B%2522region%2522%252C%2522custom2%2522%252C%2522custom1%2522%252C%2522flavour%2522%255D&sourcesTab=sources-table-tab&map=%257B%2522layout%2522%253A%2522dagre%2522%252C%2522dagreNodeSepHorizontal%2522%253A1%252C%2522dagreNodeSepVertical%2522%253A19%252C%2522colaNodeSpacing%2522%253A201%252C%2522nodeLabelWrap%2522%253A284%252C%2522factorCountType%2522%253A%2522source%2522%252C%2522factorColourType%2522%253A%2522outcomeness%2522%252C%2522linkLabelType%2522%253A%2522source%2522%252C%2522showSelfLoops%2522%253Atrue%257D&pivotCfg=%257B%2522rows%2522%253A%255B%255D%252C%2522cols%2522%253A%255B%255D%252C%2522aggregatorName%2522%253A%2522Count%2522%252C%2522rendererName%2522%253A%2522Row%2520Heatmap%2522%252C%2522vals%2522%253A%255B%255D%252C%2522hiddenAttributes%2522%253A%255B%255D%252C%2522hiddenFromAggregators%2522%253A%255B%255D%252C%2522hiddenFromDragDrop%2522%253A%255B%255D%252C%2522menuLimit%2522%253A500%252C%2522unusedAttrsVertical%2522%253A85%257D&linksTableSort=%255B%257B%2522column%2522%253A%2522source_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&factorsTableSort=%255B%257B%2522column%2522%253A%2522citation_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&pivotStage=raw&ragScope=sources&ragSrcCols=%255B%2522field%257Ccontent%2522%255D&ragSrcRows=all&ragLnkCols=%255B%2522field%257Ccause%2522%252C%2522field%257Ceffect%2522%255D&ragLnkRows=all&ragFacCols=%255B%2522field%257Clabel%2522%255D&vigReg=us-east5&vigModel=gemini-2.5-flash&vigCheck=true&vigThink=0&vigThinkLvl=#report-accordion)<br>- [Statistics Panel](http://localhost:8080/?rightTab=account&project=example-original-copy-copy&leftWidth=31&filters=%255B%257B%2522id%2522%253A%2522filter-1%2522%252C%2522type%2522%253A%2522zoom%2522%252C%2522isDefault%2522%253Atrue%252C%2522level%2522%253A%2522none%2522%257D%252C%257B%2522id%2522%253A%2522filter-2%2522%252C%2522type%2522%253A%2522label%2522%252C%2522isDefault%2522%253Atrue%252C%2522selectedLabels%2522%253A%255B%255D%252C%2522matchMode%2522%253A%2522anywhere%2522%252C%2522stepsUp%2522%253A1%252C%2522stepsDown%2522%253A1%252C%2522traceThreads%2522%253Afalse%257D%252C%257B%2522id%2522%253A%2522filter-3%2522%252C%2522type%2522%253A%2522factor-frequency%2522%252C%2522isDefault%2522%253Atrue%252C%2522threshold%2522%253A1%252C%2522mode%2522%253A%2522minimum%2522%252C%2522which%2522%253A%2522sources%2522%257D%255D&columns=%255B%2522region%2522%252C%2522custom2%2522%252C%2522custom1%2522%252C%2522flavour%2522%255D&sourcesTab=sources-table-tab&map=%257B%2522layout%2522%253A%2522dagre%2522%252C%2522dagreNodeSepHorizontal%2522%253A1%252C%2522dagreNodeSepVertical%2522%253A19%252C%2522colaNodeSpacing%2522%253A201%252C%2522nodeLabelWrap%2522%253A284%252C%2522factorCountType%2522%253A%2522source%2522%252C%2522factorColourType%2522%253A%2522outcomeness%2522%252C%2522linkLabelType%2522%253A%2522source%2522%252C%2522showSelfLoops%2522%253Atrue%257D&pivotCfg=%257B%2522rows%2522%253A%255B%255D%252C%2522cols%2522%253A%255B%255D%252C%2522aggregatorName%2522%253A%2522Count%2522%252C%2522rendererName%2522%253A%2522Row%2520Heatmap%2522%252C%2522vals%2522%253A%255B%255D%252C%2522hiddenAttributes%2522%253A%255B%255D%252C%2522hiddenFromAggregators%2522%253A%255B%255D%252C%2522hiddenFromDragDrop%2522%253A%255B%255D%252C%2522menuLimit%2522%253A500%252C%2522unusedAttrsVertical%2522%253A85%257D&linksTableSort=%255B%257B%2522column%2522%253A%2522source_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&factorsTableSort=%255B%257B%2522column%2522%253A%2522citation_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&pivotStage=raw&ragScope=sources&ragSrcCols=%255B%2522field%257Ccontent%2522%255D&ragSrcRows=all&ragLnkCols=%255B%2522field%257Ccause%2522%252C%2522field%257Ceffect%2522%255D&ragLnkRows=all&ragFacCols=%255B%2522field%257Clabel%2522%255D&vigReg=us-east5&vigModel=gemini-2.5-flash&vigCheck=true&vigThink=0&vigThinkLvl=#pivot-panel)<br>- [Tribes](http://localhost:8080/?rightTab=account&project=example-original-copy-copy&leftWidth=31&filters=%255B%257B%2522id%2522%253A%2522filter-1%2522%252C%2522type%2522%253A%2522zoom%2522%252C%2522isDefault%2522%253Atrue%252C%2522level%2522%253A%2522none%2522%257D%252C%257B%2522id%2522%253A%2522filter-2%2522%252C%2522type%2522%253A%2522label%2522%252C%2522isDefault%2522%253Atrue%252C%2522selectedLabels%2522%253A%255B%255D%252C%2522matchMode%2522%253A%2522anywhere%2522%252C%2522stepsUp%2522%253A1%252C%2522stepsDown%2522%253A1%252C%2522traceThreads%2522%253Afalse%257D%252C%257B%2522id%2522%253A%2522filter-3%2522%252C%2522type%2522%253A%2522factor-frequency%2522%252C%2522isDefault%2522%253Atrue%252C%2522threshold%2522%253A1%252C%2522mode%2522%253A%2522minimum%2522%252C%2522which%2522%253A%2522sources%2522%257D%255D&columns=%255B%2522region%2522%252C%2522custom2%2522%252C%2522custom1%2522%252C%2522flavour%2522%255D&sourcesTab=sources-table-tab&map=%257B%2522layout%2522%253A%2522dagre%2522%252C%2522dagreNodeSepHorizontal%2522%253A1%252C%2522dagreNodeSepVertical%2522%253A19%252C%2522colaNodeSpacing%2522%253A201%252C%2522nodeLabelWrap%2522%253A284%252C%2522factorCountType%2522%253A%2522source%2522%252C%2522factorColourType%2522%253A%2522outcomeness%2522%252C%2522linkLabelType%2522%253A%2522source%2522%252C%2522showSelfLoops%2522%253Atrue%257D&pivotCfg=%257B%2522rows%2522%253A%255B%255D%252C%2522cols%2522%253A%255B%255D%252C%2522aggregatorName%2522%253A%2522Count%2522%252C%2522rendererName%2522%253A%2522Row%2520Heatmap%2522%252C%2522vals%2522%253A%255B%255D%252C%2522hiddenAttributes%2522%253A%255B%255D%252C%2522hiddenFromAggregators%2522%253A%255B%255D%252C%2522hiddenFromDragDrop%2522%253A%255B%255D%252C%2522menuLimit%2522%253A500%252C%2522unusedAttrsVertical%2522%253A85%257D&linksTableSort=%255B%257B%2522column%2522%253A%2522source_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&factorsTableSort=%255B%257B%2522column%2522%253A%2522citation_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&pivotStage=raw&ragScope=sources&ragSrcCols=%255B%2522field%257Ccontent%2522%255D&ragSrcRows=all&ragLnkCols=%255B%2522field%257Ccause%2522%252C%2522field%257Ceffect%2522%255D&ragLnkRows=all&ragFacCols=%255B%2522field%257Clabel%2522%255D&vigReg=us-east5&vigModel=gemini-2.5-flash&vigCheck=true&vigThink=0&vigThinkLvl=#tribes-filter)|Add 
|**Team**|All of Pro, plus<br><br>- [Sharing within a team](http://localhost:8080/?rightTab=account&project=example-original-copy-copy&leftWidth=31&filters=%255B%257B%2522id%2522%253A%2522filter-1%2522%252C%2522type%2522%253A%2522zoom%2522%252C%2522isDefault%2522%253Atrue%252C%2522level%2522%253A%2522none%2522%257D%252C%257B%2522id%2522%253A%2522filter-2%2522%252C%2522type%2522%253A%2522label%2522%252C%2522isDefault%2522%253Atrue%252C%2522selectedLabels%2522%253A%255B%255D%252C%2522matchMode%2522%253A%2522anywhere%2522%252C%2522stepsUp%2522%253A1%252C%2522stepsDown%2522%253A1%252C%2522traceThreads%2522%253Afalse%257D%252C%257B%2522id%2522%253A%2522filter-3%2522%252C%2522type%2522%253A%2522factor-frequency%2522%252C%2522isDefault%2522%253Atrue%252C%2522threshold%2522%253A1%252C%2522mode%2522%253A%2522minimum%2522%252C%2522which%2522%253A%2522sources%2522%257D%255D&columns=%255B%2522region%2522%252C%2522custom2%2522%252C%2522custom1%2522%252C%2522flavour%2522%255D&sourcesTab=sources-table-tab&map=%257B%2522layout%2522%253A%2522dagre%2522%252C%2522dagreNodeSepHorizontal%2522%253A1%252C%2522dagreNodeSepVertical%2522%253A19%252C%2522colaNodeSpacing%2522%253A201%252C%2522nodeLabelWrap%2522%253A284%252C%2522factorCountType%2522%253A%2522source%2522%252C%2522factorColourType%2522%253A%2522outcomeness%2522%252C%2522linkLabelType%2522%253A%2522source%2522%252C%2522showSelfLoops%2522%253Atrue%257D&pivotCfg=%257B%2522rows%2522%253A%255B%255D%252C%2522cols%2522%253A%255B%255D%252C%2522aggregatorName%2522%253A%2522Count%2522%252C%2522rendererName%2522%253A%2522Row%2520Heatmap%2522%252C%2522vals%2522%253A%255B%255D%252C%2522hiddenAttributes%2522%253A%255B%255D%252C%2522hiddenFromAggregators%2522%253A%255B%255D%252C%2522hiddenFromDragDrop%2522%253A%255B%255D%252C%2522menuLimit%2522%253A500%252C%2522unusedAttrsVertical%2522%253A85%257D&linksTableSort=%255B%257B%2522column%2522%253A%2522source_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&factorsTableSort=%255B%257B%2522column%2522%253A%2522citation_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&pivotStage=raw&ragScope=sources&ragSrcCols=%255B%2522field%257Ccontent%2522%255D&ragSrcRows=all&ragLnkCols=%255B%2522field%257Ccause%2522%252C%2522field%257Ceffect%2522%255D&ragLnkRows=all&ragFacCols=%255B%2522field%257Clabel%2522%255D&vigReg=us-east5&vigModel=gemini-2.5-flash&vigCheck=true&vigThink=0&vigThinkLvl=#sharing-and-permissions)<br>- [Live collaboration](http://localhost:8080/?rightTab=account&project=example-original-copy-copy&leftWidth=31&filters=%255B%257B%2522id%2522%253A%2522filter-1%2522%252C%2522type%2522%253A%2522zoom%2522%252C%2522isDefault%2522%253Atrue%252C%2522level%2522%253A%2522none%2522%257D%252C%257B%2522id%2522%253A%2522filter-2%2522%252C%2522type%2522%253A%2522label%2522%252C%2522isDefault%2522%253Atrue%252C%2522selectedLabels%2522%253A%255B%255D%252C%2522matchMode%2522%253A%2522anywhere%2522%252C%2522stepsUp%2522%253A1%252C%2522stepsDown%2522%253A1%252C%2522traceThreads%2522%253Afalse%257D%252C%257B%2522id%2522%253A%2522filter-3%2522%252C%2522type%2522%253A%2522factor-frequency%2522%252C%2522isDefault%2522%253Atrue%252C%2522threshold%2522%253A1%252C%2522mode%2522%253A%2522minimum%2522%252C%2522which%2522%253A%2522sources%2522%257D%255D&columns=%255B%2522region%2522%252C%2522custom2%2522%252C%2522custom1%2522%252C%2522flavour%2522%255D&sourcesTab=sources-table-tab&map=%257B%2522layout%2522%253A%2522dagre%2522%252C%2522dagreNodeSepHorizontal%2522%253A1%252C%2522dagreNodeSepVertical%2522%253A19%252C%2522colaNodeSpacing%2522%253A201%252C%2522nodeLabelWrap%2522%253A284%252C%2522factorCountType%2522%253A%2522source%2522%252C%2522factorColourType%2522%253A%2522outcomeness%2522%252C%2522linkLabelType%2522%253A%2522source%2522%252C%2522showSelfLoops%2522%253Atrue%257D&pivotCfg=%257B%2522rows%2522%253A%255B%255D%252C%2522cols%2522%253A%255B%255D%252C%2522aggregatorName%2522%253A%2522Count%2522%252C%2522rendererName%2522%253A%2522Row%2520Heatmap%2522%252C%2522vals%2522%253A%255B%255D%252C%2522hiddenAttributes%2522%253A%255B%255D%252C%2522hiddenFromAggregators%2522%253A%255B%255D%252C%2522hiddenFromDragDrop%2522%253A%255B%255D%252C%2522menuLimit%2522%253A500%252C%2522unusedAttrsVertical%2522%253A85%257D&linksTableSort=%255B%257B%2522column%2522%253A%2522source_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&factorsTableSort=%255B%257B%2522column%2522%253A%2522citation_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&pivotStage=raw&ragScope=sources&ragSrcCols=%255B%2522field%257Ccontent%2522%255D&ragSrcRows=all&ragLnkCols=%255B%2522field%257Ccause%2522%252C%2522field%257Ceffect%2522%255D&ragLnkRows=all&ragFacCols=%255B%2522field%257Clabel%2522%255D&vigReg=us-east5&vigModel=gemini-2.5-flash&vigCheck=true&vigThink=0&vigThinkLvl=#live-collaboration)<br>- [Detailed logs of all actions](http://localhost:8080/?rightTab=account&project=example-original-copy-copy&leftWidth=31&filters=%255B%257B%2522id%2522%253A%2522filter-1%2522%252C%2522type%2522%253A%2522zoom%2522%252C%2522isDefault%2522%253Atrue%252C%2522level%2522%253A%2522none%2522%257D%252C%257B%2522id%2522%253A%2522filter-2%2522%252C%2522type%2522%253A%2522label%2522%252C%2522isDefault%2522%253Atrue%252C%2522selectedLabels%2522%253A%255B%255D%252C%2522matchMode%2522%253A%2522anywhere%2522%252C%2522stepsUp%2522%253A1%252C%2522stepsDown%2522%253A1%252C%2522traceThreads%2522%253Afalse%257D%252C%257B%2522id%2522%253A%2522filter-3%2522%252C%2522type%2522%253A%2522factor-frequency%2522%252C%2522isDefault%2522%253Atrue%252C%2522threshold%2522%253A1%252C%2522mode%2522%253A%2522minimum%2522%252C%2522which%2522%253A%2522sources%2522%257D%255D&columns=%255B%2522region%2522%252C%2522custom2%2522%252C%2522custom1%2522%252C%2522flavour%2522%255D&sourcesTab=sources-table-tab&map=%257B%2522layout%2522%253A%2522dagre%2522%252C%2522dagreNodeSepHorizontal%2522%253A1%252C%2522dagreNodeSepVertical%2522%253A19%252C%2522colaNodeSpacing%2522%253A201%252C%2522nodeLabelWrap%2522%253A284%252C%2522factorCountType%2522%253A%2522source%2522%252C%2522factorColourType%2522%253A%2522outcomeness%2522%252C%2522linkLabelType%2522%253A%2522source%2522%252C%2522showSelfLoops%2522%253Atrue%257D&pivotCfg=%257B%2522rows%2522%253A%255B%255D%252C%2522cols%2522%253A%255B%255D%252C%2522aggregatorName%2522%253A%2522Count%2522%252C%2522rendererName%2522%253A%2522Row%2520Heatmap%2522%252C%2522vals%2522%253A%255B%255D%252C%2522hiddenAttributes%2522%253A%255B%255D%252C%2522hiddenFromAggregators%2522%253A%255B%255D%252C%2522hiddenFromDragDrop%2522%253A%255B%255D%252C%2522menuLimit%2522%253A500%252C%2522unusedAttrsVertical%2522%253A85%257D&linksTableSort=%255B%257B%2522column%2522%253A%2522source_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&factorsTableSort=%255B%257B%2522column%2522%253A%2522citation_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&pivotStage=raw&ragScope=sources&ragSrcCols=%255B%2522field%257Ccontent%2522%255D&ragSrcRows=all&ragLnkCols=%255B%2522field%257Ccause%2522%252C%2522field%257Ceffect%2522%255D&ragLnkRows=all&ragFacCols=%255B%2522field%257Clabel%2522%255D&vigReg=us-east5&vigModel=gemini-2.5-flash&vigCheck=true&vigThink=0&vigThinkLvl=#logs-panel)<br>- [Admin can enforce two-factor authentication](http://localhost:8080/?rightTab=account&project=example-original-copy-copy&leftWidth=31&filters=%255B%257B%2522id%2522%253A%2522filter-1%2522%252C%2522type%2522%253A%2522zoom%2522%252C%2522isDefault%2522%253Atrue%252C%2522level%2522%253A%2522none%2522%257D%252C%257B%2522id%2522%253A%2522filter-2%2522%252C%2522type%2522%253A%2522label%2522%252C%2522isDefault%2522%253Atrue%252C%2522selectedLabels%2522%253A%255B%255D%252C%2522matchMode%2522%253A%2522anywhere%2522%252C%2522stepsUp%2522%253A1%252C%2522stepsDown%2522%253A1%252C%2522traceThreads%2522%253Afalse%257D%252C%257B%2522id%2522%253A%2522filter-3%2522%252C%2522type%2522%253A%2522factor-frequency%2522%252C%2522isDefault%2522%253Atrue%252C%2522threshold%2522%253A1%252C%2522mode%2522%253A%2522minimum%2522%252C%2522which%2522%253A%2522sources%2522%257D%255D&columns=%255B%2522region%2522%252C%2522custom2%2522%252C%2522custom1%2522%252C%2522flavour%2522%255D&sourcesTab=sources-table-tab&map=%257B%2522layout%2522%253A%2522dagre%2522%252C%2522dagreNodeSepHorizontal%2522%253A1%252C%2522dagreNodeSepVertical%2522%253A19%252C%2522colaNodeSpacing%2522%253A201%252C%2522nodeLabelWrap%2522%253A284%252C%2522factorCountType%2522%253A%2522source%2522%252C%2522factorColourType%2522%253A%2522outcomeness%2522%252C%2522linkLabelType%2522%253A%2522source%2522%252C%2522showSelfLoops%2522%253Atrue%257D&pivotCfg=%257B%2522rows%2522%253A%255B%255D%252C%2522cols%2522%253A%255B%255D%252C%2522aggregatorName%2522%253A%2522Count%2522%252C%2522rendererName%2522%253A%2522Row%2520Heatmap%2522%252C%2522vals%2522%253A%255B%255D%252C%2522hiddenAttributes%2522%253A%255B%255D%252C%2522hiddenFromAggregators%2522%253A%255B%255D%252C%2522hiddenFromDragDrop%2522%253A%255B%255D%252C%2522menuLimit%2522%253A500%252C%2522unusedAttrsVertical%2522%253A85%257D&linksTableSort=%255B%257B%2522column%2522%253A%2522source_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&factorsTableSort=%255B%257B%2522column%2522%253A%2522citation_count%2522%252C%2522dir%2522%253A%2522desc%2522%257D%255D&pivotStage=raw&ragScope=sources&ragSrcCols=%255B%2522field%257Ccontent%2522%255D&ragSrcRows=all&ragLnkCols=%255B%2522field%257Ccause%2522%252C%2522field%257Ceffect%2522%255D&ragLnkRows=all&ragFacCols=%255B%2522field%257Clabel%2522%255D&vigReg=us-east5&vigModel=gemini-2.5-flash&vigCheck=true&vigThink=0&vigThinkLvl=#admin-mfa-per-user)<br>- Annual team accounts also get 4x30 minute live support sessions for the whole team|

## References

·        Atari, Xue, Park, Blasi, & Henrich (2023). _Which Humans?_. PsyArXiv. [https://hmpa.hms.harvard.edu/sites/projects.iq.harvard.edu/files/culture_cognition_coevol_lab/files/which_humans_09222023.pdf](https://hmpa.hms.harvard.edu/sites/projects.iq.harvard.edu/files/culture_cognition_coevol_lab/files/which_humans_09222023.pdf).

·        Braun, V., & Clarke, V. (2023). _Toward good practice in thematic analysis: Avoiding common problems and be(com)ing a knowing researcher_. _International Journal of Transgender Health_, 24(1), 1–6. doi: 10.1080/26895269.2022.2129597

·        Dai, Xiong, & Ku (2023). _LLM-in-the-loop: Leveraging Large Language Model for Thematic Analysis_. [https://arxiv.org/abs/2310.15100v1](https://arxiv.org/abs/2310.15100v1).

·        Fardghassemi, S., & Joffe, H. (2022). _Qualitative and output data on loneliness among young adults_ (p. 15430034 Bytes) [Dataset]. University College London. [https://doi.org/10.5522/04/17212991](https://doi.org/10.5522/04/17212991)

·        Friese (2025). _Conversational Analysis with AI - CA to the Power of AI: Rethinking Coding in Qualitative Analysis_. [https://doi.org/10.2139/ssrn.5232579](https://doi.org/10.2139/ssrn.5232579).

·        Friese, S., Nguyen‑Trung, K., Powell, S., & Morgen, D. (2025). _Beyond binary positions: Making space for critical and reflexive GenAI integration in qualitative research_.

·        Jowsey, Braun, Clarke, Lupton, & Fine (2025). _We Reject the Use of Generative Artificial Intelligence for Reflexive Qualitative Research_. [https://doi.org/10.2139/ssrn.5676462](https://doi.org/10.2139/ssrn.5676462).

·        Morgan, D. (2025). _Query-Based Analysis: A Strategy for Analyzing Qualitative Data Using ChatGPT_.

·        Nguyen-Trung (2025). _ChatGPT in Thematic Analysis: Can AI Become a Research Assistant in Qualitative Research?_. [https://doi.org/10.1007/s11135-025-02165-z](https://doi.org/10.1007/s11135-025-02165-z).

·        Nguyen-Trung, & Friese (2025). _On Methodological Incongruence in Applying Generative AI in Qualitative Data Analysis_. [https://doi.org/10.2139/ssrn.5874482](https://doi.org/10.2139/ssrn.5874482).

·        Powell, & Caldas Cabral (2025). _AI-assisted Causal Mapping: A Validation Study_. Routledge. [https://doi.org/10.1080/13645579.2025.2591157](https://doi.org/10.1080/13645579.2025.2591157).