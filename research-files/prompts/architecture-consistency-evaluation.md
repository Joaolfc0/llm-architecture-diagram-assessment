## Architecture Consistency Evaluation

You are evaluating the **CONSISTENCY** of a software architecture diagram for a microservices-based system, based on the given diagram and description.

### Diagram
[Insert diagram here]

### Description
[Insert textual description here]

### Evaluation Criterion — Consistency

Consistency is about whether the diagram uses a clearly defined notation and applies it uniformly, and whether it consistently represents specific technologies.

In particular, evaluate:

1. **Notation Definition and Uniformity**  
   - Does the diagram use a clear notation for different types of elements (services, databases, communication channels, external actors) and apply it consistently?

2. **Technology Symbols**  
   - Are technology symbols used consistently throughout the diagram (e.g., the same visual convention for databases, queues, caches, and other technology types)?

3. **Naming and Representation Consistency**  
   - Are similar elements named and represented consistently across the diagram and description (no conflicting names or mixed styles for the same type of element)?

---

### Output Format (IMPORTANT)

Return **only valid JSON** (no markdown, no prose, no code fences), in English:

{
  "criterion": "consistency",
  "guidelines": [
    {
      "id": "notation_uniformity",
      "score": "4 (Excellent) | 3 (Good) | 2 (Fair) | 1 (Poor)",
      "justification": "<concise, evidence-based explanation>"
    },
    {
      "id": "technology_symbols",
      "score": "4 (Excellent) | 3 (Good) | 2 (Fair) | 1 (Poor)",
      "justification": "<concise, evidence-based explanation>"
    },
    {
      "id": "naming_consistency",
      "score": "4 (Excellent) | 3 (Good) | 2 (Fair) | 1 (Poor)",
      "justification": "<concise, evidence-based explanation>"
    }
  ]
}
