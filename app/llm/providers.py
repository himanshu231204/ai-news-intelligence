"""Direct LLM provider implementations with async httpx.

Providers:
- Groq: Primary provider (llama-3.3-70b-versatile)
- OpenRouter: Fallback with multiple free models
- Gemini: Newsletter provider (gemini-2.5-flash)

OPTIMIZATIONS:
- Multiple fallback models for OpenRouter
- Improved exponential backoff
- Rate limit handling
- Token optimization

Each function includes:
- Async httpx client
- Retry logic with exponential backoff
- Error logging
- Type hints and docstrings
"""

from __future__ import annotations

import asyncio
import json
from typing import Optional, List

import httpx

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Default retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_INITIAL_DELAY = 2.0  # Increased from 1.0 for better rate limit handling
MAX_INITIAL_DELAY = 8.0  # Cap the exponential backoff

# OpenRouter fallback models (tried in order - verified working free models)
OPENROUTER_FALLBACK_MODELS: List[str] = [
    "meta-llama/llama-3.1-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "anthropic/claude-3-haiku:free",
    "google/gemma-2-9b-it:free",
    "deepseek/deepseek-chat:free",
]


async def call_groq(
    prompt: str,
    system: str = "",
    model: str = "llama-3.3-70b-versatile",
    max_retries: int = DEFAULT_MAX_RETRIES,
    temperature: float = 0.2,
) -> Optional[str]:
    """Call Groq API with improved retry logic and exponential backoff.

    OPTIMIZATION: Better rate limit handling with capped exponential backoff.

    Args:
        prompt: User prompt content
        system: System prompt (optional)
        model: Model identifier (default: llama-3.3-70b-versatile)
        max_retries: Maximum retry attempts
        temperature: Sampling temperature

    Returns:
        Generated text or None on failure
    """
    settings = get_settings()
    api_key = settings.groq_api_key

    if not api_key:
        logger.warning("Groq API key not configured")
        return None

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "temperature": temperature,
        "messages": messages,
    }

    delay = DEFAULT_INITIAL_DELAY
    last_exception = None

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()
                logger.debug(f"Groq API call successful on attempt {attempt + 1}")
                return content

        except httpx.HTTPStatusError as e:
            last_exception = e
            status_code = e.response.status_code

            # Rate limit - retry with capped exponential backoff
            if status_code == 429:
                logger.warning(
                    "Groq rate limited (attempt %d/%d). Retrying in %.1fs...",
                    attempt + 1,
                    max_retries,
                    delay,
                )
            else:
                logger.warning(
                    "Groq HTTP error %d (attempt %d/%d): %s. Retrying in %.1fs...",
                    status_code,
                    attempt + 1,
                    max_retries,
                    e,
                    delay,
                )

        except Exception as e:
            last_exception = e
            logger.warning(
                "Groq request failed (attempt %d/%d): %s. Retrying in %.1fs...",
                attempt + 1,
                max_retries,
                e,
                delay,
            )

        if attempt < max_retries - 1:
            await asyncio.sleep(delay)
            delay = min(delay * 2, MAX_INITIAL_DELAY)  # Cap at MAX_INITIAL_DELAY

    logger.error(f"Groq API failed after {max_retries} attempts: {last_exception}")
    return None


async def call_openrouter(
    prompt: str,
    system: str = "",
    model: str = "deepseek/deepseek-chat-v3-0324:free",
    max_retries: int = DEFAULT_MAX_RETRIES,
    temperature: float = 0.2,
    use_fallback_models: bool = True,
) -> Optional[str]:
    """Call OpenRouter API with retry logic and fallback models.

    OPTIMIZATION: Tries multiple free models if primary fails.

    Args:
        prompt: User prompt content
        system: System prompt (optional)
        model: Model identifier (default: deepseek/deepseek-chat-v3-0324:free)
        max_retries: Maximum retry attempts per model
        temperature: Sampling temperature
        use_fallback_models: Try fallback models if primary fails

    Returns:
        Generated text or None on failure
    """
    settings = get_settings()
    api_key = settings.openrouter_api_key

    # Use settings model as primary
    primary_model = settings.openrouter_model or model

    if not api_key:
        logger.warning("OpenRouter API key not configured")
        return None

    # Build model list: primary + fallbacks
    models_to_try = [primary_model]
    if use_fallback_models:
        for fallback_model in OPENROUTER_FALLBACK_MODELS:
            if fallback_model not in models_to_try:
                models_to_try.append(fallback_model)

    logger.debug(f"OpenRouter will try models: {models_to_try[:3]}...")

    # Try each model in sequence
    for model_idx, current_model in enumerate(models_to_try):
        logger.info(
            f"OpenRouter trying model {model_idx + 1}/{len(models_to_try)}: {current_model}"
        )

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": current_model,
            "temperature": temperature,
            "messages": messages,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/himanshu231204/ai-news-agent",
            "X-Title": "AI News Agent",
        }

        delay = DEFAULT_INITIAL_DELAY
        last_exception = None

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    response.raise_for_status()
                    data = response.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    logger.info(f"OpenRouter succeeded with model: {current_model}")
                    return content

            except httpx.HTTPStatusError as e:
                last_exception = e
                status_code = e.response.status_code

                if status_code == 429:
                    # Rate limited - try next model immediately
                    logger.warning(
                        f"OpenRouter rate limited on model {current_model}. "
                        f"Trying next model..."
                    )
                    break  # Break retry loop, try next model
                else:
                    logger.warning(
                        "OpenRouter HTTP error %d (attempt %d/%d): %s",
                        status_code,
                        attempt + 1,
                        max_retries,
                        e,
                    )

            except Exception as e:
                last_exception = e
                logger.warning(
                    "OpenRouter request failed (attempt %d/%d): %s",
                    attempt + 1,
                    max_retries,
                    e,
                )

            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
                delay = min(delay * 2, MAX_INITIAL_DELAY)  # Cap the delay

        # If we got here, this model failed - try next one
        logger.warning(f"Model {current_model} failed, trying next fallback...")

    logger.error("All OpenRouter models exhausted")
    return None


async def call_gemini(
    prompt: str,
    system: str = "",
    model: str = "gemini-2.5-flash",
    max_retries: int = DEFAULT_MAX_RETRIES,
    temperature: float = 0.2,
) -> Optional[str]:
    """Call Gemini API via Google Generative AI SDK with retry logic.

    Args:
        prompt: User prompt content
        system: System instruction (optional, converted to generation config)
        model: Model identifier (default: gemini-2.5-flash)
        max_retries: Maximum retry attempts
        temperature: Sampling temperature

    Returns:
        Generated text or None on failure
    """
    settings = get_settings()
    api_key = settings.gemini_api_key

    if not api_key:
        logger.warning("Gemini API key not configured")
        return None

    try:
        import google.generativeai as genai

        # Configure the client
        genai.configure(api_key=api_key)

        # Create the model
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
        }

        # Build content with system instruction if provided
        contents = []
        if system:
            # Prepend system instruction to prompt
            full_prompt = f"{system}\n\n{prompt}"
            contents.append({"role": "user", "parts": [{"text": full_prompt}]})
        else:
            contents.append({"role": "user", "parts": [{"text": prompt}]})

        delay = DEFAULT_INITIAL_DELAY
        last_exception = None

        for attempt in range(max_retries):
            try:
                # Use the chat session approach for better reliability
                model_instance = genai.GenerativeModel(
                    model_name=model,
                    generation_config=generation_config,
                )

                response = await asyncio.to_thread(
                    model_instance.generate_content, contents
                )

                if response.text:
                    logger.debug(f"Gemini API call successful on attempt {attempt + 1}")
                    return response.text.strip()
                else:
                    logger.warning(
                        f"Gemini returned empty response on attempt {attempt + 1}"
                    )

            except Exception as e:
                last_exception = e
                logger.warning(
                    "Gemini request failed (attempt %d/%d): %s. Retrying in %.1fs...",
                    attempt + 1,
                    max_retries,
                    e,
                    delay,
                )

                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)
                    delay *= 2

        logger.error(
            f"Gemini API failed after {max_retries} attempts: {last_exception}"
        )
        return None

    except ImportError:
        logger.error(
            "google-generativeai SDK not installed. Install with: pip install google-generativeai"
        )
        return None
    except Exception as e:
        logger.error(f"Gemini SDK error: {e}")
        return None


async def call_provider(
    provider: str,
    prompt: str,
    system: str = "",
    model: str = "",
    temperature: float = 0.2,
) -> Optional[str]:
    """Generic provider caller for dynamic routing.

    Args:
        provider: Provider name ("groq", "openrouter", "gemini")
        prompt: User prompt
        system: System prompt
        model: Model identifier (uses defaults if empty)
        temperature: Sampling temperature

    Returns:
        Generated text or None
    """
    provider = provider.lower()

    if provider == "groq":
        return await call_groq(
            prompt, system, model or "llama-3.3-70b-versatile", temperature=temperature
        )
    elif provider == "openrouter":
        return await call_openrouter(
            prompt,
            system,
            model or "deepseek/deepseek-chat-v3-0324:free",
            temperature=temperature,
        )
    elif provider == "gemini":
        return await call_gemini(
            prompt, system, model or "gemini-2.5-flash", temperature=temperature
        )
    else:
        logger.error(f"Unknown provider: {provider}")
        return None
