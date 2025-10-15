# ADK Callbacks Reference

> Comprehensive reference for Google Agent Development Kit (ADK) Callbacks
> Source: https://google.github.io/adk-docs/callbacks/

## Table of Contents

- [Overview](#overview)
- [What are Callbacks?](#what-are-callbacks)
- [Callback Types](#callback-types)
- [Use Cases](#use-cases)
- [Callback Context](#callback-context)
- [Return Behavior](#return-behavior)
- [Best Practices](#best-practices)
- [Example Implementations](#example-implementations)

## Overview

Callbacks are functions that hook into an agent's execution process, allowing developers to observe, customize, and control agent behavior at specific points in the execution lifecycle. They provide granular control without modifying the core framework.

## What are Callbacks?

### Definition

Callbacks are functions that:
- Execute at specific points in agent execution
- Receive context about the current execution state
- Can observe, modify, or control behavior
- Integrate seamlessly with agent workflows

### Core Characteristics

- **Non-invasive**: Don't require modifying core agent code
- **Flexible**: Can be added/removed dynamically
- **Powerful**: Enable advanced customization
- **Context-aware**: Receive detailed execution information

### When to Use Callbacks

Use callbacks for:
- Debugging and logging
- Input/output validation
- Implementing guardrails
- Modifying agent behavior
- Triggering external actions
- Managing session state
- Monitoring and observability

## Callback Types

ADK provides six callback types that hook into different execution stages:

### 1. Before Agent Callback

Executes before an agent starts processing.

```python
def before_agent_callback(callback_context):
    """Called before agent execution begins.

    Args:
        callback_context: Context with agent and session info

    Returns:
        None to proceed normally, or custom response to override
    """
    agent_name = callback_context.agent.name
    print(f"Starting agent: {agent_name}")
    return None
```

**Use Cases**:
- Log agent invocation
- Validate prerequisites
- Check permissions
- Initialize resources

### 2. After Agent Callback

Executes after an agent completes processing.

```python
def after_agent_callback(callback_context, agent_response):
    """Called after agent execution completes.

    Args:
        callback_context: Context with agent and session info
        agent_response: The agent's response

    Returns:
        None to use original response, or modified response
    """
    agent_name = callback_context.agent.name
    print(f"Completed agent: {agent_name}")

    # Optionally modify response
    return agent_response
```

**Use Cases**:
- Log completion
- Validate output
- Add metadata
- Clean up resources

### 3. Before Model Callback

Executes before LLM is called.

```python
def before_model_callback(callback_context, llm_request):
    """Called before LLM inference.

    Args:
        callback_context: Context with execution details
        llm_request: The request that will be sent to LLM

    Returns:
        None to proceed, modified request, or LlmResponse to skip
    """
    # Inspect request
    messages = llm_request.messages

    # Modify system instruction
    if callback_context.agent.name == "sensitive_agent":
        llm_request.system_instruction += "\nBe extra careful with sensitive data."

    # Optionally block based on conditions
    if contains_blocked_content(messages):
        return create_blocked_response()

    return None
```

**Use Cases**:
- Content filtering
- Request modification
- Cost tracking
- Guardrails implementation
- Prompt injection prevention

### 4. After Model Callback

Executes after LLM responds.

```python
def after_model_callback(callback_context, llm_response):
    """Called after LLM generates response.

    Args:
        callback_context: Context with execution details
        llm_response: The LLM's response

    Returns:
        None to use original response, or modified response
    """
    # Log token usage
    print(f"Tokens used: {llm_response.token_count}")

    # Filter response content
    if contains_sensitive_data(llm_response.content):
        llm_response.content = redact_sensitive_data(llm_response.content)

    return llm_response
```

**Use Cases**:
- Response filtering
- Content moderation
- Token tracking
- Response validation
- PII redaction

### 5. Before Tool Callback

Executes before a tool is invoked.

```python
def before_tool_callback(callback_context, tool_call):
    """Called before tool execution.

    Args:
        callback_context: Context with execution details
        tool_call: The tool call request

    Returns:
        None to proceed, or ToolResult to skip execution
    """
    tool_name = tool_call.name
    tool_args = tool_call.args

    print(f"Calling tool: {tool_name} with args: {tool_args}")

    # Validate tool usage
    if not is_tool_allowed(tool_name, callback_context.session.user_id):
        return create_unauthorized_result()

    # Validate arguments
    if not validate_args(tool_name, tool_args):
        return create_invalid_args_result()

    return None
```

**Use Cases**:
- Tool authorization
- Argument validation
- Rate limiting
- Audit logging
- Cost control

### 6. After Tool Callback

Executes after a tool completes.

```python
def after_tool_callback(callback_context, tool_result):
    """Called after tool execution.

    Args:
        callback_context: Context with execution details
        tool_result: The tool's result

    Returns:
        None to use original result, or modified result
    """
    tool_name = callback_context.tool_name

    # Log result
    print(f"Tool {tool_name} completed")

    # Filter sensitive data from results
    if contains_sensitive_data(tool_result.data):
        tool_result.data = redact_sensitive_data(tool_result.data)

    return tool_result
```

**Use Cases**:
- Result filtering
- Error handling
- Result enrichment
- Performance tracking
- Data redaction

## Use Cases

### 1. Debugging and Logging

```python
def logging_before_agent(callback_context):
    """Log agent execution start."""
    logger.info(f"Agent started: {callback_context.agent.name}")
    logger.info(f"Session ID: {callback_context.session.id}")
    return None

def logging_after_agent(callback_context, agent_response):
    """Log agent execution completion."""
    logger.info(f"Agent completed: {callback_context.agent.name}")
    logger.info(f"Response length: {len(str(agent_response))}")
    return agent_response
```

### 2. Input Validation

```python
def validate_input(callback_context, llm_request):
    """Validate user input before processing."""
    user_message = get_last_user_message(llm_request.messages)

    # Check for prohibited patterns
    if contains_profanity(user_message):
        return create_error_response("Please use appropriate language")

    # Check message length
    if len(user_message) > 5000:
        return create_error_response("Message too long. Max 5000 characters.")

    return None
```

### 3. Implementing Guardrails

```python
def content_safety_guardrail(callback_context, llm_response):
    """Filter unsafe content from LLM responses."""
    content = llm_response.content

    # Check for harmful content
    safety_check = analyze_content_safety(content)

    if safety_check.is_harmful:
        # Replace with safe response
        llm_response.content = "I cannot provide that information."
        llm_response.metadata["blocked_reason"] = safety_check.reason

    return llm_response
```

### 4. Cost Tracking

```python
class CostTracker:
    def __init__(self):
        self.total_tokens = 0
        self.total_cost = 0.0

    def track_model_usage(self, callback_context, llm_response):
        """Track LLM usage and costs."""
        tokens = llm_response.token_count
        model = callback_context.agent.model

        cost = calculate_cost(model, tokens)

        self.total_tokens += tokens
        self.total_cost += cost

        # Log if threshold exceeded
        if self.total_cost > 10.0:
            logger.warning(f"Cost threshold exceeded: ${self.total_cost}")

        return llm_response

cost_tracker = CostTracker()
```

### 5. Authorization

```python
def tool_authorization(callback_context, tool_call):
    """Authorize tool usage based on user permissions."""
    user_id = callback_context.session.user_id
    tool_name = tool_call.name

    # Check permissions
    if not has_permission(user_id, tool_name):
        return ToolResult(
            success=False,
            error=f"User not authorized to use {tool_name}"
        )

    # Check rate limits
    if is_rate_limited(user_id, tool_name):
        return ToolResult(
            success=False,
            error="Rate limit exceeded. Please try again later."
        )

    return None
```

### 6. Session State Management

```python
def manage_session_state(callback_context):
    """Initialize or update session state."""
    state = callback_context.session.state

    # Initialize on first use
    if "initialized" not in state:
        state["initialized"] = True
        state["start_time"] = datetime.now()
        state["interaction_count"] = 0

    # Update interaction count
    state["interaction_count"] += 1

    return None
```

## Callback Context

The callback context provides access to execution details:

```python
callback_context.agent          # Current agent instance
callback_context.session        # Current session
callback_context.session.state  # Session state dictionary
callback_context.session.user_id # User identifier
callback_context.tool_name      # Tool being called (in tool callbacks)
```

### Accessing State

```python
def use_session_state(callback_context):
    """Access and modify session state."""
    state = callback_context.session.state

    # Read state
    user_preferences = state.get("preferences", {})

    # Modify state
    state["last_interaction"] = datetime.now().isoformat()
    state["interaction_count"] = state.get("interaction_count", 0) + 1

    return None
```

## Return Behavior

Callbacks control execution through their return values:

### Returning None

Proceed with normal execution:

```python
def normal_callback(callback_context):
    """Log and proceed normally."""
    print("Callback executed")
    return None  # Continue normal execution
```

### Returning Custom Response

Override default behavior:

```python
def override_model_callback(callback_context, llm_request):
    """Override LLM call for cached responses."""
    cache_key = generate_cache_key(llm_request)

    # Check cache
    if cache_key in response_cache:
        # Return cached response, skip LLM call
        return response_cache[cache_key]

    # Proceed with LLM call
    return None
```

### Modifying and Returning

Modify then return:

```python
def modify_response_callback(callback_context, llm_response):
    """Modify LLM response before returning."""
    # Add disclaimer
    llm_response.content += "\n\n*This response was generated by AI.*"

    # Return modified response
    return llm_response
```

## Best Practices

### 1. Keep Callbacks Focused

Each callback should have a single, clear purpose:

```python
# Good - Single purpose
def log_agent_start(callback_context):
    logger.info(f"Agent: {callback_context.agent.name}")
    return None

def validate_permissions(callback_context):
    if not has_permission(callback_context.session.user_id):
        raise PermissionError()
    return None

# Avoid - Multiple purposes
def do_everything(callback_context):
    logger.info("...")  # Logging
    validate_user()     # Validation
    track_cost()        # Tracking
    modify_state()      # State management
    return None
```

### 2. Handle Errors Gracefully

```python
def safe_callback(callback_context):
    """Handle errors without breaking agent execution."""
    try:
        # Callback logic
        perform_operation()
    except Exception as e:
        logger.error(f"Callback error: {e}")
        # Don't re-raise unless critical

    return None
```

### 3. Minimize Performance Impact

```python
# Good - Fast operation
def quick_callback(callback_context):
    logger.info("Quick log")
    return None

# Avoid - Slow operation
def slow_callback(callback_context):
    # Expensive operation
    result = complex_database_query()
    return None

# Better - Async if needed
async def async_callback(callback_context):
    # Non-blocking operation
    await async_operation()
    return None
```

### 4. Use Appropriate Callback Type

Choose the right callback for your use case:

```python
# Input validation → Before Model
def validate_input(callback_context, llm_request):
    pass

# Output filtering → After Model
def filter_output(callback_context, llm_response):
    pass

# Tool authorization → Before Tool
def authorize_tool(callback_context, tool_call):
    pass

# Result enrichment → After Tool
def enrich_result(callback_context, tool_result):
    pass
```

### 5. Document Callback Behavior

```python
def complex_callback(callback_context, llm_request):
    """Implement content safety guardrail.

    This callback:
    - Checks for prohibited content patterns
    - Validates against content policy
    - Blocks requests containing sensitive keywords
    - Logs all blocked requests for review

    Returns:
        None: If content is safe, proceed normally
        LlmResponse: If content is unsafe, return error message
    """
    # Implementation
    pass
```

## Example Implementations

### Complete Logging System

```python
class AgentLogger:
    """Comprehensive logging for agent execution."""

    def __init__(self, log_file: str):
        self.log_file = log_file
        self.logger = setup_logger(log_file)

    def before_agent(self, callback_context):
        """Log agent start."""
        self.logger.info(f"=== Agent Start: {callback_context.agent.name} ===")
        self.logger.info(f"Session: {callback_context.session.id}")
        return None

    def after_agent(self, callback_context, agent_response):
        """Log agent completion."""
        self.logger.info(f"=== Agent Complete: {callback_context.agent.name} ===")
        return agent_response

    def before_model(self, callback_context, llm_request):
        """Log LLM request."""
        self.logger.info("LLM Request:")
        self.logger.info(f"  Model: {callback_context.agent.model}")
        self.logger.info(f"  Messages: {len(llm_request.messages)}")
        return None

    def after_model(self, callback_context, llm_response):
        """Log LLM response."""
        self.logger.info("LLM Response:")
        self.logger.info(f"  Tokens: {llm_response.token_count}")
        self.logger.info(f"  Content length: {len(llm_response.content)}")
        return llm_response

    def before_tool(self, callback_context, tool_call):
        """Log tool invocation."""
        self.logger.info(f"Tool Call: {tool_call.name}")
        self.logger.info(f"  Args: {tool_call.args}")
        return None

    def after_tool(self, callback_context, tool_result):
        """Log tool result."""
        self.logger.info(f"Tool Result: {callback_context.tool_name}")
        self.logger.info(f"  Success: {tool_result.success}")
        return tool_result

# Usage
logger = AgentLogger("agent.log")

agent = LlmAgent(
    name="agent",
    model="gemini-2.0-flash",
    callbacks={
        "before_agent": logger.before_agent,
        "after_agent": logger.after_agent,
        "before_model": logger.before_model,
        "after_model": logger.after_model,
        "before_tool": logger.before_tool,
        "after_tool": logger.after_tool
    }
)
```

### Content Safety System

```python
class ContentSafetyGuardrail:
    """Multi-layer content safety system."""

    def __init__(self, policy_config: dict):
        self.policy = policy_config
        self.blocked_patterns = self._load_patterns()

    def _load_patterns(self):
        """Load blocked content patterns."""
        return [
            r"credit card \d{16}",
            r"ssn \d{3}-\d{2}-\d{4}",
            # ... more patterns
        ]

    def before_model_check(self, callback_context, llm_request):
        """Check input before LLM processing."""
        user_message = self._get_last_user_message(llm_request.messages)

        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, user_message, re.IGNORECASE):
                return self._create_blocked_response(
                    "Input contains prohibited content"
                )

        # Check for PII
        if self._contains_pii(user_message):
            return self._create_blocked_response(
                "Please remove personal information"
            )

        return None

    def after_model_check(self, callback_context, llm_response):
        """Check output after LLM generation."""
        content = llm_response.content

        # Redact any PII in response
        content = self._redact_pii(content)

        # Check safety categories
        safety_check = self._analyze_safety(content)

        if safety_check.is_unsafe:
            llm_response.content = "I cannot provide that information."
            llm_response.metadata["safety_blocked"] = True
        else:
            llm_response.content = content

        return llm_response

    def _contains_pii(self, text: str) -> bool:
        """Check for personally identifiable information."""
        # Implementation
        pass

    def _redact_pii(self, text: str) -> str:
        """Redact PII from text."""
        # Implementation
        pass

    def _analyze_safety(self, text: str):
        """Analyze content safety."""
        # Implementation
        pass

    def _create_blocked_response(self, reason: str):
        """Create response for blocked content."""
        return LlmResponse(
            content=f"Request blocked: {reason}",
            metadata={"blocked": True, "reason": reason}
        )

# Usage
safety = ContentSafetyGuardrail(policy_config)

agent = LlmAgent(
    name="safe_agent",
    model="gemini-2.0-flash",
    callbacks={
        "before_model": safety.before_model_check,
        "after_model": safety.after_model_check
    }
)
```

### Tool Authorization System

```python
class ToolAuthorizationSystem:
    """Manage tool permissions and rate limits."""

    def __init__(self, permissions_db):
        self.permissions_db = permissions_db
        self.rate_limiter = RateLimiter()

    def authorize_tool(self, callback_context, tool_call):
        """Authorize tool usage."""
        user_id = callback_context.session.user_id
        tool_name = tool_call.name

        # Check permissions
        if not self._has_permission(user_id, tool_name):
            return self._unauthorized_result(tool_name)

        # Check rate limit
        if not self.rate_limiter.allow(user_id, tool_name):
            return self._rate_limited_result(tool_name)

        # Validate arguments
        validation = self._validate_args(tool_name, tool_call.args)
        if not validation.valid:
            return self._invalid_args_result(validation.error)

        # Log usage
        self._log_tool_usage(user_id, tool_name, tool_call.args)

        return None

    def _has_permission(self, user_id: str, tool_name: str) -> bool:
        """Check if user has permission for tool."""
        user_perms = self.permissions_db.get_permissions(user_id)
        return tool_name in user_perms.allowed_tools

    def _unauthorized_result(self, tool_name: str):
        """Create unauthorized result."""
        return ToolResult(
            success=False,
            error=f"Not authorized to use {tool_name}",
            metadata={"error_type": "unauthorized"}
        )

    def _rate_limited_result(self, tool_name: str):
        """Create rate limited result."""
        return ToolResult(
            success=False,
            error=f"Rate limit exceeded for {tool_name}",
            metadata={"error_type": "rate_limited"}
        )

# Usage
auth_system = ToolAuthorizationSystem(permissions_db)

agent = LlmAgent(
    name="secured_agent",
    model="gemini-2.0-flash",
    tools=[sensitive_tool, dangerous_tool],
    callbacks={
        "before_tool": auth_system.authorize_tool
    }
)
```

## Callbacks vs Plugins

For comprehensive security policies, prefer **ADK Plugins** over callbacks:

- **Callbacks**: Good for simple, focused customizations
- **Plugins**: Better for complex, reusable security policies

## Summary Checklist

When implementing callbacks:

- [ ] Choose appropriate callback type
- [ ] Keep callbacks focused on single purpose
- [ ] Handle errors gracefully
- [ ] Minimize performance impact
- [ ] Document callback behavior
- [ ] Test callback thoroughly
- [ ] Consider using plugins for complex policies
- [ ] Log important operations
- [ ] Validate inputs and outputs
- [ ] Implement proper authorization

## Additional Resources

- **ADK Documentation**: https://google.github.io/adk-docs/
- **Callbacks Guide**: https://google.github.io/adk-docs/callbacks/
- **Plugins Documentation**: https://google.github.io/adk-docs/plugins/
- **API Reference**: https://google.github.io/adk-docs/api/

---

*Last Updated: 2025-10-15*
*ADK Version: 0.2.0+*
