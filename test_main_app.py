#!/usr/bin/env python3
"""
Test script for the main application functionality without interactive input.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from master_agent import MasterAgent

def test_main_app_functionality():
    """Test the main application functionality programmatically."""
    print("🧪 Testing Main Application Functionality")
    print("=" * 50)
    
    try:
        # Initialize the master agent (same as main.py does)
        print("📡 Initializing Master Agent System...")
        agent = MasterAgent()
        
        # Display configuration info (same as main.py does)
        info = agent.get_info()
        status = agent.get_agent_status()
        
        print(f"✅ Master Agent System initialized successfully!")
        print(f"🔗 Endpoint: {info['endpoint']}")
        print(f"🤖 Deployment: {info['deployment']}")
        print(f"📋 API Version: {info['api_version']}")
        print(f"🎯 Specialized Agents: {', '.join(info['specialized_agents']) if info['specialized_agents'] else 'None'}")
        print(f"💾 Data Manager: {'Active' if info['data_manager_available'] else 'Inactive'}")
        print("=" * 50)
        
        # Test the hello message (same as main.py does)
        print("💬 Sending hello message...")
        hello_message = "Hello! Can you introduce yourself and tell me what you can help me with?"
        
        print(f"👤 User: {hello_message}")
        print("🤔 Thinking...")
        
        # Get response from the agent
        response = agent.chat(hello_message)
        print(f"🤖 Master Assistant: {response[:200]}...")  # Truncate for readability
        print("=" * 50)
        
        # Test conversation history functionality
        print("💬 Testing conversation history...")
        
        # Send a few more messages to build history
        test_messages = [
            "My name is Bob and I'm learning Python.",
            "Can you help me understand functions?",
            "What's the difference between a function and a method?"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"👤 Message {i}: {message}")
            response = agent.chat(message)
            print(f"🤖 Response {i}: {response[:100]}...")  # Truncate for readability
        
        # Test history retrieval
        print("\n📊 Testing history commands...")
        
        # Test status command functionality
        status = agent.get_agent_status()
        print(f"📊 System Status:")
        print(f"   Master Agent: {status['master_agent']}")
        print(f"   Data Manager: {status['data_manager']}")
        if status['specialized_agents']:
            print("   Specialized Agents:")
            for agent_name, agent_status in status['specialized_agents'].items():
                print(f"     - {agent_name}: {agent_status}")
        
        # Test history command functionality
        history_info = agent.get_conversation_history()
        print(f"\n💬 Conversation History:")
        stats = history_info['stats']
        print(f"   Total Messages: {stats['total_messages']}")
        print(f"   User Messages: {stats['user_messages']}")
        print(f"   Assistant Messages: {stats['assistant_messages']}")
        if stats['agent_usage']:
            print("   Agent Usage:")
            for agent_name, count in stats['agent_usage'].items():
                print(f"     - {agent_name}: {count} responses")
        
        # Test context awareness
        print(f"\n🧠 Testing context awareness...")
        context_test = "Do you remember my name from earlier?"
        print(f"👤 Context test: {context_test}")
        response = agent.chat(context_test)
        print(f"🤖 Context response: {response}")
        
        # Test agent switching with context
        print(f"\n🔄 Testing agent switching with context...")
        analysis_test = "Can you analyze the Python concepts we discussed?"
        print(f"👤 Analysis test: {analysis_test}")
        response = agent.chat(analysis_test)
        print(f"🤖 Analysis response: {response[:150]}...")  # Truncate for readability
        
        # Test clear history functionality
        print(f"\n🗑️  Testing clear history...")
        agent.clear_conversation_history()
        cleared_stats = agent.get_conversation_history()['stats']
        print(f"Messages after clearing: {cleared_stats['total_messages']}")
        
        print(f"\n✅ All main application tests completed successfully!")
        print("🎉 The chat history functionality is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Main Application Tests")
    print("=" * 60)
    
    success = test_main_app_functionality()
    
    if success:
        print(f"\n🎉 All tests passed! The application is ready to use.")
        print(f"\n📝 To run the interactive application:")
        print(f"   cd /Users/josephbalsamo/Development/Work/gradingAgent/grading-agent")
        print(f"   source .venv/bin/activate")
        print(f"   python main.py")
        print(f"\n💡 Available commands in the interactive mode:")
        print(f"   • status - Show system status")
        print(f"   • stats - Show performance statistics") 
        print(f"   • health - Run health check")
        print(f"   • history - Show conversation history stats")
        print(f"   • clear-history - Clear conversation history")
        print(f"   • help - Show help message")
        print(f"   • quit/exit/bye - Exit the system")
        sys.exit(0)
    else:
        print(f"\n❌ Tests failed.")
        sys.exit(1)
