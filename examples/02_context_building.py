"""
Example 2: Context Building

Demonstrates building context for LLM prompts.
"""

from vex_memory import MemoryClient

def main():
    client = MemoryClient("http://localhost:8000")
    
    print("=== Storing Knowledge Base ===\n")
    
    # Store some facts about a project
    facts = [
        "Project Nebula is a distributed task scheduler",
        "Nebula uses PostgreSQL for task storage",
        "The team decided to use Python 3.11 for better performance",
        "Alice is the tech lead, Bob handles DevOps",
        "We're targeting Q2 2026 for beta release",
        "Current sprint focuses on authentication module",
    ]
    
    for fact in facts:
        memory = client.store(fact, importance=0.7)
        print(f"  ✓ Stored: {fact}")
    
    print("\n=== Building Context for LLM ===\n")
    
    # Build context about the project
    context = client.build_context(
        "What is Project Nebula and who is working on it?",
        max_tokens=2000,
        include_metadata=False
    )
    
    print("Generated context:")
    print("-" * 60)
    print(context)
    print("-" * 60)
    print()
    
    # Use context in an LLM prompt (simulated)
    llm_prompt = f"""
{context}

Based on the context above, answer this question:
What is Project Nebula and what's the current status?

Answer:
"""
    
    print("LLM Prompt (ready to send):")
    print("=" * 60)
    print(llm_prompt)
    print("=" * 60)
    print()
    
    # Build targeted context
    print("=== Targeted Context ===\n")
    
    tech_context = client.build_context("What technologies are being used?")
    print("Tech stack context:")
    print(tech_context)
    print()
    
    team_context = client.build_context("Who is on the team?")
    print("Team context:")
    print(team_context)


if __name__ == "__main__":
    main()
