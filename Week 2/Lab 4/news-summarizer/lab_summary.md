
# Lab Summary

- Didn't know how to run .py files, so I created a notebook
- The coordination of two different LLM provider SDKs was at the beginning very challenging, but through building a unified `LLMProviders` class it became handleable.
- When one provider makes a failure, the fallback logic jumps automatically in — this was a very satisfying solution to implement.
- The single-responsibility principle by `CostTracker`, `NewsAPI`, and `LLMProviders` made the unit testing very straightforward and the code much more übersichtlich (clear/organized).

