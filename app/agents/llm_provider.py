"""
LLM Abstraction Layer - Provider-agnostic interface.
Swap Gemini <-> Meralion by changing LLM_PROVIDER in .env.
"""
import os
import json
from abc import ABC, abstractmethod
from dotenv import load_dotenv

_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(_env_path)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        """Generate a text response."""
        pass

    @abstractmethod
    def generate_structured(self, prompt: str, schema: dict, system_prompt: str = None) -> dict:
        """Generate a response that conforms to a JSON schema."""
        pass

    @abstractmethod
    async def stream(self, prompt: str, system_prompt: str = None):
        """Stream a response token by token."""
        pass


class RateLimitError(Exception):
    """Raised when the LLM API quota is exhausted."""
    pass


class GeminiProvider(BaseLLMProvider):
    """Google Gemini implementation."""

    def __init__(self, model_name: str = "gemini-2.0-flash"):
        import google.generativeai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in .env")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.genai = genai

    def _handle_api_error(self, exc):
        """Convert API errors to friendly exceptions."""
        err_str = str(exc)
        if '429' in err_str or 'ResourceExhausted' in err_str or 'quota' in err_str.lower():
            raise RateLimitError(
                "Gemini API quota exceeded (free tier limit reached). "
                "Please wait a minute and try again, or upgrade your Gemini API plan."
            ) from exc
        raise exc

    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        try:
            config = self.genai.types.GenerationConfig(temperature=temperature)
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = self.model.generate_content(full_prompt, generation_config=config)
            return response.text
        except RateLimitError:
            raise
        except Exception as exc:
            self._handle_api_error(exc)

    def generate_structured(self, prompt: str, schema: dict, system_prompt: str = None) -> dict:
        try:
            schema_str = json.dumps(schema, indent=2)
            structured_prompt = (
                f"{system_prompt or ''}\n\n"
                f"Respond with ONLY valid JSON matching this schema:\n{schema_str}\n\n"
                f"Input: {prompt}\n\n"
                f"JSON Response:"
            )
            config = self.genai.types.GenerationConfig(
                temperature=0.3,
                response_mime_type="application/json"
            )
            response = self.model.generate_content(structured_prompt, generation_config=config)
            return json.loads(response.text)
        except RateLimitError:
            raise
        except Exception as exc:
            self._handle_api_error(exc)

    async def stream(self, prompt: str, system_prompt: str = None):
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = self.model.generate_content(full_prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text


class MeralionProvider(BaseLLMProvider):
    """
    Meralion 2 placeholder - same interface, swap in when ready.
    Expected to support an OpenAI-compatible API or custom endpoint.
    """

    def __init__(self, model_name: str = "meralion-2", api_url: str = None):
        self.model_name = model_name
        self.api_url = api_url or os.getenv('MERALION_API_URL', 'http://localhost:8080/v1')
        self.api_key = os.getenv('MERALION_API_KEY', '')

    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        # When Meralion 2 is available, implement using its API
        # Expected: OpenAI-compatible chat completions endpoint
        import httpx
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        resp = httpx.post(
            f"{self.api_url}/chat/completions",
            json={"model": self.model_name, "messages": messages, "temperature": temperature},
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=60
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def generate_structured(self, prompt: str, schema: dict, system_prompt: str = None) -> dict:
        schema_str = json.dumps(schema, indent=2)
        full_prompt = (
            f"Respond with ONLY valid JSON matching this schema:\n{schema_str}\n\n"
            f"Input: {prompt}\n\nJSON Response:"
        )
        text = self.generate(full_prompt, system_prompt=system_prompt, temperature=0.3)
        return json.loads(text)

    async def stream(self, prompt: str, system_prompt: str = None):
        # Placeholder for streaming support
        text = self.generate(prompt, system_prompt=system_prompt)
        yield text


class OllamaProvider(BaseLLMProvider):
    """
    Local Ollama provider — runs open-source models (Llama 3, Mistral, Qwen, etc.)
    completely free with no API key.
    Requires Ollama installed: https://ollama.com/download
    Set OLLAMA_MODEL in .env to change the model (default: llama3.2)
    """

    def __init__(self, model_name: str = None, api_url: str = None):
        self.model = model_name or os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.base_url = api_url or os.getenv('OLLAMA_URL', 'http://localhost:11434')
        # Verify Ollama is reachable
        import httpx
        try:
            httpx.get(f"{self.base_url}/api/tags", timeout=3).raise_for_status()
        except Exception:
            raise RuntimeError(
                f"Cannot reach Ollama at {self.base_url}. "
                "Install Ollama from https://ollama.com/download and run it, "
                f"then pull a model: `ollama pull {self.model}`"
            )

    def _chat(self, messages: list, temperature: float = 0.7, json_mode: bool = False) -> str:
        import httpx
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if json_mode:
            payload["format"] = "json"
        resp = httpx.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return self._chat(messages, temperature=temperature)

    def generate_structured(self, prompt: str, schema: dict, system_prompt: str = None) -> dict:
        schema_str = json.dumps(schema, indent=2)
        system = (system_prompt or "") + (
            f"\n\nYou MUST respond with ONLY valid JSON matching this schema:\n{schema_str}"
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Input: {prompt}\n\nJSON Response:"},
        ]
        raw = self._chat(messages, temperature=0.3, json_mode=True)
        return json.loads(raw)

    async def stream(self, prompt: str, system_prompt: str = None):
        import httpx
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": True},
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        chunk = json.loads(line)
                        if content := chunk.get("message", {}).get("content"):
                            yield content



# ============================================================================
# FACTORY
# ============================================================================

class MockLLMProvider(BaseLLMProvider):
    """Fallback provider that always raises errors to trigger heuristics."""
    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        raise RuntimeError("MockLLMProvider: LLM not available")

    def generate_structured(self, prompt: str, schema: dict, system_prompt: str = None) -> dict:
        raise RuntimeError("MockLLMProvider: LLM not available")

    async def stream(self, prompt: str, system_prompt: str = None):
        raise RuntimeError("MockLLMProvider: LLM not available")
        yield ""

_providers = {
    'gemini': GeminiProvider,
    'meralion': MeralionProvider,
    'ollama': OllamaProvider,
    'mock': MockLLMProvider,
}

_instance = None

def get_llm(provider: str = None, **kwargs) -> BaseLLMProvider:
    """Get an LLM provider instance. Uses LLM_PROVIDER env var if not specified."""
    global _instance
    if _instance is not None and provider is None:
        return _instance
    
    provider = provider or os.getenv('LLM_PROVIDER', 'gemini')
    
    # helper to safe init
    def init_provider(p_name):
        if p_name not in _providers:
             raise ValueError(f"Unknown LLM provider: {p_name}")
        return _providers[p_name](**kwargs)

    try:
        _instance = init_provider(provider)
    except (ImportError, ValueError, RuntimeError) as e:
        print(f"Warning: Failed to initialize {provider} LLM provider ({e}).")
        # If provider was Ollama (or other non-Gemini), try falling back to Gemini
        if provider != 'gemini':
            try:
                print("Falling back to GeminiProvider...")
                _instance = GeminiProvider()
            except Exception as e2:
                print(f"Gemini fallback also failed ({e2}). Using MockLLMProvider.")
                _instance = MockLLMProvider()
        else:
            print("Using MockLLMProvider.")
            _instance = MockLLMProvider()

    return _instance
