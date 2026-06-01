"""
Test suite for baseline chatbot.
Tests how a standard LLM fails on student point queries.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from src.core.openai_provider import OpenAIProvider
from src.core.gemini_provider import GeminiProvider
from src.core.local_provider import LocalProvider
from src.agent.baseline_chatbot import BaselineChatbot
from src.telemetry.logger import logger

load_dotenv()


# Test queries: 2 valid (in CSV), 2 invalid (not in CSV), 1 ambiguous (duplicate name)
TEST_QUERIES = [
    {
        "id": "Q1_VALID",
        "query": "What are Alice Johnson's points?",
        "expected_source": "CSV (Alice Johnson - S001 - 92 points)",
        "category": "valid"
    },
    {
        "id": "Q2_VALID",
        "query": "How many points did Karen Martinez get?",
        "expected_source": "CSV (Karen Martinez - S012 - 100 points)",
        "category": "valid"
    },
    {
        "id": "Q3_INVALID",
        "query": "What are Tom Wilson's points?",
        "expected_source": "NOT IN CSV (should hallucinate)",
        "category": "invalid"
    },
    {
        "id": "Q4_INVALID",
        "query": "How many points did Sarah Johnson score?",
        "expected_source": "NOT IN CSV (should hallucinate)",
        "category": "invalid"
    },
    {
        "id": "Q5_AMBIGUOUS",
        "query": "What are John Smith's points?",
        "expected_source": "AMBIGUOUS (John Smith appears twice: S010-82, S011-76)",
        "category": "ambiguous"
    }
]


def test_baseline_with_provider(provider_name: str, provider: BaselineChatbot):
    """Run all test queries with a specific provider."""
    print(f"\n{'='*70}")
    print(f"Testing Baseline Chatbot with {provider_name}")
    print(f"{'='*70}")
    
    results = []
    
    for query_info in TEST_QUERIES:
        print(f"\n[{query_info['id']}] {query_info['query']}")
        print(f"Expected: {query_info['expected_source']}")
        
        response = provider.answer(query_info['query'])
        
        print(f"Response: {response[:200]}..." if len(response) > 200 else f"Response: {response}")
        
        results.append({
            "query_id": query_info['id'],
            "query": query_info['query'],
            "category": query_info['category'],
            "expected_source": query_info['expected_source'],
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
    
    return results


def get_available_providers():
    """Detect which providers are available based on environment."""
    providers = {}
    
    # Try OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            providers["OpenAI"] = OpenAIProvider(
                model_name="gpt-3.5-turbo",
                api_key=api_key
            )
            print("✓ OpenAI provider available")
        except Exception as e:
            print(f"✗ OpenAI provider failed: {e}")
    
    # Try Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            providers["Gemini"] = GeminiProvider(
                model_name="gemini-pro",
                api_key=api_key
            )
            print("✓ Gemini provider available")
        except Exception as e:
            print(f"✗ Gemini provider failed: {e}")
    
    # Try Local
    model_path = "models/phi-3-mini-4k-instruct-gguf.gguf"
    if os.path.exists(model_path):
        try:
            providers["Local (Phi-3)"] = LocalProvider(
                model_path=model_path,
                n_ctx=4096
            )
            print("✓ Local provider (Phi-3) available")
        except Exception as e:
            print(f"✗ Local provider failed: {e}")
    else:
        print(f"✗ Local provider model not found at {model_path}")
    
    return providers


def main():
    """Run baseline chatbot tests with available providers."""
    print("Baseline Chatbot Test Suite")
    print("Testing LLM limitations on student point queries")
    
    # Detect available providers
    print("\nDetecting available providers...")
    providers = get_available_providers()
    
    if not providers:
        print("\n⚠️  No providers available. Please set OPENAI_API_KEY or GEMINI_API_KEY")
        return
    
    # Run tests
    all_results = {}
    for provider_name, provider in providers.items():
        chatbot = BaselineChatbot(provider)
        results = test_baseline_with_provider(provider_name, chatbot)
        all_results[provider_name] = results
    
    # Save results
    output_path = Path("logs") / "baseline_trace.json"
    output_path.parent.mkdir(exist_ok=True)
    
    trace_data = {
        "test_type": "baseline_chatbot",
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(TEST_QUERIES),
        "providers_tested": list(all_results.keys()),
        "results_by_provider": all_results
    }
    
    with open(output_path, 'w') as f:
        json.dump(trace_data, f, indent=2)
    
    print(f"\n✅ Baseline trace saved to {output_path}")
    
    # Summary statistics
    print("\n" + "="*70)
    print("Summary Statistics")
    print("="*70)
    for provider_name, results in all_results.items():
        print(f"\n{provider_name}:")
        print(f"  Total queries: {len(results)}")
        valid = [r for r in results if r['category'] == 'valid']
        invalid = [r for r in results if r['category'] == 'invalid']
        ambiguous = [r for r in results if r['category'] == 'ambiguous']
        print(f"  Valid queries: {len(valid)}")
        print(f"  Invalid queries (expect hallucination): {len(invalid)}")
        print(f"  Ambiguous queries (expect confusion): {len(ambiguous)}")


if __name__ == "__main__":
    main()
