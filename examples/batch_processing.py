#!/usr/bin/env python3
"""
Example: Batch processing with the Master Agent System.
This script demonstrates how to process multiple requests programmatically.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.master_agent import MasterAgent
import json
import time

def main():
    """Demonstrate batch processing capabilities."""
    print("🔄 Master Agent System - Batch Processing Example")
    print("=" * 60)
    
    # Initialize the master agent
    print("📡 Initializing Master Agent...")
    try:
        agent = MasterAgent()
        print("✅ Master Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return 1
    
    # Sample requests for different agent types
    sample_requests = [
        {
            "type": "chat",
            "request": "What is artificial intelligence?",
            "expected_agent": "chat"
        },
        {
            "type": "analysis", 
            "request": "Analyze the performance trends in this data: [1, 3, 5, 7, 9, 11]",
            "expected_agent": "analysis"
        },
        {
            "type": "grading",
            "request": "Grade this essay response: 'The water cycle is important because it helps plants grow.'",
            "expected_agent": "grading"
        },
        {
            "type": "chat",
            "request": "Tell me a joke about programming",
            "expected_agent": "chat"
        }
    ]
    
    results = []
    
    print(f"\n🚀 Processing {len(sample_requests)} requests...")
    print("-" * 60)
    
    for i, request_data in enumerate(sample_requests, 1):
        print(f"\n📝 Request {i}/{len(sample_requests)} ({request_data['type']}):")
        print(f"   Input: {request_data['request'][:50]}...")
        
        start_time = time.time()
        
        try:
            response = agent.chat(request_data['request'])
            processing_time = time.time() - start_time
            
            result = {
                "request_id": i,
                "type": request_data['type'],
                "request": request_data['request'],
                "response": response,
                "processing_time": processing_time,
                "success": True
            }
            
            print(f"   ✅ Processed in {processing_time:.2f}s")
            print(f"   Response: {response[:100]}...")
            
        except Exception as e:
            processing_time = time.time() - start_time
            result = {
                "request_id": i,
                "type": request_data['type'],
                "request": request_data['request'],
                "error": str(e),
                "processing_time": processing_time,
                "success": False
            }
            
            print(f"   ❌ Error after {processing_time:.2f}s: {e}")
        
        results.append(result)
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("📊 Batch Processing Summary")
    print("=" * 60)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"Total Requests: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        avg_time = sum(r['processing_time'] for r in successful) / len(successful)
        print(f"Average Processing Time: {avg_time:.2f}s")
    
    # Get performance stats
    stats = agent.get_performance_stats()
    print(f"\nSystem Performance:")
    print(f"  Total System Requests: {stats['total_requests']}")
    print(f"  Error Rate: {stats['error_rate']:.1f}%")
    print(f"  Uptime: {stats['uptime_formatted']}")
    
    # Save results to file
    output_file = "batch_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "summary": {
                "total_requests": len(results),
                "successful": len(successful),
                "failed": len(failed),
                "average_time": avg_time if successful else 0
            },
            "results": results,
            "system_stats": stats
        }, f, indent=2)
    
    print(f"\n💾 Results saved to {output_file}")
    
    return 0 if not failed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
