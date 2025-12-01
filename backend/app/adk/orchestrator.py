"""
A2A (Agent-to-Agent) Protocol and Multi-Agent Orchestration

Provides standardized agent-to-agent communication and workflow
orchestration using Google ADK compatibility layer (Sequential, Parallel, Loop).
"""

from app.google_adk import Agent, SequentialAgent, ParallelAgent, LoopAgent
from typing import Dict, Any, List, Optional
try:
    from .observability import logger, tracer
except ImportError:
    # Fallback if observability not available
    import logging
    logger = logging.getLogger(__name__)
    tracer = type('tracer', (), {'start_as_current_span': lambda self, name: type('span', (), {'__enter__': lambda s: s, '__exit__': lambda *args: None, 'set_attribute': lambda *args: None})()})()



class A2AOrchestrator:
    """
    Orchestrator for agent-to-agent communication and workflows.
    
    Manages multiple agents and provides methods for:
    - Direct agent-to-agent calls
    - Sequential workflows (job → resume → letter)
    - Parallel execution (evaluate multiple answers simultaneously)
    - Loop workflows (iterative refinement)
    """
    
    def __init__(self, agents: Dict[str, Agent]):
        """
        Initialize orchestrator with agent registry.
        
        Args:
            agents: Dictionary mapping agent names to Agent instances
        """
        self.agents = agents
        logger.info("a2a_orchestrator_initialized", agent_count=len(agents))
    
    async def call_agent(
        self,
        agent_name: str,
        input_data: Any,
        context: Optional[Dict] = None
    ) -> Any:
        """
        Standardized agent-to-agent communication.
        
        Args:
            agent_name: Name of the agent to call
            input_data: Input to pass to the agent
            context: Optional context dictionary
            
        Returns:
            Agent's response
            
        Raises:
            ValueError: If agent not found
        """
        if agent_name not in self.agents:
            logger.error("agent_not_found", agent=agent_name)
            raise ValueError(f"Agent '{agent_name}' not found in registry")
        
        with tracer.start_as_current_span(f"a2a_call_{agent_name}") as span:
            span.set_attribute("agent.name", agent_name)
            span.set_attribute("has_context", context is not None)
            
            logger.info(
                "a2a_call_started",
                agent=agent_name,
                context_keys=list(context.keys()) if context else []
            )
            
            try:
                # Call the agent
                agent = self.agents[agent_name]
                result = await agent.run(input_data)
                
                logger.info("a2a_call_completed", agent=agent_name, success=True)
                span.set_attribute("success", True)
                
                return result
                
            except Exception as e:
                logger.error(
                    "a2a_call_failed",
                    agent=agent_name,
                    error=str(e),
                    exc_info=True
                )
                span.set_attribute("success", False)
                span.set_attribute("error", str(e))
                raise
    
    def create_sequential_workflow(
        self,
        agent_names: List[str],
        workflow_name: str = "sequential_workflow"
    ) -> SequentialAgent:
        """
        Create a sequential workflow where agents execute in order.
        
        Example: job_analysis → resume_tailor → letter_generation
        
        Args:
            agent_names: List of agent names in execution order
            workflow_name: Name for the workflow
            
        Returns:
            SequentialAgent that executes agents in sequence
        """
        agents = [self.agents[name] for name in agent_names]
        
        logger.info(
            "sequential_workflow_created",
            workflow_name=workflow_name,
            agents=agent_names
        )
        
        return SequentialAgent(
            name=workflow_name,
            agents=agents
        )
    
    def create_parallel_workflow(
        self,
        agent_names: List[str],
        workflow_name: str = "parallel_workflow"
    ) -> ParallelAgent:
        """
        Create a parallel workflow where agents execute concurrently.
        
        Example: Evaluate multiple interview answers simultaneously
        
        Args:
            agent_names: List of agent names to execute in parallel
            workflow_name: Name for the workflow
            
        Returns:
            ParallelAgent that executes agents concurrently
        """
        agents = [self.agents[name] for name in agent_names]
        
        logger.info(
            "parallel_workflow_created",
            workflow_name=workflow_name,
            agents=agent_names
        )
        
        return ParallelAgent(
            name=workflow_name,
            agents=agents
        )
    
    def create_loop_workflow(
        self,
        agent_name: str,
        max_iterations: int = 5,
        workflow_name: str = "loop_workflow"
    ) -> LoopAgent:
        """
        Create a loop workflow for iterative refinement.
        
        Example: Iteratively improve resume until quality threshold met
        
        Args:
            agent_name: Agent to loop
            max_iterations: Maximum number of iterations
            workflow_name: Name for the workflow
            
        Returns:
            LoopAgent that executes agent iteratively
        """
        agent = self.agents[agent_name]
        
        logger.info(
            "loop_workflow_created",
            workflow_name=workflow_name,
            agent=agent_name,
            max_iterations=max_iterations
        )
        
        return LoopAgent(
            name=workflow_name,
            agent=agent,
            max_iterations=max_iterations
        )
    
    def register_agent(self, name: str, agent: Agent):
        """
        Add a new agent to the registry.
        
        Args:
            name: Agent name
            agent: Agent instance
        """
        self.agents[name] = agent
        logger.info("agent_registered", agent=name)
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """
        Retrieve an agent by name.
        
        Args:
            name: Agent name
            
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """
        Get list of all registered agent names.
        
        Returns:
            List of agent names
        """
        return list(self.agents.keys())


# Example workflow definitions for InterVu

def create_career_application_workflow(orchestrator: A2AOrchestrator) -> SequentialAgent:
    """
    Create the career application workflow:
    job_analysis → resume_tailoring → letter_generation → messaging
    
    Args:
        orchestrator: A2AOrchestrator instance
        
    Returns:
        Sequential workflow for complete job application
    """
    return orchestrator.create_sequential_workflow(
        agent_names=[
            "job_analyzer",
            "resume_tailor",
            "letter_generator",
            "messaging_generator"
        ],
        workflow_name="career_application_pipeline"
    )


def create_interview_evaluation_workflow(orchestrator: A2AOrchestrator) -> SequentialAgent:
    """
    Create the interview evaluation workflow:
    evaluation → coaching
    
    Args:
        orchestrator: A2AOrchestrator instance
        
    Returns:
        Sequential workflow for interview evaluation
    """
    return orchestrator.create_sequential_workflow(
        agent_names=[
            "evaluation_agent",
            "coaching_agent"
        ],
        workflow_name="interview_evaluation_pipeline"
    )
