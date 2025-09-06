"""
Utility functions for formatting citations and research output
"""
from typing import List
from ..models.schemas import Citation, CompanyResearchResponse


def format_citations_markdown(citations: List[Citation]) -> str:
    """
    Format citations in markdown format like the test.md example
    """
    if not citations:
        return ""
    
    citation_lines = []
    for citation in citations:
        citation_lines.append(f"[{citation.id}] {citation.title}")
        citation_lines.append(citation.url)
    
    return "\n".join(citation_lines)


def format_response_as_markdown(response: CompanyResearchResponse) -> str:
    """
    Format the complete response as markdown similar to test.md
    """
    markdown_content = []
    
    # Research Summary Section
    markdown_content.append("# Research Summary")
    markdown_content.append(response.research_summary)
    markdown_content.append("")
    
    # Facility Summary Section
    if response.facility_summary:
        markdown_content.append("# Facility Summary")
        markdown_content.append(response.facility_summary)
        markdown_content.append("")
    
    # Sustainability Summary Section
    if response.sustainability_summary:
        markdown_content.append("# Sustainability Summary")
        markdown_content.append(response.sustainability_summary)
        markdown_content.append("")
    
    # Citations Section
    if response.citations:
        markdown_content.append("# Citations")
        citation_text = format_citations_markdown(response.citations)
        markdown_content.append(citation_text)
    
    return "\n".join(markdown_content)


def save_response_as_markdown(response: CompanyResearchResponse, filename: str = None) -> str:
    """
    Save the response as a markdown file
    """
    if filename is None:
        company_name_clean = response.company_name.replace(" ", "_").replace(".", "")
        filename = f"{company_name_clean}_research_report.md"
    
    markdown_content = format_response_as_markdown(response)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return filename
