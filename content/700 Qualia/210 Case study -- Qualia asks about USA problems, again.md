---
tags: 
  - case_study
  - date: 27/02/2025
date: 2025-04-09
---
## Feb 27, 2025 at EES

How can we capture and visualise people’s mental models of a complex situation like the state of a nation? This week, as part of an EES [webinar](https://www.causalmap.app/resources/qualia-webinar-ees-2025/) demonstrating our automated AI interviewer Qualia, we asked the participants to spend a few minutes being interviewed about problems facing the USA and the reasons for them, and the reasons for the reasons. Over 90 people did, with a mean of 13 messages per conversation. Details below.

The Qualia platform provides an instant overview of the transcripts. For some reason, we didn’t think to show it at the time, but I’ve pasted it in at the bottom of this post. Qualia also provided a simple causal map:

![notion image](https://imagedelivery.net/IEMzXmjRvW0g933AN5ejrA/wwwnotionso-image-attachment0deb8ecd-d212-4263-91a7-0c1ba5f9dc85imagepng/public)

>Because this was a demo interview and many respondents only started it and only a few finished the conversation, we are not taking this analysis so seriously, it’s just an example of the types of outputs you can get with the Overview Tab in QualiaInterviews — but although we can’t make any claims to be doing fundamental social science here, the results are still worth a look.


The Overview in the Qualia Workspace app is just a simple hack which is basically like uploading all the transcripts to ChatGPT and saying “make sense of this please”. [We’ve already talked at length](https://www.linkedin.com/pulse/just-add-rigour-three-dos-donts-when-using-ai-text-analysis-powell-kgbbe/?trackingId=Ugyi4%2FV4T0WwL%2BPfsse40Q%3D%3D) about the dangers of that: basically you are entrusting a whole load of evaluative judgements to a black-box AI, which is not only completely non-transparent but is cutting corners everywhere in the attempt to come to a plausible enough result as quickly and cheaply as possible.

A much better way is to break up the vague, high-level task into multiple simple, transparent ones, in this case, identifying all the causal claims in the transcripts, where someone said that one thing leads to or influences another, and aggregating them. The result looks like this:

![notion image](https://imagedelivery.net/IEMzXmjRvW0g933AN5ejrA/wwwnotionso-image-attachmentc6956e25-43c5-40d2-8608-7379bd8d6945d138194e-6823-48c0-b43b-0b0b56f1d8e3png/public)

*A “Factor” is any box, including outcomes, drivers and things in between
The map is filtered to show most important links and/or factors: many other links and factors are hidden
Numbers on factors (boxes): number of mentions
Sizes of factors (boxes): number of mentions
Numbers on links: number of sources mentioning it
Darker backgrounds: higher “Outcomeness”: a bigger proportion of incoming links
Deeper red arrowheads: the effect was more negative in significance/sentiment*

### Some things to note:

> Many people mentioned Trump as a driver of changes (white background, positioned at left)

> Most frequently mentioned factor was “Unstable political situation”, whose only significant driver was Trump’s actions.

> We shouldn’t fall into the "transitivity trap” of thinking that, because Trump is linked to Unstable political situation which is linked to Health care cuts that many or any individual sources told us about all the sections of this chain: the information for each section might have come from different sources (in fact, it mostly did).

We have done this type of interview several times before. Here is a map from 2023. 



## EES 2023: Sharing our journey on AI’s application in qualitative research

This was a completely different method and sample. The difference between these two maps has substantial face validity, but that is about all we can say at this point.

![notion image](https://imagedelivery.net/IEMzXmjRvW0g933AN5ejrA/wwwnotionso-image-staticwixstaticcom-media-190108_9ae61b0d513742b69599141b7dd9cb8dmv2png-v1-fill-w_925h_339al_cq_85usm_066_100_001enc_auto-190108_9ae61b0d513742b69599141b7dd9cb8dmv2png/public)

## Technical annex

### The interview

The instructions for the AI interviewer are to conduct a fairly mechanical interview which simply asks the respondents to list the main problems facing the USA today, and for each problem, to ask for reasons and reasons for the reasons, and to ask how these are interconnected. It also asks the respondent to confirm the causal connections identified before finishing. It isn’t a very chatty or explorative interview, but it works.

### Producing the maps

We asked our AI to code the transcripts one at a time and to use codes for each cause and effect which were already a little abstracted, using "concepts from a social science textbook” but with no more specific codebook. This resulted in 325 links using 458 factor labels with overlapping meaning, which we then clustered using a procedure detailed in a [forthcoming publication](https://docs.google.com/document/d/18lv9r_PekLT7TiRp6rTzGoRUTzDs32SRjt3vdsJ5_s4/edit?usp=sharing).

### Instant overview of transcripts provided by Qualia (global, “black box” approach).

#### **Overview of Interview Transcripts**

The interviews highlight a wide array of challenges currently facing the USA, with themes revolving around political, social, and economic issues. Common problems include divisive politics, leadership concerns, economic inequality, governance issues, and the influence of certain political figures like Donald Trump.

#### **Common Features:**

- **Leadership and Political Instability**: Many respondents highlight issues with leadership and governance as pivotal problems. Concerns include the actions and influence of Donald Trump, new administrations, and an unstable government.

- **Economic Concerns**: Economic inequality, unemployment, and budget deficits are frequently mentioned, pointing towards systemic economic challenges.

- **Social Issues**: Polarization, racism, and loss of public services are recurrent themes, along with critiques on social justice and inequality.

- **Foreign Policy and Geopolitics**: Geopolitical tensions, particularly involving countries like Russia and China, and the USA's diminishing global influence are noted.

- **Environmental and Social Policies**: Climate change and health care are cited as critical problems needing more attention.


#### **Differences:**

> While some respondents focused on specific figures, like Trump, and their impact on the national and international stage, others highlighted systemic issues such as the neoliberal economic model or the enduring influence of oligarchs.

> Perspectives vary on underlying causes, with some pointing to specific policy decisions and others referencing broader societal trends, such as populism or media influence.