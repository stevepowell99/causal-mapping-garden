
|          |                                            |                                                               |                                                                                                |                                                                                                       |                                             |
| -------- | ------------------------------------------ | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------- |
|          | **Hard coding**                            | **Hard recoding**                                             | **Links recoding**                                                                             | **Factors recoding**                                                                                  | **Soft recoding**                           |
| Accuracy | Highest                                    | ...                                                           | ...                                                                                            | ...                                                                                                   | Lowest                                      |
| Speed    | Slowest                                    | ...                                                           | ...                                                                                            | ...                                                                                                   | Fastest                                     |
|          |                                            |                                                               |                                                                                                |                                                                                                       |                                             |
| Manual   | Just code manually                         | Make a copy of your file, delete links and start again        | Edit manually in Links table or Map, <br>- or use search/replace in Links table                | Edit manually in Factors table or Map, <br>- or use search/replace in Factors table<br>- or Bulk Edit | -                                           |
| AI       | Just code with AI, with/without a codebook | As above, or just put the switch "skip  coded sources" to off | AI Answers / Links.<br>Recode labels permanently or into temporary cause/effect columns.  <br> | AI Answers / Filters.<br>Recode labels permanently or into temporary cause/effect columns             | Apply magnetic labels in Soft Recode filter |

What's the point of Links and Factors recoding? What's the difference?

 - Soft recoding is only as good as the underlying embedding space, and it is never perfect.
 - Hard recoding can take a long time, is expensive, and does not encourage experimentation
 - With Links/Factors recoding, you can:
	 - Recode just the currently filtered sources/links (or all links)
	 - Recode the permanent cause/effect labels or recode into one or more sets of temporary columns, e.g. `experiment1_cause` and  `experiment1_effect`, and then use these temporary labels in your maps and tables.
	 - There is also another option Answers which is not about recoding; it is simply a way to send your links and/or factors data to an AI and getting a text answer.

But the main point is that rather than just hoping the magnetisation will work the way you want it to, you can do smart recoding as if you had an assistant to work through each label. For example you can say "Relabel everything which expresses a decrease or lack of something with a ~" or "Look at all these labels and tag each with `[Food]` or `[Health]"

. 
- You can even bring other columns into play, for example citation count, source count etc. 
- Links recoding is significantly more powerful because you can also include the actual Quote as well as both Cause and Effect. This means the AI can make its decision with a lot more context. So this is almost like recoding from scratch, but the original coding has already identified causal claims and all we have to do is relabel the labels with the same complete information about the claim. 
- Be careful: it's tempting to say things like "Find 3-8 top-level factor labels which cover the meaning of all these labels and recode them with the new top-level labels", but remember the "Rows per call" slider: with a large set of links and lots of quotes you will probably have to break up your work into multiple chunks, and each call may come up with different labels. In this case you could use the Answers mode (or the Cluster part of Soft Recode filter) first to develop some labels. 




![[500 Recoding labels temporarily]]