---
date: 2025-09-22
---

In our implementation of causal mapping in the Causal Map app, [[0130.2 Our approach is minimalist -- we do not code the strength of a link]]. 

Providing metadata as a column makes sense when the values of this column make sense across the whole dataset, across all multiple links, like let's say before covid and after covid. 

Such a column can function a bit like a *context* variable, for different time periods or applying to different stakeholders. Context in this sense might be seen as functioning a *bit* like a causal factor but not exactly.

But we can also provide metadata as free-form tags. We provide a hard-coded "tags" column for which users can provide comma-separated lists of tags which are made up and adapted on the fly. They don't necessarily make sense across the whole dataset.

In Causal Map 4, as well as a hard-coded Tags column, we do provide a hard-coded sentiment column which can take the values -1, 0 and 1, and which can be averaged to any number between -1 and 1.

![[720 Link metadata -- Sentiment]]

We also provide arbitrary additional free-form, free-text columns for any purpose. We often like to add a column like this:

![[730 Link metadata -- Time reference]]



![[800 Link metadata -- quality of evidence]]

... or simply to code a tag like "#doubtful".