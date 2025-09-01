from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import List
import json

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
            ("system", """You are an expert business analyst tasked with creating comprehensive company research summaries.

Your task is to analyze research data about a company and its partners/founders, then create a well-structured summary.

Guidelines:
1. Focus on factual information from the research data
2. Organize information clearly with proper sections
3. Highlight key business information, financial data, and recent developments
4. Include relevant information about partners/founders
5. Be concise but comprehensive
6. If information is limited, clearly state what was found vs. what's missing
7. Use professional business language

Structure your summary with these sections:
- Company Overview
- Business Information
- Financial Information (if available)
- Key Personnel/Partners
- Recent Developments
- Summary Assessment"""),
            
            ("human", """Please analyze the following research data and create a comprehensive summary:

Company Name: {company_name}
Partners/Founders: {partners}

Research Data:
{research_data}

Create a detailed but concise summary of the findings.""")
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
        
        summary = f"""# Research Summary for {company_name}

## Company Overview
Company Name: {company_name}
Partners/Founders: {", ".join(partners)}

## Research Results
- Total search queries executed: {len(research_results)}
- Successful queries: {successful_queries}
- Total results found: {total_results}

## Key Findings
Research data has been collected but automatic summarization was not available. 
Please review the raw research data for detailed information.

## Data Quality
{"Good data coverage" if total_results > 10 else "Limited data available"} - 
{total_results} total search results across {successful_queries} successful queries.
"""
        return summary
