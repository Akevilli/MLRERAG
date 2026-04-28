CALL apoc.custom.declareProcedure(
    'rag.extend_seeds(seeds :: LIST OF STRING) :: (response :: PATH)',
    '
        UNWIND $seeds AS seed
        MATCH (c:Chunk {id: seed})
        OPTIONAL MATCH (c)-[:NEXT*..2]-(neighbor:Chunk)
        WITH c, collect(neighbor) AS neighbors
        WITH [c] + neighbors AS all_nodes
        UNWIND all_nodes AS node

        WITH DISTINCT node

        OPTIONAL MATCH (node)-[:HAS_TABLE]->(t:Table)
        OPTIONAL MATCH (node)-[:CITES]->(cp:Paper)
        MATCH (node)-[:PART_OF]->(s:Section)-[:BELONGS_TO]->(p:Paper)

        WITH p, s, node, collect(DISTINCT t { .* }) AS chunk_tables, collect(DISTINCT cp { .* }) AS cited_papers

        WITH p, s, node, chunk_tables, cited_papers ORDER BY node.position
        WITH p, s, collect(node { .*, tables: chunk_tables, references: cited_papers }) AS section_chunks

        WITH p, s, section_chunks ORDER BY s.number
        WITH p, collect(s { .*, chunks: section_chunks }) AS paper_sections

        RETURN collect(p { .*, sections: paper_sections }) AS response
    ',
    'write',
    'Fetches chunks according to the topology logic and seed chunks.'
)