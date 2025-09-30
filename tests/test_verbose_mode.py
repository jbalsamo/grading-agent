#!/usr/bin/env python3
"""
Test script to demonstrate verbose mode functionality.
This simulates what happens when running main.py with and without -v flag.
"""
import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.master_agent import MasterAgent

def test_quiet_mode():
    """Test application in quiet mode (WARNING level)."""
    print("\n" + "=" * 60)
    print("🔇 Testing QUIET MODE (default - WARNING level and above)")
    print("=" * 60)
    
    # Set up quiet logging
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True
    )
    
    try:
        print("📡 Initializing Master Agent in quiet mode...")
        agent = MasterAgent()
        print("✅ Master Agent initialized (you should NOT see INFO logs above)")
        
        print("\n💬 Sending a test message in quiet mode...")
        response = agent.chat("Hello, this is a test in quiet mode")
        print(f"🤖 Response received: {response[:100]}...")
        print("✅ In quiet mode, you only see WARNING/ERROR logs, not INFO logs")
        
        return True
    except Exception as e:
        print(f"❌ Error in quiet mode test: {e}")
        return False

def test_verbose_mode():
    """Test application in verbose mode (INFO level)."""
    print("\n" + "=" * 60)
    print("📝 Testing VERBOSE MODE (-v flag - INFO level)")
    print("=" * 60)
    
    # Set up verbose logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True
    )
    
    try:
        print("📡 Initializing Master Agent in verbose mode...")
        agent = MasterAgent()
        print("✅ Master Agent initialized (you SHOULD see INFO logs above)")
        
        print("\n💬 Sending a test message in verbose mode...")
        response = agent.chat("Hello, this is a test in verbose mode")
        print(f"🤖 Response received: {response[:100]}...")
        print("✅ In verbose mode, you see all INFO logs including HTTP requests and agent routing")
        
        return True
    except Exception as e:
        print(f"❌ Error in verbose mode test: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Verbose Mode Functionality")
    print("=" * 60)
    print("This demonstrates the difference between running:")
    print("  • python main.py          (quiet mode - WARNING level)")
    print("  • python main.py -v       (verbose mode - INFO level)")
    print("=" * 60)
    
    # Test quiet mode first
    quiet_success = test_quiet_mode()
    
    # Test verbose mode
    verbose_success = test_verbose_mode()
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    print(f"Quiet mode test: {'✅ PASSED' if quiet_success else '❌ FAILED'}")
    print(f"Verbose mode test: {'✅ PASSED' if verbose_success else '❌ FAILED'}")
    
    if quiet_success and verbose_success:
        print("\n🎉 All tests passed!")
        print("\n💡 Usage:")
        print("  python main.py           # Run without logs (quiet)")
        print("  python main.py -v        # Run with INFO logs (verbose)")
        print("  python main.py --verbose # Run with INFO logs (verbose, long form)")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
