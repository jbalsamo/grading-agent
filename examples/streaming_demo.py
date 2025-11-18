"""
Streaming Demo: Basic Real-Time Streaming Example

This example demonstrates the basic streaming capabilities of the grading agent,
showing how to receive real-time responses with progress indicators.

Run:
    python examples/streaming_demo.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.master_agent import MasterAgent


async def basic_streaming_example():
    """Demonstrate basic streaming with visual feedback."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Streaming")
    print("=" * 70)
    
    agent = MasterAgent()
    
    print("\n🔄 Streaming response for: 'Tell me about Python'\n")
    print("-" * 70)
    
    full_response = ""
    chunk_count = 0
    
    async for event in agent.chat_streaming("Tell me about Python programming"):
        if event['type'] == 'status':
            print(f"\n📊 [{event['agent']}] {event['content']}")
        elif event['type'] == 'chunk':
            print(event['content'], end='', flush=True)
            full_response += event['content']
            chunk_count += 1
        elif event['type'] == 'complete':
            print(f"\n✅ {event['agent']} completed!")
        elif event['type'] == 'error':
            print(f"\n❌ Error: {event['content']}")
    
    print("\n" + "-" * 70)
    print(f"📈 Stats: {chunk_count} chunks, {len(full_response)} characters")
    print("=" * 70)


async def streaming_with_progress():
    """Demonstrate streaming with progress tracking."""
    print("\n\n" + "=" * 70)
    print("EXAMPLE 2: Streaming with Progress Tracking")
    print("=" * 70)
    
    from modules.streaming import StreamingProgressTracker
    
    agent = MasterAgent()
    tracker = StreamingProgressTracker(expected_agents=['chat'])
    
    print("\n🔄 Asking: 'What are the key features of async/await in Python?'\n")
    print("-" * 70)
    
    current_agent = None
    
    async for event in agent.chat_streaming(
        "What are the key features of async/await in Python?"
    ):
        agent_name = event.get('agent')
        
        if event['type'] == 'status':
            if current_agent is None and agent_name:
                tracker.start_agent(agent_name)
                current_agent = agent_name
            print(f"\n📊 [{agent_name}] {event['content']}")
            
        elif event['type'] == 'chunk':
            if current_agent:
                tracker.add_chunk(current_agent, event['content'])
            print(event['content'], end='', flush=True)
            
        elif event['type'] == 'complete':
            if current_agent:
                tracker.complete_agent(current_agent)
            print(f"\n✅ {agent_name} completed!")
            
            # Show progress
            progress = tracker.get_overall_progress()
            print(f"📊 Overall Progress: {progress:.1f}%")
    
    print("\n" + "-" * 70)
    metrics = tracker.get_metrics()
    print(f"📈 Final Metrics:")
    print(f"   - Duration: {metrics['duration']:.2f}s")
    print(f"   - Total Chunks: {metrics['total_chunks']}")
    print(f"   - Total Characters: {metrics['total_chars']}")
    print("=" * 70)


async def streaming_with_cancellation():
    """Demonstrate streaming cancellation."""
    print("\n\n" + "=" * 70)
    print("EXAMPLE 3: Streaming with Early Cancellation")
    print("=" * 70)
    
    agent = MasterAgent()
    
    print("\n🔄 Starting stream, will cancel after 5 chunks...\n")
    print("-" * 70)
    
    chunk_count = 0
    max_chunks = 5
    
    try:
        async for event in agent.chat_streaming(
            "Write a long story about artificial intelligence"
        ):
            if event['type'] == 'chunk':
                print(event['content'], end='', flush=True)
                chunk_count += 1
                
                if chunk_count >= max_chunks:
                    print(f"\n\n⏸️ Cancelling after {max_chunks} chunks...")
                    break
            elif event['type'] == 'status':
                print(f"\n📊 {event['content']}")
    except Exception as e:
        print(f"\n❌ Error during streaming: {e}")
    
    print("\n" + "-" * 70)
    print(f"📈 Received {chunk_count} chunks before cancellation")
    print("=" * 70)


async def compare_blocking_vs_streaming():
    """Compare blocking vs streaming approaches."""
    print("\n\n" + "=" * 70)
    print("EXAMPLE 4: Blocking vs Streaming Comparison")
    print("=" * 70)
    
    import time
    
    agent = MasterAgent()
    query = "What is machine learning?"
    
    # Blocking approach
    print("\n🔄 BLOCKING APPROACH (Traditional):")
    print("-" * 70)
    start = time.time()
    print("⏳ Waiting for complete response...")
    response = agent.chat(query)
    blocking_time = time.time() - start
    print(f"⏱️ Time to first output: {blocking_time:.2f}s")
    print(f"📝 Response: {response[:100]}...")
    
    # Streaming approach
    print("\n\n🔄 STREAMING APPROACH (New):")
    print("-" * 70)
    start = time.time()
    first_chunk_time = None
    
    async for event in agent.chat_streaming(query):
        if event['type'] == 'chunk':
            if first_chunk_time is None:
                first_chunk_time = time.time() - start
                print(f"⚡ Time to first chunk: {first_chunk_time:.2f}s")
                print("📝 Response: ", end='')
            print(event['content'], end='', flush=True)
    
    total_time = time.time() - start
    
    print("\n\n" + "-" * 70)
    print("📊 COMPARISON:")
    print(f"   Blocking - Time to first output: {blocking_time:.2f}s")
    print(f"   Streaming - Time to first chunk: {first_chunk_time:.2f}s")
    print(f"   Improvement: {((blocking_time - first_chunk_time) / blocking_time * 100):.1f}%")
    print("=" * 70)


async def main():
    """Run all examples."""
    print("\n" + "🚀" * 35)
    print("STREAMING DEMO - Grading Agent Examples")
    print("🚀" * 35 + "\n")
    
    try:
        # Run all examples
        await basic_streaming_example()
        await streaming_with_progress()
        await streaming_with_cancellation()
        await compare_blocking_vs_streaming()
        
        print("\n\n" + "✅" * 35)
        print("All examples completed successfully!")
        print("✅" * 35 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⏸️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running demos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run async main
    asyncio.run(main())
