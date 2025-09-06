from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import List, Tuple
import json
import re

from ..models.schemas import ResearchResult, Citation
from ..config import Config


class SummarizerAgent:
    """Agent responsible for summarizing research data using GPT-4o"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            api_key=Config.OPENAI_API_KEY,
            temperature=0.3
        )
        
        self.summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert business analyst tasked with creating comprehensive company research summaries with proper citations.

Your task is to analyze research data about a company and its partners/founders, then create a well-structured summary WITH CITATIONS.

IMPORTANT: Always respond in Turkish language. The entire summary must be written in Turkish.

CITATION RULES:
1. Use numbered citations [1], [2], [3] etc. throughout your text
2. When referencing information, add the citation number immediately after the claim
3. Multiple citations can be used: [1][2][3] 
4. The same source can be cited multiple times with the same number
5. Be precise about which information comes from which source

Guidelines:
1. Focus on factual information from the research data
2. Organize information clearly with proper sections
3. Include citations for every factual claim
4. Highlight key business information, financial data, and recent developments
5. Include relevant information about partners/founders with citations
6. Be concise but comprehensive
7. If information is limited, clearly state what was found vs. what's missing
8. Use professional business language in Turkish

Structure your summary with these sections (in Turkish):
- Şirket Genel Bakış (Company Overview)
- İş Bilgileri (Business Information)
- Finansal Bilgiler (Financial Information - if available)
- Kilit Personel/Ortaklar (Key Personnel/Partners)
- Son Gelişmeler (Recent Developments)
- Genel Değerlendirme (Summary Assessment)

EXAMPLE CITATION FORMAT:
"Banat Fırça ve Plastik San. Anonim Şirketi, 1947 yılında kurulmuş ve Türkiye'nin ilk diş fırçası üreticisi olarak tanınmaktadır[1]. Şirket, ağız bakım ürünleri, ev bakım ürünleri, kişisel bakım ürünleri ve endüstriyel ürünler alanında faaliyet göstermektedir[2]."

Remember: Every factual statement should have a citation!"""),
            
            ("human", """Please analyze the following research data and create a comprehensive summary in Turkish language:

Company Name: {company_name}
Company URL: {company_url}
Keywords: {keywords}
Partners/Founders: {partners}

Research Data:
{research_data}

Create a detailed but concise summary of the findings with proper citations. Remember to write the entire response in Turkish.""")
        ])
        
        self.facility_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert analyst specialized in company facilities and locations.

Create a detailed facility summary in Turkish with proper citations [1], [2], etc.

Focus on:
- Factory and production facility locations with addresses
- Office and branch locations  
- Distribution centers
- Geographic distribution of operations
- Facility sizes and capacities
- Any additional operational information

Use numbered citations [1], [2], [3] for every factual claim.
Write entirely in Turkish language."""),
            
            ("human", """Company: {company_name}
Company URL: {company_url}
Keywords: {keywords}
Partners: {partners}

Research Data:
{research_data}

Create a comprehensive facility summary with citations.""")
        ])
        
        self.sustainability_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in sustainability and ESG reporting.

Create a detailed sustainability summary in Turkish with proper citations [1], [2], etc.

Focus on:
- Existing sustainability reports and their dates
- Key environmental performance indicators
- Carbon footprint and climate commitments
- Certifications (ISO 14001, ISO 45001, etc.)
- Sustainability strategies and goals
- Environmental management systems

Use numbered citations [1], [2], [3] for every factual claim.
Write entirely in Turkish language."""),
            
            ("human", """Company: {company_name}
Company URL: {company_url}
Keywords: {keywords}
Partners: {partners}

Research Data:
{research_data}

Create a comprehensive sustainability summary with citations.""")
        ])
    
    async def summarize(self, company_name: str, company_url: str = None, keywords: List[str] = None, partners: List[str] = None, research_results: List[ResearchResult] = None) -> Tuple[str, str, str, List[Citation]]:
        """
        Summarize the research results using GPT-4o
        
        Args:
            company_name: Name of the company
            company_url: Company website URL (optional)
            keywords: Keywords about the company (optional)
            partners: List of partner names (optional)
            research_results: List of research results to summarize
            
        Returns:
            Tuple of (research_summary, facility_summary, sustainability_summary, citations)
        """
        partners = partners or []
        keywords = keywords or []
        research_results = research_results or []
        
        # Prepare research data for the prompt
        research_data = self._format_research_data_with_citations(research_results)
        citations = self._extract_citations(research_results)
        
        try:
            # Generate main summary
            main_prompt = self.summary_prompt.format_messages(
                company_name=company_name,
                company_url=company_url if company_url else "Not provided",
                keywords=", ".join(keywords) if keywords else "None",
                partners=", ".join(partners),
                research_data=research_data
            )
            main_response = await self.llm.ainvoke(main_prompt)
            research_summary = main_response.content
            
            # Generate facility summary
            facility_prompt = self.facility_prompt.format_messages(
                company_name=company_name,
                company_url=company_url if company_url else "Not provided",
                keywords=", ".join(keywords) if keywords else "None",
                partners=", ".join(partners),
                research_data=research_data
            )
            facility_response = await self.llm.ainvoke(facility_prompt)
            facility_summary = facility_response.content
            
            # Generate sustainability summary
            sustainability_prompt = self.sustainability_prompt.format_messages(
                company_name=company_name,
                company_url=company_url if company_url else "Not provided",
                keywords=", ".join(keywords) if keywords else "None",
                partners=", ".join(partners),
                research_data=research_data
            )
            sustainability_response = await self.llm.ainvoke(sustainability_prompt)
            sustainability_summary = sustainability_response.content
            
            return research_summary, facility_summary, sustainability_summary, citations
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            fallback = self._create_fallback_summary(company_name, company_url, keywords, partners, research_results)
            return fallback, "", "", citations
    
    def _format_research_data_with_citations(self, research_results: List[ResearchResult]) -> str:
        """Format research results for the prompt with citation numbers"""
        formatted_data = []
        citation_counter = 1
        
        for i, result in enumerate(research_results, 1):
            if not result.results:
                continue
                
            formatted_data.append(f"\n--- Search Query {i}: {result.query} ---")
            
            for j, search_result in enumerate(result.results[:3], 1):  # Limit to top 3 results per query
                formatted_data.append(f"\nResult {j} [Citation {citation_counter}]:")
                formatted_data.append(f"Title: {search_result.title}")
                formatted_data.append(f"URL: {search_result.url}")
                formatted_data.append(f"Content: {search_result.content[:800]}...")  # Increased content length
                if search_result.relevance_score > 0:
                    formatted_data.append(f"Relevance: {search_result.relevance_score:.2f}")
                citation_counter += 1
        
        return "\n".join(formatted_data) if formatted_data else "No research data available."
    
    def _extract_citations(self, research_results: List[ResearchResult]) -> List[Citation]:
        """Extract citations from research results"""
        citations = []
        citation_counter = 1
        
        for result in research_results:
            for search_result in result.results[:3]:  # Limit to top 3 results per query
                citation = Citation(
                    id=str(citation_counter),
                    title=search_result.title,
                    url=search_result.url,
                    content_preview=search_result.content[:200] + "..." if len(search_result.content) > 200 else search_result.content
                )
                citations.append(citation)
                citation_counter += 1
                
        return citations
    
    def _create_fallback_summary(self, company_name: str, company_url: str = None, keywords: List[str] = None, partners: List[str] = None, research_results: List[ResearchResult] = None) -> str:
        """Create a basic summary if AI summarization fails"""
        partners = partners or []
        keywords = keywords or []
        research_results = research_results or []
        
        total_results = sum(len(result.results) for result in research_results)
        successful_queries = len([r for r in research_results if r.results])
        
        summary = f"""# {company_name} için Araştırma Özeti

## Şirket Genel Bakış
Şirket Adı: {company_name}
Web Sitesi: {company_url if company_url else 'Belirtilmemiş'}
Anahtar Kelimeler: {', '.join(keywords) if keywords else 'Yok'}
Ortaklar/Kurucular: {", ".join(partners)}

## Araştırma Sonuçları
- Toplam gerçekleştirilen arama sorgusu: {len(research_results)}
- Başarılı sorgular: {successful_queries}
- Toplam bulunan sonuç: {total_results}

## Ana Bulgular
Araştırma verileri toplandı ancak otomatik özetleme mevcut değildi. 
Detaylı bilgi için lütfen ham araştırma verilerini inceleyin.

## Veri Kalitesi
{"İyi veri kapsamı" if total_results > 10 else "Sınırlı veri mevcut"} - 
{successful_queries} başarılı sorguda toplam {total_results} arama sonucu.
"""
        return summary
