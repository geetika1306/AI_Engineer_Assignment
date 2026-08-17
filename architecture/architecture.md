# System Architecture

## AI Engineer Assignment — Research Paper Intelligence Pipeline

This project implements an end-to-end research paper intelligence pipeline.

The system collects research papers from arXiv, standardizes their metadata, removes duplicates, enriches the papers using GitHub and Hugging Face information, validates data quality, and performs structured information extraction using a Groq-based LLM.

---

## 1. High-Level Architecture

```text
                         ┌─────────────────────────┐
                         │          arXiv          │
                         │   Research Paper API    │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │     Paper Scraper       │
                         │                         │
                         │ arxiv_scraper.py        │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │     Raw Paper Data      │
                         │                         │
                         │ data/raw/               │
                         │ research_papers.json    │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │     Normalization       │
                         │                         │
                         │ Standardized Schema     │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      Deduplication      │
                         │                         │
                         │ Remove duplicate papers │
                         └────────────┬────────────┘
                                      │
                                      ▼
              ┌───────────────────────┴────────────────────────┐
              │                                                │
              ▼                                                ▼
   ┌─────────────────────────┐                    ┌─────────────────────────┐
   │    GitHub Enrichment    │                    │  Hugging Face           │
   │                         │                    │  Enrichment              │
   │ Repository matching     │                    │                         │
   │ GitHub URL              │                    │ Paper metadata          │
   │ GitHub stars            │                    │ Linked resources        │
   │ Match confidence        │                    │                         │
   └────────────┬────────────┘                    └────────────┬────────────┘
                │                                              │
                └──────────────────────┬───────────────────────┘
                                       │
                                       ▼
                         ┌─────────────────────────┐
                         │     Quality Report      │
                         │                         │
                         │ Required fields         │
                         │ GitHub matches          │
                         │ Missing fields          │
                         │ Data quality statistics  │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      LLM Pipeline       │
                         │                         │
                         │ Text Chunking            │
                         │ Groq API                │
                         │ Structured Extraction   │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │    Final Dataset        │
                         │                         │
                         │ final_papers.json       │
                         │                         │
                         │ 1,000 Papers            │
                         │ 27 GitHub Matches       │
                         │ 230 LLM Extractions     │
                         └─────────────────────────┘
2. Pipeline Components
2.1 Research Paper Collection
Component
src/scrapers/arxiv_scraper.py
Input

The system queries the arXiv research paper source.

Processing

The scraper collects paper information such as:

Paper ID
Title
Authors
Abstract
Publication date
arXiv URL
Output
data/raw/research_papers.json

The collected records are stored as JSON for downstream processing.

3. Data Normalization

The collected paper information is converted into a standardized schema.

Each research paper follows a consistent structure:

{
    "schemaVersion": "1.0",
    "recordType": "RESEARCH_PAPER",
    "source": {},
    "content": {},
    "collectedAt": ""
}

The standardized structure makes it easier for all downstream components to process the papers consistently.

4. Deduplication
Component
src/resolver/deduplicator.py

The deduplication stage identifies duplicate research papers.

The system compares paper information and removes duplicate records before enrichment and LLM processing.

Output
data/processed/deduplicated_papers.json

In the current run:

Input papers:        1000
Unique papers:       1000
Duplicates removed:  0
5. GitHub Enrichment
Component
src/resolver/

The GitHub enrichment stage attempts to associate research papers with their corresponding GitHub repositories.

The enrichment can provide:

GitHub repository URL
GitHub star count
Match confidence
Match method
Match explanation

Example:

{
    "github_url": "https://github.com/Yaxin9Luo/AutoDesign",
    "github_stars": 53,
    "match_confidence": 1.0,
    "match_method": "verified_paper_metadata"
}
Current Results
Total papers:          1000
GitHub matches:        27
GitHub stars available: 27

Not every research paper has an associated GitHub repository.

6. Hugging Face Enrichment
Component
src/extractors/huggingface_enricher.py

The Hugging Face enrichment stage retrieves additional metadata when available.

The enrichment process can provide information related to:

Paper metadata
Linked models
Linked datasets
Other available research resources

The enriched data is stored in:

data/processed/huggingface_enriched_papers.json

If no additional Hugging Face information is available, the original paper metadata is retained.

7. Data Quality Validation
Output
data/processed/quality_report.json

The quality validation stage checks the completeness and consistency of the processed records.

The quality report tracks fields such as:

Title
Authors
Abstract
GitHub URL
GitHub stars

It also provides enrichment statistics.

The final dataset contains complete basic paper information for all 1,000 records.

8. LLM Information Extraction
8.1 LLM Architecture
                    ┌─────────────────────────┐
                    │     Research Paper      │
                    │        Abstract         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       Text Chunker       │
                    │                          │
                    │ Split long text into     │
                    │ manageable chunks        │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      Extraction Prompt   │
                    │                          │
                    │ Problem                  │
                    │ Methods                  │
                    │ Datasets                 │
                    │ Metrics                  │
                    │ Key Findings             │
                    │ Limitations              │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │        Groq API          │
                    │                          │
                    │ LLM-based extraction     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      JSON Parser         │
                    │                          │
                    │ Validate structured      │
                    │ response                 │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Structured Extraction  │
                    └─────────────────────────┘
9. LLM Extraction Schema

For successfully processed papers, the LLM produces the following structure:

{
    "problem": "",
    "methods": [],
    "datasets": [],
    "metrics": [],
    "key_findings": [],
    "limitations": []
}
Problem

The research problem addressed by the paper.

Methods

Methods, techniques, models, or approaches explicitly mentioned in the paper.

Datasets

Datasets used or introduced by the research.

Metrics

Evaluation metrics explicitly mentioned.

Key Findings

Important results or conclusions supported by the paper.

Limitations

Limitations explicitly mentioned or supported by the supplied text.

10. LLM Provider

The project uses:

Groq

The LLM pipeline was designed with:

API integration
Retry handling
Rate-limit handling
Exponential backoff
Checkpointing
Incremental saving

The extraction prompt instructs the model to:

Extract ONLY information explicitly supported
by the supplied text.


DO NOT invent or infer facts.


Return ONLY valid JSON.

This reduces unsupported or hallucinated information in the structured output.

11. Rate Limit Handling

External LLM APIs can impose request limits.

The project includes retry and backoff mechanisms.

The retry flow is:

              ┌─────────────────┐
              │   Send Request  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Request Success?│
              └──────┬─────┬────┘
                     │     │
                   YES      NO
                     │     │
                     │     ▼
                     │  ┌───────────────┐
                     │  │ Check Error   │
                     │  │               │
                     │  │ 429 / API     │
                     │  │ failure       │
                     │  └───────┬───────┘
                     │          │
                     │          ▼
                     │  ┌───────────────┐
                     │  │ Wait using    │
                     │  │ exponential   │
                     │  │ backoff       │
                     │  └───────┬───────┘
                     │          │
                     │          ▼
                     │      Retry Request
                     │
                     ▼
              Save Successful
                  Result
12. Checkpointing

The LLM batch processing system uses checkpoints so that successful work is not lost if:

The program is interrupted
An API request fails
A rate limit occurs
The computer is restarted

Checkpoint information is stored in:

data/processed/llm_checkpoint.json

The pipeline saves successful progress incrementally.

This allows processing to resume from the last successful position instead of starting from the beginning.

13. Final Dataset Construction

The final dataset combines:

Original Paper Metadata
          +
GitHub Enrichment
          +
Hugging Face Enrichment
          +
Available LLM Extraction

The final output is:

data/processed/final_papers.json
14. Final Dataset Statistics

The current final dataset contains:

Total research papers:        1000


Unique papers:                1000


Duplicates removed:           0


GitHub matches:                27


GitHub stars available:        27


Successful LLM extractions:   230


LLM not processed:            770

The 770 papers that were not successfully processed by the LLM are still retained in the final dataset.

Their extraction status is recorded as:

not_processed

This prevents loss of the original research-paper metadata.

15. Final Record Structure

Each final record contains:

schemaVersion
recordType
source
content
collectedAt
llm_extraction
llm_extraction_status

The content section can contain:

title
authors
abstract
published_date
paper_url
arxiv_id
github_url
github_stars
match_confidence
match_method
match_explanation

The llm_extraction section contains:

problem
methods
datasets
metrics
key_findings
limitations
16. End-to-End Data Flow
┌───────────────────┐
│      arXiv        │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Paper Scraper    │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Raw JSON Dataset  │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   Normalization   │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Deduplication    │
└─────────┬─────────┘
          │
          ├──────────────────────┐
          │                      │
          ▼                      ▼
┌───────────────────┐  ┌────────────────────┐
│ GitHub Enrichment │  │ Hugging Face       │
│                   │  │ Enrichment         │
└─────────┬─────────┘  └──────────┬─────────┘
          │                       │
          └───────────┬───────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Quality Report  │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Text Chunking   │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │   Groq LLM      │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ JSON Extraction │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Final Dataset   │
             │ 1,000 Papers    │
             └─────────────────┘
17. Project Directory Mapping
src/
│
├── scrapers/
│   └── arxiv_scraper.py
│       └── Collects research papers
│
├── extractors/
│   └── huggingface_enricher.py
│       └── Adds Hugging Face metadata
│
├── resolver/
│   └── GitHub matching components
│       └── Matches papers with repositories
│
├── llm/
│   ├── chunker.py
│   │   └── Splits text into chunks
│   │
│   ├── providers.py
│   │   └── Groq API integration
│   │
│   ├── orchestrator.py
│   │   └── LLM extraction orchestration
│   │
│   ├── batch_extractor.py
│   │   └── Processes papers in batches
│   │
│   └── complete_remaining.py
│       └── Builds the final dataset
│
└── utils/
    ├── checkpoint.py
    │   └── Saves processing progress
    │
    ├── retry.py
    │   └── Handles API retries
    │
    └── paper_metadata.py
        └── Paper metadata utilities
18. Testing Architecture

The project includes automated tests in:

tests/test_pipeline.py

The tests validate:

Final dataset exists
        │
        ▼
Exactly 1,000 papers
        │
        ▼
Required fields exist
        │
        ▼
Content fields exist
        │
        ▼
LLM extraction structure
        │
        ▼
LLM success count

Tests are executed using:

pytest -v
19. Design Principles

The architecture follows these principles:

Modularity

Each major processing stage is implemented as a separate component.

Reliability

Retry handling and checkpointing protect long-running processing jobs.

Data Consistency

All papers follow a standardized schema.

Traceability

Enrichment fields include match information and confidence where available.

Fault Tolerance

API failures do not require restarting the complete pipeline.

Reproducibility

Intermediate JSON files allow individual pipeline stages to be inspected and rerun.

Structured Output

LLM responses are converted into a predictable JSON schema.

20. Final Output

The primary final artifact is:

data/processed/final_papers.json

It contains the complete collection of 1,000 research papers along with available enrichment and LLM extraction results.

The architecture is designed so that additional papers, enrichment providers, and LLM providers can be integrated in the future without redesigning the entire pipeline.