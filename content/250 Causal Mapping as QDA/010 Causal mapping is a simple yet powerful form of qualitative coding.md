---
date: 2025-11-17
---

> **SOURCE NOTE (consolidation):** This file is a draft/fragment. The flagship QDA-facing paper is now: [[040 Causal mapping as causal QDA]].  
> Companion methods notes: [[900 Magnetisation]]; [[900 A simple measure of the goodness of fit of a causal theory to a text corpus]].

**Is this for you?** If you're at least a bit familiar with qualitative coding and Qualitative Data Analysis (QDA) as a way of making sense of texts, but you're not yet convinced that causal mapping is a really interesting twist on that, or you've never even heard of causal mapping, this short series on causal QDA is for you! Plus, we are now making available a new version of our [software](https://causalmap.app/cm4) for exploring causal mapping which is free for core functionality.

**Quick background on causal mapping**: Causal mapping has been used since the 1970s across a range of disciplines from management science to ecology. It helps make sense of the causal claims (about "what influences what") that people make in interviews, conversations, and documents. This data is coded, combined, and displayed in the form of a causal map. Each claim adds a link to the map. These maps represent individuals' and groups' mental models: individual links and (often interlocking) longer chains of causal explanations. For every link, we can store the original sources and quotes. Causal mapping is an approach to coding texts but also to synthesising the coding, so we can think of it as a form of qualitative coding in particular and of QDA more generally. A wider overview of causal mapping as applied in disciplines from ecology to organisation science is presented in (Powell et al., 2024) and in [this bibliography](https://garden.causalmap.app/bibliography).

Our aim is to present causal QDA as a particularly useful way to make sense of text in a way which is straightforward to apply with a highly, though not completely, standardised approach.

Our steps in doing this are:

- We present causal QDA as an important and useful form of QDA
- We explain why causal coding can be easier to apply than non-causal coding.
- We explain how the result of causal coding is a causal network which can be visualised in the form of causal maps and used to answer useful questions.
- We claim that the kinds of questions which causal maps can help answer tend to be particularly useful and practical questions because they are about what causes what, through the eyes of stakeholders.
- Although the focus of this series is not on AI assistance, we also argue that these properties make causal mapping particularly suitable for automation with AI in a way which is verifiable and avoids using the AI as a “black box”.

In two later posts, we will argue:

- [[020 Causal mapping benefits from out-of-the box algorithms to answer important questions]]
- [[030 Causal mapping is easy to automate transparently, so is a great fit for scaling with AI]]

### Why now?

If you've been following our work at Causal Map Ltd (and the work of our colleagues at BathSDR), you'll now that we've been talking about and promoting causal mapping for some years now. We've been providing software like the Causal Map app as well as consultancy services for evaluators and researchers. But we were the first to admit that our Causal Map app was sometimes slow and frustrating to use. We're happy to say that the latest version of the app, the **completely new Causal Map 4**, is not only a vast improvement (and a lot faster!) but also, public projects are **free** for core functionality. We've done this to lower the bar for evaluators, researchers and academics to explore and use causal mapping.

### What is causal coding?

Causal mapping has been used across multiple disciplines for over 50 years (Ackermann et al., 2004; Axelrod, 1976; Eden, 1992; Hodgkinson et al., 2004; Laukkanen, 1994; Narayanan, 2005; Powell et al., 2024), but though some causal mapping practitioners have published guides to causal coding, starting from (Wrightson, 1976) it has not often been presented as (also) a stand-alone form of QDA. We tried to rectify that in (Powell et al., 2024). This post follows on from that explication.

Coding for causal mapping has traditionally been done manually, just like working with Nvivo, Dedoose et al., but instead of coding individual _themes_ we code _links between themes_ (aka causal factors). For example in the text “the floods destroyed our crops”, we would code “the floods” as the cause, “destruction of our crops” as the effect.

Some forms of causal mapping may involve constructing maps directly, for example in participatory fashion with a group of people. In this post we don’t cover that kind of method, focusing only on cases where an analyst codes causal claims within text -- similar to other forms of qualitative coding.

### What makes causal coding special

Qualitative coding is usually designed to capture **concepts or themes in general**, whereas in causal QDA we code (claimed) causal **links between causal factors**: things, events, phenomena, changes: anything which can affect or influence, or be affected or influenced by, something else.

![Article content](https://media.licdn.com/dms/image/v2/D4E12AQGSxgHhe_2xWw/article-inline_image-shrink_1500_2232/B4EZm5KNlDIIAU-/0/1759748087752?e=1762992000&v=beta&t=pYjd6S4DitXWFNHK59khrHGL6mjrNhqk4_NecxSKARc)

Using non-causal coding we can create post-hoc causal links between independent concepts as in the figure above, version 2. This could make it of epistemic network analysis, , see Lazarus (zotero ) TODO. Or we can create the causal link as a monolithic concept as in version 1. (This option is mentioned in (Saldaña, 2015).) But then the word “cause” does not really do anything: we can’t automatically deduce anything from it1. We can do ordinary common-sense reasoning on the basis of the coding because we understand the words "cause" and "influence", just as we can do reasoning based on our understanding of floods or crops. But causal coding goes further because it is explicitly designed as an input to causal reasoning algorithms.

In causal QDA, the primary act of coding is to highlight a specific quote from within a statement and identify the causal claim made by simultaneously identifying a pair of causal factors: a "cause" and an "effect". In causal QDA, we _only_ code causal claims. The causal factors only exist as one or other end of a causal link and have no meaning except in their role as either end of a causal link. The coding _Floods happened → Crops destroyed_ IS a causal link, and a set of such links can be immediately visualised as a network or map using suitable software – for example with [Excel and Gephi](https://causalmap.notion.site/Coding-with-Excel-f5d2ea5542004d28882f67613bef1850).

In causal coding, the result of each act of coding is a link, a pair of factors (an ordered pair, because B → C is not the same as C → B). It is the factors which are the atomic units, which form the codebook, even though the factors only make sense as part of causal links.

Causal coding can, of course, take account of **context** simply by ensuring it that context is noted separately and included in the interpretation of the resulting causal maps. A more interesting challenge is to include context as part of the coding, for example by using cross-codebook tags (such as, say "post-COVID only") which can appear as part of many different factor labels, or by including additional tags as part of each link, or by introducing contextual factors (such as "COVID pandemic") as additional causal factors in the map itself.

### What are the advantages of causal QDA?

### A more restricted, causal, ontology simplifies the coding task

> What are the causal factors, the cause and the effect, at each end of this causal claim?

This is a very challenging question, but it is a whole ballgame less challenging, less open to interpretation, than this one:

> What themes/concepts are mentioned here?

This fact makes it much easier to get started on and complete our coding, whether we are going to code deductively (from an established codebook) or inductively (developing the codebook iteratively). It is particularly easy when working inductively and using in-vivo labels close to the original text: we simply have to identify each and every causal claim in the text, and for each one, identify the cause and the effect – the “causal factors”. (Using in-vivo labels means we will later need another way to consolidate the resulting large number of factor labels.)

In some cases it might be necessary to define in more detail (as part of the codebook) exactly what we mean be "X causes or influences Y", for example to distinguish hypothetical from factual claims. Inter-rater agreement in causal coding can be good (Buzogany et al., 2024; McCardle-Keurentjes et al., 2018). This means that in the simplest case we can reduce most of causal coding to a series of low-level tasks: _code each and every causal claim in the text_. Of course, it is possible to work in a more deductive way, with a more explicit causal codebook.

There are still lots of theoretical, high-level decisions to make when doing causal coding, many of which cannot be easily anticipated, for example, How shall we deal with time, or with tentative or hypothetical statements? What shall we do with claims which one person makes about another's beliefs? And so on. These kinds of problems are familiar across all kinds of qualitative coding. But the focus on causal claims is still a massive simplification of the coding task.

### The product of causal mapping is explicitly a theory or qualitative model which can be easily queried to ask and answer important questions

Just like with any other form of QDA, when we finish the coding we can if we like report a bunch of statistics. In the ontology of causal QDA, we have factors, which are something like concepts, and also links, which are ordered pairs of factors. We can immediately make use of all of the usual frequency/occurrence logic for both factors and links, e.g. to report which was the most commonly mentioned causal factor and/or which was the most commonly mentioned causal link. The usual caveats about granularity and frequency apply (here and also in the following section).

But of course these frequencies are just the tip of the iceberg. The main product of causal mapping is not a set of tables or a static report but a qualitative causal network (a database of links) -- a live object which we can query to bunch of much more interesting and perhaps unanticipated questions, for example: which causal pathways do people identify as leading to their own wellbeing?

![Article content](https://media.licdn.com/dms/image/v2/D4E12AQEnvhaYeuCvmQ/article-inline_image-shrink_1500_2232/B4EZm5KNl4HEAU-/0/1759748087612?e=1762992000&v=beta&t=DBCfaM62UOWdwDzstow28e7TaHYCQ5kx7BSoYcYR7v8)

The causal beliefs of a larger number of people will of course be a mass of somewhat overlapping and somewhat contradictory information; maybe some whole sections of the causal map are only mentioned by particular sub-groups, or maybe there are some factors for which different groups disagree about the causes and effects; or maybe different groups mention approximately the same factor but use different language to describe it. A causal map, as a database of links, can contain all of these tensions and contradictions. The challenge is to apply the right queries to it in order to present these differences clearly.

This is possible above all because causal links have the special property of _transitivity_: if we know something about the paths from B to C and from C to D we can start to reason about the path from B to D. Just as a road map can help answer unanticipated questions like ...

> How can I get from Glasgow to Manchester, avoiding motorways?

.... a causal map can help us answer unanticipated questions like

> What is the collected evidence for a causal path from this intervention to that outcome?. By which route? For which pathway is there most evidence? Does everyone agree or are there relevant sub-groups of respondents?

### Focusing on causation helps cut to the chase in asking and answering questions which are really useful

The result of causal QDA is a network, a map, already structured to answer questions about causal beliefs (effects of causes and causes of effects). **Many practical, real-world questions, especially those of interest to program evaluators are at least partly causal in nature:**

- what leads to what?
- why does Z happen?
- what contributed to Q?
- what might happen if X?
- what are the dominant explanations for Y?

Causal mapping makes use of a causal vocabulary which provides some semi-standard ways not only to ask but also to answer causal questions.

In the next post we will look at some of these semi-standard procedures in more detail.

### Limitations and caveats

You want caveats? We've got loads of caveats, as outlined in Powell et al (2023). Here are a few.

- **Causal claims are not causal facts.** _Somebody_ claiming that X causes Y is certainly not enough evidence for _us_ to believe the same, without further information. We need to remain constantly vigilant to avoid confusing beliefs with facts.
- **Contribution not determination.** In the world of social science we rarely need to even consider anything like total causation: we deal with causal contribution, any form of possible influence, and hardly ever with determination. This goes for beliefs about causation just as much as facts about causation.
- **Beware the transitivity trap.** We have to be especially aware of the transitivity trap: even if we know that someone claims B influences C and someone else claims that C influences D, this does not mean that either of them does or should believe that B (indirectly) influences D.
- **Chunking and granularity.** As with any other form of coding, when creating our causal codes we have to pay attention to problems of chunking (where do phenomena begin and end) and granularity (how big are the chunks). This is important to bear in mind when dealing with coding frequencies, which can be very misleading if not interpreted and presented with care, just as with frequencies in any other form of coding, For example we might report that the factor "children's achievements" was very frequently mentioned, whereas if our codebook had instead included two separate factors for girls' achievements and boys' achievements, the frequencies would have been lower.
- **Always go back to the evidence.** While we can be guided by relative frequencies of links, we always consider the specific (combined) evidence for each link, for example when some evidence might be weak or valid only for a specific context. Frequencies start to become most interesting when a larger number of sources are included; but causal mapping has been very effectively used also for purely idiographic or single-source studies (e.g. in the earliest works by Ackerman and his team), in order to surface, for example, a politician's internal model of how a regional conflict is fuelled by coding their speeches and writings. (Here too, it can still be important to track the multiple mentions of the same factor or link.)
- **Causal coding cannot answer all questions about a text!** Causal coding will fail to code claims or statements which contain material which never influences anything else or is influenced by anything else. Causal coding, obviously, captures things which make a difference or are affected by things which make a difference, and while there is a strong argument that this is where we should be spending most of our research energy, we certainly would not claim that nothing else is important.
- **Broader theories.** Causal QDA is not on its own well suited to constructing broader theories with wider applicability in the sense of (Glaser & Strauss, 1967).
- **Latent vs explicit.** In our team, we have not used causal coding explicitly to search for latent as opposed to explicit material, ibid, (Braun & Clarke, 2006). We see no inherent reason why causal coding should be limited to explicit causal connections even though this more limited approach has been most common in the wider causal mapping literature.
- **Bare causation.** We also do not attempt to code anything other than what we call "bare" causation. Some causal mapping approaches do try to code the believed strength and/or polarity of the link (positive Vs negative), but one could also try to code ideas like necessity and/or sufficiency or even non-linear connections. For various reasons we believe this to be a wild goose chase in practice, but we do acknowledge that important information may go missing when we restrict coding to bare causation.

### Conclusion

When you've read all three posts in this series, we hope you will be convinced that causal mapping in general and causal coding in particular can and should be considered members of the family of QDA approaches, offering particular strengths. They: - simplify the coding task; - result in qualitative causal models which can be queried to answer important questions making use of a range of pre-existing algorithms; - are particularly amenable to automation and scaling using generative AI in a way which remains transparent and verifiable.

### What Causal Map Ltd provides

We provide a web app [Causal Map](http://causalmap.app/cm4) which is specifically designed for causal coding and has been used in many [academic and practical applications](http://causalmap.app/resources). Colleagues at BathSDR and others have applied (human-powered) causal coding in over 100 evaluation projects using the Qualitative Impact Protocol (Copestake et al., 2019), mostly in the field of international development, more recently using the Causal Map app.

Here is a broader list of [causal mapping software](https://en.wikipedia.org/wiki/List_of_causal_mapping_software).

---

1. Thanks to [Walter Antonio Canu](https://www.linkedin.com/feed/update/urn:li:activity:7310602473180676097/?commentUrn=urn%3Ali%3Acomment%3A\(ugcPost%3A7310602472496979968%2C7310650308542529537\)&dashCommentUrn=urn%3Ali%3Afsd_comment%3A\(7310650308542529537%2Curn%3Ali%3AugcPost%3A7310602472496979968\)#), [Filip Zielinski](https://www.linkedin.com/in/filip-zielinski-803207197), [Dr. Susanne Friese](https://www.linkedin.com/in/dr-susanne-friese/) and [Christina Silver, PhD](https://www.surrey.ac.uk/people/christina-silver) for suggesting additions here. ↩