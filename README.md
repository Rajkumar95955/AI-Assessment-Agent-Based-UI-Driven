Here’s a clean, ready-to-use **README.md** for that assessment.

---

# 🤖 Agent-Based AI Assessment (Generator + Reviewer + UI)

This project demonstrates a lightweight **agent-based architecture** with a **UI-driven pipeline** where two AI agents collaborate to generate and evaluate educational content.

## ✨ Overview

The system contains:

* **Generator Agent** → Creates educational content
* **Reviewer Agent** → Evaluates the generated content
* **UI Layer** → Triggers the pipeline and displays results

If the Reviewer returns `fail`, the system performs **one refinement pass** using the feedback.

---

## 🧠 Agents

### 1. Generator Agent

**Responsibility:**
Generates age-appropriate educational content for a given grade and topic.

**Input (Structured JSON):**

```json
{
  "grade": 4,
  "topic": "Types of angles"
}
```

**Output (Structured JSON):**

```json
{
  "explanation": "An angle is formed when two lines meet...",
  "mcqs": [
    {
      "question": "Which angle is less than 90 degrees?",
      "options": ["Right angle", "Obtuse angle", "Acute angle", "Straight angle"],
      "answer": "C"
    }
  ]
}
```

**Must ensure:**

* Language matches grade level
* Concepts are correct
* Output structure is always consistent

---

### 2. Reviewer Agent

**Responsibility:**
Evaluates the Generator’s output.

**Input:**
Generator’s output JSON

**Output (Structured JSON):**

```json
{
  "status": "fail",
  "feedback": [
    "Sentence 2 is too complex for Grade 4",
    "Question 3 tests a concept not introduced"
  ]
}
```

**Evaluation Criteria:**

* Age appropriateness
* Conceptual correctness
* Clarity

---

## 🔁 Refinement Logic

* If Reviewer returns `"pass"` → Pipeline ends
* If Reviewer returns `"fail"` →

  * Generator is re-run once with feedback embedded
  * Only **one refinement pass** is allowed

No separate Refiner agent is required.

---

## 🖥️ UI Requirements (Mandatory)

The UI must clearly show the agent workflow.

It should display:

* ✅ Generator Output
* 🧪 Reviewer Feedback
* 🔁 Refined Output (if Reviewer fails)

The UI must:

* Trigger the agent pipeline
* Make the agent interaction obvious to the user

Examples of valid UI:

* Streamlit app
* Gradio interface
* Simple web app (React / HTML + JS)
* CLI UI (acceptable if clearly structured)

---

## 📂 Suggested Project Structure

```
project/
│
├── agents.py          # GeneratorAgent & ReviewerAgent
├── app.py             # UI logic (Streamlit/Gradio/etc.)
├── pipeline.py        # Orchestration logic
├── README.md          # This file
└── requirements.txt
```

---

## ▶️ Example Flow

1. User selects:

   * Grade: 4
   * Topic: Types of angles

2. UI calls Generator Agent → Displays generated content

3. UI calls Reviewer Agent → Displays feedback

4. If failed → Shows refined output after one retry


