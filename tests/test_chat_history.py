"""
Test script for conversation history functionality.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.master_agent import MasterAgent
from modules.conversation_history import ConversationHistory
import time

def test_conversation_history():
    """Test the conversation history functionality."""
    print("🧪 Testing Conversation History Functionality")
    
    try:
        # Initialize the master agent
        print("📡 Initializing Master Agent...")
        agent = MasterAgent()
        print("✅ Master Agent initialized successfully!")
        
        # Test conversation flow
        test_messages = [
            "Hello! My name is Alice and I'm a student.",
            "Can you help me with math problems?",
            "What's 15 + 27?",
            "Great! Now can you explain how you solved that?",
            "Can you remember my name from earlier?"
        ]
        
        print(f"\n💬 Testing conversation flow with {len(test_messages)} messages...")
        print("=" * 50)
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n👤 Message {i}: {message}")
            
            # Get response
            response = agent.chat(message)
            print(f"🤖 Response: {response}")
            
            # Show conversation history stats after each message
            history_info = agent.get_conversation_history()
            stats = history_info['stats']
            print(f"📊 History: {stats['total_messages']} total messages, {stats['user_messages']} user, {stats['assistant_messages']} assistant")
            
            # Small delay for readability
            time.sleep(0.5)
        
        # Test history retrieval
        print(f"\n📝 Final Conversation History:")
        print("=" * 50)
        history_info = agent.get_conversation_history()
        print(history_info['recent_context'])
        
        # Test agent switching with context
        print(f"\n🔄 Testing Agent Switching with Context:")
        print("=" * 50)
        
        analysis_message = "Can you analyze the math problem we just solved?"
        print(f"👤 Analysis request: {analysis_message}")
        response = agent.chat(analysis_message)
        print(f"🤖 Analysis response: {response}")
        
        grading_message = "Grade my understanding of the math problem on a scale of 1-10"
        print(f"👤 Grading request: {grading_message}")
        response = agent.chat(grading_message)
        print(f"🤖 Grading response: {response}")
        
        # Final stats
        print(f"\n📈 Final Statistics:")
        print("=" * 50)
        final_stats = agent.get_conversation_history()['stats']
        print(f"Total Messages: {final_stats['total_messages']}")
        print(f"User Messages: {final_stats['user_messages']}")
        print(f"Assistant Messages: {final_stats['assistant_messages']}")
        if final_stats['agent_usage']:
            print("Agent Usage:")
            for agent_name, count in final_stats['agent_usage'].items():
                print(f"  - {agent_name}: {count} responses")
        
        # Test history clearing
        print(f"\n🗑️  Testing History Clearing:")
        print("=" * 50)
        agent.clear_conversation_history()
        cleared_stats = agent.get_conversation_history()['stats']
        print(f"Messages after clearing: {cleared_stats['total_messages']}")
        
        print(f"\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversation_history_class():
    """Test the ConversationHistory class directly."""
    print("\n🧪 Testing ConversationHistory Class")
    print("=" * 50)
    
    try:
        # Test basic functionality
        history = ConversationHistory(max_messages=5)
        
        # Add some messages
        history.add_user_message("Hello!")
        history.add_assistant_message("Hi there!", "chat")
        history.add_user_message("How are you?")
        history.add_assistant_message("I'm doing well, thanks!", "chat")
        
        print(f"Messages after adding 4: {len(history)}")
        
        # Test rolling window
        for i in range(5):
            history.add_user_message(f"Message {i+3}")
            history.add_assistant_message(f"Response {i+3}", "chat")
        
        print(f"Messages after adding 10 more (should be 5 max): {len(history)}")
        
        # Test message formatting
        langchain_messages = history.get_langchain_messages()
        print(f"LangChain messages: {len(langchain_messages)}")
        
        # Test context retrieval
        context = history.get_recent_context(3)
        print(f"Recent context (3 messages):\n{context}")
        
        # Test stats
        stats = history.get_stats()
        print(f"Stats: {stats}")
        
        print("✅ ConversationHistory class tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ ConversationHistory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Conversation History Tests")
    print("=" * 60)
    
    # Test the ConversationHistory class first
    class_test_passed = test_conversation_history_class()
    
    if class_test_passed:
        # Test the full integration
        integration_test_passed = test_conversation_history()
        
        if integration_test_passed:
            print(f"\n🎉 All tests passed! Conversation history is working correctly.")
            sys.exit(0)
        else:
            print(f"\n❌ Integration tests failed.")
            sys.exit(1)
    else:
        print(f"\n❌ Class tests failed.")
        sys.exit(1)
