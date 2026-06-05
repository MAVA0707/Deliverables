# Data Source

**Source**: Generated synthetic evaluation data (`01_generate_evaluation_data.ipynb`)

The dataset was produced programmatically using realistic score distributions drawn from normal distributions per model × category combination. It contains 1,200 rows covering three model versions (`model-v1`, `model-v2`, `model-v3`) across five evaluation categories (`reasoning`, `knowledge`, `code`, `instruction_following`, `tool_calling`), dated between January 2025 and June 2025.

This approach was chosen because no prior-lab evaluation output was available in the project environment, and generated data with realistic variance profiles provides a more instructive dashboard than a trivially uniform dataset.
