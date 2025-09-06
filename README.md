# Company Research API with ESG Analysis

A REST service built with FastAPI, LangChain, and Tavily for researching companies and their partners/founders with comprehensive ESG analysis.

## Features

- **FastAPI** REST API with automatic documentation
- **Tavily** for web search and data gathering
- **LangChain** agents for research and summarization
- **GPT-4o** for intelligent summarization and ESG analysis
- **ESG Analysis** covering 7 key areas:
  1. Facility locations and coordinates
  2. Sustainability reporting (CDP, TCFD, TSRS)
  3. ESG policies and standards
  4. Environmental management systems (ISO 14001, ISO 45001)
  5. Legal issues and environmental lawsuits
  6. Governance issues (tax, corruption, human rights)
  7. Climate action plans and commitments

- Three-agent architecture:
  - **Researcher Agent**: Performs searches via Tavily (general + ESG-specific)
  - **Summarizer Agent**: Processes and summarizes the retrieved data
  - **ESG Agent**: Analyzes ESG-related data and risks

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   copy .env.example .env
   ```
   Then edit `.env` with your API keys.

## Usage

1. Start the server:
   ```bash
   uvicorn src.main:app --reload
   ```

2. Visit `http://localhost:8000/docs` for the interactive API documentation.

3. Make a POST request to `/research` with the following format:
   ```json
   {
     "company_name": "Banat Fırça ve Plastik San. Anonim Şti",
     "company_url": "https://www.banat.com.tr",
     "keywords": ["plastic manufacturing", "brush production", "industrial materials"],
     "partners": [
       "Abdullah Hakan Özkök", 
       "Gökhan Özkök", 
       "Şemen Özkök Erbağan",
       "Helen Özkök"
     ],
     "include_esg_analysis": true
   }
   ```

### Request Fields

- `company_name` (required): Name of the company to research
- `company_url` (optional): Company website URL for enhanced search
- `keywords` (optional): List of keywords related to the company's business
- `partners` (required): List of partner/founder names
- `include_esg_analysis` (optional): Include ESG analysis (default: true)

### Enhanced Search Capabilities

The API now supports:
- **URL-based searches**: When `company_url` is provided, the system performs targeted searches on the company website
- **Keyword-enhanced queries**: `keywords` help create more focused search queries
- **English query optimization**: All search queries are now optimized for English to improve international data coverage

## API Endpoints

- `POST /research` - Research a company and its partners (JSON response)
- `POST /research/markdown` - Research a company and return markdown format (like test.md)
- `GET /` - Health check endpoint
- `GET /health` - Detailed health check with service status

### Response Format

The API now returns enhanced responses with:
- **Research Summary**: Main company analysis with citations
- **Facility Summary**: Detailed facility and location information
- **Sustainability Summary**: ESG and sustainability analysis
- **Citations**: Numbered references [1], [2], [3] with source URLs
- **ESG Analysis**: Comprehensive 7-category ESG evaluation

### Citations Format

All factual statements include numbered citations:
```
Banat Fırça ve Plastik San. Anonim Şirketi, 1947 yılında kurulmuş[1]...
```

Citations list:
```
[1] Company Profile - Banat Official Website
https://www.banat.com/
[2] Financial Information - Business Registry
https://example.com/business-info
```

## Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key
- `TAVILY_API_KEY` - Your Tavily API key
- `OPENAI_MODEL` - OpenAI model to use (default: gpt-4o)
- `TAVILY_MAX_RESULTS` - Maximum search results per query (default: 10)
