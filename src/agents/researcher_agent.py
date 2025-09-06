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
    
    def _create_search_queries(self, company_name: str, company_url: str = None, keywords: List[str] = None, partners: List[str] = None) -> List[str]:
        """Create optimized English search queries for company research"""
        queries = []
        keywords = keywords or []
        partners = partners or []
        
        # 1. BASIC COMPANY INFORMATION (English queries)
        queries.append(f'"{company_name}" company profile information')
        queries.append(f'"{company_name}" corporation general information')
        queries.append(f'"{company_name}" founding date capital')
        queries.append(f'"{company_name}" business sector industry')
        queries.append(f'"{company_name}" headquarters address facility location')
        
        # Add URL-based queries if company URL is provided
        if company_url:
            domain = company_url.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
            queries.append(f'site:{domain} about company')
            queries.append(f'site:{domain} management team')
            queries.append(f'site:{domain} financial information')
        
        # Add keyword-based queries
        for keyword in keywords:
            queries.append(f'"{company_name}" {keyword}')
            queries.append(f'"{company_name}" {keyword} industry sector')
        
        # 2. FINANCIAL AND LEGAL INFORMATION
        queries.append(f'"{company_name}" financial statements balance sheet')
        queries.append(f'"{company_name}" financial disclosure reports')
        queries.append(f'"{company_name}" revenue profitability performance')
        queries.append(f'"{company_name}" stock exchange listing shares')
        queries.append(f'"{company_name}" trade registry gazette')
        
        # 3. MANAGEMENT AND PARTNERS (detailed for each partner)
        for partner in partners:
            queries.append(f'"{partner}" "{company_name}" board of directors')
            queries.append(f'"{partner}" businessman profile biography')
            queries.append(f'"{partner}" CEO executive president')
            queries.append(f'"{partner}" LinkedIn profile experience')
            queries.append(f'"{partner}" news interview press')
        
        # 4. COMPANY NEWS AND DEVELOPMENTS
        queries.append(f'"{company_name}" latest news 2024 2025')
        queries.append(f'"{company_name}" investment project expansion')
        queries.append(f'"{company_name}" export market growth')
        queries.append(f'"{company_name}" technology innovation R&D')
        
        # 5. SECTOR RESEARCH
        queries.append(f'"{company_name}" competitor analysis market share')
        queries.append(f'"{company_name}" industry leader position')
        queries.append(f'"{company_name}" customer reference project')
        
        # 6. COMBINED SEARCHES (partner + company)
        if len(partners) > 0:
            main_partners = " ".join([f'"{partner}"' for partner in partners[:3]])
            queries.append(f'"{company_name}" {main_partners} management')
            queries.append(f'{main_partners} partnership collaboration')
        
        return queries
    
    def _create_esg_search_queries(self, company_name: str, company_url: str = None, keywords: List[str] = None, partners: List[str] = None) -> List[str]:
        """Create English optimized search queries for ESG analysis"""
        esg_queries = []
        keywords = keywords or []
        partners = partners or []
        
        # 1. FACILITY LOCATIONS AND OPERATIONS
        esg_queries.append(f'"{company_name}" factory facility location address')
        esg_queries.append(f'"{company_name}" production center locations')
        esg_queries.append(f'"{company_name}" branch office distribution center')
        
        # Add URL-based ESG queries if company URL is provided
        if company_url:
            domain = company_url.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
            esg_queries.append(f'site:{domain} sustainability report')
            esg_queries.append(f'site:{domain} environmental policy')
            esg_queries.append(f'site:{domain} ESG disclosure')
        
        # Add keyword-based ESG queries
        for keyword in keywords:
            if any(term in keyword.lower() for term in ['environment', 'sustainability', 'green', 'carbon', 'climate']):
                esg_queries.append(f'"{company_name}" {keyword} environmental')
                esg_queries.append(f'"{company_name}" {keyword} sustainability')
        
        # 2. SUSTAINABILITY REPORTING
        esg_queries.append(f'"{company_name}" sustainability report CDP')
        esg_queries.append(f'"{company_name}" integrated annual report ESG')
        esg_queries.append(f'"{company_name}" environmental performance carbon footprint')
        esg_queries.append(f'"{company_name}" TCFD SASB GRI reporting')
        
        # 3. ESG POLICIES AND CERTIFICATIONS
        esg_queries.append(f'"{company_name}" ESG policy environmental social')
        esg_queries.append(f'"{company_name}" ISO 14001 ISO 45001 certification')
        esg_queries.append(f'"{company_name}" quality environmental management system')
        esg_queries.append(f'"{company_name}" sustainability commitment')
        
        # 4. ENVIRONMENTAL PERFORMANCE AND RISKS
        esg_queries.append(f'"{company_name}" environmental impact assessment EIA')
        esg_queries.append(f'"{company_name}" waste management recycling')
        esg_queries.append(f'"{company_name}" energy efficiency renewable')
        esg_queries.append(f'"{company_name}" water management pollution')
        
        # 5. LEGAL ISSUES AND PENALTIES
        esg_queries.append(f'"{company_name}" environmental lawsuit penalty violation')
        esg_queries.append(f'"{company_name}" administrative fine EIA')
        esg_queries.append(f'"{company_name}" workplace accident employee safety')
        esg_queries.append(f'"{company_name}" worker rights union')
        
        # 6. GOVERNANCE AND ETHICS ISSUES (For Partners)
        for partner in partners[:3]:  # First 3 partners
            esg_queries.append(f'"{partner}" tax lawsuit court')
            esg_queries.append(f'"{partner}" bribery corruption justice')
            esg_queries.append(f'"{partner}" competition authority investigation')
            esg_queries.append(f'"{partner}" human rights ethics')
        
        # 7. CLIMATE CHANGE AND CARBON MANAGEMENT
        esg_queries.append(f'"{company_name}" climate change strategy')
        esg_queries.append(f'"{company_name}" carbon emission reduction target')
        esg_queries.append(f'"{company_name}" net zero carbon neutral')
        esg_queries.append(f'"{company_name}" green technology clean energy')
        
        # 8. SOCIAL PERFORMANCE
        esg_queries.append(f'"{company_name}" corporate social responsibility project')
        esg_queries.append(f'"{company_name}" employee rights diversity')
        esg_queries.append(f'"{company_name}" local community contribution')
        
        return esg_queries
    
    async def research(self, company_name: str, company_url: str = None, keywords: List[str] = None, partners: List[str] = None, include_esg: bool = True) -> List[ResearchResult]:
        """
        Research the company and its partners using focused sources with English queries
        
        Args:
            company_name: Name of the company to research
            company_url: Company website URL (optional)
            keywords: Keywords about the company (optional)
            partners: List of partner/founder names (optional)
            include_esg: Include ESG-specific research
            
        Returns:
            List of ResearchResult objects containing search results
        """
        partners = partners or []
        keywords = keywords or []
        
        # Generate search queries
        queries = self._create_search_queries(company_name, company_url, keywords, partners)
        
        # Add ESG queries
        if include_esg:
            esg_queries = self._create_esg_search_queries(company_name, company_url, keywords, partners)
            queries.extend(esg_queries)
        
        print(f"Generated {len(queries)} search queries for research (ESG: {include_esg})")
        print(f"Company URL: {company_url if company_url else 'Not provided'}")
        print(f"Keywords: {', '.join(keywords) if keywords else 'None'}")
        
        # Define focused domains for Turkish company research
        include_domains = [
            # Resmi kaynaklar
            "kap.org.tr",           # Kamuyu Aydınlatma Platformu
            "ttsg.org.tr",          # Ticaret Sicil Gazetesi
            "resmigazete.gov.tr",   # Resmi Gazete
            "ilan.gov.tr",          # İhale ilanları
            "merkur.org.tr",        # Merkezi Kayıt Kuruluşu
            
            # Finansal ve ekonomi kaynakları
            "ekonomim.com",
            "dunya.com",
            "paraanaliz.com",
            "bloomberght.com",
            "marketwatch.com.tr",
            "investing.com.tr",
            
            # Haber kaynakları
            "hurriyet.com.tr",
            "milliyet.com.tr",
            "sabah.com.tr",
            "sozcu.com.tr",
            "haberturk.com",
            "ntv.com.tr",
            "cnnturk.com",
            "aa.com.tr",            # Anadolu Ajansı
            "trt.net.tr",
            
            # Uluslararası kaynaklar
            "reuters.com",
            "bloomberg.com",
            "ft.com",               # Financial Times
            "wsj.com",              # Wall Street Journal
            
            # Profesyonel ağlar
            "linkedin.com",         # Profesyonel profiller
            
            # Sektörel kaynaklar
            "iso.org.tr",           # İstanbul Sanayi Odası
            "tobb.org.tr",          # Türkiye Odalar Birliği
            "musiad.org.tr",        # MÜSİAD
            "tusiad.org",           # TÜSİAD
            
            # Şirket web siteleri (genel domain'ler)
            "com.tr",
            "org.tr",
            "net.tr"
        ]
        
        exclude_domains = [
            # Sosyal medya platformları
            "facebook.com",
            "instagram.com", 
            "twitter.com",
            "x.com",
            "tiktok.com",
            "youtube.com",
            "pinterest.com",
            "snapchat.com",
            "whatsapp.com",
            
            # Forum ve blog siteleri
            "reddit.com",
            "quora.com",
            "medium.com",
            "wordpress.com",
            "blogspot.com",
            
            # Alışveriş siteleri
            "amazon.com",
            "alibaba.com",
            "hepsiburada.com",
            "trendyol.com",
            "n11.com"
        ]
        
        # Perform searches with domain filtering
        research_results = await self.tavily_service.search_multiple(
            queries, 
            include_domains=include_domains,
            exclude_domains=exclude_domains
        )
        
        print(f"Completed research with {len(research_results)} result sets")
        
        return research_results
    
    def get_research_summary(self, research_results: List[ResearchResult]) -> str:
        """Generate a brief summary of research findings"""
        total_results = sum(len(result.results) for result in research_results)
        successful_queries = len([r for r in research_results if r.results])
        
        return f"Research completed: {successful_queries} successful queries, {total_results} total results found"
