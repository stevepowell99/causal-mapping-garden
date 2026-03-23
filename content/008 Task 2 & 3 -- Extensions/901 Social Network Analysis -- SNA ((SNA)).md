
For this extension, we can simply tweak our coding rule to code sending/receiving relationships between social actors instead of causal links between factors or events.

Social Network Analysis (SNA) is a useful tool for understanding and visualising connections between actors.

- In a **causal map**, the links are of just one type: X causes Y.
- A **social network map** is similar but the nodes are **actors** and the links can be of different types like "supports" or "knows" and they can have a direction or be undirected, like "works with".

## But how do you actually draw a social map?

1. With SNA just as with causal mapping you are faced with a choice. You can, just like in participatory systems mapping, simply get some experts or stakeholders to sit in a room and **collaboratively construct a map** -- out of their heads, so to speak -- with a whiteboard or some software like [sticky.studio](http://sticky.studio/) or [prsm.uk](http://prsm.uk/), and that can work really well.
2. But what if you want to do it more systematically and **empirically on the basis of, say, a whole bunch of interviews or reports**? It can be quite wearisome -- just like manual causal mapping at scale.

You can do it quite simply with [Causal Map](https://app.causalmap.app/), just drawing links as network connections rather than causal connections You can do that manually, or at scale with AI.

## For comparison: A causal map

Here is a top-level view of a familiar anonymized International Development project, which we auto-coded as a **causal** map. If you want to play with it in Causal Map (it's free), this is the bookmark [#1190.](https://app.causalmap.app/?bookmark=1190)

  

![[008 Task 2 & 3 -- Extensions/img/653a89a760b1297cb606adfafbaf9adf_MD5.png]]

  

## The social map

Here's the same set of interviews but coded as a kind of social network: _actor-focused._

![[008 Task 2 & 3 -- Extensions/img/0cc45609991b0872c124f69a405dc2f2_MD5.png]]

The coding instruction to the AI was very similar, just tweaking the instruction to focus relationship links rather causal links. Coding the 18 interviews took a few minutes. The big **difference is that in this case the links encode many different kinds of relationships**. Notice also that we've also automatically coded the sentiment of the associated link, and here the **average sentiment is shown as a colour** between red (negative) and blue (positive). Bookmark: **[#1191.](https://app.causalmap.app/?bookmark=1191)**

In Causal Map you can click on the individual links to see the quotes and explore the relationships.

We can show the different kinds of relationships on the links like this. This is part of a map filtered only to show female respondents. [#1066.](https://app.causalmap.app/?bookmark=1066)

![[008 Task 2 & 3 -- Extensions/img/a9d0eb57ac241731a19e1d54a4aa7f32_MD5.png]]

Pretty crass: the women say they collaborate/engage with their husbands but the arrow coming back to the respondents from their husbands is mostly negative.

## Coding rule

We used this instruction for SNA coding of our standard `example-original` project.

```
You will receive texts from an international development project.

Try to understand the overall social network in these texts: who is related to whom and how are they interrelated? then give me a standard table with columns, Sender, Receiver, Relationship, Sentiment, Time, and Quote.


## Sender/receiver

Identify places in the text where it says that one (type of) social actor has a relationship to another, and identify how these kinds of claims fit together into chains or networks.

In the table you give me, each row is one relationship mentioned in the text. Find common elements which appear as Sender and/or Receiver multiple times, forming chains and other patterns that tell bigger stories, not just isolated pairs of links. In the end, if one relationship really does not link up with anything else, it's ok to add it to the table. 

IT IS CRUCIAL THAT YOU UNDERSTAND THESE HAVE TO BE SOCIAL ACTORS (CITIZENS, INDIVIDUALS, GOVERNMENTS, GOVERNMENT DEPARTMENTS, SPECIFIC GROUPS OF PEOPLE, FIRMS, INSTITUTIONS ETC ETC ETC AND *NOT* NON-SOCIAL THINGS LIKE CLIMATE CHANGE, POSTERITY, THE PAST, etc etc. We are only interested in RELATIONSHIPS AND TRANSACTIONS.

ALSO NOT A RELATIONSHIP BETWEEN ACTORS (and therefore not to be coded): larger than, better than ... because these are abstract comparisons, not actual relationships or transactions.


Sending and receiving are not meant physically. For example "the children were suspicious of the policewoman" could be coded as Sender=children, Receiver=Police Officer, Relationship=Other; suspicion.

All the links have a direction. If you find mutual relationships for example "the children and the policewoman collaborated with another" then code two links, one in each direction.

Do not include a link just because something happened and it vaguely involved two actors. Only include it if this is primarily a relationship or transfer from one actor to another.


### Relationship

To characterise the relationship, you must choose one of these tags from the list. Only use "Other" if the relationship really does not fit the main list. Also use this as a final check that your link really is a relationship of some kind between two or more (kinds of) actors. If not, skip this link.

#### List of allowed relationship tags.


"Collaborates/ engages with"
"Advocates to"
"Asks for help from"
"Enables implementation for"
"Listens to"
"Builds trust with"
"Empowers through training and information sharing"
"Provides technical assistance / advice"
"Provides funding and strategic support"
"Provides reporting support to"
"Represses/ clamps down on"
"Provides aid to e.g. food"
"Causes social friction/problems among"
"Maintains colonial pressure on"
"Exploits"
"Places a burden on / imposes requirements on"
"Excludes"
"Fails to collaborate with"
"Divides and misinforms"
"Other"


Do NOT invent your own tags. Choose from this list. Except that with the "Other" tag, you can add details after a semicolon e.g. "Other; suspicious of". You MUST use relational phrases like "Other; afraid of" not "Other; afraid". Do NOT use commas ANYWHERE in your tags. 


### Sender/receiver labels

Invent a label for sender and for receiver. 


#### **Quote**

- The quote **must be a verbatim excerpt** from the text.

- **Do NOT modify or translate it.**

- **Do NOT break sentences apart or reassemble them differently.**

The quote should be long enough to be understood independently, usually 2-3 full sentences with surrounding context. Do not provide a fragment only, provide enough text that we can check if the entire causal claim with cause and effect are really evidenced by this quote.
Do NOT use ellipses ("...")—only full, uncut text.


### Sentiment
1 = Positive 0 = Neutral or unclear, -1 = Negative .
Consider the context and the text's perspective when determining sentiment. Use 0 for texts that have no clear positive/negative connotation, or when sentiment is ambiguous. You can only add -1, 0, or 1 to the sentiment column, do not use words.

### Time
In this column, just put the time when the relationship happened / was prevalent
- Before and not during project
- During project
- Hypothetical / future




# Finishing

Now, for a technical reason, go back and change the Sender column to "Cause" and the Receiver column to "Effect" and the Relationship column to "Tags". WE ARE STILL NOT TALKING ABOUT ACTUAL CAUSATION AT ALL, FOR A TECHINCAL REASON WE HAVE TO SAY CAUSE AND EFFECT INSTEAD OF SENDER AND RECEIVER.

So, your final column names are Cause, Effect, Tags, Sentiment, Time and Quote.

IT IS ESSENTIAL THAT YOU DON'T FORGET THE "Tags" column (which is renamed from "Relationship") where you characterise the relationship between the actors. The links are worth nothing to me if you miss off this "Tags" column.

```

## Soft-recoding actors

...

## Example filter

Respondent (female), Husband and Organisation 1: SNA.

[[008 Task 2 & 3 -- Extensions/img/022533df5e95d660b4071c6c60fc37e9_MD5.jpg|Open: Pasted image 20260212102636.png]]
![[008 Task 2 & 3 -- Extensions/img/022533df5e95d660b4071c6c60fc37e9_MD5.jpg]]


_Filename: example-original-sna2. Citation coverage 8% of all sources: 20 citations shown out of 264. Factors — size: citation count; numbers: source count; colour: source count: in; border: avg incoming sentiment (blue=positive, grey=neutral, red=negative). Links — width: citation count; labels: unique tags (tally); arrowheads: effect sentiment (blue=positive, grey=neutral, red=negative). Filters applied: Sources included: All sources. Labels: Respondent, Husband; Source Groups: custom_#Sex of the respondent=1; Factor freq: top 3 by source count. Bookmark [#1066](https://app.causalmap.app/?bookmark=1066) 2026-02-12 10:25_

## Transformation and interpretation rules {.banner}

### Transformation rule {.rounded}

- **Input:** text describing relationships/transactions between social actors.
- **Transformation:** code each directed relationship as one row with role labels (sender/receiver), relationship tag, sentiment, time, and verbatim quote; then rename columns to app-compatible `Cause`, `Effect`, and `Tags`.
- **Output:** a links table in Causal Map format representing social-actor relationships.

### Interpretation rule {.rounded}

- `Cause -> Effect` here denotes actor-to-actor relational direction, not abstract causal mechanism.
- `Tags` classify relationship type and should be read as relation semantics, not effect size.