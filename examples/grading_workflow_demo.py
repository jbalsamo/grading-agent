"""
Grading Workflow Demo: Multi-Agent Grading Pipeline

This example demonstrates the automatic multi-agent grading workflow:
Master Agent → Grading Agent → Formatting Agent → (Optional) Chat Agent

Run:
    python examples/grading_workflow_demo.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.master_agent import MasterAgent


# Sample clinical note for grading
SAMPLE_CLINICAL_NOTE = """
Please grade this clinical student note:

**Patient:** John Doe, 45-year-old male
**Chief Complaint:** Chest pain

**History of Present Illness:**
Patient presents with sudden onset chest pain that started 2 hours ago while at rest.
Pain is described as pressure-like, 7/10 severity, radiating to left arm.
Associated with shortness of breath and diaphoresis.

**Vital Signs:**
- BP: 140/90 mmHg
- HR: 95 bpm
- RR: 18 breaths/min
- Temp: 98.6°F
- SpO2: 97% on room air

**Physical Exam:**
- General: Alert, oriented, appears uncomfortable
- Cardiovascular: Regular rate and rhythm, no murmurs
- Respiratory: Clear to auscultation bilaterally
- Extremities: No edema

**Assessment:**
Acute chest pain, concerning for acute coronary syndrome

**Plan:**
1. EKG immediately
2. Cardiac enzymes (troponin, CK-MB)
3. Chest X-ray
4. Aspirin 325mg PO
5. Oxygen therapy if SpO2 < 95%
6. Cardiology consult
7. Continuous cardiac monitoring
"""


async def basic_grading_workflow():
    """Demonstrate automatic grading workflow."""
    print("=" * 80)
    print("EXAMPLE 1: Automatic Grading Workflow")
    print("=" * 80)
    
    agent = MasterAgent()
    
    print("\n📋 Clinical Note to Grade:")
    print("-" * 80)
    print(SAMPLE_CLINICAL_NOTE[:300] + "...")
    print("-" * 80)
    
    print("\n🔄 Starting automatic grading workflow...\n")
    
    current_agent = None
    agent_outputs = {}
    
    async for event in agent.chat_streaming(SAMPLE_CLINICAL_NOTE):
        agent_name = event.get('agent')
        
        if event['type'] == 'status':
            print(f"\n📊 [{agent_name}] {event['content']}")
            current_agent = agent_name
            if agent_name not in agent_outputs:
                agent_outputs[agent_name] = ""
                
        elif event['type'] == 'chunk':
            print(event['content'], end='', flush=True)
            if current_agent:
                agent_outputs[current_agent] += event['content']
                
        elif event['type'] == 'complete':
            print(f"\n✅ {agent_name} completed!")
            
        elif event['type'] == 'error':
            print(f"\n❌ Error: {event['content']}")
    
    print("\n\n" + "=" * 80)
    print("WORKFLOW SUMMARY")
    print("=" * 80)
    
    for agent_name, output in agent_outputs.items():
        print(f"\n📌 {agent_name.upper()} Agent:")
        print(f"   Output length: {len(output)} characters")
        print(f"   Preview: {output[:100]}...")
    
    print("\n" + "=" * 80)


async def grading_with_progress_visualization():
    """Show workflow progress visually."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 2: Grading Workflow with Visual Progress")
    print("=" * 80)
    
    from modules.streaming import StreamingProgressTracker
    
    agent = MasterAgent()
    tracker = StreamingProgressTracker(
        expected_agents=['grading', 'formatting', 'chat']
    )
    
    print("\n🔄 Processing grading request with progress tracking...\n")
    
    workflow_steps = []
    
    async for event in agent.chat_streaming("Grade this student assignment: Good work on sections A and B."):
        agent_name = event.get('agent')
        
        if event['type'] == 'status':
            if 'starting' in event['content'].lower() or 'processing' in event['content'].lower():
                tracker.start_agent(agent_name)
                workflow_steps.append(agent_name)
                print(f"\n{'→ ' * len(workflow_steps)}🔄 {agent_name}")
                
        elif event['type'] == 'chunk':
            tracker.add_chunk(agent_name, event['content'])
            # Show abbreviated output
            if len(event['content']) > 0:
                print(".", end='', flush=True)
                
        elif event['type'] == 'complete':
            tracker.complete_agent(agent_name)
            progress = tracker.get_overall_progress()
            print(f"\n✅ {agent_name} done! Overall progress: {progress:.0f}%")
    
    print("\n\n" + "-" * 80)
    print("📊 WORKFLOW METRICS:")
    metrics = tracker.get_metrics()
    print(f"   Total Duration: {metrics['duration']:.2f}s")
    print(f"   Agents Used: {metrics['total_agents']}")
    print(f"   Total Chunks: {metrics['total_chunks']}")
    print(f"   Total Output: {metrics['total_chars']} characters")
    print("=" * 80)


async def compare_agents_side_by_side():
    """Compare what each agent in the workflow does."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 3: Agent Comparison (What Each Agent Does)")
    print("=" * 80)
    
    agent = MasterAgent()
    
    grading_request = """
    Grade this assignment:
    
    Student: Jane Smith
    Section A: 8/10 points
    Section B: 7/10 points
    Total: 15/20
    """
    
    print("\n📝 Request:", grading_request)
    print("\n🔄 Processing through multi-agent pipeline...\n")
    
    current_agent = None
    agent_sections = {}
    
    async for event in agent.chat_streaming(grading_request):
        agent_name = event.get('agent')
        
        if event['type'] == 'status' and agent_name:
            current_agent = agent_name
            if agent_name not in agent_sections:
                agent_sections[agent_name] = []
            print(f"\n{'=' * 80}")
            print(f"AGENT: {agent_name.upper()}")
            print(f"{'=' * 80}")
            
        elif event['type'] == 'chunk' and current_agent:
            agent_sections[current_agent].append(event['content'])
            print(event['content'], end='', flush=True)
            
        elif event['type'] == 'complete':
            print(f"\n{'-' * 80}")
    
    # Show summary
    print("\n\n" + "=" * 80)
    print("AGENT CONTRIBUTIONS SUMMARY")
    print("=" * 80)
    
    roles = {
        'master': '🧠 Classifies and routes',
        'grading': '📊 Evaluates performance',
        'formatting': '📋 Creates tables',
        'chat': '💬 Adds explanations'
    }
    
    for agent_name in agent_sections:
        role = roles.get(agent_name, '❓ Unknown role')
        content = ''.join(agent_sections[agent_name])
        print(f"\n{agent_name.upper()}: {role}")
        print(f"   Output: {len(content)} chars")
    
    print("\n" + "=" * 80)


async def formatting_agent_showcase():
    """Highlight the FormattingAgent's capabilities."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 4: FormattingAgent Showcase")
    print("=" * 80)
    
    from modules.agents.formatting_agent import FormattingAgent
    
    formatter = FormattingAgent()
    
    # Sample grading data
    grading_data = """
    Student: Alex Johnson
    
    Section PS (Patient Safety): 8/10 (AI) vs 9/10 (Human)
    Section DX (Diagnosis): 7/10 (AI) vs 7/10 (Human)
    Section TX (Treatment): 9/10 (AI) vs 8/10 (Human)
    
    Total: 24/30 (AI) vs 24/30 (Human)
    """
    
    print("\n📝 Raw Grading Data:")
    print("-" * 80)
    print(grading_data)
    print("-" * 80)
    
    print("\n🔄 Formatting with FormattingAgent (streaming)...\n")
    print("=" * 80)
    
    async for chunk in formatter.stream_process(grading_data):
        print(chunk, end='', flush=True)
    
    print("\n" + "=" * 80)
    print("✅ Formatted as professional spreadsheet-style table!")
    print("=" * 80)


async def main():
    """Run all grading workflow examples."""
    print("\n" + "🎓" * 40)
    print("GRADING WORKFLOW DEMO - Multi-Agent Pipeline")
    print("🎓" * 40 + "\n")
    
    try:
        await basic_grading_workflow()
        await grading_with_progress_visualization()
        await compare_agents_side_by_side()
        await formatting_agent_showcase()
        
        print("\n\n" + "✅" * 40)
        print("All grading workflow examples completed!")
        print("✅" * 40 + "\n")
        
        print("\n💡 KEY TAKEAWAYS:")
        print("   1. Grading requests automatically use multi-agent workflow")
        print("   2. Master → Grading → Formatting → (Optional) Chat")
        print("   3. Real-time streaming shows each agent's progress")
        print("   4. FormattingAgent creates professional tables")
        print("   5. All agents share conversation history")
        
    except KeyboardInterrupt:
        print("\n\n⏸️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running demos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
