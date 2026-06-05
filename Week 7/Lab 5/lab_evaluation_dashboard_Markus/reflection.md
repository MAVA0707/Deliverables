# Reflection

## What communication layer principles did I apply?

The dashboard is built entirely around conclusions, not methods. Every chart answers one of two questions: "what is the score?" or "where should we focus?" There are no p-values, confidence intervals, or references to how the scores were computed. Category labels use plain English ("Instruction Following", not "instruction_following"). The KPI cards give a stakeholder the essential numbers in under five seconds. The key-findings cell at the end converts numbers into three numbered actions — because a decision-maker needs a recommendation, not a table.

## What did I include vs. exclude?

**Included**: KPI summary cards, overall score distribution, per-category box plots, grouped bar comparison, heatmap, monthly trend, and a plain-language findings summary. These answer the practical questions: which model is best, which categories are weak, and is performance improving over time?

**Excluded**: raw score tables, statistical test results, effect sizes, bootstrap intervals, and any chart that requires methodological context to interpret. Those belong in the analyst notebook (`03_statistical_analysis.ipynb`), not the stakeholder dashboard. I also excluded individual evaluation IDs — stakeholders do not need row-level data; they need patterns.

## What I would do differently next time

I would build the filter variables in Section 1 into a lightweight widget (e.g., `ipywidgets` dropdowns) so stakeholders could adjust them without editing code. I would also export the combined dashboard automatically to a PDF alongside the PNG, making it easier to share via email without requiring the recipient to have Jupyter installed.
