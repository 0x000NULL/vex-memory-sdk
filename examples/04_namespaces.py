"""
Example 4: Namespace Organization

Demonstrates organizing memories with namespaces.
"""

from vex_memory import MemoryClient

def main():
    client = MemoryClient("http://localhost:8000")
    
    print("=== Creating Namespaces ===\n")
    
    # Create namespaces for different contexts
    work_ns = client.create_namespace(
        "work",
        owner="agent-alice",
        description="Work-related memories"
    )
    print(f"Created work namespace: {work_ns.namespace_id}")
    
    personal_ns = client.create_namespace(
        "personal",
        owner="agent-alice",
        description="Personal memories"
    )
    print(f"Created personal namespace: {personal_ns.namespace_id}")
    
    print("\n=== Storing to Different Namespaces ===\n")
    
    # Use work namespace
    client.use_namespace("work")
    client.store("Team meeting scheduled for Monday 9am")
    client.store("Q2 roadmap approved by management")
    print("  ✓ Stored work memories")
    
    # Use personal namespace
    client.use_namespace("personal")
    client.store("Remember to buy groceries")
    client.store("Dentist appointment next Tuesday")
    print("  ✓ Stored personal memories")
    
    print("\n=== Searching Within Namespaces ===\n")
    
    # Search in work namespace
    client.use_namespace("work")
    work_results = client.search("meeting")
    print(f"Work memories about 'meeting': {len(work_results)}")
    for memory in work_results:
        print(f"  - {memory.content}")
    
    # Search in personal namespace
    client.use_namespace("personal")
    personal_results = client.search("appointment")
    print(f"\nPersonal memories about 'appointment': {len(personal_results)}")
    for memory in personal_results:
        print(f"  - {memory.content}")
    
    print("\n=== Using Context Manager ===\n")
    
    # Temporarily switch namespace
    with client.namespace("work"):
        print("Inside work namespace:")
        results = client.search("roadmap")
        for memory in results:
            print(f"  - {memory.content}")
    
    # Automatically switched back
    print("\nBack to default namespace")
    
    print("\n=== Listing Namespaces ===\n")
    
    namespaces = client.list_namespaces()
    print(f"Total namespaces: {len(namespaces)}")
    for ns in namespaces:
        print(f"  - {ns.name} (owner: {ns.owner_agent})")
    
    print("\n=== Resource API ===\n")
    
    # Create namespace using resource API
    test_ns = client.namespaces.create("test", owner="agent-alice")
    print(f"Created namespace via resource API: {test_ns.name}")
    
    # List using resource API
    all_ns = client.namespaces.list()
    print(f"Total namespaces (resource API): {len(all_ns)}")


if __name__ == "__main__":
    main()
