# Reflection

## Question 1: What would change if my client's data was in French?

Most of the evaluation setup would need to change. First, all 5 prompts would need to be written in French, and the expected responses would need to match French consumer law (for example, French return law is 14 days for online purchases, not 30 days as I assumed). Using the same prompts but translated is probably a mistake because the underlying policy context differs by country.

Finding benchmarks is harder for French. Most well-known benchmarks are English-only. There are some multilingual evaluation sets like XCOPA or mC4-based evaluations, but they're less developed and possibly more saturated. I'd rely more heavily on custom prompts.

The LLM-as-judge gets more complicated. If I use an English-language judge model to evaluate French responses, I'm adding a translation step that could introduce errors. The judge might miss a subtle tone problem in French or misread a phrase that's polite in French but awkward in English. Ideally, I'd use a French-language judge or at least verify a sample manually with a French speaker.

---

## Question 2: A client asks "is this model AGI-level?" — how do I respond?

I'd say that question is too vague to answer as asked, and I'd try to make it concrete instead.

"AGI-level" doesn't have a shared definition. If the client means "can it reason about novel problems it's never seen before," there's no evaluation that reliably tests that. Current benchmarks test performance on specific tasks with known formats. A model that scores 90% on GSM8K (math word problems) might still fail on a slightly different problem framing. That's not AGI-level robustness.

If the client means "is it good enough to replace a human customer service agent for this task," that's a question I can actually answer with the kind of evaluation I ran. And even then, I'd add caveats: the model performs well on the scenarios we tested, but we only tested 5 prompts. Edge cases, unusual phrasing, and multi-turn conversations were outside our test scope.

My honest answer to the client would be: this model is good enough to handle most routine customer service questions reliably, but it needs human oversight for high-stakes cases (allergen questions, legal complaints, refunds over a certain amount). That's a practical claim I can back up with data.

---

## Question 3: What is the one thing I couldn't evaluate without a human?

Brand voice. Whether a response sounds like this specific company or just like a generic chatbot.

A rule-based check can verify that the return policy is accurate. An LLM judge can assess whether the tone is calm and empathetic. But neither can tell me whether the response sounds like the brand the client spent years building. Is the language playful or formal? Does it use short sentences or longer flowing ones? Does it use "you" or something more distant?

The judge model has its own idea of what good customer service writing sounds like, based on its training data. That might not match this brand's style guide at all. A response that scores 1 out of 1 on my judge criteria might still feel completely wrong to the brand team when they read it.

To handle this in practice, I'd run a small human review alongside the automated evaluation. I'd pick 10-15 responses, send them to someone who knows the brand well, and ask them to mark anything that sounds "off-brand." That feedback would then go into refining the system prompt or the style constraints, not into the benchmark scores.
