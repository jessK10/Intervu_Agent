"""
Context Engineering and Compaction

Provides strategies for managing context window limits through
summarization, relevance filtering, and intelligent token management.
"""

from app.google_adk import Agent, LLMAgent
from app.google_adk.llms import GeminiModel
from typing import List, Dict, Any, Tuple
try:
    from .observability import logger, tracer
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    tracer = type('tracer', (), {'start_as_current_span': lambda self, name: type('span', (), {'__enter__': lambda s: s, '__exit__': lambda *args: None, 'set_attribute': lambda *args: None})()})()
import re


class ContextCompactor:
    """
    Manages context compaction for fitting information within token limits.
    
    Strategies:
    - Summarization: Condense long texts while preserving key information
    - Relevance filtering: Select most relevant items based on query
    - Sliding window: Keep most recent N items
    - Hierarchical summarization: Summarize in chunks then combine
    """
    
    def __init__(self, max_tokens: int = 2000):
        """
        Initialize context compactor.
        
        Args:
            max_tokens: Maximum tokens to target for compacted context
        """
        self.max_tokens = max_tokens
        
        # Create compaction agent
        self.compaction_agent = LLMAgent(
            name="context_compactor",
            model=GeminiModel("gemini-pro"),
            instructions=f"""You are a context compaction specialist. 
            Your job is to summarize and condense information while preserving 
            the most important details. Target length: {max_tokens} tokens or less.
            Be concise but comprehensive."""
        )
        
        logger.info("context_compactor_initialized", max_tokens=max_tokens)
    
    async def compact_interview_history(
        self,
        interviews: List[Dict[str, Any]]
    ) -> str:
        """
        Summarize interview history to fit context window.
        
        Args:
            interviews: List of interview dictionaries with questions, answers, scores
            
        Returns:
            Compacted summary string
        """
        with tracer.start_as_current_span("compact_interview_history") as span:
            span.set_attribute("interview_count", len(interviews))
            
            if not interviews:
                return ""
            
            # Format interviews for summarization
            formatted_history = self._format_interviews(interviews)
            
            # Estimate token count (rough approximation: 1 token ≈ 4 chars)
            estimated_tokens = len(formatted_history) // 4
            
            if estimated_tokens <= self.max_tokens:
                logger.info("interview_history_within_limit", estimated_tokens=estimated_tokens)
                return formatted_history
            
            # Need compaction
            logger.info(
                "compacting_interview_history",
                estimated_tokens=estimated_tokens,
                target_tokens=self.max_tokens
            )
            
            prompt = f"""Summarize this interview history concisely:

{formatted_history}

Focus on:
- Overall performance trends
- Key strengths and weaknesses
- Notable patterns

Keep under {self.max_tokens} tokens."""
            
            try:
                summary = await self.compaction_agent.run(prompt)
                span.set_attribute("success", True)
                return summary if isinstance(summary, str) else str(summary)
                
            except Exception as e:
                logger.error("compaction_failed", error=str(e), exc_info=True)
                span.set_attribute("success", False)
                # Fallback: return truncated history
                return formatted_history[:self.max_tokens * 4]
    
    def select_relevant_context(
        self,
        query: str,
        context_items: List[str],
        top_k: int = 5
    ) -> List[str]:
        """
        Select most relevant context items based on query.
        
        Uses simple keyword matching (can be enhanced with embeddings).
        
        Args:
            query: The user's query or task
            context_items: List of context strings
            top_k: Number of items to return
            
        Returns:
            Top-k most relevant context items
        """
        with tracer.start_as_current_span("select_relevant_context") as span:
            span.set_attribute("total_items", len(context_items))
            span.set_attribute("top_k", top_k)
            
            # Score each item by relevance
            scored_items = []
            query_terms = set(self._tokenize(query.lower()))
            
            for item in context_items:
                score = self._relevance_score(query_terms, item)
                scored_items.append((score, item))
            
            # Sort by score and take top-k
            sorted_items = sorted(scored_items, key=lambda x: x[0], reverse=True)
            selected = [item for _, item in sorted_items[:top_k]]
            
            logger.info(
                "context_selected",
                total_items=len(context_items),
                selected_count=len(selected)
            )
            
            return selected
    
    def sliding_window(
        self,
        items: List[Any],
        window_size: int = 10
    ) -> List[Any]:
        """
        Keep only the most recent N items.
        
        Args:
            items: List of items (e.g., messages, events)
            window_size: Number of items to keep
            
        Returns:
            Most recent items
        """
        return items[-window_size:] if len(items) > window_size else items
    
    async def hierarchical_summarization(
        self,
        text: str,
        chunk_size: int = 1000
    ) -> str:
        """
        Summarize long text by chunking and hierarchical summarization.
        
        Args:
            text: Long text to summarize
            chunk_size: Size of each chunk (in characters)
            
        Returns:
            Final summary
        """
        # Split into chunks
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        if len(chunks) == 1:
            return await self.compact_interview_history([{"raw": text}])
        
        # Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            logger.info(f"summarizing_chunk_{i}", chunk_length=len(chunk))
            summary = await self.compaction_agent.run(
                f"Summarize this concisely:\n\n{chunk}"
            )
            chunk_summaries.append(summary if isinstance(summary, str) else str(summary))
        
        # Combine summaries
        combined = "\n\n".join(chunk_summaries)
        
        # Final summary if still too long
        if len(combined) > self.max_tokens * 4:
            final_summary = await self.compaction_agent.run(
                f"Create a final concise summary:\n\n{combined}"
            )
            return final_summary if isinstance(final_summary, str) else str(final_summary)
        
        return combined
    
    def _format_interviews(self, interviews: List[Dict]) -> str:
        """Format interviews for display."""
        formatted = []
        for idx, interview in enumerate(interviews, 1):
            role = interview.get("role", "Unknown")
            score = interview.get("overall_score", "N/A")
            strengths = interview.get("strengths", [])
            weaknesses = interview.get("weaknesses", [])
            
            formatted.append(f"""Interview {idx} ({role}):
- Score: {score}/10
- Strengths: {', '.join(strengths[:3]) if strengths else 'None noted'}
- Weaknesses: {', '.join(weaknesses[:3]) if weaknesses else 'None noted'}""")
        
        return "\n\n".join(formatted)
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        return re.findall(r'\w+', text.lower())
    
    def _relevance_score(self, query_terms: set, item: str) -> float:
        """Calculate relevance score based on term overlap."""
        item_terms = set(self._tokenize(item.lower()))
        overlap = len(query_terms & item_terms)
        return overlap / max(len(query_terms), 1)
