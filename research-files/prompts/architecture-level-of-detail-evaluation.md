## Architecture Level of Detail Evaluation

You are evaluating the **LEVEL OF DETAIL** of a software architecture diagram for a microservices-based system, based on the given diagram and description.

Assume the primary audience is software developers and architects.

### Diagram
[Insert diagram here]

### Description
[Insert textual description here]


### Evaluation Criterion — Level of Detail

Level of detail is about whether the elements of the diagram are presented with an appropriate amount of detail for understanding the architecture.

In particular, evaluate:

1. **Element Detail**  
   - Are components described with enough information (names, roles, responsibilities, grouping, colors) to understand what they do?

2. **Interaction Detail**  
   - Are interactions shown with sufficient detail (direction and type of communication, such as request/response or messaging) to understand how the system behaves?

3. **Overall Appropriateness for Developers and Architects**  
   - Considering developers and architects as the audience, is the level of detail balanced (neither too superficial nor excessively detailed for the architectural view)?

---

### Output Format (IMPORTANT)

Return **only valid JSON** (no markdown, no prose, no code fences), in English:

{
  "criterion": "level_of_detail",
  "guidelines": [
    {
      "id": "element_detail",
      "score": "4 (Excellent) | 3 (Good) | 2 (Fair) | 1 (Poor)",
      "justification": "<concise, evidence-based explanation>"
    },
    {
      "id": "interaction_detail",
      "score": "4 (Excellent) | 3 (Good) | 2 (Fair) | 1 (Poor)",
      "justification": "<concise, evidence-based explanation>"
    },
    {
      "id": "overall_appropriateness",
      "score": "4 (Excellent) | 3 (Good) | 2 (Fair) | 1 (Poor)",
      "justification": "<concise, evidence-based explanation>"
    }
  ]
}
