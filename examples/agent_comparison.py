#!/usr/bin/env python3
"""
Example: Compare responses from different specialized agents.
This script demonstrates how different agents handle the same query.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.agents.chat_agent import ChatAgent
from modules.agents.analysis_agent import AnalysisAgent
from modules.agents.grading_agent import GradingAgent
import time

def main():
    """Compare agent responses to the same query."""
    print("🔍 Agent Comparison Example")
    print("=" * 50)
    
    # Initialize agents
    print("📡 Initializing specialized agents...")
    try:
        chat_agent = ChatAgent()
        analysis_agent = AnalysisAgent()
        grading_agent = GradingAgent()
        print("✅ All agents initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize agents: {e}")
        return 1
    
    # Test query that could be interpreted differently
    test_query = "How can we improve student performance in mathematics?"
    
    print(f"\n📝 Test Query: {test_query}")
    print("=" * 50)
    
    agents = {
        "Chat Agent": chat_agent,
        "Analysis Agent": analysis_agent,
        "Grading Agent": grading_agent
    }
    
    responses = {}
    
    for agent_name, agent in agents.items():
        print(f"\n🤖 {agent_name} Response:")
        print("-" * 30)
        
        start_time = time.time()
        try:
            response = agent.process(test_query)
            processing_time = time.time() - start_time
            
            responses[agent_name] = {
                "response": response,
                "processing_time": processing_time,
                "success": True
            }
            
            print(f"⏱️  Processing Time: {processing_time:.2f}s")
            print(f"📄 Response: {response}")
            
        except Exception as e:
            processing_time = time.time() - start_time
            responses[agent_name] = {
                "error": str(e),
                "processing_time": processing_time,
                "success": False
            }
            
            print(f"❌ Error after {processing_time:.2f}s: {e}")
    
    # Analysis
    print("\n" + "=" * 50)
    print("📊 Comparison Analysis")
    print("=" * 50)
    
    successful_responses = {k: v for k, v in responses.items() if v['success']}
    
    if successful_responses:
        # Response length comparison
        print("\n📏 Response Lengths:")
        for agent_name, data in successful_responses.items():
            length = len(data['response'])
            print(f"  {agent_name}: {length} characters")
        
        # Processing time comparison
        print("\n⏱️  Processing Times:")
        for agent_name, data in successful_responses.items():
            time_ms = data['processing_time'] * 1000
            print(f"  {agent_name}: {time_ms:.0f}ms")
        
        # Response focus analysis
        print("\n🎯 Response Focus Analysis:")
        keywords = {
            "educational": ["teaching", "learning", "education", "curriculum", "pedagogy"],
            "analytical": ["data", "analysis", "statistics", "metrics", "performance"],
            "practical": ["methods", "strategies", "techniques", "approaches", "solutions"]
        }
        
        for agent_name, data in successful_responses.items():
            response_lower = data['response'].lower()
            focus_scores = {}
            
            for category, words in keywords.items():
                score = sum(1 for word in words if word in response_lower)
                focus_scores[category] = score
            
            dominant_focus = max(focus_scores, key=focus_scores.get)
            print(f"  {agent_name}: {dominant_focus} focus ({focus_scores[dominant_focus]} keywords)")
    
    # Capabilities comparison
    print("\n🛠️  Agent Capabilities:")
    for agent_name, agent in agents.items():
        if hasattr(agent, 'get_capabilities'):
            capabilities = agent.get_capabilities()
            print(f"\n  {agent_name}:")
            print(f"    Specialization: {capabilities.get('specialization', 'N/A')}")
            print(f"    Capabilities: {len(capabilities.get('capabilities', []))} listed")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
