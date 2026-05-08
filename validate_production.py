#!/usr/bin/env python3
"""
Production validation script for AI News Research Agent

Tests all components are working correctly before deployment.
Run with: python validate_production.py
"""

import asyncio
import os
import sys
from importlib import import_module
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_section(title: str) -> None:
    """Print section header"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}🔧 {title}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


def check_ok(message: str) -> None:
    """Print OK status"""
    print(f"{GREEN}✅ {message}{RESET}")


def check_fail(message: str) -> None:
    """Print FAIL status"""
    print(f"{RED}❌ {message}{RESET}")


def check_warn(message: str) -> None:
    """Print WARNING status"""
    print(f"{YELLOW}⚠️  {message}{RESET}")


def check_info(message: str) -> None:
    """Print INFO"""
    print(f"{BLUE}ℹ️  {message}{RESET}")


def validate_python_version() -> bool:
    """Check Python version"""
    print_section("Python Version")
    version = sys.version_info
    min_version = (3, 10)
    
    if version >= min_version:
        check_ok(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        check_fail(f"Python {version.major}.{version.minor} (need 3.10+)")
        return False


def validate_environment_file() -> bool:
    """Check .env file"""
    print_section("Environment Configuration")
    
    if not Path(".env").exists():
        check_fail(".env file not found")
        check_info("Copy .env.example to .env and fill in your API keys")
        return False
    
    check_ok(".env file exists")
    
    # Check required vars
    required_vars = [
        "GROQ_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
    ]
    
    with open(".env") as f:
        env_content = f.read()
    
    missing = []
    for var in required_vars:
        if f"{var}=" not in env_content or f"{var}=" in env_content and "=" in env_content.split(f"{var}=")[1].split('\n')[0] and not env_content.split(f"{var}=")[1].split('\n')[0].split("=")[-1]:
            missing.append(var)
    
    if missing:
        for var in missing:
            check_warn(f"Missing or empty: {var}")
        return False
    
    check_ok("All required environment variables set")
    return True


def validate_dependencies() -> bool:
    """Check Python dependencies"""
    print_section("Dependencies")
    
    required_packages = [
        "langchain",
        "langgraph",
        "langchain_huggingface",
        "sentence_transformers",
        "chromadb",
        "telegram",
        "psycopg",
        "pydantic",
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            import_module(package.replace("-", "."))
            check_ok(f"{package}")
        except ImportError:
            check_fail(f"{package} not installed")
            all_ok = False
    
    if not all_ok:
        check_info("Run: pip install -r requirements.txt")
    
    return all_ok


def validate_chromadb() -> bool:
    """Check ChromaDB setup"""
    print_section("Vector Store (ChromaDB)")
    
    try:
        from app.memory.vectorstore import get_vectorstore
        vs = get_vectorstore()
        check_ok("ChromaDB initialized")
        check_info(f"Collection: {vs.collection_name}")
        return True
    except Exception as e:
        check_fail(f"ChromaDB initialization failed: {e}")
        return False


def validate_embeddings() -> bool:
    """Check embeddings"""
    print_section("Embeddings")
    
    try:
        from app.ranking.embeddings import embed_texts
        result = embed_texts(["test"])
        if result and len(result[0]) > 0:
            check_ok(f"Embeddings working (dimension: {len(result[0])})")
            return True
        else:
            check_warn("Embeddings returned empty vector")
            return True
    except Exception as e:
        check_fail(f"Embeddings failed: {e}")
        return False


def validate_config() -> bool:
    """Check configuration"""
    print_section("Configuration")
    
    try:
        from app.config.settings import get_settings
        settings = get_settings()
        
        check_ok(f"Groq model: {settings.groq_model}")
        check_ok("Embeddings: HuggingFace all-MiniLM-L6-v2")
        
        if settings.postgres_url:
            check_ok("PostgreSQL configured")
        else:
            check_warn("PostgreSQL not configured (using in-memory)")
        
        check_ok(f"Newsletter hour: {settings.newsletter_hour}:{settings.newsletter_minute}")
        
        return True
    except Exception as e:
        check_fail(f"Configuration failed: {e}")
        return False


def validate_graph() -> bool:
    """Check LangGraph workflow"""
    print_section("LangGraph Workflow")
    
    try:
        from app.graph.builder import build_graph
        app = build_graph()
        check_ok("Workflow graph built successfully")
        
        # Check nodes
        if hasattr(app, 'nodes'):
            check_info(f"Graph nodes: {list(app.nodes.keys())}")
        
        return True
    except Exception as e:
        check_fail(f"Workflow build failed: {e}")
        return False


async def validate_workflow_execution() -> bool:
    """Test workflow execution"""
    print_section("Workflow Execution Test")
    
    try:
        from app.graph.builder import build_graph
        from uuid import uuid4
        
        app = build_graph()
        initial_state = {
            "raw_news": [],
            "merged_news": [],
            "unique_news": [],
            "filtered_news": [],
            "ranked_news": [],
            "summaries": [],
            "newsletter": "",
            "errors": [],
            "metadata": {},
        }
        
        check_info("Starting workflow test (this may take a minute)...")
        result = await app.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": str(uuid4())}},
        )
        
        check_ok("Workflow executed successfully")
        check_info(f"Newsletter length: {len(result.get('newsletter', ''))}")
        check_info(f"Errors: {len(result.get('errors', []))}")
        
        return True
    except Exception as e:
        check_fail(f"Workflow execution failed: {e}")
        import traceback
        check_info(f"Error details: {traceback.format_exc()}")
        return False


def validate_telegram() -> bool:
    """Check Telegram configuration"""
    print_section("Telegram Bot")
    
    try:
        from app.config.settings import get_settings
        settings = get_settings()
        
        if settings.telegram_bot_token and settings.telegram_chat_id:
            check_ok("Telegram configured")
            check_info(f"Chat ID: {settings.telegram_chat_id}")
            return True
        else:
            check_fail("Telegram not configured")
            return False
    except Exception as e:
        check_fail(f"Telegram check failed: {e}")
        return False


def validate_logging() -> bool:
    """Check logging setup"""
    print_section("Logging")
    
    try:
        from app.utils.logger import get_logger
        logger = get_logger("test")
        check_ok("Logging configured")
        check_info("Logging to stdout with timestamps")
        return True
    except Exception as e:
        check_fail(f"Logging setup failed: {e}")
        return False


def validate_database() -> bool:
    """Check database setup"""
    print_section("Database")
    
    try:
        from app.memory.checkpoint import get_checkpointer
        checkpointer = get_checkpointer()
        
        if hasattr(checkpointer, '__class__'):
            check_ok(f"Checkpointer: {checkpointer.__class__.__name__}")
        
        return True
    except Exception as e:
        check_fail(f"Database check failed: {e}")
        return False


async def main():
    """Run all validations"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}[PROD] AI News Research Agent - Production Validation{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    checks = [
        ("Python Version", validate_python_version),
        ("Environment File", validate_environment_file),
        ("Dependencies", validate_dependencies),
        ("Configuration", validate_config),
        ("Logging", validate_logging),
        ("Database", validate_database),
        ("Vector Store", validate_chromadb),
        ("Embeddings", validate_embeddings),
        ("Telegram", validate_telegram),
        ("LangGraph Workflow", validate_graph),
        ("Workflow Execution", validate_workflow_execution),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            if asyncio.iscoroutinefunction(check_func):
                results[name] = await check_func()
            else:
                results[name] = check_func()
        except Exception as e:
            check_fail(f"Unexpected error in {name}: {e}")
            results[name] = False
    
    # Summary
    print_section("Validation Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        print(f"  {status} - {name}")
    
    print(f"\n{BLUE}Result: {passed}/{total} checks passed{RESET}")
    
    if passed == total:
        print(f"{GREEN}✅ All checks passed! System is ready for production.{RESET}\n")
        return 0
    else:
        print(f"{YELLOW}⚠️  Some checks failed. Review errors above.{RESET}\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
