---
date: 2025-09-22
---

# Why magnetic labels

You have already coded your dataset, manually or using AI, and now you want to relabel.

Suppose you already know what labels you want to use, perhaps:

- you knew before you even started
- you decided what labels you wanted after reviewing your data and looking at different auto-cluster solutions

Magnetic labels are a really simple solution for these cases.

# How to use them

![Untitled](img/9452d8de42e2466ca14c68ff0a67b6bb--Untitled.png)

You simply type the list of magnetic labels you want and decide on the power of the magnets (”magnetism”).

Magnetic labels attract existing labels of similar meaning, essentially relabelling these old labels with the new magnetic label. If an existing label is similar to two or more different labels, it is relabelled with the magnetic label it is most similar to. 

If you use low magnetism, the magnets are weak and only attract existing labels which are very similar to them.

Increasing the magnetism means that more and more existing labels are attracted to the magnetic labels.

Existing labels which are not attracted to any label are unchanged. This means that you can easily see if your magnetic labels cover most of the original content.

Best practice is then, after applying magnetic labels, to then auto-cluster the links in order to pick out important themes which are not covered by the magnetic labels.

> If you want you can even include hierarchical magnetic labels like `Health behaviour; hand washing`.
> 

## Storing your labels

Your magnetic labels are included if you save a bookmark aka saved View. 

You can also store your preferred label set in the Codebook in [The Files tab](https://www.notion.so/The-Files-tab-154b98461eca4b8296e7096c0fc41a6b?pvs=21).

# Use cases

- Drop in magnetic labels which contain the text from the “official” theory of change.
- See how much the existing labels get attracted to the magnetic labels, and what material is left over.
- Conduct “radical zero shot” auto coding with no codebook at all,
    - let the AI decide the best label for each case
    - do some auto clustering until you get a feel for the labels you really want in your story
    - type the labels into the magnetic clusters box

# Tips

## What if you have a *semantically ambiguous label?*

An example: you have some research about animals and you want to look for mentions of the organisation Animal Aid. If you use Animal Aid as a label, it might also pick up any mention of helping animals which have nothing to do with the organisation itself. 

One way to get round this is to use [🔗 The Manage Links tab](%F0%9F%94%97%20The%20Manage%20Links%20tab%2070835b4b20664837870680b7151d4c6e.md) to permanently recode any mention of Animal Aid in your factor labels into something unambiguous like, say, The Archibald Organisation. Choose a meaningless name which is not going to appear in or be related to to the rest of your material.

When doing this “hard recoding” remember to recode AnimalAid, Animals Aid etc as well.

## Attracting unwanted material *away* from your map

You can add an factor into magnetic clusters even if it doesn't appear in the final map. 

For example you might have a lot of material about blood donors and you don’t want material about donating clothes. As well as donating blood you might add the labels donating goods and donating money. You can filter these out later, but they will help restrict donating blood to what you want.

## Increasing coverage with hierarchical magnetic labels

It might just be that your interview material is so heterogeneous that, however you choose your magnetic labels, if you only have say 10 or 20 of them then they are just not going to cover more than say 30% of your links in all of your stories and that's just the way it is because the material is very broad. 

You might have hoped to arrive at a kind of global mind map - but the best you can do is just these most frequently mentioned common factors. You'd have to accept that it isn't in any sense a summary of *all* of the material because there's lots of other stuff that doesn't feature amongst the top 10 or 20 magnetic labels. 

You might then also want to focus on more specific maps for more specific subject areas.

Or maybe you have a sense that in fact much of the material really is held in common but you're struggling to find the right magnetic labels? One way to increase coverage is to use hierarchical magnetic labels, of which you might have even 30 or 60 or even 100, and then zoom out to level one. So you might have, say, magnets like:

Desire for innovation; digital

Desire for innovation; management approaches

....

And then you'd apply a zoom level of 1 in order to bundle these things together.

## Transformation and interpretation rules {.banner}### Transformation rule {.rounded}- **Input:** a links table with existing factor labels, a user-provided list of magnetic labels, and a magnetism threshold.
- **Transformation:** for each existing label, map it to the most similar magnetic label if similarity is high enough; otherwise keep the original label unchanged.
- **Output:** a links table/map with partially transformed labels, updated bundles/counts, and visible uncovered material.### Interpretation rule {.rounded}- Magnetic labels are a soft recoding layer for harmonization and exploration.
- Stronger magnetism usually increases coverage but can also pull in weaker semantic matches.
