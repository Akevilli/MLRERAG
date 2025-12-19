This document describes the main processes and entities of this project.

## Entities

### Downloader

The main goal of downloader is downloading a papers via api and save it into special folder `papers/`. Each downloader has *download* method which executes downloading process.

### Parser

The main goal of parsers is parsing downloaded papers into `.md` format. Each parser has *parse* method which executes parsing process.

### Chunker

The main goal of chunkers is chunking parsed data. Each chunker has *chunk* method which executes chunking process.

### Embedder

The main goal of embedders is calculating embeddings. Embedders are use in **upload** and **retrieval** processes. Each embedder has *embed* method which calculates embeddings.

### Vector Database(Vector DB)

Vector DB stores embedded chunks and etire documents with its metadata.

---

## Processes

### Upload

This process needs to upload new documents to vector db.

![general process](cache/mermaid-diagram-2025-11-04-141938.png)