# ADK Tools Reference

> Comprehensive reference for Google Agent Development Kit (ADK) Tools
> Source: https://google.github.io/adk-docs/tools/

## Table of Contents

- [Overview](#overview)
- [What is a Tool?](#what-is-a-tool)
- [Tool Types](#tool-types)
- [Tool Usage Process](#tool-usage-process)
- [Best Practices](#best-practices)
- [ToolContext](#toolcontext)
- [Toolsets](#toolsets)
- [Example Implementations](#example-implementations)

## Overview

Tools in ADK represent specific capabilities provided to an AI agent, enabling it to perform actions beyond basic text generation. Tools are modular code components that extend agent capabilities and execute developer-defined logic.

## What is a Tool?

### Definition

A tool is a specific capability that enables an agent to:
- Perform actions beyond text generation
- Interact with external systems
- Execute predefined tasks
- Access real-time information

### Key Characteristics

- **Action-oriented**: Performs specific actions (e.g., querying databases, making API requests)
- **Extends capabilities**: Allows agents to interact with external systems and data
- **Executes predefined logic**: Runs developer-defined code without independent reasoning
- **LLM-driven selection**: The agent's LLM decides which tool to use and when

### Why Tools Matter

Tools overcome the knowledge limitations of an agent's training data by:
- Providing access to current, real-time information
- Enabling interaction with external APIs and services
- Performing computations and code execution
- Retrieving information from specialized data sources

## Tool Types

### 1. Function Tools

Custom functions tailored to specific application needs.

**Types of Function Tools:**
- **Synchronous functions**: Standard Python functions that return immediately
- **Agents-as-tools**: Use specialized agents as tools for parent agents
- **Long-running function tools**: For asynchronous or time-consuming operations

### 2. Built-in Tools

Ready-to-use tools for common tasks:
- **Google Search**: Web search capabilities
- **Code Execution**: Execute code snippets
- **RAG (Retrieval-Augmented Generation)**: Document retrieval and context
- **BigQuery**: Database queries
- **Vertex AI Search**: Advanced search functionality
- **Spanner**: Cloud database access

### 3. Third-Party Tools

Integration with external libraries:
- **LangChain Tools**: Leverage LangChain ecosystem
- **CrewAI Tools**: Integration with CrewAI framework
- **OpenAPI Tools**: REST API integration via OpenAPI specs
- **MCP Tools**: Model Context Protocol standardized tools

## Tool Usage Process

The agent follows this workflow when using tools:

```
1. LLM Analyzes Context
   ↓
2. Selects Appropriate Tool
   ↓
3. Generates Tool Arguments
   ↓
4. Executes Tool
   ↓
5. Incorporates Output into Reasoning
```

### Function Calling Mechanism

Agents utilize tools dynamically through function calling:
1. **Reasoning**: LLM evaluates available tools and current context
2. **Selection**: Chooses the most appropriate tool
3. **Invocation**: Calls the tool with generated arguments
4. **Observation**: Processes tool output
5. **Integration**: Incorporates results into response

## Best Practices

### 1. Naming Conventions

Use descriptive, verb-noun function names:

```python
# Good
def lookup_order_status(order_id: str) -> dict:
    pass

def calculate_shipping_cost(weight: float, destination: str) -> dict:
    pass

# Avoid
def get_data(id: str) -> dict:
    pass

def process(input: str) -> dict:
    pass
```

### 2. Type Hints

Provide clear type annotations:

```python
from typing import Dict, List, Optional

def search_products(
    query: str,
    category: Optional[str] = None,
    max_results: int = 10
) -> Dict[str, List[Dict]]:
    """Search products with optional filters."""
    pass
```

### 3. Return Values

Return dictionaries with meaningful keys:

```python
def lookup_order_status(order_id: str) -> dict:
    """Fetches the current status of a customer's order.

    Args:
        order_id: The unique identifier for the order

    Returns:
        Dictionary containing:
        - status: Current order status (pending, shipped, delivered)
        - tracking_number: Shipping tracking number (if available)
        - estimated_delivery: Expected delivery date
        - items: List of items in the order
    """
    return {
        "status": "shipped",
        "tracking_number": "1Z999AA10123456784",
        "estimated_delivery": "2025-10-18",
        "items": [...]
    }
```

### 4. Documentation

Include comprehensive docstrings:

```python
def lookup_order_status(order_id: str) -> dict:
    """Fetches the current status of a customer's order using its ID.

    Use this tool ONLY when a user explicitly asks for order status.
    Do not use this tool for order creation or modification.

    Args:
        order_id: The unique order identifier (format: ORD-XXXXXX)

    Returns:
        Dictionary with order status details including:
        - status: Order status string
        - tracking_number: Tracking ID if shipped
        - estimated_delivery: Expected delivery date

    Raises:
        ValueError: If order_id format is invalid
        NotFoundError: If order does not exist

    Example:
        >>> lookup_order_status("ORD-123456")
        {'status': 'shipped', 'tracking_number': '...', ...}
    """
    # Implementation
    pass
```

### 5. Single Responsibility

Keep tools focused on one task:

```python
# Good - Single responsibility
def get_order_status(order_id: str) -> dict:
    """Get order status only."""
    pass

def cancel_order(order_id: str) -> dict:
    """Cancel order only."""
    pass

# Avoid - Multiple responsibilities
def manage_order(order_id: str, action: str) -> dict:
    """Handles all order operations."""
    pass
```

### 6. Simple Data Types

Use simple, serializable data types:

```python
# Good - Simple types
def calculate_total(items: List[Dict[str, Any]]) -> Dict[str, float]:
    return {
        "subtotal": 100.0,
        "tax": 8.0,
        "total": 108.0
    }

# Avoid - Complex custom objects
def calculate_total(cart: ShoppingCart) -> OrderTotal:
    return OrderTotal(...)
```

## ToolContext

ToolContext provides advanced capabilities for accessing agent state and services.

### Available Context

```python
from google.genai import ToolContext

def advanced_tool(context: ToolContext, query: str) -> dict:
    """Tool with access to context."""

    # Session state management
    user_preferences = context.state.get("preferences", {})
    context.state["last_query"] = query

    # Event actions control
    context.event_actions.pause()
    context.event_actions.resume()

    # Authentication responses
    auth_data = context.auth_response

    # Artifact and memory services
    artifacts = context.artifact_service
    memory = context.memory_service

    return {"result": "processed"}
```

### Common Use Cases

1. **State Management**: Store and retrieve session-specific data
2. **Event Control**: Pause/resume agent execution
3. **Authentication**: Access user authentication details
4. **Artifacts**: Manage files and binary data
5. **Memory**: Access long-term memory across sessions

## Toolsets

Toolsets group related tools and enable dynamic tool availability.

### Creating a Toolset

```python
from google.genai import BaseToolset

class OrderManagementToolset(BaseToolset):
    """Toolset for order-related operations."""

    def get_tools(self) -> List[Callable]:
        """Return available tools in this toolset."""
        return [
            self.lookup_order_status,
            self.cancel_order,
            self.update_shipping_address
        ]

    def lookup_order_status(self, order_id: str) -> dict:
        """Get order status."""
        pass

    def cancel_order(self, order_id: str) -> dict:
        """Cancel an order."""
        pass

    def update_shipping_address(
        self,
        order_id: str,
        new_address: str
    ) -> dict:
        """Update shipping address."""
        pass
```

### Benefits of Toolsets

- **Organization**: Group related tools logically
- **Reusability**: Share toolsets across agents
- **Dynamic availability**: Enable/disable tools based on context
- **Maintainability**: Manage related functionality together

## Example Implementations

### Basic Function Tool

```python
def get_weather(location: str, units: str = "celsius") -> dict:
    """Get current weather for a location.

    Args:
        location: City name or zip code
        units: Temperature units (celsius or fahrenheit)

    Returns:
        Weather data including temperature, conditions, humidity
    """
    # Implementation
    return {
        "location": location,
        "temperature": 22,
        "units": units,
        "conditions": "sunny",
        "humidity": 65
    }
```

### Tool with Context

```python
from google.genai import ToolContext

def personalized_search(
    context: ToolContext,
    query: str
) -> dict:
    """Search with user preferences from state.

    Args:
        context: Tool context with state access
        query: Search query string

    Returns:
        Search results filtered by user preferences
    """
    # Get user preferences from state
    preferences = context.state.get("preferences", {})
    language = preferences.get("language", "en")
    safe_search = preferences.get("safe_search", True)

    # Perform search with preferences
    results = perform_search(query, language, safe_search)

    # Store query in state
    context.state["last_search"] = query

    return {
        "query": query,
        "results": results,
        "result_count": len(results)
    }
```

### Agent as Tool

```python
from google.genai import Agent, LlmAgent

# Create specialist agent
research_agent = LlmAgent(
    name="research_specialist",
    model="gemini-2.0-flash",
    description="Specialist in web research and information gathering"
)

# Use as tool in parent agent
parent_agent = LlmAgent(
    name="coordinator",
    model="gemini-2.0-flash",
    tools=[research_agent]  # Agent as tool
)
```

### Long-Running Tool

```python
import asyncio

async def analyze_large_dataset(
    dataset_url: str,
    analysis_type: str
) -> dict:
    """Analyze large dataset asynchronously.

    Args:
        dataset_url: URL to dataset file
        analysis_type: Type of analysis to perform

    Returns:
        Analysis results
    """
    # Download dataset
    data = await download_dataset(dataset_url)

    # Perform analysis (long-running)
    results = await run_analysis(data, analysis_type)

    return {
        "analysis_type": analysis_type,
        "summary": results.summary,
        "details": results.details
    }
```

### Complete Toolset Example

```python
from google.genai import BaseToolset, ToolContext
from typing import List, Callable, Dict

class EcommerceToolset(BaseToolset):
    """Comprehensive e-commerce operations toolset."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_tools(self) -> List[Callable]:
        return [
            self.search_products,
            self.get_product_details,
            self.check_inventory,
            self.calculate_shipping
        ]

    def search_products(
        self,
        query: str,
        category: str = None
    ) -> Dict:
        """Search products by query and optional category."""
        return {
            "query": query,
            "category": category,
            "results": []
        }

    def get_product_details(self, product_id: str) -> Dict:
        """Get detailed information for a product."""
        return {
            "product_id": product_id,
            "name": "",
            "price": 0.0,
            "description": ""
        }

    def check_inventory(
        self,
        product_id: str,
        location: str = None
    ) -> Dict:
        """Check product inventory levels."""
        return {
            "product_id": product_id,
            "in_stock": True,
            "quantity": 0
        }

    def calculate_shipping(
        self,
        weight: float,
        destination: str
    ) -> Dict:
        """Calculate shipping cost for order."""
        return {
            "weight": weight,
            "destination": destination,
            "cost": 0.0,
            "estimated_days": 0
        }
```

## Summary Checklist

When creating tools, ensure:

- [ ] Descriptive verb-noun function names
- [ ] Clear type hints for all parameters
- [ ] Dictionary return values with meaningful keys
- [ ] Comprehensive docstrings explaining usage
- [ ] Single responsibility per tool
- [ ] Simple, serializable data types
- [ ] Error handling for edge cases
- [ ] Examples in documentation
- [ ] Consider using ToolContext when needed
- [ ] Group related tools in Toolsets

## Additional Resources

- **ADK Documentation**: https://google.github.io/adk-docs/
- **Tool Examples**: https://google.github.io/adk-docs/tools/examples/
- **API Reference**: https://google.github.io/adk-docs/api/
- **GitHub Repository**: https://github.com/google/adk

---

*Last Updated: 2025-10-15*
*ADK Version: 0.2.0+*
