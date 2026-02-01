# Text2Trait – GitHub Copilot Instructions

## 🎯 Purpose
This file provides **authoritative guidance for GitHub Copilot** when generating or modifying code in the **Text2Trait** repository.

It is **explicitly aligned with the HARVEST copilot instructions**, while being adapted to Text2Trait’s **frontend-only** scope and extended with **ARIA research‑grade UX expectations**.

Copilot should prioritise:
- Correctness over cleverness
- Clarity over abstraction
- Traceability over convenience
- Research-grade robustness over product shortcuts

---

## 🧠 Project Context

### What This Repository Is
- A **frontend-only application**
- Designed to:
  - Accept user inputs (text or structured)
  - Display Text2Trait outputs
  - Visualise traits, summaries, or evidence
  - Interface with *external* services or precomputed outputs

### What This Repository Is NOT
- ❌ No backend services
- ❌ No model training or inference
- ❌ No databases
- ❌ No orchestration of compute pipelines

Copilot **must not invent backend logic**, APIs, or ML workflows.

---

## 🧱 Architectural Alignment (HARVEST-Compatible)

Copilot must follow the same architectural philosophy as HARVEST:

- **Strict separation of concerns**
  - UI logic
  - Presentation / rendering
  - Lightweight client-side data handling
- **Explicit data flow**
  - Inputs → validation → transformation → rendering
- **Minimal magic**
  - Prefer explicit functions over implicit behavior

No hidden state. No side effects without explanation.

---

## 🎨 Frontend & UX Expectations

### Core UI Principles
Copilot-generated UI code must be:

- Deterministic
- Inspectable
- Fail-safe
- Understandable by non-developers

Avoid:
- Silent failures
- Implicit assumptions about data completeness
- Overloaded UI components

### Input Handling
- Validate all user input at the boundary.
- Surface validation errors clearly and immediately.
- Never assume well-formed or complete input.

### Output Rendering
- Outputs must be:
  - Clearly labelled
  - Contextualised
  - Visually separable
- Optional or missing fields must be handled gracefully.

---

## 🧪 ARIA Research‑Grade UX Requirements

Text2Trait is a **research-facing tool**. Copilot must assume outputs may inform:
- Scientific interpretation
- Policy or funding decisions
- Downstream automated workflows

Therefore, UI code should support:

### 🔍 Provenance & Traceability
Where applicable, Copilot should:
- Preserve source identifiers
- Display references or evidence markers
- Avoid collapsing or hiding uncertainty

### ⚠️ Uncertainty Awareness
- If data is partial, inferred, or missing, this must be visible.
- Do not present inferred values as ground truth.
- Prefer explicit “unknown / not available” states.

### 🔁 Reproducibility Signals
- Avoid non-deterministic UI behavior.
- Ensure the same input produces the same displayed output.
- Do not cache or mutate results silently.

### 🧭 Interpretability First
- Prefer simple tables, lists, and annotated summaries.
- Avoid decorative visualisations that obscure meaning.
- UX should prioritise understanding over aesthetics.

---

## ⚙️ Configuration & Environment

- Configuration must be:
  - Centralised
  - Human-readable
  - Overrideable via environment variables where appropriate
- Copilot must not hard-code:
  - URLs
  - Paths
  - Secrets
  - Deployment assumptions

---

## 🧹 Code Quality & Style (HARVEST-Aligned)

Copilot should generate code that:
- Follows **PEP 8**
- Uses meaningful, domain-relevant names
- Includes docstrings for non-trivial logic
- Avoids commented-out or placeholder code

Prefer:

```python
def render_trait_summary(traits: dict) -> None:
    """Render extracted traits with labels and provenance indicators."""
```

Over opaque or generic helpers.

---

## 🧪 Testing Expectations

If tests are added:
- Focus on **UI logic and helpers**
- Use mock or synthetic data
- Avoid filesystem or network dependencies

Copilot should **not assume an existing test framework** unless present.

---

## 📘 Documentation Discipline

- Inline comments explain *why*, not *what*
- Any new UI component or transformation step should include a docstring
- README alignment is mandatory — Copilot must not contradict it

---

## 🚫 Explicit Anti-Patterns

Copilot must not:
- Invent backend APIs or services
- Introduce database logic
- Assume local ML execution
- Introduce unnecessary frameworks or abstractions
- Collapse uncertainty or provenance into opaque UI elements

---

## 🧠 Copilot Operating Assumption

Copilot should behave as if:

> “This frontend is part of a wider ARIA-style research ecosystem.  
> Every output must be explainable, traceable, and safe to interpret.”

When uncertain, **prefer simpler, more explicit solutions**.

---

By following these instructions, Copilot will generate code that remains:
- Architecturally aligned with HARVEST
- Appropriate for ARIA-grade research tooling
- Robust, transparent, and maintainable
