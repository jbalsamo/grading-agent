"""
Main application entry point for the Azure OpenAI Master Agent System.
"""
import logging
import argparse
from modules.master_agent import MasterAgent
from modules.config import config
from modules.security import InputValidationException, RateLimitException

logger = logging.getLogger(__name__)

def setup_logging(verbose: bool = False):
    """Set up logging configuration based on verbose flag.
    
    Args:
        verbose: If True, show INFO level logs. If False, show WARNING and above only.
    """
    log_level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True  # Force reconfiguration if already configured
    )
    if verbose:
        print("📝 Verbose logging enabled (INFO level)")
    else:
        print("🔇 Quiet mode (WARNING level and above)")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Azure OpenAI Master Agent System - Multi-agent chat application with conversation history',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s              # Run in quiet mode
  %(prog)s -v           # Run with verbose logging
  %(prog)s --verbose    # Run with verbose logging (long form)

Available commands during chat:
  status         - Show system status
  stats          - Show performance statistics
  health         - Run health check
  history        - Show conversation history stats
  clear-history  - Clear conversation history
  help           - Show help message
  quit/exit/bye  - Exit the system
        """
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging (show INFO level logs)'
    )
    return parser.parse_args()

def main():
    """Main function to run the Azure OpenAI Master Agent System."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Set up logging based on verbose flag
    setup_logging(verbose=args.verbose)
    
    print("🚀 Starting Azure OpenAI Master Agent System...")
    print("=" * 60)
    
    try:
        # Initialize the master agent
        print("📡 Initializing Master Agent System...")
        agent = MasterAgent()
        
        # Display configuration info
        info = agent.get_info()
        status = agent.get_agent_status()
        
        print(f"✅ Master Agent System initialized successfully!")
        print(f"🔗 Endpoint: {info['endpoint']}")
        print(f"🤖 Deployment: {info['deployment']}")
        print(f"📋 API Version: {info['api_version']}")
        print(f"🎯 Specialized Agents: {', '.join(info['specialized_agents']) if info['specialized_agents'] else 'None'}")
        print(f"💾 Data Manager: {'Active' if info['data_manager_available'] else 'Inactive'}")
        print("=" * 60)
        
        # Send hello message
        print("💬 Sending hello message to Azure OpenAI...")
        hello_message = "Hello! Can you introduce yourself and tell me what you can help me with?"
        
        print(f"👤 User: {hello_message}")
        print("🤔 Thinking...")
        
        # Get response from the agent
        response = agent.chat(hello_message)
        
        print(f"🤖 Master Assistant: {response}")
        print("=" * 60)
        
        # Interactive chat loop
        print("💡 You can now chat with the Master Agent System!")
        print("💡 The system will automatically route your requests to specialized agents.")
        print("💡 Type 'quit', 'exit', or 'status' for system status. Type 'help' for commands.")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    agent.shutdown()
                    print("👋 Goodbye! Thanks for using the Master Agent System!")
                    break
                
                if user_input.lower() == 'status':
                    status = agent.get_agent_status()
                    print("\n📊 System Status:")
                    print(f"   Master Agent: {status['master_agent']}")
                    print(f"   Data Manager: {status['data_manager']}")
                    if status['specialized_agents']:
                        print("   Specialized Agents:")
                        for agent_name, agent_status in status['specialized_agents'].items():
                            print(f"     - {agent_name}: {agent_status}")
                    continue
                
                if user_input.lower() == 'help':
                    print("\n🆘 Available Commands:")
                    print("   • status - Show system status")
                    print("   • stats - Show performance statistics")
                    print("   • health - Run health check")
                    print("   • history - Show conversation history stats")
                    print("   • clear-history - Clear conversation history")
                    print("   • save - Manually save conversation history")
                    print("   • cache - Show cache statistics")
                    print("   • clear-cache - Clear response cache")
                    print("   • metrics - Show monitoring metrics")
                    print("   • export-metrics - Export metrics to file")
                    print("   • help - Show this help message")
                    print("   • quit/exit/bye - Exit the system (auto-saves)")
                    print("   • Any other input - Chat with the system")
                    continue
                
                if user_input.lower() == 'stats':
                    stats = agent.get_performance_stats()
                    print("\n📈 Performance Statistics:")
                    print(f"   Uptime: {stats['uptime_formatted']}")
                    print(f"   Total Requests: {stats['total_requests']}")
                    print(f"   Error Rate: {stats['error_rate']:.1f}%")
                    print(f"   Avg Response Time: {stats['average_response_time']:.2f}s")
                    print(f"   Requests/Minute: {stats['requests_per_minute']:.1f}")
                    if stats['agent_usage']:
                        print("   Agent Usage:")
                        for agent_name, usage in stats['agent_usage'].items():
                            print(f"     - {agent_name}: {usage['requests']} requests, {usage['avg_time']:.2f}s avg")
                    continue
                
                if user_input.lower() == 'health':
                    print("🔍 Running health check...")
                    health = agent.run_health_check()
                    print(f"\n🏥 Health Check Results:")
                    print(f"   Overall Status: {health['overall_status'].upper()}")
                    for check_name, check_result in health['checks'].items():
                        status_emoji = "✅" if check_result['status'] == 'pass' else "⚠️" if check_result['status'] == 'warning' else "❌"
                        print(f"   {status_emoji} {check_name.replace('_', ' ').title()}: {check_result['status']}")
                    continue
                
                if user_input.lower() == 'history':
                    history_info = agent.get_conversation_history()
                    print("\n💬 Conversation History:")
                    stats = history_info['stats']
                    print(f"   Total Messages: {stats['total_messages']}")
                    print(f"   User Messages: {stats['user_messages']}")
                    print(f"   Assistant Messages: {stats['assistant_messages']}")
                    if stats['agent_usage']:
                        print("   Agent Usage:")
                        for agent_name, count in stats['agent_usage'].items():
                            print(f"     - {agent_name}: {count} responses")
                    if stats['total_messages'] > 0:
                        print(f"\n📝 Recent Context (last 5 messages):")
                        recent_context = agent.conversation_history.get_recent_context(5)
                        print(recent_context)
                    continue
                
                if user_input.lower() == 'clear-history':
                    agent.clear_conversation_history()
                    # Also delete the saved file
                    agent.conversation_history.delete_saved_history()
                    print("🗑️  Conversation history cleared!")
                    continue
                
                if user_input.lower() == 'save':
                    print("💾 Saving conversation history...")
                    if agent.save_conversation_history():
                        print(f"✅ Saved {len(agent.conversation_history)} messages to disk")
                    else:
                        print("⚠️  Failed to save conversation history")
                    continue
                
                if user_input.lower() == 'cache':
                    cache_stats = agent.get_cache_stats()
                    print("\n💨 Cache Statistics:")
                    print(f"   Enabled: {cache_stats['enabled']}")
                    print(f"   Size: {cache_stats['size']}/{cache_stats['max_size']}")
                    print(f"   Hits: {cache_stats['hits']}")
                    print(f"   Misses: {cache_stats['misses']}")
                    print(f"   Hit Rate: {cache_stats['hit_rate']}%")
                    print(f"   TTL: {cache_stats['ttl']}s")
                    continue
                
                if user_input.lower() == 'clear-cache':
                    agent.clear_cache()
                    print("🗑️  Response cache cleared!")
                    continue
                
                if user_input.lower() == 'metrics':
                    metrics = agent.get_metrics()
                    print("\n📊 Monitoring Metrics:")
                    print(f"   Uptime: {metrics['uptime_seconds']}s")
                    print(f"   Total Requests: {metrics['total_requests']}")
                    print(f"   Total Errors: {metrics['total_errors']}")
                    print(f"   Error Rate: {metrics['overall_error_rate']}%")
                    if metrics['agents']:
                        print("   Agent Metrics:")
                        for agent_name, agent_metrics in metrics['agents'].items():
                            print(f"     - {agent_name}:")
                            print(f"       Requests: {agent_metrics['request_count']}")
                            print(f"       Avg Duration: {agent_metrics['average_duration']}s")
                            print(f"       Errors: {agent_metrics['error_count']}")
                    continue
                
                if user_input.lower() == 'export-metrics':
                    print("📊 Exporting metrics...")
                    agent.export_metrics()
                    print("✅ Metrics exported to metrics.json")
                    continue
                
                if not user_input:
                    print("⚠️  Please enter a message.")
                    continue
                
                print("🤔 Processing with Master Agent System...")
                try:
                    response = agent.chat(user_input)
                    print(f"🤖 Master Assistant: {response}")
                except InputValidationException as e:
                    print(f"⚠️  Input validation error: {e}")
                except RateLimitException as e:
                    print(f"⏱️  {e}")
                
            except KeyboardInterrupt:
                print("\n")
                agent.shutdown()
                print("\n👋 Goodbye! Thanks for using the Master Agent System!")
                break
            except Exception as e:
                print(f"❌ Error during chat: {e}")
                logger.error(f"Chat error: {e}")
    
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        logger.error(f"Initialization error: {e}")
        print("\n🔧 Please check your .env file configuration:")
        print("   - AZURE_OPENAI_ENDPOINT")
        print("   - AZURE_OPENAI_API_KEY") 
        print("   - AZURE_OPENAI_CHAT_DEPLOYMENT")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
