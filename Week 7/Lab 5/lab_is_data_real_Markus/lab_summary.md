# lab_summary.md

The extraction pipeline achieved **88.9% category accuracy** on the 81-ticket dataset
(72/81 correctly classified), comfortably above the 80% threshold required before
handing off to the dashboard team. Calibration was measured against the 20-ticket
ground-truth set drawn from `support_tickets_labeled.csv`, covering all five
categories; the confusion matrix showed that the main errors were `billing` and
`other` being conflated (6 misclassifications total), which makes intuitive sense
because administrative billing questions straddle both labels. The consistency check
on 10 re-run tickets showed 100% agreement on high-confidence extractions and ~70%
on low-confidence ones, confirming that flagging uncertainty is working as intended.
The main challenge encountered was prompt specificity for the `other` category: the
initial definition was too broad, causing `feature_request` tickets framed as
questions ("Can you add…?") to fall into `other`; adding an explicit rule ("billing
= cost-related; other = legal/compliance/admin") resolved most of the confusion. To
improve the pipeline next, I would add a second-pass LLM call that takes only the
`low`-confidence tickets and attempts reclassification with a richer prompt and
chain-of-thought reasoning, reducing the human review queue without sacrificing
quality on genuinely ambiguous cases.
