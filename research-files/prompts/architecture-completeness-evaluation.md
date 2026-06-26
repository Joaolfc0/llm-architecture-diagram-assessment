## Architecture Completeness Evaluation

You are evaluating the **COMPLETENESS** of a software architecture diagram for a microservices-based system, based on the given diagram and description.

### Diagram
[Insert diagram here]

### Description
[Insert textual description here]


### Evaluation Criterion — Completeness

Completeness is about whether the diagram includes the main architectural elements and interactions needed to understand the system as a whole.

In particular, evaluate:

1. **Coverage of Main Components**
   - Are all major components mentioned in the description (e.g., microservices, databases, message brokers, external systems) represented in the diagram?

2. **External Actors Coverage**  
   - Are relevant external actors (users, external APIs, third-party systems) shown when they are important to understanding how the system works end-to-end?

3. **Main Interactions Coverage**  
   - Are the primary interactions between components (requests, messages, events) represented so that the overall behavior of the system can be understood?
---

### Output Format (IMPORTANT)

Return **only valid JSON** (no markdown, no prose, no code fences), in English:

{
  "criterion": "completeness",
  "guidelines": [
    {
      "id": "coverage_main_components",
      "score": "4 (Excellent) | 3 (Good) | 2 (Fair) | 1 (Poor)",
      "justification": "<concise, evidence-based explanation>"
    },
    {
      "id": "external_actors_coverage",
      "score": "4 (Excellent) | 3 (Good) | 2 (Fair) | 1 (Poor)",
      "justification": "<concise, evidence-based explanation>"
    },
    {
      "id": "main_interactions_coverage",
      "score": "4 (Excellent) | 3 (Good) | 2 (Fair) | 1 (Poor)",
      "justification": "<concise, evidence-based explanation>"
    }
  ]
}
