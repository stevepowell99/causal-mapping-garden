
If you are interested in how to formalise causal mapping or in building software, we'd like to share this insight. If you are not, ignore this.

> Factors are implied by links

We don't need to have a separate table for the factors because the factors can be derived from the links table. If you cannot find a factor <u>X</u>  as cause or effect in the links table, it does not exist. 

This means that our data model (since version 3 of Causal Map) does not need to have a table for factors. Essentially we just have a table for links, plus a table for sources both to supply the texts and to more conveniently store metadata like gender and district. 

It's of course possible to formalise causal mapping in other ways, but we have found dropping a special table for factors to solve a lot of the problems associated with having to keep factors and links tables in sync.

This does bring its own problems: [[300 Factor label tags -- coding factor metadata within its label]]
