"""
Test suite for ReAct agent.
Tests how the agent with tools succeeds where baseline fails.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from src.core.openai_provider import OpenAIProvider
from src.core.gemini_provider import GeminiProvider
from src.core.local_provider import LocalProvider
from src.agent.agent import ReActAgent
from src.telemetry.logger import logger

load_dotenv()


# Same test queries as baseline for direct comparison
TEST_QUERIES = [
    {
        "id": "Q1_VALID",
        "query": "What are Alice Johnson's points?",
        "expected_answer": "92",
        "expected_subject": "Mathematics",
        "category": "valid"
    },
    {
        "id": "Q2_VALID",
        "query": "How many points did Karen Martinez get?",
        "expected_answer": "100",
        "expected_subject": "Physics",
        "category": "valid"
    },
    {
        "id": "Q3_INVALID",
        "query": "What are Tom Wilson's points?",
        "expected_answer": "not found",
        "category": "invalid"
    },
    {
        "id": "Q4_INVALID",
        "query": "How many points did Sarah Johnson score?",
        "expected_answer": "not found",
        "category": "invalid"
    },
    {
        "id": "Q5_AMBIGUOUS",
        "query": "What are John Smith's points?",
        "expected_answer": "two students",
        "category": "ambiguous"
    }
]


def test_react_agent_with_provider(provider_name: str, provider: ReActAgent):
    """Run all test queries with ReAct agent using a specific provider."""
    print(f"\n{'='*70}")
    print(f"Testing ReAct Agent with {provider_name}")
    print(f"{'='*70}")
    
    results = []
    
    for query_info in TEST_QUERIES:
        print(f"\n[{query_info['id']}] {query_info['query']}")
        print(f"Expected: {query_info.get('expected_answer', 'N/A')}")
        
        response = provider.run(query_info['query'])
        
        print(f"Response: {response[:300]}..." if len(response) > 300 else f"Response: {response}")
        
        # Analyze response for correctness
        accuracy = evaluate_response(response, query_info)
        print(f"Accuracy: {accuracy['assessment']} (confidence: {accuracy['confidence']:.0%})")
        
        results.append({
            "query_id": query_info['id'],
            "query": query_info['query'],
            "category": query_info['category'],
            "expected": query_info.get('expected_answer', 'N/A'),
            "response": response,
            "accuracy": accuracy['assessment'],
            "confidence": accuracy['confidence'],
            "timestamp": datetime.now().isoformat()
        })
    
    return results


def evaluate_response(response: str, query_info: dict) -> dict:
    """
    Evaluate if response matches expected answer.
    
    Returns:
        Dict with assessment and confidence (0.0-1.0)
    """
    response_lower = response.lower()
    expected = query_info.get('expected_answer', '').lower()
    
    if query_info['category'] == 'valid':
        # Should contain the expected number
        if expected in response_lower:
            return {"assessment": "CORRECT", "confidence": 0.95}
        # Check for partial matches
        if query_info.get('expected_subject', '').lower() in response_lower:
            return {"assessment": "PARTIALLY_CORRECT", "confidence": 0.7}
        return {"assessment": "INCORRECT", "confidence": 0.1}
    
    elif query_info['category'] == 'invalid':
        # Should indicate student not found
        if "not found" in response_lower or "no student" in response_lower or "error" in response_lower:
            return {"assessment": "CORRECT", "confidence": 0.95}
        # False positive: hallucination
        return {"assessment": "HALLUCINATION", "confidence": 0.05}
    
    elif query_info['category'] == 'ambiguous':
        # Should handle multiple results
        if "two" in response_lower or "multiple" in response_lower or "john smith" in response_lower:
            if ("s010" in response_lower or "s011" in response_lower or "82" in response_lower or "76" in response_lower):
                return {"assessment": "CORRECT", "confidence": 0.95}
        # At least acknowledge ambiguity
        if "ambig" in response_lower or "multiple" in response_lower:
            return {"assessment": "PARTIALLY_CORRECT", "confidence": 0.6}
        
        return {"assessment": "INCORRECT", "confidence": 0.2}
    
    return {"assessment": "UNKNOWN", "confidence": 0.0}


def get_available_providers():
    """Detect which providers are available."""
    providers = {}
    
    # Try OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            provider = OpenAIProvider(
                model_name="gpt-3.5-turbo",
                api_key=api_key
            )
            providers["OpenAI"] = provider
            print("✓ OpenAI provider available")
        except Exception as e:
            print(f"✗ OpenAI provider failed: {e}")
    
    # Try Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            provider = GeminiProvider(
                model_name="gemini-pro",
                api_key=api_key
            )
            providers["Gemini"] = provider
            print("✓ Gemini provider available")
        except Exception as e:
            print(f"✗ Gemini provider failed: {e}")
    
    # Try Local
    model_path = "models/phi-3-mini-4k-instruct-gguf.gguf"
    if os.path.exists(model_path):
        try:
            provider = LocalProvider(
                model_path=model_path,
                n_ctx=4096
            )
            providers["Local (Phi-3)"] = provider
            print("✓ Local provider (Phi-3) available")
        except Exception as e:
            print(f"✗ Local provider failed: {e}")
    else:
        print(f"✗ Local provider model not found at {model_path}")
    
    return providers


def main():
    """Run ReAct agent tests with available providers."""
    print("ReAct Agent Test Suite")
    print("Testing agent with tools on student point queries")
    
    # Detect available providers
    print("\nDetecting available providers...")
    providers = get_available_providers()
    
    if not providers:
        print("\n⚠️  No providers available. Please set OPENAI_API_KEY or GEMINI_API_KEY")
        return
    
    # Run tests
    all_results = {}
    for provider_name, provider_instance in providers.items():
        agent = ReActAgent(llm=provider_instance, tools=[], max_steps=5)
        results = test_react_agent_with_provider(provider_name, agent)
        all_results[provider_name] = results
    
    # Save results
    output_path = Path("logs") / "agent_trace.json"
    output_path.parent.mkdir(exist_ok=True)
    
    trace_data = {
        "test_type": "react_agent",
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(TEST_QUERIES),
        "providers_tested": list(all_results.keys()),
        "results_by_provider": all_results
    }
    
    with open(output_path, 'w') as f:
        json.dump(trace_data, f, indent=2)
    
    print(f"\n✅ ReAct agent trace saved to {output_path}")
    
    # Summary statistics
    print("\n" + "="*70)
    print("Summary Statistics")
    print("="*70)
    for provider_name, results in all_results.items():
        print(f"\n{provider_name}:")
        print(f"  Total queries: {len(results)}")
        
        correct = sum(1 for r in results if r['accuracy'] == 'CORRECT')
        partial = sum(1 for r in results if r['accuracy'] == 'PARTIALLY_CORRECT')
        incorrect = sum(1 for r in results if r['accuracy'] in ['INCORRECT', 'HALLUCINATION'])
        
        print(f"  Correct: {correct} ({correct/len(results):.0%})")
        print(f"  Partial: {partial} ({partial/len(results):.0%})")
        print(f"  Incorrect: {incorrect} ({incorrect/len(results):.0%})")
        
        hallucinations = sum(1 for r in results if r['accuracy'] == 'HALLUCINATION')
        print(f"  Hallucinations: {hallucinations}")


if __name__ == "__main__":
    main()
