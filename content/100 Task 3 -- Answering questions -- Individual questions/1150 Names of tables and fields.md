---
date: 2025-10-02
---

## Columns and tables



We can think of a causal map as a database consisting of two tables, the links table and the sources table. We don't need to have a separate table for the factors because the factors can be derived from the links table.

### Columns in both the links and factors tables

| Field name                    | Explanation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| :---------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Citation count aka Link count | Number of citations of a given factor or link.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Source count                  | Number of sources mentioning a given factor or link. Source count cannot be higher than citation count and may be a lot lower if some sources mentioned the same factor or link many times.                                                                                                                                                                                                                                                                                                                                                          |

### Columns in the factors table

| Field name                | Explanation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| :------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| incoming_links, indegree  | Number of citations of all the incoming links to a particular factor.                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| outgoing_links, outdegree | Number of citations of all the outgoing links from a particular factor.                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| outcome-ness (%)          | A factor with a high outcomeness percentage is mostly an outcome; it has mostly incoming links. If it has low outcomeness it has mostly outgoing links so it is mostly a driver. Outcomeness is the proportion of citations of incoming links out of all the citations of a particular factor: a normalised version of the Copeland Score [@copelandReasonableSocialWelfare1951]. So factors with high *outcomeness* can be thought of as “outcomes”. And factors with low outcomeness can be thought of as inputs or drivers. |

### Columns in the links table

| Field name | Explanation |
| :--------- | :---------- |
|            |             |



### Columns in the sources table


| Field name                    | Explanation                                                                                                                                                                                 |
| :---------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| source_id                     |                                                                                                                                                                                             |
| title                         |                                                                                                                                                                                             |
| filename                      |                                                                                                                                                                                             |

![[1150- Glossary]]

