# InterVu: Google ADK-Powered Interview & Career Agent Platform

## Problem Statement

Job seekers face critical challenges in interview preparation and job applications that traditional approaches fail to address effectively:

- **No personalized interview practice**: Candidates lack access to AI-powered mock interviews customized to their role, experience level, and target companies
- **Limited feedback quality**: Generic interview coaching doesn't provide actionable, multi-criteria evaluation with historical tracking
- **Time-consuming application processes**: Tailoring resumes, writing cover letters, and crafting outreach messages for each job is manual and repetitive
- **No performance insights**: Candidates can't track their progress over time or identify specific weaknesses to improve

This is an important problem because **interview performance directly impacts career trajectory**. Poor preparation leads to missed opportunities, while effective practice with quality feedback significantly increases success rates. With the job market becoming increasingly competitive, candidates need intelligent, scalable tools that provide personalized coaching at a fraction of the cost of human coaches.

## Why Agents?

Agents are the ideal solution for interview preparation and career assistance because this problem inherently requires:

**1. Specialized Expertise Across Domains**  
Different aspects of job preparation require different skills - CV parsing needs structured extraction, interview evaluation needs multi-criteria scoring, resume tailoring needs job-matching logic. **Multi-agent systems** allow each agent to specialize in one domain while collaborating on complex workflows.

**2. Sequential and Parallel Workflows**  
Career preparation follows natural sequences: parse CV → analyze job → tailor resume → generate letter → create outreach. **Google ADK's Sequential, Parallel, and Loop agents** enable orchestrating these workflows intelligently while allowing parallel processing (e.g., evaluating multiple interview answers simultaneously).

**3. Stateful Conversations with Memory**  
Interview coaching improves when the system "remembers" past performance. **Google ADK's Session Management** (InMemorySessionService + DatabaseSessionService) maintains context across interactions, enabling agents to provide increasingly personalized feedback based on historical strengths and weaknesses.

**4. Context-Aware Intelligence**  
Interview history can become long. **Google ADK's context engineering** allows agents to summarize histories, select relevant past interviews, and fit information within token limits without losing critical insights.

**5. Production-Grade Infrastructure**  
This isn't a toy - candidates need reliable, observable, scalable systems. **Google ADK provides built-in observability** (OpenTelemetry tracing, structured logging), session persistence, and deployment to Vertex AI Agent Engine out of the box.

**Why Google ADK Specifically?**  
Google's Agent Development Kit is production-ready, powers Google's own agent products (Agentspace, Customer Engagement Suite), and provides everything needed: agent orchestration, MCP tools, session management, observability, and cloud deployment - all in one cohesive framework.

## What You Created

### Overall Architecture

InterVu is a full-stack platform built on **Google ADK** with **8 specialized AI agents** orchestrated to handle the complete job preparation lifecycle.


## Demo

### Voice-Powered Mock Interviews

**User Flow:**
1. User selects role ("Senior Software Engineer"), level, type (technical/behavioral), and tech stack
2. System generates customized questions using Question Generation agent
3. **Voice Interface**: AI interviewer speaks questions aloud (Web Speech Synthesis)
4. User responds verbally or via text (Web Speech Recognition)
5. All Q&A pairs stored in session state

**Session Management in Action:**
```python
# Create interview session with ADK
session = await session_service.create_session(
    app_name="interview_practice",
    user_id=user_id,
    initial_state={
        "role": "Senior Software Engineer",
        "questions": generated_questions,
        "answers": []
    }
)
```

### Intelligent Evaluation with Multi-Agent Orchestration

**Evaluation Workflow:**
```python
# A2A Orchestrator manages sequential workflow
eval_workflow = orchestrator.create_sequential_workflow([
    "evaluation_agent",  # Scores each answer on 4 criteria
    "coaching_agent"     # Provides personalized improvement tips
])

result = await eval_workflow.run({
    "questions": session.state["questions"],
    "answers": session.state["answers"],
    "role": session.state["role"]
})
```

**Output:**
- **Overall Score**: 7.5/10
- **Per-Question Breakdown**: Clarity (8), Structure (7), Technical Depth (6), Examples (9)
- **Strengths**: "Good concrete examples", "Clear communication"
- **Weaknesses**: "Could add more technical detail", "Missing edge case discussion"
- **Coaching Tips**: Personalized based on historical weaknesses stored in session state

### Career Application Suite

**Complete Job Application in One Workflow:**

```python
# Sequential workflow using ADK orchestrator
career_pipeline = orchestrator.create_sequential_workflow([
    "job_analyzer",      # MCP tool scrapes + analyzes job posting
    "resume_tailor",     # Matches user profile to requirements
    "letter_generator",  # Creates personalized cover letter
    "messaging_generator" # Generates recruiter outreach
])

application = await career_pipeline.run(job_url)
```

**What User Gets:**
- **Analyzed Job**: Requirements, responsibilities, tech stack, company culture
- **Tailored Resume**: Highlights relevant experience for this specific role
- **Cover Letter**: Personalized professional or friendly tone
- **Outreach Messages**: LinkedIn connection message + recruiter email

### Observability in Production

**Every agent call is traced:**
```python
with tracer.start_as_current_span("evaluate_interview") as span:
    span.set_attribute("interview_id", interview_id)
    span.set_attribute("question_count", len(questions))
    logger.info("evaluation_started", user_id=user_id)
    
    result = await evaluation_agent.run(data)
    
    logger.info("evaluation_complete", 
                score=result["overall_score"],
                duration_ms=elapsed)
```

**Structured JSON logs** enable easy parsing and monitoring in production.

## The Build

### Technologies Used

**Google ADK Framework:**
- `google-adk==0.1.0` - Core agent framework
- **LLMAgent** pattern for all 8 agents (using Gemini Pro model)
- **Sequential/Parallel/Loop agents** for workflow orchestration
- **MCP (Model Context Protocol)** for tool integration
- **SessionService** for state management (InMemory + PostgreSQL backends)

**Observability Stack:**
- `structlog==23.1.0` - Structured JSON logging
- `opentelemetry-api` + `opentelemetry-sdk` - Distributed tracing
- OpenTelemetry span attributes for performance metrics

**Backend Infrastructure:**
- FastAPI (Python async) - API layer
- MongoDB (Motor async driver) - User data, interviews, applications
- PostgreSQL (`psycopg2-binary`) - ADK session persistence
- JWT authentication with bcrypt

**Frontend:**
- Next.js 15 with TypeScript
- Tailwind CSS + ShadCN UI
- Web Speech API (synthesis + recognition)

### Implementation Highlights

**1. Session Management** (`app/adk/session_service.py`):
```python
class InterVuSessionService:
    def __init__(self, use_db=False):
        if use_db:
            # Production: PostgreSQL persistence
            self.service = DatabaseSessionService(connection_string=...)
        else:
            # Development: In-memory sessions
            self.service = InMemorySessionService()
    
    # Persistent state across sessions using magic prefixes
    def create_persistent_state_key(self, key, scope="user"):
        return f"{scope}:{key}"  # e.g., "user:weaknesses"
```

**2. A2A Protocol & Orchestration** (`app/adk/orchestrator.py`):
```python
class A2AOrchestrator:
    async def call_agent(self, agent_name, input_data, context=None):
        """Standardized agent-to-agent communication with tracing"""
        with tracer.start_as_current_span(f"a2a_call_{agent_name}"):
            return await self.agents[agent_name].run(input_data)
    
    def create_sequential_workflow(self, agent_names):
        """Chain agents in sequence"""
        return SequentialAgent(agents=[self.agents[n] for n in agent_names])
```

**3. Context Compaction** (`app/adk/context_compaction.py`):
```python
class ContextCompactor:
    async def compact_interview_history(self, interviews):
        """Summarize long interview history to fit token limits"""
        if len(formatted_history) > self.max_tokens * 4:
            # Use LLMAgent to summarize
            summary = await self.compaction_agent.run(formatted_history)
            return summary
        return formatted_history
```

**4. MCP Tools** (`app/adk/tools/`):
```python
@Tool(name="parse_cv", description="Parse CV into structured JSON")
async def cv_parser_tool(cv_text: str) -> dict:
    parser = LLMAgent(
        name="cv_parser",
        model=GeminiModel("gemini-pro"),
        instructions="Extract education, experience, projects, skills..."
    )
    return await parser.run(cv_text)
```

**5. Long-Running Operations** (`app/adk/long_running.py`):
```python
class LongRunningOperation:
    async def start_operation(self, operation_id, user_id, task_func, **kwargs):
        """Start pausable/resumable background task"""
        session = await self.session_service.create_session(...)
        session.state["status"] = "running"
        asyncio.create_task(self._run_task(session, task_func, kwargs))
```

### Agent Submission Requirements: 8/8 ✅

| Requirement | Implementation |
|------------|----------------|
| **Multi-Agent System** | 8 specialized agents + Sequential/Parallel/Loop workflows via A2AOrchestrator |
| **Tools** | MCP tools (@Tool decorator) + Built-in (SearchTool, CodeExecutionTool) |
| **Sessions & Memory** | InMemorySessionService + DatabaseSessionService with persistent state keys |
| **Context Engineering** | ContextCompactor with summarization, relevance filtering, sliding windows |
| **Observability** | Structlog (JSON logs) + OpenTelemetry (distributed tracing + span attributes) |
| **Agent Evaluation** | Multi-criteria evaluation (clarity, structure, depth, examples) + historical tracking |
| **A2A Protocol** | A2AOrchestrator with standardized call_agent() and workflow composition |
| **Deployment** | Docker + docker-compose + Vertex AI Agent Engine ready |

## If I Had More Time

**1. Complete Agent Migration to Pure ADK Pattern**  
While the infrastructure is Google ADK, some existing agents still use direct `google.generativeai` calls. I'd migrate all agents to use ADK's `LLMAgent` pattern exclusively for consistency and to leverage ADK's built-in features like automatic retries and structured output validation.

**2. Add OpenAPI Tool Integration**  
Integrate external APIs via OpenAPI specifications:
- LinkedIn API for automatic profile import and job recommendations
- Indeed/Glassdoor APIs for real-time job market data
- GitHub API for developers to import project portfolios
- Salary databases for compensation negotiation coaching

**3. Implement LLM-Driven Routing**  
Add dynamic workflow selection based on user intent:
```python
router_agent = LLMAgent(
    name="intent_router",
    instructions="Analyze user request and select optimal workflow..."
)
workflow = await router_agent.select_workflow(user_input)
```

**4. Enhanced Memory with Vector Database**  
Replace simple session state with semantic search:
- Store interview histories in vector database (Pinecone/Weaviate)
- Retrieve most relevant past performances for current context
- Enable  "find interviews where I struggled with system design" queries

**5. Real-Time Collaboration Features**  
Add multi-user capabilities:
- Peer mock interviews (two users practice together)
- Recruiter/coach access for reviewing candidate performance
- Team interview preparation for coordinated practice

**6. Deploy to Vertex AI Agent Engine**  
Move from Docker to Google Cloud's managed service:
- Auto-scaling based on demand
- Managed session storage with Cloud SQL
- Integration with Google Cloud Monitoring and Logging
- A/B testing different agent prompts and workflows

**7. Mobile App with Voice-First UX**  
Build native iOS/Android apps:
- Hands-free interview practice while commuting
- Push notifications for daily practice reminders
- Offline mode for question generation

**8. Advanced Analytics Dashboard**  
Provide candidates with deeper insights:
- Performance trends over time (line charts)
- Comparison against role benchmarks
- Predictive success scoring based on historical data
- Personalized study plans generated by coaching agent

**9. Integration with ATS Systems**  
Allow candidates to:
- Auto-apply to jobs with tailored resumes
- Track application status across platforms
- Get alerts when skills match new job postings

**10. Multi-Language Support**  
Expand beyond English:
- Interview practice in 20+ languages
- Culture-specific coaching (e.g., interview norms in Japan vs US)
- Translation between user language and job posting language
