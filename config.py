#!/usr/bin/env python3
"""
Configuration management for Noor MCP Code Assistant.
Loads settings from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    🔧 Central configuration for the MCP Code Assistant.
    All settings can be overridden via environment variables.
    """
    
    # ─────────────────────────────────────────────────────────────────────────
    # 🌐 RAG API Settings
    # ─────────────────────────────────────────────────────────────────────────
    
    RAG_API_BASE_URL: str = os.getenv("RAG_API_BASE_URL", "http://localhost:8900")
    RAG_CHAT_ENDPOINT: str = os.getenv("RAG_CHAT_ENDPOINT", "/api/chat/rag")
    UNIVERSAL_RAG_ENDPOINT: str = os.getenv("UNIVERSAL_RAG_ENDPOINT", "/api/chat/universal")
    
    
    @property
    def rag_chat_url(self) -> str:
        """Full URL for RAG chat endpoint."""
        return f"{self.RAG_API_BASE_URL}{self.RAG_CHAT_ENDPOINT}"
    
    @property
    def universal_rag_url(self) -> str:
        """Full URL for Universal RAG chat endpoint."""
        return f"{self.RAG_API_BASE_URL}{self.UNIVERSAL_RAG_ENDPOINT}"
    
    # ─────────────────────────────────────────────────────────────────────────
    # ⚙️ General Settings
    # ─────────────────────────────────────────────────────────────────────────
    
    DEFAULT_SESSION_ID: str = os.getenv("DEFAULT_SESSION_ID", "claude-desktop-session")
    REQUEST_TIMEOUT: float = float(os.getenv("REQUEST_TIMEOUT", "120"))
    ENABLE_DOTNET_RAG: bool = os.getenv("ENABLE_DOTNET_RAG", "true").lower() == "true"
    ENABLE_UNIVERSAL_RAG: bool = os.getenv("ENABLE_UNIVERSAL_RAG", "true").lower() == "true"
    
    # ─────────────────────────────────────────────────────────────────────────
    # 🔮 Future Agent Endpoints (Add as needed)
    # ─────────────────────────────────────────────────────────────────────────
    
    SQL_AGENT_ENDPOINT: str = os.getenv("SQL_AGENT_ENDPOINT", "/api/sql/agent")
    REACT_AGENT_ENDPOINT: str = os.getenv("REACT_AGENT_ENDPOINT", "/api/react/agent")
    JAVA_AGENT_ENDPOINT: str = os.getenv("JAVA_AGENT_ENDPOINT", "/api/java/agent")
    
    @property
    def sql_agent_url(self) -> str:
        """Full URL for SQL agent endpoint."""
        return f"{self.RAG_API_BASE_URL}{self.SQL_AGENT_ENDPOINT}"
    
    @property
    def react_agent_url(self) -> str:
        """Full URL for React agent endpoint."""
        return f"{self.RAG_API_BASE_URL}{self.REACT_AGENT_ENDPOINT}"
    
    @property
    def java_agent_url(self) -> str:
        """Full URL for Java agent endpoint."""
        return f"{self.RAG_API_BASE_URL}{self.JAVA_AGENT_ENDPOINT}"


# Global config instance
config = Config()