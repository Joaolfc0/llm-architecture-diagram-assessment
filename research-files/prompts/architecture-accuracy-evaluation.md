## Architecture Accuracy Evaluation

You are evaluating the **ACCURACY** of a software architecture diagram for a microservices-based system, based on the given diagram and description.

### Diagram
[Insert diagram here]

### Description
[Insert textual description here]


### Evaluation Criterion — Accuracy

Accuracy is about whether the diagram correctly reflects the architecture described in the text, including components, interactions, and technologies.

In particular, evaluate:

1. **Component Matching**  
   - Do the components and characteristics in the diagram correspond to the components and characteristics described in the text, with compatible names, roles, colors and responsibilities?

2. **Interaction Matching**  
   - Do the interactions in the diagram (calls, messages, data flows) match the interactions described in the text in terms of direction, main participants, and purpose?
---

### Output Format (IMPORTANT)

Return **only valid JSON** (no markdown, no prose, no code fences), in English:

{
  "criterion": "accuracy",
  "guidelines": [
    {
      "id": "component_matching",
      "score": "4 (Excellent) | 3 (Good) | 2 (Fair) | 1 (Poor)",
      "justification": "<concise, evidence-based explanation>"
    },
    {
      "id": "interaction_matching",
      "score": "4 (Excellent) | 3 (Good) | 2 (Fair) | 1 (Poor)",
      "justification": "<concise, evidence-based explanation>"
    }
  ]
}
