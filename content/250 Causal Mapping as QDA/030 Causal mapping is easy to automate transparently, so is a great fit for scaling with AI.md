---
date: 2025-10-05
---

> **SOURCE NOTE (consolidation):** This file is a draft/fragment. The flagship QDA-facing paper is now: [[040 Causal mapping as causal QDA]].  
> Companion methods notes: [[900 Magnetisation]]; [[900 A simple measure of the goodness of fit of a causal theory to a text corpus]].

### Inter-rater agreement for causal coding is high, making it suitable for automation with AI

The fact that causal coding can be largely reduced to a series of low-level tasks makes it very suitable for automation with AI. High [precision and recall scores](https://drive.google.com/file/d/1-1SjT7B86BFn0sR9hRgjXCWnMDYWXh8T/view?usp=sharing) can be achieved. (Consolidating a large number of in-vivo labels can be accomplished mostly automatically with [clustering of text embeddings](https://docs.google.com/document/d/1d7J-aTOPnkOH1AQ2DsWZLFjlgaRxk8VG/edit).)

The AI is used only as a tireless, low-level but incredibly fast assistant with the instruction to code each and every causal claim in the text. This is radically different from the kind of AI-supported “black box” coding which essentially treats the AI as a trusted co-coder who is asked to make, or help make, high-level decisions such as "what are the main themes in this text?" or even “What is the overarching causal network in this text?”. 

The accuracy (precision and recall) of AI-supported causal coding is not perfect, but it is improving all the time. Creating, implementing and monitoring the coding protocol remains an essential task ("human in the loop") but we claim that AI-supported causal coding comes closer than other approaches to providing an almost out-of-the-box way to make sense of texts at scale.



The causal coding procedures we have outlined here represent a single-pass, non-iterative approach. Of course this can be expanded to include the more iterative approach essential to most QDA approaches, with varying levels of human oversight. For example we can quickly and cheaply experiment with different coding rules, compare the results, modify the rules and iterate again. This ability to experiment with, compare and iterate potentially hundreds of coding rules and algorithms is a real strength of (semi-)automated coding.

Vulnerable to limited attention: if we really process only one section at a time, we will be unable to notice cross-references or places where one section qualifies another, as pointed out by Udo Kelle (1997) xx. This may not be a fundamental limitation of machine-led approaches if we arbitrarily expand the surrounding context, increasing the attention or context window, but at present this is slow and expensive. See A 2023 study by Rezaee et al. compared topic modeling (LDA) vs human qualitative coding of tweets, finding that automated methods reliably find dominant themes but miss subtle frames that human interpretive coding can catch.
