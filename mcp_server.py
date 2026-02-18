#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                     Noor MCP Code Assistant Server                                   ║
║                                                                                      ║
║  Author: Noor Uddin                                                                  ║
║  Description: MCP Server bridge for Claude Desktop to access "Noor RAG Code Agent"   ║
║  GitHub: https://github.com/Nooruddin-dev                                            ║
║  Linkedin: https://www.linkedin.com/in/nooruddin-dev                                 ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import sys
import logging
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)

from config import config


# ============================================================================
# 📋 Logging Configuration (writes to stderr, NOT stdout)
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr  # CRITICAL: Use stderr, not stdout!
)
logger = logging.getLogger("noor-mcp")


# ============================================================================
# 🏗️ MCP Server Instance
# ============================================================================

server = Server("noor-code-assistant")


# ============================================================================
# 📋 Tool Definitions
# ============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    Define all available tools for Claude Desktop.
    Each tool maps to an API endpoint in the RAG system.
    """
    tools = [
        Tool(
            name="code_assistant",
            description="""
            Intelligent Code Assistant powered by RAG (Retrieval-Augmented Generation).

            Use this tool when you need to:
            - Generate C#/.NET code based on existing codebase patterns
            - Query information about project architecture and structure
            - Get code snippets that follow the project's conventions
            - Find existing methods, DTOs, services, or interfaces
            - Generate SQL queries for the project's database schema
            - Understand how specific features are implemented

            The tool has access to complete codebase context including:
            - ASP.NET Core 8 APIs and Controllers
            - PostgreSQL/SQL Server database schemas
            - Service interfaces and implementations
            - DTOs, Entities, and ViewModels
            - Repository patterns and data access layers
            - Clean Architecture project structures

            Returns detailed code examples with comprehensive explanations.
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": (
                            "Your code-related question or request. Be specific about what you need. "
                            "Examples: 'Create a C# function to get employee requests by ID', "
                            "'Show me how pagination is implemented in this project', "
                            "'Generate a DTO for the Employee table'"
                        )
                    },
                    "session_id": {
                        "type": "string",
                        "description": (
                            "Optional session ID for conversation continuity. "
                            "Use the same session_id to maintain context across multiple questions."
                        ),
                        "default": config.DEFAULT_SESSION_ID
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="universal_code_assistant",
            description="""
            Universal Code Assistant powered by RAG for ANY programming language.

            Use this tool when you need to:
            - Query any non-.NET codebase (Python, Java, React, Go, Rust, PHP, Ruby, C++, Flutter)
            - Understand project architecture and patterns for any language
            - Find existing functions, classes, components, or modules
            - Generate code following the project's conventions
            - Get code snippets with explanations

            The language/framework is configured on the server side via config.yaml.
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": (
                            "Your code-related question or request. Be specific about what you need. "
                            "Examples: 'How is authentication implemented?', "
                            "'Show me the main API routes', "
                            "'How is state management done in this project?'"
                        )
                    },
                    "session_id": {
                        "type": "string",
                        "description": (
                            "Optional session ID for conversation continuity. "
                            "Use the same session_id to maintain context across multiple questions."
                        ),
                        "default": config.DEFAULT_SESSION_ID
                    }
                },
                "required": ["message"]
            }
        ),
    ]
    
    # Filter based on config flags
    filtered_tools = []
    for tool in tools:
        if tool.name == "code_assistant" and not config.ENABLE_DOTNET_RAG:
            continue
        if tool.name == "universal_code_assistant" and not config.ENABLE_UNIVERSAL_RAG:
            continue
        filtered_tools.append(tool)
    
    return filtered_tools


# ============================================================================
# 🎯 Tool Execution Handler
# ============================================================================

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    """
    Handle tool execution requests from Claude Desktop.
    Routes to appropriate handler based on tool name.
    """
    
    logger.info(f"Tool called: {name}")  # This goes to stderr, safe!
    
    handlers = {}
    if config.ENABLE_DOTNET_RAG:
        handlers["code_assistant"] = handle_code_assistant
    if config.ENABLE_UNIVERSAL_RAG:
        handlers["universal_code_assistant"] = handle_universal_code_assistant
    
    handler = handlers.get(name)
    
    if handler is None:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Unknown tool: '{name}'. Available tools: {', '.join(handlers.keys())}"
            )],
            isError=True
        )
    
    try:
        return await handler(arguments)
    except Exception as e:
        logger.error(f"Error executing tool '{name}': {str(e)}")
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error executing tool '{name}': {str(e)}"
            )],
            isError=True
        )


# ============================================================================
# 🔧 Tool Handlers
# ============================================================================

async def handle_code_assistant(arguments: dict[str, Any]) -> CallToolResult:
    """
    Handle .NET code assistant requests by calling the RAG API.
    """
    message = arguments.get("message", "").strip()
    session_id = arguments.get("session_id", config.DEFAULT_SESSION_ID)
    
    # Validate input
    if not message:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="Please provide a message/question for the code assistant."
            )],
            isError=True
        )
    
    # Prepare request payload
    payload = {
        "session_id": session_id,
        "message": message
    }
    
    logger.info(f"Calling RAG API: {config.rag_chat_url}")
    
    try:
        async with httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT) as client:
            response = await client.post(
                config.rag_chat_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
        
        logger.info(f"RAG API response received, ok={data.get('ok')}")
        
        if not data.get("ok", False):
            error_msg = data.get("error") or data.get("message") or "Unknown error from RAG API"
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"RAG API Error: {error_msg}"
                )],
                isError=True
            )
        
        # Build response content
        result_parts = []
        
        # Main answer
        if data.get("answer"):
            result_parts.append(data["answer"])
        
        # SQL if present
        if data.get("sql"):
            result_parts.append(f"\n\n### Generated SQL\n```sql\n{data['sql']}\n```")
        
        # Markdown content if present
        if data.get("markdown"):
            result_parts.append(f"\n\n{data['markdown']}")
        
        # Clarification needed
        if data.get("needs_clarification"):
            result_parts.append(
                f"\n\n**Clarification Needed:** {data['needs_clarification']}"
            )
        
        # Metadata footer
        chunks_count = data.get("chunks_count", 0)
        if chunks_count > 0:
            result_parts.append(
                f"\n\n---\n*Context: {chunks_count} code chunks analyzed from your codebase*"
            )
        
        final_response = "\n".join(result_parts) if result_parts else "No response from code assistant."
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=final_response
            )]
        )
    
    except httpx.ConnectError:
        logger.error(f"Connection error to {config.rag_chat_url}")
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=(
                    f"Connection Error: Cannot reach RAG API at {config.rag_chat_url}\n\n"
                    f"Please ensure your Python RAG server is running:\n"
                    f"cd /path/to/your/rag-project\n"
                    f"source env_container/bin/activate\n"
                    f"uvicorn main:app --reload --port 8900"
                )
            )],
            isError=True
        )
    
    except httpx.TimeoutException:
        logger.error(f"Timeout after {config.REQUEST_TIMEOUT}s")
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=(
                    f"Request Timeout: The RAG API did not respond within {config.REQUEST_TIMEOUT} seconds.\n\n"
                    f"Try simplifying your question or increasing REQUEST_TIMEOUT in .env"
                )
            )],
            isError=True
        )
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code}")
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"HTTP Error {e.response.status_code}: {e.response.text}"
            )],
            isError=True
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Unexpected Error: {type(e).__name__}: {str(e)}"
            )],
            isError=True
        )


async def handle_universal_code_assistant(arguments: dict[str, Any]) -> CallToolResult:
    """
    Handle universal code assistant requests by calling the Universal RAG API.
    """
    message = arguments.get("message", "").strip()
    session_id = arguments.get("session_id", config.DEFAULT_SESSION_ID)
    
    if not message:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="Please provide a message/question for the universal code assistant."
            )],
            isError=True
        )
    
    payload = {
        "session_id": session_id,
        "message": message
    }
    
    logger.info(f"Calling Universal RAG API: {config.universal_rag_url}")
    
    try:
        async with httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT) as client:
            response = await client.post(
                config.universal_rag_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
        
        logger.info(f"Universal RAG API response received, ok={data.get('ok')}")
        
        if not data.get("ok", False):
            error_msg = data.get("error") or data.get("message") or "Unknown error from Universal RAG API"
            return CallToolResult(
                content=[TextContent(type="text", text=f"Universal RAG API Error: {error_msg}")],
                isError=True
            )
        
        result_parts = []
        
        if data.get("answer"):
            result_parts.append(data["answer"])
        
        if data.get("needs_clarification"):
            result_parts.append(f"\n\n**Clarification Needed:** {data['needs_clarification']}")
        
        # Metadata footer
        chunks_count = data.get("chunks_count", 0)
        language = data.get("language", "unknown")
        if chunks_count > 0:
            result_parts.append(
                f"\n\n---\n*Context: {chunks_count} code chunks analyzed ({language} codebase)*"
            )
        
        final_response = "\n".join(result_parts) if result_parts else "No response from universal code assistant."
        
        return CallToolResult(
            content=[TextContent(type="text", text=final_response)]
        )
    
    except httpx.ConnectError:
        logger.error(f"Connection error to {config.universal_rag_url}")
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=(
                    f"Connection Error: Cannot reach Universal RAG API at {config.universal_rag_url}\n\n"
                    f"Please ensure your Python RAG server is running:\n"
                    f"uvicorn main:app --reload --port 8900"
                )
            )],
            isError=True
        )
    
    except httpx.TimeoutException:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Request Timeout: The Universal RAG API did not respond within {config.REQUEST_TIMEOUT} seconds."
            )],
            isError=True
        )
    
    except httpx.HTTPStatusError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"HTTP Error {e.response.status_code}: {e.response.text}")],
            isError=True
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Unexpected Error: {type(e).__name__}: {str(e)}")],
            isError=True
        )


# ============================================================================
# 🚀 Main Entry Point
# ============================================================================

async def main():
    """Start the MCP server using stdio transport."""
    logger.info("Starting Noor MCP Code Assistant Server...")
    logger.info(f"RAG API URL (.NET): {config.rag_chat_url} ({'✅ Enabled' if config.ENABLE_DOTNET_RAG else '❌ Disabled'})")
    logger.info(f"RAG API URL (Universal): {config.universal_rag_url} ({'✅ Enabled' if config.ENABLE_UNIVERSAL_RAG else '❌ Disabled'})")
    logger.info(f"Request Timeout: {config.REQUEST_TIMEOUT}s")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())