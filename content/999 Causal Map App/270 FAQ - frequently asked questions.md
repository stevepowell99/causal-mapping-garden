### Tips on coding

First of all, there's nothing to worry about, it's fun!

The versioning / backups feature means you can always go back to any version of your file at any earlier time point.

Also, [bulk editing of factor labels](../links-search-replace/) makes it easy to rapidly change one or many links or factors. And you can do it either globally, i.e. changing one factor everywhere in the file, or you can do it for particular sources or specific kinds of links by using filters.

Usually, don't bother coding the same link more than once for the same source, unless they bring up distinctively different evidence each time.
- It's okay not to code a source at all. If there's nothing in it, or if people are just making vague and general sources.
- You'll find you're constantly shifting between sometimes creating new factors, and then going back and reviewing them and merging them and organising them using the [bulk editing of factor labels](../links-search-replace/).
- Don't forget you can combine two or more factors into one using the [bulk editing of factor labels](../links-search-replace/) .
- Don't forget when you want to search rapidly through already coded links through all of the sources, you can click on the rows in [the bulk editing of factor labels](../links-search-replace/) to go back to the relevant sources directly.
- Occasionally, a source will make a comment about something which is worth coding, even though there isn't actually a causal link. For example, they might make general comments about some outcome without saying what causes it. In this case just use plain coding. (But if you find you are doing this a lot, you might need to rethink your research design.)
- If you are using [hierarchical/nested coding](../zoom-filter/) (and you probably should) don't forget you can see the whole map zoomed out to the top level: just press the appropriate button in the Filters panel.

### Help, I have too many factor labels!!

That's a classic problem with causal mapping (or any free text coding). 
We have several ways to help you regain control when you have dozens or even thousands of factor labels with overlapping meaning.
 
1. Use the [Bulk editor](../factors-relabel/). It's a really powerful way to inspect and change all or part of your factor labels. You can sort alphabetically, by citation count ... and you can highlight and edit  multiple matching labels at once!
2. Use the quick [Search/Replace box](../factors-search-replace/) at the top of the Factors Table tab. It's simple but also powerful. If you want to rename your factors in the context of thinking about causes and effects, there is a similar widget in the [links table](../links-search-replace/).
3. To look at similar labels in the map, type one or more fragments (e.g. "income", "Money") into a [Factor label filter](../factor-label-filter/) so you can see where the corresponding factors appear in your map
4. If you have more than a hundred labels and you have an AI subscription, the [Soft Recode](../soft-recode-plus-filter--soft-recode-plus/) filter is amazing!  

### Do I have the latest version?

See [Navbar → About menu](../navbar-about/) to view the version number. The app should silently update itself when a new version is available.

### How can I adjust my links or sources data in bulk (round-tripping)?

As an alternative to editing your [links](../links-panel/) and [sources](../sources-panel/) tables manually in the app, you can do what we call round-tripping: [download](../manage-current-project/) your file, tweak this Excel file manually (e.g. by adding additional columns to the sources tab) and [upload](../manage-projects/) it again into a new Causal Map project. Like this you always have to create a new project, which helps you not get mixed up with which version is which. 


### How can I deal with closed questions like in QuIP?

In Causal Map 4 there is no special treatment of QuIP-style closed questions. What you can do is this:

1) if you want to be able to see the closed question answers while coding, include the answers to the closed questions simply as part of the text of the interview with an appropriate question number. None of this has any meaning to the app, but it might be useful to have for coding.
2) If you want to also use the closed question scores for further analysis, e.g. to make a map of all the interviews which answered an average of better than 0 to some question, then just add a custom column for each question and add the average scores for each question into each column. Then you can apply these values as filters, see [here](../source-groups-filter/).

### What does the 'recycle weakest magnets' slider do?

The slider temporarily removes the N weakest magnets from your list and reassigns their raw labels to the stronger magnets. 

For example, if you created 50 magnets but after filtering you only have 5 factors showing with 9% coverage, those 45 weak magnets might be taking evidence away from your main ones. Try moving the slider to 40 to recycle those weakest magnets - this gives their evidence a chance to match with the stronger magnets instead (using the same similarity criterion).

This is most useful when you have lots of fiddly magnets that nibble away at your main ones but then disappear without trace. Note that the slider is a bit unpredictable if you have intervening filters.

### My pasted images are failing after a while in my markdown editor

If you paste not just an image but the html including image, legend etc from a bookmark, it works ok if you paste it into an app like Word, but with a markdown editor like Obsidian, the image remains as a URL, but our URLs are only temporary (we don't save images forever at Causal Map), so after a while the image will fail. So, you need to install a plugin for your markdown editor, like the Obsidian plugin called Local Images Plus.