# ADK Agents Reference

> Comprehensive reference for Google Agent Development Kit (ADK) Agents
> Source: https://google.github.io/adk-docs/agents/

## Table of Contents

- [Overview](#overview)
- [What is an Agent?](#what-is-an-agent)
- [Agent Types](#agent-types)
- [LLM Agents](#llm-agents)
- [Workflow Agents](#workflow-agents)
- [Custom Agents](#custom-agents)
- [Multi-Agent Systems](#multi-agent-systems)
- [Best Practices](#best-practices)
- [Example Implementations](#example-implementations)

## Overview

An Agent in ADK is a self-contained execution unit designed to act autonomously to achieve specific goals. Agents can perform tasks, interact with users, use external tools, and coordinate with other agents to accomplish complex objectives.

## What is an Agent?

### Definition

An agent is an autonomous program that:
- Acts independently to achieve goals
- Interacts with AI models for reasoning
- Uses available tools and context
- Makes autonomous decisions
- Can collaborate with other agents

### Core Characteristics

- **Autonomy**: Operates independently to achieve objectives
- **Goal-oriented**: Designed for specific tasks or outcomes
- **Tool-enabled**: Can use external capabilities
- **Contextual**: Maintains conversation history and state
- **Collaborative**: Works with other agents in multi-agent systems

### Base Class

All agents extend from the `BaseAgent` foundational class, which provides:
- Common interface for agent operations
- Session management capabilities
- Event handling mechanisms
- State management

## Agent Types

ADK provides three primary categories of agents:

### 1. LLM Agents

Utilize Large Language Models for intelligent reasoning.

**Classes**: `LlmAgent`, `Agent`

**Capabilities**:
- Natural language understanding
- Dynamic reasoning and planning
- Context-aware responses
- Dynamic tool selection
- Flexible, language-centric tasks

**Best for**:
- Conversational interfaces
- Complex problem-solving
- Tasks requiring interpretation
- Dynamic decision-making

### 2. Workflow Agents

Control execution flow with predefined patterns.

**Types**: `SequentialAgent`, `ParallelAgent`, `LoopAgent`

**Capabilities**:
- Deterministic execution
- Predictable flow control
- Sub-agent orchestration
- Structured process management

**Best for**:
- Multi-step workflows
- Coordinating multiple agents
- Reliable, repeatable processes
- Structured task execution

### 3. Custom Agents

Extend `BaseAgent` for specialized requirements.

**Capabilities**:
- Unique operational logic
- Specialized integrations
- Highly tailored functionality
- Domain-specific behaviors

**Best for**:
- Unique application requirements
- Specialized system integrations
- Custom execution patterns
- Domain-specific needs

## LLM Agents

LLM Agents leverage Large Language Models for intelligent, context-aware operations.

### Core Configuration

```python
from google.genai import LlmAgent

agent = LlmAgent(
    name="assistant",
    model="gemini-2.0-flash",
    description="Helpful assistant for customer support",
    instruction="You are a friendly customer support agent...",
    tools=[search_tool, order_lookup_tool]
)
```

### Essential Parameters

#### 1. Identity and Purpose

**name** (required)
- Unique identifier for the agent
- Used in multi-agent systems for routing
- Should be descriptive and memorable

```python
name="customer_support_agent"
```

**description** (optional)
- Summary of agent capabilities
- Helps in multi-agent coordination
- Used by orchestrator agents

```python
description="Handles customer inquiries about orders, shipping, and returns"
```

**model** (required)
- Specifies the underlying LLM
- Common options: `gemini-2.0-flash`, `gemini-1.5-pro`, `gemini-1.5-flash`

```python
model="gemini-2.0-flash"  # Fast, efficient
model="gemini-1.5-pro"    # More capable, higher quality
```

#### 2. Guidance and Behavior

**instruction** (critical parameter)
- Defines the agent's core task
- Sets personality and tone
- Establishes behavioral constraints
- Guides tool usage
- Specifies output format

```python
instruction="""
You are a helpful customer support agent for an e-commerce company.

Your responsibilities:
- Answer questions about orders, shipping, and returns
- Use the order_lookup tool to find order information
- Be polite, professional, and empathetic
- If you cannot help, escalate to a human agent

Guidelines:
- Always verify order ID before looking up information
- Protect customer privacy - never share full credit card numbers
- Provide clear, concise responses
- Use markdown formatting for better readability

Output format:
- Greet the customer
- Address their concern
- Provide relevant information
- Offer additional help if needed
"""
```

**Best Practices for Instructions**:
- Be clear and specific
- Use markdown for structure
- Provide examples for complex tasks
- Include constraints and limitations
- Specify when to use tools
- Define desired output format

#### 3. Capabilities

**tools** (optional)
- Provide external capabilities
- Extend beyond LLM's knowledge
- Enable actions in external systems

```python
tools=[
    search_products,
    lookup_order,
    calculate_shipping,
    other_agents  # Agents can be tools too
]
```

### Advanced Configuration

#### generate_content_config

Fine-tune LLM response generation:

```python
from google.genai import GenerateContentConfig

agent = LlmAgent(
    name="creative_writer",
    model="gemini-2.0-flash",
    generate_content_config=GenerateContentConfig(
        temperature=0.9,        # Higher = more creative
        top_p=0.95,            # Nucleus sampling
        top_k=40,              # Top-k sampling
        max_output_tokens=2048, # Response length limit
        stop_sequences=["END"] # Stop generation triggers
    )
)
```

**Parameters**:
- `temperature`: Controls randomness (0.0-2.0)
  - 0.0: Deterministic, focused
  - 1.0: Balanced
  - 2.0: Very creative, diverse
- `top_p`: Nucleus sampling threshold
- `top_k`: Number of top tokens to consider
- `max_output_tokens`: Maximum response length
- `stop_sequences`: Strings that stop generation

#### input_schema and output_schema

Define structured data expectations:

```python
from pydantic import BaseModel

class OrderQuery(BaseModel):
    order_id: str
    customer_email: str

class OrderResponse(BaseModel):
    status: str
    tracking_number: str
    estimated_delivery: str

agent = LlmAgent(
    name="order_agent",
    model="gemini-2.0-flash",
    input_schema=OrderQuery,
    output_schema=OrderResponse
)
```

**Benefits**:
- Type validation
- Structured input/output
- Better integration with systems
- Clearer agent contracts

#### include_contents

Control conversation history:

```python
agent = LlmAgent(
    name="agent",
    model="gemini-2.0-flash",
    include_contents=["user", "model", "tool"]  # What to include in context
)
```

**Options**:
- `"user"`: User messages
- `"model"`: Agent responses
- `"tool"`: Tool calls and responses
- `"system"`: System messages

#### planner

Enable multi-step reasoning:

```python
from google.genai import ReActPlanner

agent = LlmAgent(
    name="research_agent",
    model="gemini-2.0-flash",
    planner=ReActPlanner(
        max_iterations=5,
        reflection_enabled=True
    )
)
```

**Planner Types**:
- `ReActPlanner`: Reason + Act pattern
- Breaks complex tasks into steps
- Reflects on progress
- Adjusts strategy as needed

### Key Characteristics

**Non-deterministic**:
- Responses may vary
- Unpredictable tool selection
- Creative problem-solving

**Dynamic Decision-Making**:
- Adapts to context
- Chooses tools dynamically
- Reasons about approach

**Flexible**:
- Handles ambiguous inputs
- Interprets user intent
- Generates natural responses

## Workflow Agents

Workflow Agents orchestrate sub-agents with predefined execution patterns.

### Sequential Agent

Execute agents one after another in order.

#### Configuration

```python
from google.genai import SequentialAgent

workflow = SequentialAgent(
    name="sequential_workflow",
    agents=[agent1, agent2, agent3]
)
```

#### Use Cases

1. **Multi-step processing**:
```python
data_pipeline = SequentialAgent(
    name="data_pipeline",
    agents=[
        extract_agent,   # Extract data from source
        transform_agent, # Transform and clean data
        load_agent       # Load into database
    ]
)
```

2. **Approval workflows**:
```python
approval_flow = SequentialAgent(
    name="approval_workflow",
    agents=[
        validation_agent,  # Validate request
        review_agent,      # Review for compliance
        approval_agent     # Final approval
    ]
)
```

3. **Task decomposition**:
```python
research_workflow = SequentialAgent(
    name="research_task",
    agents=[
        planning_agent,    # Plan research approach
        gathering_agent,   # Gather information
        analysis_agent,    # Analyze findings
        summary_agent      # Summarize results
    ]
)
```

#### Characteristics

- **Predictable**: Always executes in same order
- **Sequential**: One agent completes before next starts
- **State passing**: Output of one agent flows to next
- **Error handling**: Can stop on failure or continue

### Parallel Agent

Execute multiple agents simultaneously.

#### Configuration

```python
from google.genai import ParallelAgent

workflow = ParallelAgent(
    name="parallel_workflow",
    agents=[agent1, agent2, agent3]
)
```

#### Use Cases

1. **Independent tasks**:
```python
data_collection = ParallelAgent(
    name="data_collection",
    agents=[
        weather_agent,    # Fetch weather data
        traffic_agent,    # Fetch traffic data
        news_agent        # Fetch news data
    ]
)
```

2. **Multiple perspectives**:
```python
analysis_team = ParallelAgent(
    name="multi_perspective_analysis",
    agents=[
        technical_analyst,  # Technical perspective
        business_analyst,   # Business perspective
        user_analyst        # User perspective
    ]
)
```

3. **Parallel processing**:
```python
batch_processor = ParallelAgent(
    name="batch_processing",
    agents=[
        processor_1,  # Process batch 1
        processor_2,  # Process batch 2
        processor_3   # Process batch 3
    ]
)
```

#### Characteristics

- **Concurrent**: All agents run simultaneously
- **Independent**: Agents don't depend on each other
- **Faster**: Reduces total execution time
- **Aggregation**: Combines results from all agents

### Loop Agent

Repeatedly execute agents until condition is met.

#### Configuration

```python
from google.genai import LoopAgent

workflow = LoopAgent(
    name="loop_workflow",
    agents=[processing_agent],
    max_iterations=10,
    termination_condition=lambda state: state.get("complete", False)
)
```

#### Use Cases

1. **Iterative refinement**:
```python
refinement_loop = LoopAgent(
    name="iterative_refinement",
    agents=[
        draft_agent,    # Create draft
        review_agent,   # Review quality
        improve_agent   # Improve based on feedback
    ],
    max_iterations=5,
    termination_condition=lambda state: state.get("quality_score", 0) >= 0.9
)
```

2. **Data processing**:
```python
batch_processor = LoopAgent(
    name="batch_processor",
    agents=[process_batch_agent],
    max_iterations=100,
    termination_condition=lambda state: state.get("remaining_items", 1) == 0
)
```

3. **Monitoring**:
```python
monitor_loop = LoopAgent(
    name="system_monitor",
    agents=[check_status_agent],
    max_iterations=1440,  # 24 hours worth
    termination_condition=lambda state: state.get("alert_triggered", False)
)
```

#### Characteristics

- **Iterative**: Repeats execution
- **Conditional**: Stops when condition met
- **Bounded**: Max iterations prevents infinite loops
- **Stateful**: Maintains state across iterations

### Workflow Agent Characteristics

**Common Features**:
- Deterministic execution patterns
- Predictable behavior
- Reliable process management
- Sub-agent orchestration

**Benefits**:
- Structured workflows
- Clear execution flow
- Easier debugging
- Reproducible results

## Custom Agents

Create specialized agents by extending `BaseAgent`.

### Basic Structure

```python
from google.genai import BaseAgent
from google.genai.types import Session, Event, EventList

class CustomAgent(BaseAgent):
    """Custom agent with specialized logic."""

    def __init__(self, name: str, custom_param: str):
        super().__init__(name=name)
        self.custom_param = custom_param

    async def run(
        self,
        session: Session,
        input_event: Event
    ) -> EventList:
        """Execute custom agent logic.

        Args:
            session: Current session context
            input_event: Input event to process

        Returns:
            List of output events
        """
        # Custom logic here
        result = self._custom_processing(input_event)

        # Return events
        return EventList(events=[
            Event(content=result, role="model")
        ])

    def _custom_processing(self, event: Event) -> str:
        """Custom processing logic."""
        # Implement specialized behavior
        return f"Processed with {self.custom_param}"
```

### Use Cases

1. **Database Integration Agent**:
```python
class DatabaseAgent(BaseAgent):
    """Agent that queries database directly."""

    def __init__(self, name: str, connection_string: str):
        super().__init__(name=name)
        self.db = connect_database(connection_string)

    async def run(self, session: Session, input_event: Event) -> EventList:
        query = extract_query(input_event)
        results = await self.db.query(query)
        return EventList(events=[
            Event(content=format_results(results), role="model")
        ])
```

2. **API Integration Agent**:
```python
class APIAgent(BaseAgent):
    """Agent that interacts with external API."""

    def __init__(self, name: str, api_key: str, endpoint: str):
        super().__init__(name=name)
        self.api_key = api_key
        self.endpoint = endpoint

    async def run(self, session: Session, input_event: Event) -> EventList:
        request = prepare_request(input_event)
        response = await call_api(
            endpoint=self.endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            data=request
        )
        return EventList(events=[
            Event(content=response.data, role="model")
        ])
```

3. **Rule-Based Agent**:
```python
class RuleBasedAgent(BaseAgent):
    """Agent with deterministic rule-based logic."""

    def __init__(self, name: str, rules: Dict[str, Callable]):
        super().__init__(name=name)
        self.rules = rules

    async def run(self, session: Session, input_event: Event) -> EventList:
        # Extract intent
        intent = classify_intent(input_event)

        # Apply matching rule
        if intent in self.rules:
            result = self.rules[intent](input_event, session)
        else:
            result = "No matching rule found"

        return EventList(events=[
            Event(content=result, role="model")
        ])
```

## Multi-Agent Systems

Combine different agent types for complex applications.

### Architecture Patterns

#### 1. Hierarchical Coordination

```python
# Coordinator agent with specialist sub-agents
coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.0-flash",
    instruction="Route tasks to appropriate specialist agents",
    tools=[
        research_specialist,
        data_analyst,
        code_generator
    ]
)
```

#### 2. Pipeline Processing

```python
# Sequential workflow with different agent types
pipeline = SequentialAgent(
    name="processing_pipeline",
    agents=[
        LlmAgent(name="extractor", ...),   # Extract information
        CustomAgent(name="validator", ...), # Validate data
        LlmAgent(name="enricher", ...),    # Enrich with context
        CustomAgent(name="loader", ...)     # Load to system
    ]
)
```

#### 3. Parallel Analysis

```python
# Parallel execution of specialist agents
analysis_team = ParallelAgent(
    name="analysis_team",
    agents=[
        LlmAgent(name="technical_analyst", ...),
        LlmAgent(name="business_analyst", ...),
        LlmAgent(name="risk_analyst", ...)
    ]
)

# Synthesizer combines results
synthesizer = LlmAgent(
    name="synthesizer",
    model="gemini-2.0-flash",
    instruction="Synthesize insights from multiple analyses"
)

# Overall workflow
workflow = SequentialAgent(
    name="complete_analysis",
    agents=[analysis_team, synthesizer]
)
```

#### 4. Iterative Improvement

```python
# Loop for iterative refinement
refinement = LoopAgent(
    name="iterative_refinement",
    agents=[
        LlmAgent(name="generator", ...),
        LlmAgent(name="critic", ...),
        LlmAgent(name="improver", ...)
    ],
    max_iterations=5,
    termination_condition=lambda s: s.get("quality", 0) >= 0.9
)
```

### Best Practices for Multi-Agent Systems

1. **Clear Responsibilities**: Each agent has specific role
2. **Minimal Overlap**: Avoid duplicate capabilities
3. **Efficient Communication**: Pass only necessary data
4. **Error Handling**: Handle failures gracefully
5. **Monitoring**: Track performance of each agent
6. **Modularity**: Keep agents independent and reusable

## Best Practices

### Agent Selection

Choose agent type based on requirements:

| Requirement | Agent Type | Reason |
|------------|------------|--------|
| Natural language understanding | LLM Agent | Language comprehension |
| Deterministic flow | Workflow Agent | Predictable execution |
| Complex reasoning | LLM Agent | Dynamic decision-making |
| Multi-step process | Sequential Agent | Ordered execution |
| Parallel tasks | Parallel Agent | Concurrent processing |
| Iterative refinement | Loop Agent | Repeated execution |
| Specialized integration | Custom Agent | Tailored logic |

### Configuration Guidelines

1. **Name**: Use descriptive, unique identifiers
2. **Description**: Summarize capabilities clearly
3. **Model**: Choose based on task complexity
4. **Instruction**: Be specific and comprehensive
5. **Tools**: Provide only necessary tools
6. **Validation**: Test with edge cases

### Instruction Writing

**Structure**:
```markdown
# Role and Context
You are a [role] for [domain].

# Responsibilities
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]

# Guidelines
- [Guideline 1]
- [Guideline 2]

# Tool Usage
- Use [tool] when [condition]
- Avoid [tool] for [situation]

# Output Format
[Describe expected output structure]

# Constraints
- [Constraint 1]
- [Constraint 2]
```

**Tips**:
- Use markdown for readability
- Provide examples for complex tasks
- Specify when to use each tool
- Define success criteria
- Include error handling guidance

### Testing

1. **Unit Testing**: Test individual agents
2. **Integration Testing**: Test agent interactions
3. **Edge Cases**: Test unusual inputs
4. **Performance**: Monitor response times
5. **Evaluation**: Use ADK's built-in evaluation tools

## Example Implementations

### Basic LLM Agent

```python
from google.genai import LlmAgent

agent = LlmAgent(
    name="helpful_assistant",
    model="gemini-2.0-flash",
    description="General-purpose helpful assistant",
    instruction="""
    You are a helpful assistant that answers questions accurately and concisely.

    Guidelines:
    - Provide clear, accurate information
    - If uncertain, say so
    - Use examples when helpful
    - Be friendly and professional
    """
)
```

### LLM Agent with Tools

```python
from google.genai import LlmAgent

def search_web(query: str) -> dict:
    """Search the web for information."""
    return {"results": [...]}

def calculate(expression: str) -> dict:
    """Evaluate mathematical expression."""
    return {"result": eval(expression)}

agent = LlmAgent(
    name="research_assistant",
    model="gemini-2.0-flash",
    instruction="""
    You are a research assistant that helps find and analyze information.

    Use search_web to find current information on the internet.
    Use calculate for mathematical computations.

    Always cite sources and verify information.
    """,
    tools=[search_web, calculate]
)
```

### Sequential Workflow

```python
from google.genai import LlmAgent, SequentialAgent

# Define specialist agents
planner = LlmAgent(
    name="planner",
    model="gemini-2.0-flash",
    instruction="Create a detailed plan for the task"
)

executor = LlmAgent(
    name="executor",
    model="gemini-2.0-flash",
    instruction="Execute the plan step by step"
)

reviewer = LlmAgent(
    name="reviewer",
    model="gemini-2.0-flash",
    instruction="Review the execution and provide feedback"
)

# Create workflow
workflow = SequentialAgent(
    name="complete_workflow",
    agents=[planner, executor, reviewer]
)
```

### Parallel Analysis

```python
from google.genai import LlmAgent, ParallelAgent, SequentialAgent

# Parallel analysts
analysts = ParallelAgent(
    name="analysts",
    agents=[
        LlmAgent(
            name="technical",
            model="gemini-2.0-flash",
            instruction="Analyze from technical perspective"
        ),
        LlmAgent(
            name="business",
            model="gemini-2.0-flash",
            instruction="Analyze from business perspective"
        ),
        LlmAgent(
            name="user",
            model="gemini-2.0-flash",
            instruction="Analyze from user perspective"
        )
    ]
)

# Synthesizer
synthesizer = LlmAgent(
    name="synthesizer",
    model="gemini-2.0-flash",
    instruction="Combine all perspectives into comprehensive analysis"
)

# Complete workflow
analysis_workflow = SequentialAgent(
    name="multi_perspective_analysis",
    agents=[analysts, synthesizer]
)
```

### Loop with Refinement

```python
from google.genai import LlmAgent, LoopAgent

# Iterative refinement
refinement_loop = LoopAgent(
    name="refinement",
    agents=[
        LlmAgent(
            name="generator",
            model="gemini-2.0-flash",
            instruction="Generate content based on requirements"
        ),
        LlmAgent(
            name="critic",
            model="gemini-2.0-flash",
            instruction="Evaluate quality and suggest improvements"
        ),
        LlmAgent(
            name="improver",
            model="gemini-2.0-flash",
            instruction="Improve content based on feedback"
        )
    ],
    max_iterations=5,
    termination_condition=lambda state: state.get("quality_score", 0) >= 0.9
)
```

### Custom Integration Agent

```python
from google.genai import BaseAgent
from google.genai.types import Session, Event, EventList
import requests

class WeatherAgent(BaseAgent):
    """Custom agent that fetches weather data."""

    def __init__(self, name: str, api_key: str):
        super().__init__(name=name)
        self.api_key = api_key
        self.base_url = "https://api.weather.com"

    async def run(
        self,
        session: Session,
        input_event: Event
    ) -> EventList:
        """Fetch weather for requested location."""

        # Extract location from input
        location = self._extract_location(input_event.content)

        # Call weather API
        response = requests.get(
            f"{self.base_url}/current",
            params={"location": location, "apikey": self.api_key}
        )
        weather_data = response.json()

        # Format response
        result = f"""
        Weather for {location}:
        Temperature: {weather_data['temp']}°F
        Conditions: {weather_data['conditions']}
        Humidity: {weather_data['humidity']}%
        """

        return EventList(events=[
            Event(content=result, role="model")
        ])

    def _extract_location(self, content: str) -> str:
        """Extract location from user message."""
        # Simple extraction logic
        return content.split("in")[-1].strip()
```

## Summary Checklist

When creating agents, ensure:

- [ ] Choose appropriate agent type for task
- [ ] Use descriptive, unique name
- [ ] Provide clear description
- [ ] Select appropriate model
- [ ] Write comprehensive instructions
- [ ] Provide necessary tools only
- [ ] Configure generation parameters
- [ ] Test with various inputs
- [ ] Handle errors gracefully
- [ ] Monitor performance
- [ ] Document usage and limitations

## Additional Resources

- **ADK Documentation**: https://google.github.io/adk-docs/
- **Agent Examples**: https://google.github.io/adk-docs/agents/examples/
- **API Reference**: https://google.github.io/adk-docs/api/
- **GitHub Repository**: https://github.com/google/adk
- **Codelabs**: https://google.github.io/adk-docs/codelabs/

---

*Last Updated: 2025-10-15*
*ADK Version: 0.2.0+*
