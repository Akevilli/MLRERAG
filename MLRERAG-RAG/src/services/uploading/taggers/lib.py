from src.shared.schemas import ArxivPaper


def construct_user_prompt(paper: ArxivPaper) -> str:
    """Constructs a user prompt for the LLM to analyze a paper.

    Formats the paper's title, summary, and sections into a structured
    prompt for tag extraction.

    Args:
        paper: An ArxivPaper instance containing metadata and content.

    Returns:
        A formatted string prompt for the LLM.
    """
    return f"""
    Analyze the following paper and extract tags based on it:

    TITLE: {paper.metadata.title}
    SUMMARY: {paper.metadata.summary}
    CONTENT:
    {paper.sections}
    """