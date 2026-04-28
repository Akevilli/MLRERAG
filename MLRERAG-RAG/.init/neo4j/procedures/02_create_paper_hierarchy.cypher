CALL apoc.custom.declareProcedure(
  'rag.create_paper_hierarchy(papers :: LIST OF MAP) :: (answer :: STRING)',
  '
    UNWIND $papers AS paper
    MERGE (p:Paper {arxiv_id: paper.metadata.arxiv_id})
    SET p += paper.metadata,
        p.tags = paper.tags,
        p.is_loaded = true

    WITH paper, p
    UNWIND paper.sections AS section
    MERGE (s:Section {id: section.id})
    SET s.number = section.number,
        s.title = section.title,
        s.page = section.page
    MERGE (s)-[:BELONGS_TO]->(p)

    WITH section, s
    UNWIND section.chunks AS chunk
    MERGE (c:Chunk {id: chunk.id})
    SET c.text = chunk.text,
        c.page = chunk.page,
        c.position = chunk.position
    MERGE (c)-[:PART_OF]->(s)

    WITH section, s, chunk, c
    FOREACH (table IN chunk.tables |
        MERGE (t:Table {id: table.id})
        ON CREATE SET
            t.caption = table.caption,
            t.text = table.text,
            t.description = table.description,
            t.page = table.page
        MERGE (c)-[:HAS_TABLE]->(t)
    )

    WITH DISTINCT s, c
    ORDER BY s, c.position
    WITH s, collect(c) AS sorted_nodes
    CALL apoc.nodes.link(sorted_nodes, "NEXT")

    RETURN "OK" as answer
  ',
  'write',
  'Procedure for uploading parsed papers.'
)