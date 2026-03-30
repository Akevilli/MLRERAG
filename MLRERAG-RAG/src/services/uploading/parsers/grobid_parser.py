from typing import List, Tuple

from bs4 import BeautifulSoup, Tag
from fastapi import HTTPException
from httpx import AsyncClient

from .base_parser import Parser
from src.shared.schemas import (
    ArxivMetadata,
    Paragraph,
    Section,
    Table,
    Reference,
    ArxivPaper
)


class GrobidParser(Parser):
    """Parser implementation using GROBID service to extract structured data from PDF papers."""

    def __init__(
            self,
            httpx_client: AsyncClient,
            grobid_host: str,
            grobid_port: int,
    ):
        """
        Initializes the GrobidParser.

        Args:
            httpx_client: An asynchronous HTTP client for making requests.
            grobid_host: Hostname of the GROBID service.
            grobid_port: Port number of the GROBID service.
        """
        self._httpx_client = httpx_client
        self._grobid_url = f"http://{grobid_host}:{grobid_port}/api/processFulltextDocument"

    async def parse(self, unloaded_papers: List[Tuple[ArxivMetadata, bytes]]) -> List[ArxivPaper]:
        """
        Parses a list of raw PDF contents into structured ArxivPaper objects.

        Args:
            unloaded_papers: A list of tuples containing paper metadata and raw PDF bytes.

        Returns:
            List[ArxivPaper]: A list of objects containing structured sections, tables, and references.
        """
        results = []

        for metadata, paper_bytes in unloaded_papers:
            xml_content = await self._get_xml(metadata, paper_bytes)
            soup = BeautifulSoup(xml_content, "lxml-xml")

            paper = ArxivPaper(
                sections=self._get_sections(soup),
                tables=self._get_tables(soup),
                references=self._get_references(soup),
                metadata=metadata,
            )
            results.append(paper)

        return results

    async def _get_xml(self, arxiv_metadata: ArxivMetadata, content: bytes) -> bytes:
        """
        Sends PDF content to GROBID API and retrieves the TEI XML response.

        Args:
            arxiv_metadata: Metadata of the paper being processed.
            content: Raw PDF bytes.

        Returns:
            bytes: The XML response content from GROBID.

        Raises:
            HTTPException: If the GROBID service returns a non-200 status code.
        """
        files = {"input": (f"{arxiv_metadata.arxiv_id}.pdf", content, "application/pdf")}
        data = {"teiCoordinates": ["p", "head", "figure", "table", "biblStruct"]}

        try:
            response = await self._httpx_client.post(
                self._grobid_url,
                files=files,
                data=data,
                timeout=60
            )
            response.raise_for_status()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Grobid request failed for {arxiv_metadata.arxiv_id}: {str(e)}"
            )

        return response.content

    def _get_page(self, tag: Tag) -> str:
        """
        Extracts the page number from the 'coords' attribute of a TEI tag.

        Args:
            tag: A BeautifulSoup Tag object.

        Returns:
            str: The page number or "unknown" if coordinates are missing.
        """
        coords = tag.get("coords")
        if not coords:
            return "unknown"

        return coords.split(",")[0]

    def _get_paragraphs(self, container: Tag) -> List[Paragraph]:
        """
        Extracts all paragraphs from a given XML container.

        Args:
            container: The XML tag (like a <div>) containing <p> tags.

        Returns:
            List[Paragraph]: A list of Paragraph objects with text and page numbers.
        """
        return [
            Paragraph(
                text=p_tag.get_text(strip=True),
                page=self._get_page(p_tag)
            )
            for p_tag in container.select("p")
            if p_tag.get_text(strip=True)
        ]

    def _get_sections(self, soup: BeautifulSoup) -> List[Section]:
        """
        Extracts document sections (Introduction, Methods, etc.) from the TEI body.

        Args:
            soup: The parsed BeautifulSoup object.

        Returns:
            List[Section]: A list of structured Section objects.
        """
        sections = []
        # Select top-level divs in the body which usually represent sections
        for div in soup.select("body > div"):
            head = div.select_one("head")
            if not head:
                continue

            sections.append(Section(
                number=head.get("n", "—"),  # Use "—" if section number is missing
                title=head.get_text(strip=True),
                page=self._get_page(head),
                paragraphs=self._get_paragraphs(div)
            ))

        return sections

    def _get_tables(self, soup: BeautifulSoup) -> List[Table]:
        """
        Extracts tables and converts them from TEI format to Markdown.

        Args:
            soup: The parsed BeautifulSoup object.

        Returns:
            List[Table]: A list of Table objects with Markdown content and descriptions.
        """
        tables = []
        for table_fig in soup.select("body > figure[type='table']"):
            head = table_fig.select_one("head")
            desc = table_fig.select_one("figDesc")
            xml_table = table_fig.select_one("table")

            if not xml_table:
                continue

            tables.append(Table(
                caption=head.get_text(strip=True) if head else "Table",
                text=self._tei_table_to_md(xml_table),
                description=desc.get_text(strip=True) if desc else "",
                page=self._get_page(table_fig)
            ))

        return tables

    def _tei_table_to_md(self, table_tag: Tag) -> str:
        """
        Converts a TEI <table> structure into a Github-flavored Markdown table.

        Args:
            table_tag: The <table> Tag object.

        Returns:
            str: Markdown formatted table string.
        """
        rows = table_tag.select("row")
        if not rows:
            return ""

        md_lines = []
        for i, row in enumerate(rows):
            # Clean cells: replace pipe to avoid breaking MD structure
            cells = [c.get_text(strip=True).replace("|", "\\|") for c in row.find_all("cell")]
            md_lines.append(f"| {' | '.join(cells)} |")

            # Insert MD header separator after the first row
            if i == 0:
                md_lines.append(f"| {' | '.join(['---'] * len(cells))} |")

        return "\n".join(md_lines)

    def _get_references(self, soup: BeautifulSoup) -> List[Reference]:
        """
        Extracts bibliography references, specifically focusing on Arxiv links.

        Args:
            soup: The parsed BeautifulSoup object.

        Returns:
            List[Reference]: A list of Reference objects containing URLs.
        """
        references = []
        # Target specific Arxiv identifiers in the bibliography
        for idno in soup.select("back listBibl idno[type='arXiv']"):
            raw_id = idno.get_text(strip=True)
            # Handle cases where id might be prefixed (e.g., "arXiv:1706.03762")
            clean_id = raw_id.split(":")[-1] if ":" in raw_id else raw_id
            references.append(Reference(
                link=f"https://arxiv.org/pdf/{clean_id}"
            ))

        return references