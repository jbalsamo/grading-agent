"""
Main application entry point for the Azure OpenAI Master Agent System.
"""
import logging
from master_agent import MasterAgent
from config import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the Azure OpenAI Master Agent System."""
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
                    print("   • help - Show this help message")
                    print("   • quit/exit/bye - Exit the system")
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
                
                if not user_input:
                    print("⚠️  Please enter a message.")
                    continue
                
                print("🤔 Processing with Master Agent System...")
                response = agent.chat(user_input)
                print(f"🤖 Master Assistant: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for using the Master Agent System!")
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
