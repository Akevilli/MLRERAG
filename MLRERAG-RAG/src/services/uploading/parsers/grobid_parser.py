import asyncio
import re
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from bs4 import BeautifulSoup, Tag
from fastapi import HTTPException
from httpx import AsyncClient
from loguru import logger

from .base_parser import Parser
from src.shared.schemas import (
    ArxivMetadata,
    ArxivPaper,
    FileUploadDTO,
    Paragraph,
    PDFDTO,
    Reference,
    Section,
    Table,
)


class GrobidClient:
    """Отвечает только за сетевое взаимодействие с GROBID API."""

    def __init__(self, httpx_client: AsyncClient, host: str, port: int):
        self._client = httpx_client
        self._url = f"http://{host}:{port}/api/processFulltextDocument"

    async def process_pdf(self, pdf_bytes: bytes, filename: str = "document.pdf") -> bytes:
        files = {"input": (filename, pdf_bytes, "application/pdf")}
        data = {"teiCoordinates": ["p", "head", "figure", "table", "biblStruct"]}

        try:
            response = await self._client.post(
                self._url,
                files=files,
                data=data,
                timeout=60,
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Grobid request failed for {filename}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"GROBID service error while processing {filename}: {str(e)}",
            )


class TeiXmlParser:
    """Синхронный парсер TEI XML структуры в доменные Pydantic-модели."""

    def parse(self, xml_content: bytes, metadata: Optional[ArxivMetadata] = None) -> ArxivPaper:
        soup = BeautifulSoup(xml_content, "lxml-xml")

        # Если внешние метаданные не переданы, извлекаем их из самого XML
        if metadata is None:
            metadata = self._extract_metadata(soup)

        tables = self._get_tables(soup)
        references = self._get_references(soup)
        sections = self._get_sections(soup, tables, references)

        return ArxivPaper(
            sections=sections,
            tables=list(tables.values()),
            references=list(references.values()),
            metadata=metadata,
        )

    def _extract_metadata(self, soup: BeautifulSoup) -> ArxivMetadata:
        """Извлекает и формирует ArxivMetadata из XML, когда внешние данные отсутствуют."""
        # 1. Извлекаем ID и версию из XML
        arxiv_id, version = self.extract_arxiv_id_and_version(soup)
        arxiv_id = arxiv_id or "unknown"
        version = version or "1"  # Версия без буквы 'v'

        # Заголовок
        title_tag = soup.select_one("titleStmt > title")
        title = title_tag.get_text(strip=True) if title_tag else "Untitled Paper"

        # Аннотация (Summary)
        abstract_tag = soup.select_one("profileDesc > abstract")
        summary = abstract_tag.get_text(strip=True) if abstract_tag else ""

        # Авторы
        authors = []
        for author_tag in soup.select("sourceDesc author"):
            pers_name = author_tag.select_one("persName")
            if pers_name:
                authors.append(pers_name.get_text(separator=" ", strip=True))

        return ArxivMetadata(
            arxiv_id=arxiv_id,  # Теперь здесь строго "1231.1234"
            version=version,    # Теперь здесь строго "2" (или "1")
            title=title,
            summary=summary,
            source_url=f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id != "unknown" else "",
            authors=authors or ["Unknown"],
        )

    def extract_arxiv_id_and_version(self, soup: BeautifulSoup) -> Tuple[Optional[str], Optional[str]]:
        """
        Извлекает arxiv_id (без 'v') и версию (число без 'v').
        Возвращает кортеж (arxiv_id, version).
        """
        arxiv_id_tag = soup.select_one("sourceDesc idno[type='arXiv']")
        if not arxiv_id_tag:
            return None, None

        tag_text = arxiv_id_tag.get_text()
        
        # Регулярка делит ID на две группы:
        # Group 1: сам ID (например, "1231.1234")
        # Group 2: только цифра версии (например, "2" из "v2" или "V2")
        match = re.search(r"(\d+\.\d+)(?:[vV](\d+))?", tag_text)
        if not match:
            return None, None

        clean_id = match.group(1)
        version_num = match.group(2) if match.group(2) else "1"

        return clean_id, version_num

    # Оставляем метод для обратной совместимости, если он вызывается где-то ещё
    def extract_arxiv_id(self, soup: BeautifulSoup) -> Optional[str]:
        clean_id, _ = self.extract_arxiv_id_and_version(soup)
        return clean_id

    def _get_page(self, tag: Tag) -> str:
        coords = tag.get("coords")
        if not coords:
            return "unknown"
        return str(coords).split(",")[0]

    def _get_paragraphs(
        self,
        section: Tag,
        table_map: Dict[str, Table],
        reference_map: Dict[str, Reference],
    ) -> List[Paragraph]:
        paragraphs = []

        for paragraph_tag in section.select("p"):
            text = paragraph_tag.get_text()
            if not text:
                continue

            table_ids = {
                ref.attrs["target"][1:]
                for ref in paragraph_tag.select('ref[type="table"]')
                if "target" in ref.attrs
            }

            reference_ids = {
                ref.attrs["target"][1:]
                for ref in paragraph_tag.select('ref[type="bibr"]')
                if "target" in ref.attrs
            }

            paragraphs.append(
                Paragraph(
                    text=text,
                    page=self._get_page(paragraph_tag),
                    tables=[table_map[t_id] for t_id in table_ids if t_id in table_map],
                    references=[reference_map[r_id] for r_id in reference_ids if r_id in reference_map],
                )
            )

        return paragraphs

    def _get_sections(
        self,
        soup: BeautifulSoup,
        table_map: Dict[str, Table],
        reference_map: Dict[str, Reference],
    ) -> List[Section]:
        sections = []

        for div in soup.select("body > div"):
            head = div.select_one("head")
            if not head:
                continue

            sections.append(
                Section(
                    id=uuid4(),
                    number=str(head.get("n", "—")),
                    title=head.get_text(strip=True),
                    page=self._get_page(head),
                    paragraphs=self._get_paragraphs(div, table_map, reference_map),
                )
            )

        return sections

    def _get_tables(self, soup: BeautifulSoup) -> Dict[str, Table]:
        tables = {}

        for table_fig in soup.select("body > figure[type='table']"):
            table_id = table_fig.attrs.get("xml:id")
            xml_table = table_fig.select_one("table")

            if not xml_table or not table_id:
                continue

            head = table_fig.select_one("head")
            desc = table_fig.select_one("figDesc")

            tables[table_id] = Table(
                id=uuid4(),
                caption=head.get_text(strip=True) if head else "Table",
                text=self._tei_table_to_md(xml_table),
                description=desc.get_text(strip=True) if desc else "",
                page=self._get_page(table_fig),
            )

        return tables

    def _tei_table_to_md(self, table_tag: Tag) -> str:
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
        references = {}

        for bibl_struct in soup.select("listBibl biblStruct"):
            tag_id = bibl_struct.attrs.get("xml:id")
            if not tag_id:
                continue

            idno_tag = bibl_struct.select_one('idno[type="arXiv"]')
            if idno_tag and (text := idno_tag.get_text(strip=True)):
                arxiv_id = text.split(":")[-1]
                references[tag_id] = Reference(arxiv_id=arxiv_id)

        return references


class GrobidParser(Parser):
    """Главный сервис-оркестратор парсинга PDF."""

    def __init__(
        self,
        httpx_client: AsyncClient,
        grobid_host: str,
        grobid_port: int,
        xml_parser: Optional[TeiXmlParser] = None,
    ):
        self._grobid_client = GrobidClient(httpx_client, grobid_host, grobid_port)
        self._xml_parser = xml_parser or TeiXmlParser()

    async def parse(
        self,
        unloaded_papers: List[Tuple[Optional[ArxivMetadata], bytes]],
    ) -> List[ArxivPaper]:
        """
        Основной метод парсинга. Принимает список кортежей (метаданные или None, байты PDF).
        """
        tasks = [
            self._parse_single(metadata, paper_bytes)
            for metadata, paper_bytes in unloaded_papers
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error parsing paper: {str(result)}")
            elif isinstance(result, ArxivPaper):
                valid_results.append(result)

        return valid_results

    async def parse_files(self, files_dto: FileUploadDTO) -> List[ArxivPaper]:
        """
        Метод для распарсивания загруженных PDF-файлов без предварительных метаданных arXiv.
        """
        papers_payload = [(None, file_item.content) for file_item in files_dto.files]
        return await self.parse(papers_payload)

    async def _parse_single(
        self,
        metadata: Optional[ArxivMetadata],
        content: bytes,
    ) -> ArxivPaper:
        filename = f"{metadata.arxiv_id}.pdf" if metadata else "document.pdf"
        
        # 1. Отправляем в GROBID
        xml_bytes = await self._grobid_client.process_pdf(content, filename=filename)

        # 2. Преобразуем TEI XML в ArxivPaper
        paper = self._xml_parser.parse(xml_bytes, metadata=metadata)
        return paper