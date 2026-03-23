---
date: 2025-10-02
---

The logic of QDA: you’ve done your analysis, now what?

The result of qualitative data analysis can be understood as, at least, some kind of qualitative theory or model at least of the sources’ beliefs, with at least some possibility of generalising beyond them. But it can be hard to know what to do with the results of an emergent qualitative text analysis. There is no clear decision procedure: we can ask the author, and the answer is: some explanation, i.e. more text. In more reproducible approaches we do get some more structured outputs such as tables of frequencies. Some authors such as Mayring see these kinds of outputs as an important analysis result. QDA software is often used to capture and structure and even make inferences with these kinds of outputs. 

In the logic of (non-causal) reproducible QDA, we can do things like this:

- - count occurrences of concepts, and use ordinary arithmetic to report eg which of two concepts was more common
    
- - count co-occurrences of two concepts, and construct measures like association between concepts, and more generally combine and query occurrences with boolean logic
    
- - create case/code matrices
    
- - report relationships between sources and concepts, for example to compare codings of one concept for different genders
    
- - reason about concepts, for example to deduce that an occurrence of "lion" is also an occurrence of "mammal", either relying on our implicit understanding of the concepts or through the explicit declaration of a parent-child relationship. 


Of course frequency statistics are notoriously unstable, because they depend on our decisions about granularity and chunking. If I have a codebook which has 100 different codes for cats and only 1 code for dogs, we may conclude that dogs were mentioned in the text more often than any other animal-concept even if cat-concepts were mentioned more often in combination.  This is one reason why reasoning with these kinds of outputs can never be merely automated. There always has to be a “human in the loop”. 

Nevertheless the point is that we can understand the output of QDA coding as some proportion of "more text", which itself needs to be interpreted by humans, and a complementary proportion of machine-readable, structured output which can be used to ask and answer questions (Which are the overarching themes? How much does climate anxiety come up as a theme? Who mentions it most?) at least somewhat independently of human guidance. 

  

QDA logic can also be extended beyond the simple logic of frequencies and occurrences to apply (special kinds of) codes which have additional explicit rules associated with them, such as code weighting (as for example in MaxQDA). This means we can for example apply codes like “somewhat happy” or ‘very unhappy’ which enable us to say that the expression of happiness in one case is stronger than the other, or (if we also allow coding for time) that happiness increases or decreases over time. These extra deductions we can make come free with the (implicit or explicit) underlying ordinal logic of comparison of intensity.



### QDA without coding

Coding does not have to be central to qualitative data analysis [@morganQueryBasedAnalysisStrategy2025a; @nguyen-trungNarrativeIntegratedThematicAnalysis2025]. …
  