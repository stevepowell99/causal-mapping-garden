---
date: 2025-12-13
---

Here is the complete reference guide for the **Qualitative Causal Parser (QCP v1.0)**.

---

### **1. The Core Equation**

Every causal claim is mapped as a force interaction between an **Agonist** (the subject with a will/tendency) and an **Antagonist** (the opposing force).

**Formal Syntax:** `(ID) [Context] :: Agonist(Tendency) Operator Antagonist`

#### **1.1 The Context (Optional)**

Defines the scope, time, or location where this dynamic applies. Used primarily when contrasting two different states.

- _Syntax:_ `[Time: Past]`, `[Loc: Garden]`, `[Mode: Hypothetical]`
    

#### **1.2 The Agonist & Tendency**

The subject of the sentence and their intrinsic aim.

- **Syntax:** `Actor(Direction: Verb[Intensity])`
    
- **Direction:**
    
    - **`M` (Motion/Change):** The will to start an action, change state, or disrupt the status quo. (e.g., _Grow, Enter, Attack, Quit_).
        
    - **`R` (Rest/Maintenance):** The will to maintain the current state, resist change, or withstand pressure. (e.g., _Remain, Calm, Survive, Stand_).
        
- **Intensity (Optional):**
    
    - **`+`**: High magnitude (e.g., _Grow+_ = Thrive).
        
    - **`-`**: Low magnitude (e.g., _Burn-_ = Flicker).
        

#### **1.3 The Operator**

Defines the outcome of the struggle.

- **`>`** : **Overcomes.** Agonist wins. (Logic: _Despite_).
    
- **`<`** : **Overpowered.** Antagonist wins. (Logic: _Because of_).
    
- **`>>`**: **Easily Overcomes.** High-margin victory.
    
- **`0`** : **Unimpeded.** No active antagonism. Agonist acts naturally.
    

#### **1.4 The Antagonist**

The force opposing the Agonist.

- **Entity:** `Name` (e.g., _Rain, Friction, Parents_).
    
- **Reference:** `(ID)` (The outcome of a previous statement acts as the opposing force).
    

---

### **2. Chaining & Dependency**

How to link statements to form a narrative or causal chain.

#### **2.1 Result as Antagonist (Interaction)**

The outcome of a previous event **is** the force acting in the current event.

- **Syntax:** `Agonist > (ID)`
    
- _Meaning:_ The Agonist is fighting against the result of statement (ID).
    
- _Example:_
    
    - `(1) Mum > Dementia` (The Spark)
        
    - `(2) Chloe(M: Give Up) < (1)` (Chloe's despair is blocked by The Spark).
        

#### **2.2 Result as Enabler (Conditionality)**

The current event is only possible because a previous event removed the obstacle.

- **Syntax:** `Agonist 0 | (ID)`
    
- _Meaning:_ The Agonist is unimpeded **given that** (ID) successfully removed the blocker.
    
- _Example:_
    
    - `(1) Umbrella > Rain`
        
    - `(2) Me(R: Dry) 0 | (1)` (I am naturally dry, enabled by the umbrella).
        

---

### **3. Differential Syntax (Comparisons)**

Used when the explanation relies on the **difference** between two states rather than a single event.

**Syntax:** `Agonist(Tendency) :: [Context A: Op Antagonist] -> [Context B: Op Antagonist]`

**Semantic Rules:**

1. **Agonist Shift:** If the Operator flips (e.g., `<` to `>`) and the Antagonist is constant, the explanation is the **Change in Agonist**.
    
    - _Ex:_ `Seeds :: [Old: < Dry] -> [New: > Dry]` (Cause = Seed Quality).
        
2. **Antagonist Shift:** If the Operator flips and the Agonist is constant, the explanation is the **Change in Environment**.
    
    - _Ex:_ `Tank :: [Road: >> Friction] -> [Mud: < Friction]` (Cause = Terrain).
        

---

### **4. Semantic Reference Table**

|Component|Notation|Meaning / Translation|
|---|---|---|
|**Motion**|`(M: Verb)`|"Tried to X", "Wanted to change to X"|
|**Rest**|`(R: Verb)`|"Tried to stay X", "Refused to move"|
|**Win**|`A > B`|"Succeeded in spite of B", "Withstood B"|
|**Lose**|`A < B`|"Failed because of B", "Forced by B"|
|**Natural**|`A 0`|"Did X naturally", "Just X'd"|
|**Easy Win**|`A >> B`|"Easily X'd", "X'd with no trouble"|
|**Ref Force**|`... < (1)`|"Was stopped by the outcome of (1)"|
|**Enable**|`...|(1)`|

Export to Sheets

---

### **5. Example: Full Stack Parsing**

**Text:** _"I usually can't focus because of the noise. But today I put on headphones and got the work done easily."_

**Parsing:**

1. **(1)** `[Usual] :: Noise(M: Impinge) 0` _(Noise exists naturally)._
    
2. **(2)** `[Usual] :: Me(R: Focus) < (1)` _(My tendency to maintain focus is overpowered by the Noise)._
    
3. **(3)** `[Today] :: Noise(M: Impinge) < Headphones` _(The Headphones block the Noise)._
    
4. **(4)** `[Today] :: Me(R: Focus) 0 | (3)` _(I maintain focus naturally, enabled by the headphones)._
    
5. **(5)** `[Today] :: Work(M: Complete) >> Difficulty | (4)` _(I complete the work easily, enabled by the focus state)._