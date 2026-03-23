---
date: 2025-10-22
---

> Question: *I  already have a codebook I want the AI to use. How to work this codebook into the prompt?*


First, you have to make a decision. Do you want to: 

a. stick only to the codebook
b. stick to codebook mostly but code other stuff too which does not fit into the codebook. If you do this, tell the AI to add an additional tag so you can easily find and exclude those if you want, e.g. `[new]`, or just tell it to add a star at the end `*` .
c. you want to make a compromise between (a) and (b). If so you can use [[Hierarchical coding]] . Tell the AI to use only top-level labels from the codebook, but it is free to improvise the last part of the label.

> Question: *Also, am I right in thinking that, especially when I do not specify a codebook, I should get the AI to code sentiment (positive and negative) sentiments for each link?

Yes! That's because when you use a zero codebook, you will probably go on to use  magnets in soft recoding. It's a special feature of soft recoding that `decrease in blah blah` turns out to be quite close in meaning to `increase in blah blah` , so it can be hard to distinguish the two. In that case, getting the AI to code sentiment as well is a good way to distinguish between them. 

But if you are using an explicit codebook, it's good to explicitly offer both versions of labels which are likely to appear in both a "positive" and a "negative" version, e.g. `increased income` and `decreased income`, and `good/available health care` and `poor/ unavailable health care`. In this case, you probably don't need to ask the AI to also code sentiment, unless you want that for other reasons.
