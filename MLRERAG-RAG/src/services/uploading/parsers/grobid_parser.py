import asyncio
from uuid import uuid4
from typing import List, Tuple, Dict

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

# TODO: Merge sections without number with the first previous section with number.

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
        tasks = [self._parse_single(metadata, paper_bytes) for metadata, paper_bytes in unloaded_papers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_results = [result for result in results if isinstance(result, ArxivPaper)]

        return valid_results

    async def _parse_single(self, arxiv_metadata: ArxivMetadata, content: bytes) -> ArxivPaper:
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
        data = {
            "teiCoordinates": ["p", "head", "figure", "table", "biblStruct"]
        }

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

        soup = BeautifulSoup(response.content, "lxml-xml")
        tables = self._get_tables(soup)
        references = self._get_references(soup)

        paper = ArxivPaper(
            sections=self._get_sections(soup, tables, references),
            tables=[table for table in tables.values()],
            references=[reference for reference in references.values()],
            metadata=arxiv_metadata,
        )

        return paper

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

    def _get_paragraphs(
            self,
            section: Tag,
            table_map: Dict[str, Table],
            reference_map: Dict[str, Reference]
    ) -> List[Paragraph]:
        """
        Extracts all paragraphs from a given XML container.

        Args:
            section: The XML tag (like a <div>) containing <p> tags.
            table_map: Dict with tables object with corresponding ids.
            reference_map: Dict with references object with corresponding ids.

        Returns:
            List[Paragraph]: A list of Paragraph objects with text and page numbers.
        """
        paragraphs = []

        for paragraph_tag in section.select("p"):
            if text:=paragraph_tag.get_text():
                table_ids = set()
                reference_ids = set()

                for ref_tag in paragraph_tag.select("ref[type=\"table\"]"):
                    if "target" in ref_tag.attrs:
                        table_ids.add(ref_tag.attrs["target"][1:])

                for ref_tag in paragraph_tag.select("ref[type=\"bibr\"]"):
                    if "target" in ref_tag.attrs:
                        reference_ids.add(ref_tag.attrs["target"][1:])

                paragraphs.append(
                    Paragraph(
                        text=text,
                        page=self._get_page(paragraph_tag),
                        tables=[table_map[id] for id in table_ids],
                        references=[reference_map[id] for id in reference_ids if id in reference_map]
                    )
                )

        return paragraphs

    def _get_sections(
            self,
            soup: BeautifulSoup,
            table_map: Dict[str, Table],
            reference_map: Dict[str, Reference]
    ) -> List[Section]:
        """
        Extracts document sections (Introduction, Methods, etc.) from the TEI body.

        Args:
            soup: The parsed BeautifulSoup object.

        Returns:
            List[Section]: A list of structured Section objects.
        """
        sections = []

        for div in soup.select("body > div"):
            head = div.select_one("head")
            if not head:
                continue

            sections.append(
                Section(
                    id=uuid4(),
                    number=head.get("n", "—"),  # Use "—" if section number is missing
                    title=head.get_text(strip=True),
                    page=self._get_page(head),
                    paragraphs=self._get_paragraphs(div, table_map, reference_map)
                )
            )

        return sections

    def _get_tables(self, soup: BeautifulSoup) -> Dict[str, Table]:
        """
        Extracts tables and converts them from TEI format to Markdown.

        Args:
            soup: The parsed BeautifulSoup object.

        Returns:
            Dict[str, Table]: A map containing table's ids and tables.
        """
        tables = {}

        for table_fig in soup.select("body > figure[type='table']"):
            head = table_fig.select_one("head")
            desc = table_fig.select_one("figDesc")
            xml_table = table_fig.select_one("table")
            id = table_fig.attrs["xml:id"]

            if not xml_table:
                continue

            tables[id] = Table(
                id=uuid4(),
                caption=head.get_text(strip=True) if head else "Table",
                text=self._tei_table_to_md(xml_table),
                description=desc.get_text(strip=True) if desc else "",
                page=self._get_page(table_fig)
            )

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
            cells = [c.get_text(strip=True).replace("|", "\\|") for c in row.find_all("cell")]
            md_lines.append(f"| {' | '.join(cells)} |")

            if i == 0:
                md_lines.append(f"| {' | '.join(['---'] * len(cells))} |")

        return "\n".join(md_lines)

    def _get_references(self, soup: BeautifulSoup) -> Dict[str, Reference]:
        """
        Extracts bibliography references, specifically focusing on Arxiv links.

        Args:
            soup: The parsed BeautifulSoup object.

        Returns:
            List[Reference]: A list of Reference objects containing URLs.
        """
        references = {}

        for biblStruct_tag in soup.select("listBibl biblStruct"):
            tag_id = biblStruct_tag.attrs["xml:id"]

            if idno_tag:=biblStruct_tag.select_one("idno[type=\"arXiv\"]"):
                if text:=idno_tag.get_text(strip=True):
                    references[tag_id] = Reference(arxiv_id=text.split(":")[1])

        return references