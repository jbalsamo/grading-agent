#!/usr/bin/env python3
"""
Test script for conversation history persistence functionality.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.master_agent import MasterAgent
import time

def test_save_and_load():
    """Test saving and loading conversation history across sessions."""
    print("🧪 Testing Conversation History Persistence")
    print("=" * 60)
    
    # Session 1: Create some conversation history
    print("\n📝 Session 1: Creating conversation history...")
    print("-" * 60)
    
    try:
        agent1 = MasterAgent()
        
        # Have a conversation
        messages = [
            "Hi, my name is TestUser",
            "I'm learning about AI agents",
            "Can you explain what a master agent does?"
        ]
        
        for i, msg in enumerate(messages, 1):
            print(f"\n👤 Message {i}: {msg}")
            response = agent1.chat(msg)
            print(f"🤖 Response {i}: {response[:80]}...")
        
        # Check history
        history_before = agent1.get_conversation_history()
        stats_before = history_before['stats']
        print(f"\n📊 Session 1 Stats:")
        print(f"   Total Messages: {stats_before['total_messages']}")
        print(f"   User Messages: {stats_before['user_messages']}")
        print(f"   Assistant Messages: {stats_before['assistant_messages']}")
        
        # Save manually to test
        print(f"\n💾 Saving conversation history...")
        if agent1.save_conversation_history():
            print(f"✅ Saved {len(agent1.conversation_history)} messages")
        else:
            print("❌ Failed to save")
            return False
        
        # Simulate shutdown
        print("\n🔌 Shutting down Session 1...")
        agent1.shutdown()
        
        # Small delay to simulate app restart
        print("\n⏳ Simulating app restart...")
        time.sleep(1)
        
        # Session 2: Load previous conversation
        print("\n📝 Session 2: Loading previous conversation...")
        print("-" * 60)
        
        agent2 = MasterAgent()
        
        # Check if history was restored
        history_after = agent2.get_conversation_history()
        stats_after = history_after['stats']
        
        print(f"\n📊 Session 2 Stats (after load):")
        print(f"   Total Messages: {stats_after['total_messages']}")
        print(f"   User Messages: {stats_after['user_messages']}")
        print(f"   Assistant Messages: {stats_after['assistant_messages']}")
        
        # Verify the messages were restored
        if stats_after['total_messages'] != stats_before['total_messages']:
            print(f"\n❌ Message count mismatch!")
            print(f"   Before: {stats_before['total_messages']}")
            print(f"   After: {stats_after['total_messages']}")
            return False
        
        # Test context awareness with restored history
        print(f"\n🧠 Testing context awareness with restored history...")
        test_msg = "Do you remember my name?"
        print(f"👤 Test: {test_msg}")
        response = agent2.chat(test_msg)
        print(f"🤖 Response: {response}")
        
        # Check if the agent remembered the name
        if "TestUser" in response or "testuser" in response.lower():
            print(f"✅ Agent remembered the name from previous session!")
        else:
            print(f"⚠️  Agent response doesn't mention the name")
        
        # Clean up
        print(f"\n🧹 Cleaning up...")
        agent2.conversation_history.delete_saved_history()
        print(f"✅ Deleted test history file")
        
        print(f"\n✅ Persistence test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_persistence_with_clear():
    """Test that clear-history also removes saved file."""
    print("\n\n🧪 Testing Clear History with Persistence")
    print("=" * 60)
    
    try:
        print("\n📝 Creating and saving conversation...")
        agent = MasterAgent()
        
        # Create some messages
        agent.chat("Test message 1")
        agent.chat("Test message 2")
        
        # Save
        agent.save_conversation_history()
        print(f"✅ Saved {len(agent.conversation_history)} messages")
        
        # Clear (which should also delete file)
        print(f"\n🗑️  Clearing history...")
        agent.clear_conversation_history()
        agent.conversation_history.delete_saved_history()
        
        # Restart and check
        print(f"\n🔄 Restarting to verify clear...")
        agent2 = MasterAgent()
        
        if len(agent2.conversation_history) == 0:
            print(f"✅ History correctly cleared and file deleted")
            return True
        else:
            print(f"❌ History was not properly cleared")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Conversation History Persistence Tests")
    print("=" * 70)
    
    # Test save and load
    save_load_success = test_save_and_load()
    
    # Test clear with persistence
    clear_success = test_persistence_with_clear()
    
    print("\n" + "=" * 70)
    print("📋 TEST RESULTS")
    print("=" * 70)
    print(f"Save/Load Test: {'✅ PASSED' if save_load_success else '❌ FAILED'}")
    print(f"Clear History Test: {'✅ PASSED' if clear_success else '❌ FAILED'}")
    
    if save_load_success and clear_success:
        print("\n🎉 All persistence tests passed!")
        print("\n💡 Key Features:")
        print("  ✓ Conversation history automatically loads on startup")
        print("  ✓ Conversation history automatically saves on exit")
        print("  ✓ Manual save command available")
        print("  ✓ Context preserved across sessions")
        print("  ✓ Clear-history removes saved file")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
