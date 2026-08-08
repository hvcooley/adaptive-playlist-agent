This project has multiple components organized in folders:
1. data-ingestion-pipeline: A data-ingestion-pipeline that takes semantic text data from wikipedia articles on music artists and stores them in a vector database as embeddings. The subfodler corpus_previews contains the raw text extracted from wikipedia in each run of the ingestion pipeline, and within corpus_previews there are two subfolders separating the corpus_previews by test sample size full and small.
2. backend: Not in use for now. In case of further customization to agent behavior, we will store our own custom filtering attributes on artist metadata using this component.


Development Patterns:
1. When creating a constant like a string for a re-used url or a string for a re-used key, create the constant in one of the files in the constants folder of the respective module you are working in. If it makes sense to create a new constants file because the new constant will have several others like it that belong in the same group, then you should create a new constants file for it.