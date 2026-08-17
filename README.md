# AI Engineer Assignment
## Research Paper Intelligence Pipeline

An end-to-end AI engineering pipeline for collecting, processing, enriching, validating, and extracting structured information from research papers.

The pipeline collects research papers from arXiv, standardizes their metadata, removes duplicates, enriches records with GitHub and Hugging Face information, performs data-quality checks, and uses a Groq LLM to extract structured research information.

---

## Project Overview

The pipeline performs the following major tasks:

1. Collect research papers from arXiv
2. Normalize paper metadata
3. Remove duplicate papers
4. Match papers with GitHub repositories
5. Enrich paper metadata using Hugging Face
6. Generate a data-quality report
7. Extract structured information using an LLM
8. Save checkpoints during long-running processing
9. Build the final research-paper dataset
10. Run automated tests

---

## System Architecture

```text
                         ┌─────────────────────┐
                         │       arXiv         │
                         │   Research Papers   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Paper Scraper     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Raw Paper Data    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Normalization     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Deduplication     │
                         └──────────┬──────────┘
                                    │
                       ┌────────────┴────────────┐
                       │                         │
                       ▼                         ▼
              ┌─────────────────┐       ┌──────────────────┐
              │ GitHub Enrichment│       │ Hugging Face     │
              │                 │       │ Enrichment       │
              │ URL + Stars     │       │ Metadata         │
              └────────┬────────┘       └────────┬─────────┘
                       │                         │
                       └────────────┬────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Quality Validation │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Text Chunking    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      Groq LLM       │
                         │ Structured Extraction│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Final Dataset     │
                         │  final_papers.json  │
                         └─────────────────────┘
Project Structure
AI_Engineer_Assignment/
│
├── architecture/
│   └── architecture.md
│
├── data/
│   ├── raw/
│   │   └── research_papers.json
│   │
│   └── processed/
│       ├── deduplicated_papers.json
│       ├── huggingface_enriched_papers.json
│       ├── quality_report.json
│       └── final_papers.json
│
├── src/
│   │
│   ├── scrapers/
│   │   └── arxiv_scraper.py
│   │
│   ├── extractors/
│   │   └── huggingface_enricher.py
│   │
│   ├── resolver/
│   │   └── GitHub matching components
│   │
│   ├── llm/
│   │   ├── chunker.py
│   │   ├── providers.py
│   │   ├── orchestrator.py
│   │   ├── batch_extractor.py
│   │   └── complete_remaining.py
│   │
│   └── utils/
│       ├── checkpoint.py
│       ├── retry.py
│       └── paper_metadata.py
│
├── tests/
│   └── test_pipeline.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md

