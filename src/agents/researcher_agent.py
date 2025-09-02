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
        """Türkçe şirket araştırması için optimize edilmiş sorgular oluştur"""
        queries = []
        
        # 1. TEMEL ŞİRKET BİLGİLERİ (Türkçe odaklı)
        queries.append(f'"{company_name}" şirket profili hakkında bilgi')
        queries.append(f'"{company_name}" anonim şirketi genel bilgiler')
        queries.append(f'"{company_name}" kuruluş tarihi sermaye')
        queries.append(f'"{company_name}" faaliyet alanı sektör')
        queries.append(f'"{company_name}" merkez adresi fabrika tesis')
        
        # 2. FİNANSAL VE YASAL BİLGİLER
        queries.append(f'"{company_name}" mali tablo bilanço kar zarar')
        queries.append(f'"{company_name}" KAP bildirimleri finansal durum')
        queries.append(f'"{company_name}" ciro karlılık performans')
        queries.append(f'"{company_name}" borsa kotasyon hisse senedi')
        queries.append(f'"{company_name}" ticaret sicil gazetesi')
        
        # 3. YÖNETİM KADROSU VE ORTAKLAR (her ortak için detaylı)
        for partner in partners:
            queries.append(f'"{partner}" "{company_name}" yönetim kurulu')
            queries.append(f'"{partner}" işadamı profil biyografi')
            queries.append(f'"{partner}" genel müdür CEO başkan')
            queries.append(f'"{partner}" LinkedIn profil deneyim')
            queries.append(f'"{partner}" haber röportaj basın')
        
        # 4. ŞİRKET HABERLERİ VE GELİŞMELER
        queries.append(f'"{company_name}" son haberler 2024 2025')
        queries.append(f'"{company_name}" yatırım proje genişleme')
        queries.append(f'"{company_name}" ihracat pazar büyüme')
        queries.append(f'"{company_name}" teknoloji inovasyon AR-GE')
        
        # 5. SEKTÖREL ARAŞTIRMA
        queries.append(f'"{company_name}" rakip analiz pazar payı')
        queries.append(f'"{company_name}" sektör lideri konumu')
        queries.append(f'"{company_name}" müşteri referans proje')
        
        # 6. KOMBİNE ARAMALAR (ortak + şirket)
        if len(partners) > 0:
            main_partners = " ".join([f'"{partner}"' for partner in partners[:3]])
            queries.append(f'"{company_name}" {main_partners} yönetim')
            queries.append(f'{main_partners} işbirliği ortaklık')
        
        return queries
    
    def _create_esg_search_queries(self, company_name: str, partners: List[str]) -> List[str]:
        """ESG analizi için Türkçe optimize edilmiş arama sorguları"""
        esg_queries = []
        
        # 1. TESİS KONUMLARI VE OPERASYONLAR
        esg_queries.append(f'"{company_name}" fabrika tesis konum adres il ilçe')
        esg_queries.append(f'"{company_name}" üretim merkezi lokasyon')
        esg_queries.append(f'"{company_name}" şube ofis dağıtım merkezi')
        
        # 2. SÜRDÜRÜLEBİLİRLİK RAPORLAMASI
        esg_queries.append(f'"{company_name}" sürdürülebilirlik raporu CDP')
        esg_queries.append(f'"{company_name}" entegre faaliyet raporu ESG')
        esg_queries.append(f'"{company_name}" çevre performans karbon ayak izi')
        esg_queries.append(f'"{company_name}" TCFD SASB GRI raporlama')
        
        # 3. ESG POLİTİKALARI VE SERTİFİKALAR
        esg_queries.append(f'"{company_name}" ESG politika çevre sosyal')
        esg_queries.append(f'"{company_name}" ISO 14001 ISO 45001 sertifika')
        esg_queries.append(f'"{company_name}" kalite çevre yönetim sistemi')
        esg_queries.append(f'"{company_name}" sürdürülebilirlik taahhüt')
        
        # 4. ÇEVRESEL PERFORMANS VE RİSKLER
        esg_queries.append(f'"{company_name}" çevre etkisi değerlendirme ÇED')
        esg_queries.append(f'"{company_name}" atık yönetimi geri dönüşüm')
        esg_queries.append(f'"{company_name}" enerji verimlilik yenilenebilir')
        esg_queries.append(f'"{company_name}" su yönetimi kirlilik')
        
        # 5. HUKUKİ SORUNLAR VE CEZALAR
        esg_queries.append(f'"{company_name}" çevre dava ceza ihlal')
        esg_queries.append(f'"{company_name}" idari para cezası ÇED')
        esg_queries.append(f'"{company_name}" iş kazası çalışan güvenlik')
        esg_queries.append(f'"{company_name}" işçi hakları sendika')
        
        # 6. YÖNETİŞİM VE ETİK SORUNLAR (Ortaklar için)
        for partner in partners[:3]:  # İlk 3 ortak
            esg_queries.append(f'"{partner}" vergi dava mahkeme')
            esg_queries.append(f'"{partner}" rüşvet yolsuzluk adalet')
            esg_queries.append(f'"{partner}" rekabet kurulu soruşturma')
            esg_queries.append(f'"{partner}" insan hakları etik')
        
        # 7. İKLİM DEĞİŞİKLİĞİ VE KARBON YÖNETİMİ
        esg_queries.append(f'"{company_name}" iklim değişikliği strateji')
        esg_queries.append(f'"{company_name}" karbon emisyon azaltım hedef')
        esg_queries.append(f'"{company_name}" net sıfır karbon nötr')
        esg_queries.append(f'"{company_name}" yeşil teknoloji temiz enerji')
        
        # 8. SOSYAL PERFORMANS
        esg_queries.append(f'"{company_name}" toplumsal sorumluluk projesi')
        esg_queries.append(f'"{company_name}" çalışan hakları çeşitlilik')
        esg_queries.append(f'"{company_name}" yerel toplum katkı')
        
        return esg_queries
    
    async def research(self, company_name: str, partners: List[str], include_esg: bool = True) -> List[ResearchResult]:
        """
        Research the company and its partners using focused Turkish sources
        
        Args:
            company_name: Name of the company to research
            partners: List of partner/founder names
            include_esg: Include ESG-specific research
            
        Returns:
            List of ResearchResult objects containing search results
        """
        # Generate search queries
        queries = self._create_search_queries(company_name, partners)
        
        # ESG sorguları ekle
        if include_esg:
            esg_queries = self._create_esg_search_queries(company_name, partners)
            queries.extend(esg_queries)
        
        print(f"Generated {len(queries)} search queries for research (ESG: {include_esg})")
        
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
