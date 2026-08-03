# URL Shortener : Project Evolution Log

This document tracks the major milestones and design decisions made while building the system.

## 2026-07-30 : Project Initialization

**Goal:** Build a production-style URL shortener while learning backend architecture.

**Initial stack chosen:**
- FastAPI for API development
- PostgreSQL for persistent storage
- SQLAlchemy as ORM
- Docker Compose for local infrastructure

**Reasoning:**
The project was designed to focus on backend concepts such as persistence, caching, scalability, and system design rather than just creating a working API.

## 2026-07-30 : Database Design

**Decision:** PostgreSQL + SQLAlchemy

**Stored data:**
- Original long URL
- Short code
- Creation timestamp
- Click count

**Why:**
URL mappings have a fixed structure and benefit from relational querying and consistency.

## 2026-07-31 : Short Code Generation

**Initial approach:**
Random short strings.

**Problem discovered:**
Random generation requires collision handling and additional database checks.

**Final approach:**
Sequential database ID + Base62 encoding.

Example:
```
Database ID → Base62 → Short Code
12345       → 3D7    → /3D7
```

**Benefits:**
- Guaranteed uniqueness
- URL-safe characters
- No collision retries

## 2026-07-31 : Application Refactoring

The initial application had multiple responsibilities inside `main.py`.

The project was restructured into:
```
config.py          → environment configuration
database.py        → database connection
dependencies.py    → reusable dependencies
models.py          → database models
schemas.py         → API validation
services/          → business logic
main.py            → application entry point
```

**Goal:**
Improve maintainability and make future features easier to add.

## 2026-08-03 : Redis Caching Layer

**Problem:**
Every redirect request required a PostgreSQL lookup.

```
Request
   ↓
PostgreSQL
   ↓
Redirect
```

**Solution:**
Implemented Redis using the cache-aside pattern.

New flow:
```
Request
   ↓
Redis
   ↓
Cache hit → Redirect

Cache miss
   ↓
PostgreSQL
   ↓
Store in Redis
   ↓
Redirect
```

**Benefits:**
- Reduced database reads
- Faster redirects
- Demonstrates production caching strategy

## 2026-08-04 : Short code generation

**Problem:**
- Sequential Base62 produced predictable short codes.

**Decision:**
- Add configurable offset before Base62 encoding.

**Reason:**
- Maintains collision-free generation while preventing obvious sequential URLs.