from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import List
import json
from urllib.parse import urlparse

from ..models.schemas import ResearchResult
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
            ("system", """Sen Türkiye'deki şirketleri araştıran uzman bir business analistsin. 

Görevin, bir şirket ve ortakları/kurucuları hakkındaki araştırma verilerini analiz ederek kapsamlı bir özet oluşturmak.

Kullanacağın Türkiye'ye özel kaynaklar:
- KAP (Kamuyu Aydınlatma Platformu) - finansal ve kurumsal bilgiler
- Ticaret Sicil Gazetesi - yasal değişiklikler, sermaye yapısı
- Resmi Gazete - resmi açıklamalar
- ilan.gov.tr - ihale ve ilan bilgileri  
- LinkedIn - profesyonel profiller
- Yerel basın - güncel haberler

Yönergeler:
1. Araştırma verilerindeki gerçek bilgilere odaklan
2. Bilgileri net bölümlerle düzenle
3. Finansal veri, son gelişmeler ve kurumsal bilgileri öne çıkar
4. Ortaklar/kurucular hakkında ilgili bilgileri dahil et
5. Özlü ama kapsamlı ol
6. Bilgi sınırlıysa, bulunanları vs. eksik olanları açıkça belirt
7. Profesyonel iş dili kullan
8. Risk faktörleri varsa belirt

Özetini şu bölümlerle yapılandır:
- Şirket Genel Bilgileri
- Faaliyet Alanı ve İş Modeli  
- Finansal Durum (varsa)
- Kilit Personel/Ortaklar
- Son Gelişmeler ve Haberler
- Risk Analizi (varsa)
- Genel Değerlendirme"""),
            
            ("human", """Lütfen aşağıdaki araştırma verilerini analiz ederek kapsamlı bir özet oluştur:

Şirket Adı: {company_name}
Ortaklar/Kurucular: {partners}

Araştırma Verileri:
{research_data}

Detaylı ama özlü bir bulgular özeti oluştur.""")
        ])
    
    async def summarize(self, company_name: str, partners: List[str], research_results: List[ResearchResult]) -> str:
        """
        Summarize the research results using GPT-4o
        
        Args:
            company_name: Name of the company
            partners: List of partner names
            research_results: List of research results to summarize
            
        Returns:
            Comprehensive summary string
        """
        # Prepare research data for the prompt
        research_data = self._format_research_data(research_results)
        
        # Create the prompt
        formatted_prompt = self.summary_prompt.format_messages(
            company_name=company_name,
            partners=", ".join(partners),
            research_data=research_data
        )
        
        try:
            # Generate summary
            response = await self.llm.ainvoke(formatted_prompt)
            return response.content
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return self._create_fallback_summary(company_name, partners, research_results)
    
    def _format_research_data(self, research_results: List[ResearchResult]) -> str:
        """Format research results for the prompt"""
        formatted_data = []
        
        for i, result in enumerate(research_results, 1):
            if not result.results:
                continue
                
            formatted_data.append(f"\n--- Search Query {i}: {result.query} ---")
            
            for j, search_result in enumerate(result.results[:3], 1):  # Limit to top 3 results per query
                formatted_data.append(f"\nResult {j}:")
                formatted_data.append(f"Title: {search_result.title}")
                formatted_data.append(f"URL: {search_result.url}")
                formatted_data.append(f"Content: {search_result.content[:500]}...")  # Limit content length
                if search_result.relevance_score > 0:
                    formatted_data.append(f"Relevance: {search_result.relevance_score:.2f}")
        
        return "\n".join(formatted_data) if formatted_data else "No research data available."
    
    def _create_fallback_summary(self, company_name: str, partners: List[str], research_results: List[ResearchResult]) -> str:
        """Create a basic summary if AI summarization fails"""
        total_results = sum(len(result.results) for result in research_results)
        successful_queries = len([r for r in research_results if r.results])
        
        # Count sources by domain
        source_counts = {}
        for result in research_results:
            for search_result in result.results:
                # Safe URL parsing with normalization
                url = search_result.url
                # Prepend scheme if missing
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                
                # Strip leading "www." if present
                if domain.startswith('www.'):
                    domain = domain[4:]
                
                # Fall back to "unknown" if empty
                domain = domain if domain else 'unknown'
                
                source_counts[domain] = source_counts.get(domain, 0) + 1
        
        summary = f"""# {company_name} - Araştırma Özeti

## Şirket Genel Bilgileri
Şirket Adı: {company_name}
Ortaklar/Kurucular: {", ".join(partners)}

## Araştırma Sonuçları
- Toplam arama sorgusu: {len(research_results)}
- Başarılı sorgular: {successful_queries}
- Toplam bulunan sonuç: {total_results}

## Kaynak Dağılımı"""
        
        for domain, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            summary += f"\n- {domain}: {count} sonuç"
        
        summary += f"""

## Veri Kalitesi
{"İyi veri kapsamı" if total_results > 15 else "Sınırlı veri mevcut"} - 
{total_results} toplam sonuç, {successful_queries} başarılı sorgu ile elde edildi.

## Not
Araştırma verileri toplanmış ancak otomatik özetleme kullanılamadı.
Detaylı bilgi için ham araştırma verilerini inceleyiniz.
"""
        return summary
