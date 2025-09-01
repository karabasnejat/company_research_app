# Company Research API

A REST service built with FastAPI, LangChain, and Tavily for researching companies and their partners/founders.

## Features

- **FastAPI** REST API with automatic documentation
- **Tavily** for web search and data gathering
- **LangChain** agents for research and summarization
- **GPT-4o** for intelligent summarization
- Two-agent architecture:
  - **Researcher Agent**: Performs searches via Tavily
  - **Summarizer Agent**: Processes and summarizes the retrieved data

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
     "company_name": "Midas Hediyelik Eşya San. ve Tic. Anonim Şti.",
     "partners": [
       "Can Özkök", 
       "Münir Özkök", 
       "İlyas Özkök"
     ]
   }
   ```

## API Endpoints

- `POST /research` - Research a company and its partners
- `GET /` - Health check endpoint

## Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key
- `TAVILY_API_KEY` - Your Tavily API key
- `OPENAI_MODEL` - OpenAI model to use (default: gpt-4o)
- `TAVILY_MAX_RESULTS` - Maximum search results per query (default: 10)
