---
date: 2025-10-22
---

For example you might want to code the respondent's happiness at work as different from yet similar to their happiness at home. With a factor table, you could have a field called `label` = "Happiness" and another, say `context`, which is = either "Home" or "Work". This is what we do with the links table in Causal Map, where we do have some hard-coded (but optional) fields and some user-definable fields. 

Hierarchical coding is one way to bring some order to a whole crowd of factors. However, sometimes you don’t want to think in terms of a strict hierarchy, or maybe you have an additional set of themes which cut across that hierarchy.

[https://vimeo.com/671894620](https://vimeo.com/671894620)

**Tags** are useful in either of these cases.

Tags are just sequences of characters within a factor label to which you have given a special meaning, and which are unique and easy to search for. These can include letters, emojis or phrases. You can do coding without any such tags if you want, but it can help when searching and filtering.

Factor tags are just like [#️⃣ Link hashtags](#%EF%B8%8F%E2%83%A3%20Link%20hashtags%2050a789cc60ad4b1e9cad10b81c68e2a1.md). Confusingly, a link hashtag doesn’t have to actually start with a `#`, and a factor tag can indeed start with a `#`, but we find it easier to keep the names separate like this. 

So a tag is nothing more than any sequence of characters which is repeated in several factor labels. Any sequence of characters will do. For example you could consider the letter “a” to be a tag and display the map showing all the factors which contain the letter “a”. But this wouldn’t be interesting. The trick when using tags is to decide on short, meaningful codes which will not be repeated anywhere else. For example you wouldn’t want to use a pair of tags like “women” and “men” to distinguish factors which are only relevant for one or the other gender because the “wo**men**” factors would also turn up when you search for “**men**”. That is why we have to be careful when creating tags, for example by preceding a sequence of characters with a tag `"#"`.

A quote like “family situation is better now because of improved food availability” can be coded like this:

> More food –> Improved wellbeing
> 

Now, maybe you are asked also to keep track of any aspects of the project which have to do with nutrition. Nutrition is not really part of your system of factors, but you would like to be able to construct some maps just to look at this aspect. So you can write this:

> More food #nutrition –> Improved wellbeing
> 

Similarly, if Improved Wellbeing is one of the desired outcomes of the project, we might want to reflect that by adding a tag “(Outcome)” like this.

> More food –> Improved wellbeing (Outcome)
> 

Then we can easily search for this and other desired outcomes.

A tag like “men” is not suitable because it is likely to appear elsewhere (e.g. as part of “women” or “management”). To get round this, add additional characters like a hash: “#men”; this makes the tag unique.

If you use curved or square brackets around your tags, you can use one of the app filters to hide the tags for specific maps if desired.
