"""
Example 1: Basic Usage

Demonstrates simple memory storage and retrieval.
"""

from vex_memory import MemoryClient

def main():
    # Initialize client
    client = MemoryClient("http://localhost:8000")
    
    print("=== Basic Memory Storage ===\n")
    
    # Store a simple memory
    memory1 = client.store("Python 3.12 was released in October 2023")
    print(f"Stored memory: {memory1.id}")
    print(f"Content: {memory1.content}\n")
    
    # Store with metadata
    memory2 = client.store(
        "Met with Alice to discuss Q2 roadmap",
        importance=0.8,
        metadata={
            "attendees": ["Alice", "Bob"],
            "date": "2026-02-28",
            "category": "meeting"
        }
    )
    print(f"Stored meeting memory: {memory2.id}")
    print(f"Importance: {memory2.importance_score}\n")
    
    # Retrieve a memory
    retrieved = client.get(memory1.id)
    print(f"Retrieved memory: {retrieved.content}\n")
    
    print("=== Searching Memories ===\n")
    
    # Simple search
    results = client.search("Python")
    print(f"Found {len(results)} memories about Python:")
    for memory in results:
        print(f"  - {memory.content}")
    print()
    
    # Search with filters
    results = client.search("meetings", limit=5)
    print(f"Found {len(results)} memories about meetings:")
    for memory in results:
        print(f"  - {memory.content} (importance: {memory.importance_score})")
    print()
    
    # Find single best match
    best = client.find_one("most important recent event")
    if best:
        print(f"Most important: {best.content}\n")
    
    print("=== Updating and Deleting ===\n")
    
    # Update a memory
    updated = client.update(
        memory1.id,
        importance=0.9,
        metadata={"verified": True}
    )
    print(f"Updated importance: {updated.importance_score}")
    print(f"Updated metadata: {updated.metadata}\n")
    
    # Delete a memory
    client.delete(memory1.id)
    print(f"Deleted memory: {memory1.id}\n")
    
    # Verify deletion
    try:
        client.get(memory1.id)
    except Exception as e:
        print(f"Confirmed deletion: {type(e).__name__}")


if __name__ == "__main__":
    main()
