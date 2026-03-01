# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-28

### Added

**Core Features:**
- ✅ Memory CRUD operations (create, read, update, delete)
- ✅ Semantic search with vector similarity
- ✅ Context building for LLM prompts
- ✅ Session management for conversation tracking
- ✅ Namespace support for memory organization
- ✅ Bulk operations for efficient batch processing
- ✅ Module-level shortcuts for quick scripts

**API Design:**
- ✅ Simple API for beginners (`client.store()`, `client.search()`)
- ✅ Resource-based API for power users (`client.memories.create()`)
- ✅ Context manager support (`with MemoryClient():`)
- ✅ Environment variable configuration

**Resilience:**
- ✅ Automatic retry with exponential backoff
- ✅ Circuit breaker pattern (optional, can be disabled)
- ✅ Comprehensive error handling with clear exceptions
- ✅ Timeout handling

**Developer Experience:**
- ✅ Type-safe Pydantic models
- ✅ Comprehensive docstrings
- ✅ Examples for common use cases
- ✅ Clean, intuitive API

**Testing:**
- ✅ Unit tests for all core functionality
- ✅ Integration tests against live server
- ✅ Test fixtures and helpers

**Documentation:**
- ✅ Comprehensive README
- ✅ API reference
- ✅ Examples directory
- ✅ Inline documentation

### Notes

Initial release of vex-memory Python SDK implementing Plan D (Best-of-Breed) design.

**Compatibility:**
- Tested against vex-memory server v0.3.1
- Python 3.8+ required
- Uses requests, pydantic v2, tenacity

**Design Philosophy:**
- Sync-first architecture (async planned for v2.0)
- Progressive complexity (simple → advanced → expert)
- Proven patterns over novel approaches
- Production-ready from day one

### Known Limitations

**Deferred to v1.1:**
- Graph API (needs proper design)
- Advanced namespace ACL operations
- Response caching
- Streaming optimizations

**Deferred to v2.0:**
- Async/await support (`AsyncMemoryClient`)
- HTTP/2 optimizations
- Local-first mode

---

## [Unreleased]

### Planned for v1.1 (March 2026)

- [ ] Graph API for relationship queries
- [ ] Advanced namespace access control
- [ ] Entity extraction helpers
- [ ] Timeline queries
- [ ] Response caching
- [ ] Performance optimizations

### Planned for v2.0 (Q2 2026)

- [ ] AsyncMemoryClient with identical API
- [ ] HTTP/2 support
- [ ] Local-first mode with offline support
- [ ] Advanced graph operations
- [ ] Bulk graph linking

---

[1.0.0]: https://github.com/0x000NULL/vex-memory-sdk/releases/tag/v1.0.0
