from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import List
import asyncio

from ..services.tavily_service import TavilyService
from ..models.schemas import ResearchResult
from ..config import Config


class ResearcherAgent:
    """Agent responsible for researching companies and partners using Tavily"""
    
    def __init__(self):
        self.tavily_service = TavilyService()
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            api_key=Config.OPENAI_API_KEY,
            temperature=0.1
        )
    
    def _create_search_queries(self, company_name: str, partners: List[str]) -> List[str]:
        """Generate comprehensive search queries for Turkish companies and partners"""
        # Sanitize inputs to prevent query breakage
        def sanitize_query_input(text: str) -> str:
            """Escape quotes and backslashes for safe query interpolation"""
            return text.replace('\\', '\\\\').replace('"', '\\"')
        
        sanitized_company_name = sanitize_query_input(company_name)
        sanitized_partners = [sanitize_query_input(partner) for partner in partners]
        
        queries = []
        
        # KAP (Kamuyu Aydınlatma Platformu) aramaları
        queries.extend([
            f'site:kap.org.tr "{sanitized_company_name}"',
            f'site:kap.org.tr "{sanitized_company_name}" mali tablo',
            f'site:kap.org.tr "{sanitized_company_name}" yatırımcı sunumu',
            f'site:kap.org.tr "{sanitized_company_name}" özel durum açıklaması'
        ])
        
        # Ticaret Sicil Gazetesi aramaları
        queries.extend([
            f'site:ticaretsicil.gov.tr "{sanitized_company_name}"',
            f'"{sanitized_company_name}" ticaret sicili',
            f'"{sanitized_company_name}" sermaye artırımı',
            f'"{sanitized_company_name}" ortaklık yapısı değişikliği'
        ])
        
        # LinkedIn profesyonel aramaları
        for sanitized_partner in sanitized_partners[:5]:  # İlk 5 ortak için
            queries.extend([
                f'site:linkedin.com "{sanitized_partner}" "{sanitized_company_name}"',
                f'site:linkedin.com "{sanitized_partner}" türkiye'
            ])
        
        # Genel şirket bilgileri
        queries.extend([
            f'"{sanitized_company_name}" şirket profili',
            f'"{sanitized_company_name}" faaliyet alanı',
            f'"{sanitized_company_name}" finansal durum',
            f'"{sanitized_company_name}" son gelişmeler haberler'
        ])
        
        # Ortak/partner aramaları
        for sanitized_partner in sanitized_partners[:3]:  # İlk 3 ortak için detaylı arama
            queries.extend([
                f'"{sanitized_partner}" "{sanitized_company_name}" yönetici',
                f'"{sanitized_partner}" iş deneyimi özgeçmiş',
                f'"{sanitized_partner}" şirket ortağı'
            ])
        
        # Risk ve hukuki aramaları
        queries.extend([
            f'"{sanitized_company_name}" dava icra borç',
            f'"{sanitized_company_name}" risk analizi',
            f'"{sanitized_company_name}" olumsuz haber'
        ])
        
        # Resmi kaynak aramaları
        queries.extend([
            f'site:resmigazete.gov.tr "{sanitized_company_name}"',
            f'site:ilan.gov.tr "{sanitized_company_name}"'
        ])
        
        # Kombine aramalar
        partners_str = " ".join([f'"{sanitized_partner}"' for sanitized_partner in sanitized_partners[:3]])
        queries.extend([
            f'"{sanitized_company_name}" {partners_str} yönetim',
            f'"{sanitized_company_name}" ortaklar kurucu'
        ])
        
        return queries
    
    async def research(self, company_name: str, partners: List[str]) -> List[ResearchResult]:
        """
        Research the company and its partners with Turkish-focused strategy
        
        Args:
            company_name: Name of the company to research
            partners: List of partner/founder names
            
        Returns:
            List of ResearchResult objects containing search results
        """
        print(f"🔍 Başlıyor: {company_name} şirketi araştırması")
        print(f"👥 Ortaklar: {', '.join(partners)}")
        
        # Generate comprehensive search queries
        queries = self._create_search_queries(company_name, partners)
        print(f"📋 {len(queries)} arama sorgusu oluşturuldu")
        
        # Perform general searches
        print("🌐 Genel aramalar yapılıyor...")
        general_results = await self.tavily_service.search_multiple(queries)
        
        # Perform legal and regulatory focused searches
        print("⚖️ Hukuki ve düzenleyici aramalar yapılıyor...")
        legal_results = await self.tavily_service.search_with_legal_focus(company_name, partners)
        
        # Combine all results
        all_results = general_results + legal_results
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            # Build filtered list containing only new URLs for this result set
            filtered_results = []
            for search_result in result.results:
                # Normalize URL by removing UTM params and trailing slash
                normalized_url = self._normalize_url(search_result.url)
                if normalized_url not in seen_urls:
                    seen_urls.add(normalized_url)
                    filtered_results.append(search_result)
            
            # Only append result if filtered list has new URLs
            if filtered_results:
                # Create new result with filtered list
                filtered_result = ResearchResult(
                    query=result.query,
                    results=filtered_results,
                    partners_mentioned=result.partners_mentioned
                )
                unique_results.append(filtered_result)
        
        total_results = sum(len(result.results) for result in unique_results)
        print(f"✅ Araştırma tamamlandı: {len(unique_results)} sorgu seti, {total_results} toplam sonuç")
        
        return unique_results
    
    def get_research_summary(self, research_results: List[ResearchResult]) -> str:
        """Generate a brief summary of research findings"""
        total_results = sum(len(result.results) for result in research_results)
        successful_queries = len([r for r in research_results if r.results])
        
        return f"Research completed: {successful_queries} successful queries, {total_results} total results found"
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing UTM parameters and trailing slash"""
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        parsed = urlparse(url)
        
        # Remove UTM parameters and other tracking parameters
        query_params = parse_qs(parsed.query)
        filtered_params = {
            k: v for k, v in query_params.items() 
            if not k.lower().startswith(('utm_', 'gclid', 'fbclid', 'mc_eid', '_ga'))
        }
        
        # Rebuild query string
        new_query = urlencode(filtered_params, doseq=True)
        
        # Remove trailing slash from path
        new_path = parsed.path.rstrip('/')
        
        # Reconstruct URL
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            new_path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        return normalized
