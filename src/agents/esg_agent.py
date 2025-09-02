from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import List
import json

from ..models.schemas import ResearchResult, ESGAnalysisResult
from ..config import Config


class ESGAgent:
    """ESG analizi yapmaktan sorumlu agent"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            api_key=Config.OPENAI_API_KEY,
            temperature=0.2
        )
        
        self.esg_prompt = ChatPromptTemplate.from_messages([
            ("system", """Sen ESG (Çevresel, Sosyal ve Yönetişim) analizi konusunda uzman bir analitiksin.

Görevin, bir şirket hakkında toplanan araştırma verilerini analiz ederek kapsamlı bir ESG değerlendirmesi yapmaktır.

ÖNEMLİ: Tüm yanıtları Türkçe dilinde ver. ESG analizi tamamen Türkçe olmalı.

Aşağıdaki 7 ana kategoriyi analiz et:

1. TESİS KONUMLARI: Şirketin fabrika/tesis konumları (il, ilçe, mahalle, koordinat bilgileri)
2. SÜRDÜRÜLEBİLİRLİK RAPORLAMASI: CDP, sürdürülebilirlik raporları, çevresel performans açıklamaları
3. ESG POLİTİKALARI: ISO 14001, ISO 45001, çevre ve sosyal politikalar
4. ÇEVRE YÖNETİM SİSTEMİ: Çevre yönetim sertifikaları ve sistemleri
5. HUKUKİ SORUNLAR: Çevresel davalar, cezalar, ÇED kararları, iş kazaları
6. YÖNETİŞİM SORUNLARI: Vergi, rekabet, rüşvet, insan hakları davaları
7. İKLİM AKSIYON PLANLARI: İklim değişikliği hafifletme ve uyum planları

Her kategori için:
- Bulunan somut bilgileri özetle
- Bilgi eksikse bunu belirt
- Risk seviyesini değerlendir (Düşük/Orta/Yüksek)"""),
            
            ("human", """Şirket: {company_name}
Ortaklar: {partners}

Araştırma Verileri:
{research_data}

Bu verileri analiz ederek yukarıdaki 7 kategori için ESG analizi yap. Her kategori için detaylı bulgular ver.""")
        ])
    
    async def analyze_esg(self, company_name: str, partners: List[str], research_results: List[ResearchResult]) -> ESGAnalysisResult:
        """
        ESG analizi yap
        
        Args:
            company_name: Şirket adı
            partners: Ortak listesi
            research_results: Araştırma sonuçları
            
        Returns:
            ESGAnalysisResult
        """
        # Araştırma verilerini formatlayalım
        research_data = self._format_research_data(research_results)
        
        # ESG prompt'unu oluştur
        formatted_prompt = self.esg_prompt.format_messages(
            company_name=company_name,
            partners=", ".join(partners),
            research_data=research_data
        )
        
        try:
            # ESG analizi yap
            response = await self.llm.ainvoke(formatted_prompt)
            analysis_text = response.content
            
            # Analizi kategorilere ayır
            return self._parse_esg_analysis(analysis_text)
            
        except Exception as e:
            print(f"ESG analizi hatası: {e}")
            return self._create_fallback_esg_analysis(company_name)
    
    def _format_research_data(self, research_results: List[ResearchResult]) -> str:
        """Araştırma verilerini formatla"""
        formatted_data = []
        
        for i, result in enumerate(research_results, 1):
            if not result.results:
                continue
                
            formatted_data.append(f"\n--- Arama Sorgusu {i}: {result.query} ---")
            
            for j, search_result in enumerate(result.results[:3], 1):
                formatted_data.append(f"\nSonuç {j}:")
                formatted_data.append(f"Başlık: {search_result.title}")
                formatted_data.append(f"URL: {search_result.url}")
                formatted_data.append(f"İçerik: {search_result.content[:800]}...")
                if search_result.relevance_score > 0:
                    formatted_data.append(f"İlgililik: {search_result.relevance_score:.2f}")
        
        return "\n".join(formatted_data) if formatted_data else "ESG analizi için veri bulunamadı."
    
    def _parse_esg_analysis(self, analysis_text: str) -> ESGAnalysisResult:
        """ESG analizini kategorilere ayır"""
        # Basit ayrıştırma - gelişmiş parsing için regex kullanılabilir
        lines = analysis_text.split('\n')
        
        categories = {
            'facility_locations': '',
            'sustainability_reporting': '',
            'esg_policies': '',
            'environmental_management': '',
            'legal_issues': '',
            'governance_issues': '',
            'climate_action': ''
        }
        
        current_category = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            # Kategori başlıklarını tespit et
            if any(keyword in line.upper() for keyword in ['TESİS', 'KONUM', 'FABRİKA']):
                if current_category and current_content:
                    categories[current_category] = '\n'.join(current_content)
                current_category = 'facility_locations'
                current_content = [line]
            elif any(keyword in line.upper() for keyword in ['SÜRDÜRÜLEBİLİRLİK', 'RAPOR', 'CDP']):
                if current_category and current_content:
                    categories[current_category] = '\n'.join(current_content)
                current_category = 'sustainability_reporting'
                current_content = [line]
            elif any(keyword in line.upper() for keyword in ['POLİTİKA', 'ESG']):
                if current_category and current_content:
                    categories[current_category] = '\n'.join(current_content)
                current_category = 'esg_policies'
                current_content = [line]
            elif any(keyword in line.upper() for keyword in ['ÇEVRE YÖNETİM', 'ISO', 'SERTİFİKA']):
                if current_category and current_content:
                    categories[current_category] = '\n'.join(current_content)
                current_category = 'environmental_management'
                current_content = [line]
            elif any(keyword in line.upper() for keyword in ['DAVA', 'CEZA', 'HUKUKİ', 'ÇED']):
                if current_category and current_content:
                    categories[current_category] = '\n'.join(current_content)
                current_category = 'legal_issues'
                current_content = [line]
            elif any(keyword in line.upper() for keyword in ['VERGİ', 'RÜŞVET', 'REKABET', 'İNSAN HAKLARI']):
                if current_category and current_content:
                    categories[current_category] = '\n'.join(current_content)
                current_category = 'governance_issues'
                current_content = [line]
            elif any(keyword in line.upper() for keyword in ['İKLİM', 'KARBON', 'EMİSYON', 'UYUM']):
                if current_category and current_content:
                    categories[current_category] = '\n'.join(current_content)
                current_category = 'climate_action'
                current_content = [line]
            elif current_category and line:
                current_content.append(line)
        
        # Son kategoriyi ekle
        if current_category and current_content:
            categories[current_category] = '\n'.join(current_content)
        
        # Eğer kategoriler boşsa, tüm metni ilk kategoriye koy
        if not any(categories.values()):
            categories['facility_locations'] = analysis_text
        
        return ESGAnalysisResult(**categories)
    
    def _create_fallback_esg_analysis(self, company_name: str) -> ESGAnalysisResult:
        """ESG analizi başarısız olursa yedek analiz"""
        return ESGAnalysisResult(
            facility_locations=f"{company_name} için tesis konum bilgisi bulunamadı.",
            sustainability_reporting=f"{company_name} için sürdürülebilirlik raporu bilgisi bulunamadı.",
            esg_policies=f"{company_name} için ESG politika bilgisi bulunamadı.",
            environmental_management=f"{company_name} için çevre yönetim sistemi bilgisi bulunamadı.",
            legal_issues=f"{company_name} için hukuki sorun bilgisi bulunamadı.",
            governance_issues=f"{company_name} için yönetişim sorunu bilgisi bulunamadı.",
            climate_action=f"{company_name} için iklim aksiyonu bilgisi bulunamadı."
        )
