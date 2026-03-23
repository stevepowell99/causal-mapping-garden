---
date: 2025-12-19
---

### 1) The smallest possible map is like this


```
A:: Cause
B:: Effect
A -> B
```

### 2) Comments (important)

- `#` starts a comment.
- Everything after `#` on that line is ignored.

This also means: **don’t use `#` for hex colours** (`#ff0000`) because it will be treated as a comment.

### 3) Settings (styles at the top)

Settings look like `Key: Value` and usually go near the top.

Common settings:

- **Title**: text title shown above the diagram.
- **Background**: background colour (named colour or `rgb(r,g,b)`).
- **Default box colour**: default node fill colour.
- **Default box border**: default node border, like `1px solid gray`.
- **Default link colour**: default link/arrow colour.
- **Default link style**: `solid | dotted | dashed | bold`.
- **Default link width**: a number (interpreted like px), e.g. `2`.
- **Default box shape**: `rounded` for rounded nodes.
- **Default box shadow**: `none | subtle | medium | strong`.
- **Direction**: `top-bottom | bottom-top | left-right | right-left`.
- **Label wrap**: wraps node labels after N characters (best-effort).
- **Rank gap / Node gap**: spacing controls (small numbers like `2`–`8` are typical).

Colour rules (keep it simple):

- Use **named colours** like `red`, `aliceblue`, `seagreen`, `dimgray`, etc.
- Or use **`rgb(r,g,b)`**, e.g. `rgb(255, 0, 0)`.

Example style block:

```
Background: aliceblue
Default box colour: wheat
Default box shape: rounded
Default box border: 1px dotted dimgray
Default link colour: dimgray
Default link style: dotted
Default link width: 2
Default box shadow: subtle
Direction: left-right
```

### 4) Nodes

Define a node like this:

ID:: Label

- **ID** is a short name you use in links (like `A`, `B2`, `MyNode`).
- **Label** is what you see in the diagram (can include spaces).

Examples:

```
A:: A short label
B:: A longer label with spaces
```

### 5) Links (arrows)

Links look like this:

```
A -> B
```

You can create multiple links in one line using `|`:

```
A -> B | C
A | Q -> B
A | Q -> B | C
```

(That last one creates the full cross-product: A→B, A→C, Q→B, Q→C.)

Optional link label + border:

```
A -> B [increases | 1px dotted gray]
```

Optional link label style + size (use `key=value` inside the brackets):

```
A -> B [label=increases | border=1px dotted gray | label style=italic | label size=10]
```

### 6) Grouping boxes (optional)

Grouping boxes are just lines starting with dashes:

- `--Label` opens a grouping box (level 1)
- `----Label` opens a nested grouping box (level 2)
- `----` closes the most recent level-2 grouping box
- `--` closes the most recent level-1 grouping box (and anything nested)

Example:

```
--Drivers
A:: Training quality
B:: Tool usability
--

--Outcomes
C:: Adoption
D:: Error rate
--

A | B -> C | D
```

### 7) Styling nodes inline (optional)

You can put a small “style list” after a node label:

```
A:: Hello [colour=red | border=2px dashed dimgray | shape=rounded]
```

Supported node attributes:

- `colour=...` (or `color=...`): fill colour
- `background=...`: fill colour (alias)
- `border=...`: border like `2px solid gray`
- `shape=rounded`: rounded corners

### 8) Border syntax (for nodes and links)

Border text is:

```
WIDTH STYLE COLOUR
```

Examples:

```
1px solid blue
2px dotted gray
```