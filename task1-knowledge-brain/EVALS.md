# Evaluation Report — AI Tech Consultant Knowledge Brain

## 1. Objective

Evaluate whether the Knowledge Brain retrieves relevant support articles, returns useful source metadata, rejects empty input, and escalates unsupported questions for human review.

## 2. Automated Unit Tests

Command used:

`python -m unittest test_knowledge_brain -v`

**Observed result:** 5 tests passed.

| Test | Expected behavior | Observed result |
|---|---|---|
| Email-forwarding search | Relevant articles are returned | Passed |
| Source metadata | Results include title, URL, and content | Passed |
| Unrelated dolphin question | No articles are returned | Passed |
| Empty query | Empty result list | Passed |
| Whitespace query | Empty result list | Passed |

These tests cover basic search behavior. They do not independently prove the accuracy of generated answers.

## 3. Manual API Tests

The following cases were tested manually through the FastAPI Swagger interface.

| Scenario | Expected behavior | Observed result |
|---|---|---|
| Create an expert task | Return HTTP 200 and an open task | Passed |
| Save a human answer | Return HTTP 200 and mark the task answered | Passed |
| Ask an unsupported dolphin-training question | Return no sources and request human review | Passed |
| Ask about email forwarding | Return an answer with source URLs | Passed |
| Ask about website color sets | Return instructions with relevant documentation links | Passed |

The manual results were observed during development. They should be repeated after any substantial code change.

## 4. Evaluation Limitations

The current evaluation is an initial functional test, not a comprehensive accuracy benchmark.

- Only five automated unit tests are implemented.
- Manual testing covers a small number of questions.
- The retrieval threshold is a heuristic and has not been calibrated on a labeled dataset.
- Answer factuality and citation support have not been scored independently.
- Latency, token usage, and cost have not been benchmarked systematically.
- No comparative evaluation between different language models has been completed.

## 5. Recommended Expanded Test Set

Before submission, expand the evaluation to at least 20 representative questions.

Include:
1. Questions clearly answered by one article.
2. Questions requiring information from multiple articles.
3. Questions using synonyms or alternate wording.
4. Questions with no relevant documentation.
5. Questions containing spelling mistakes.
6. Questions about similar but distinct product settings.
7. Empty and malformed inputs.
8. Questions where retrieved articles conflict or provide incomplete instructions.

For each case, record the question, expected evidence, retrieved sources, answer quality, escalation decision, and pass/fail result.

## 6. Metrics to Track

- **Retrieval relevance:** Whether retrieved articles actually support the question.
- **Answer groundedness:** Whether factual statements are supported by the cited documentation.
- **Source accuracy:** Whether links point to the articles used to generate the answer.
- **Escalation accuracy:** Whether unsupported questions are routed to human review.
- **Latency:** Time taken to retrieve articles and generate an answer.
- **Reliability:** Percentage of requests completed without errors.

## 7. Conclusion

The prototype passes the current five automated search tests and the documented manual API checks. Additional labeled test cases and answer-quality measurements are needed before claiming production-level accuracy or complete assignment compliance.