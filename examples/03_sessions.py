"""
Example 3: Session Management

Demonstrates conversation session tracking.
"""

from vex_memory import MemoryClient

def main():
    client = MemoryClient("http://localhost:8000")
    
    print("=== Creating Conversation Session ===\n")
    
    # Create a session
    session = client.create_session(
        "chat-demo-001",
        metadata={"user": "alice", "app": "chatbot"}
    )
    print(f"Created session: {session.session_id}\n")
    
    # Add conversation messages
    print("=== Adding Messages ===\n")
    
    client.add_to_session(
        "chat-demo-001",
        role="user",
        content="What's the status of Project Nebula?"
    )
    print("  User: What's the status of Project Nebula?")
    
    client.add_to_session(
        "chat-demo-001",
        role="assistant",
        content="Project Nebula is on track for Q2 2026 beta release."
    )
    print("  Assistant: Project Nebula is on track for Q2 2026 beta release.")
    
    client.add_to_session(
        "chat-demo-001",
        role="user",
        content="Who's the tech lead?"
    )
    print("  User: Who's the tech lead?")
    
    client.add_to_session(
        "chat-demo-001",
        role="assistant",
        content="Alice is the tech lead for Project Nebula."
    )
    print("  Assistant: Alice is the tech lead for Project Nebula.")
    print()
    
    # Get session context
    print("=== Session Context ===\n")
    
    context = client.get_session_context("chat-demo-001", max_tokens=1000)
    print("Full conversation context:")
    print("-" * 60)
    print(context)
    print("-" * 60)
    print()
    
    # Get session details
    session = client.get_session("chat-demo-001")
    print(f"Session has {len(session.messages)} messages")
    print(f"Created: {session.created_at}")
    
    # Using resource API
    print("\n=== Resource API Example ===\n")
    
    # Create another session using resource API
    session2 = client.sessions.create("chat-demo-002")
    print(f"Created session via resource API: {session2.session_id}")
    
    # Add message using resource API
    client.sessions.add_message(
        "chat-demo-002",
        role="user",
        content="Hello, world!"
    )
    
    # Get context using resource API
    context2 = client.sessions.get_context("chat-demo-002", max_tokens=500)
    print(f"Context: {context2}")


if __name__ == "__main__":
    main()
