"""
Job Scraper MCP Tool

Fetches and extracts job posting information from URLs using web scraping.
"""

from app.google_adk.tools import Tool
from typing import Optional
import requests
from bs4 import BeautifulSoup
import re


@Tool(
    name="scrape_job",
    description="Fetch and extract job posting content from a URL"
)
async def job_scraper_tool(url: str) -> str:
    """
    Scrape job posting from URL.
    
    Args:
        url: Job posting URL
        
    Returns:
        Extracted job posting text
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Try to find job description in common containers
        job_content = None
        
        # Common class/id patterns for job descriptions
        patterns = [
            {'class': re.compile('job.*description', re.I)},
            {'class': re.compile('description', re.I)},
            {'id': re.compile('job.*description', re.I)},
            {'class': re.compile('posting.*body', re.I)},
        ]
        
        for pattern in patterns:
            job_content = soup.find('div', pattern)
            if job_content:
                break
        
        # Fallback: use main or article tag
        if not job_content:
            job_content = soup.find('main') or soup.find('article') or soup.find('body')
        
        if job_content:
            text = job_content.get_text(separator='\n', strip=True)
            # Clean up excessive whitespace
            text = re.sub(r'\n\s*\n', '\n\n', text)
            return text
        
        return "Could not extract job posting content from URL"
        
    except requests.RequestException as e:
        return f"Error fetching URL: {str(e)}"
    except Exception as e:
        return f"Error parsing job posting: {str(e)}"


@Tool(
    name="analyze_job_text",
    description="Analyze job description text and extract structured information"
)
async def analyze_job_text_tool(job_text: str, job_url: Optional[str] = None) -> dict:
    """
    Analyze job description and extract key information.
    
    This is a simple extraction tool. For full analysis, use the job_analyzer agent.
    
    Args:
        job_text: Job description text
        job_url: Optional URL where job was found
        
    Returns:
        Dictionary with extracted job information
    """
    from app.google_adk import LLMAgent
    from app.google_adk.llms import GeminiModel
    import json
    
    analyzer = LLMAgent(
        name="job_analyzer",
        model=GeminiModel("gemini-pro"),
        instructions="""Extract job information into JSON format:
{
    "job_title": "Title",
    "company": "Company name",
    "location": "Location",
    "remote": true/false,
    "salary_range": "Salary if mentioned",
    "requirements": ["Requirement 1", "Requirement 2"],
    "responsibilities": ["Responsibility 1", "Responsibility 2"],
    "preferred_qualifications": [...],
    "tech_stack": ["Tech1", "Tech2"]
}"""
    )
    
    try:
        response = await analyzer.run(f"Analyze this job posting:\n\n{job_text}")
        response_text = response if isinstance(response, str) else str(response)
        
        # Clean markdown
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        
        job_data = json.loads(response_text.strip())
        if job_url:
            job_data["url"] = job_url
        
        return job_data
        
    except Exception as e:
        return {
            "error": str(e),
            "job_text": job_text[:500],
            "url": job_url
        }
