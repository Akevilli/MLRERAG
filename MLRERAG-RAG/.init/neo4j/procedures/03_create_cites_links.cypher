CALL apoc.custom.declareProcedure(
    'rag.create_cites_links(papers :: LIST OF MAP, cited_papers_metadata :: LIST OF MAP) :: (count :: INTEGER)',
    '
        UNWIND $cited_papers_metadata AS cited_paper_metadata
        MERGE (cp:Paper {arxiv_id: cited_paper_metadata.arxiv_id})
        ON CREATE SET
            cp += cited_paper_metadata,
            cp.is_loaded = false
        ON MATCH SET
            cp += cited_paper_metadata

        WITH $papers AS papers
        UNWIND papers AS paper
        UNWIND paper.sections AS section
        UNWIND section.chunks AS chunk
        UNWIND chunk.references AS reference

        MATCH (c:Chunk {id: chunk.id})
        MATCH (p:Paper {arxiv_id: reference.arxiv_id})

        MERGE (c)-[:CITES]->(p)

        WITH count(*) AS total
        RETURN total AS count
    ',
    'write',
    'Creates cite links between chunks and papers.'
)