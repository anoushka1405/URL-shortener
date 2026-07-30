# Architecture Decision Log

This file documents every major architecture decision made in this project,
the alternatives considered, and why the chosen option won. Entries are
added *before* the corresponding code is written, not after.

---

## 2026-07-30 — Backend framework: FastAPI

**Decision:** FastAPI (Python)

**Alternatives considered:**
- **Node.js / Express** — equally valid, but I already know Flask/FastAPI.
  Learning backend *concepts* (routing, persistence, caching, system design)
  is the actual goal here, not a new language. Switching stacks mid-learning
  would trade concept-depth for syntax-relearning, with no real upside.
- **Flask** — FastAPI is Flask's modern successor for API work: built-in
  request/response validation via Pydantic, native async support, and
  automatic OpenAPI docs. For a project explicitly meant to look
  production-minded, FastAPI is the closer match to what's used in industry.

---

## 2026-07-30 — Database: PostgreSQL

**Decision:** PostgreSQL, accessed via SQLAlchemy (ORM)

**Alternatives considered:**
- **SQLite** — simpler to set up (just a file, no server), but doesn't
  handle concurrent writes well. A project that's also adding Redis caching
  and aiming to look production-realistic shouldn't be undercut by a
  storage layer that can't handle concurrent access. Also weaker to defend
  in an interview ("how would this scale?" → "it wouldn't").
- **NoSQL (MongoDB, etc.)** — the data here is inherently tabular/fixed-schema
  (short_code, long_url, created_at, click_count) with no nested or
  variable structure. Relational is the better semantic fit, and SQL
  querying (e.g. "top 10 most-clicked links") maps naturally onto it.
- **Raw SQL vs ORM** — using SQLAlchemy instead of hand-written SQL, but
  will inspect the generated SQL to make sure the underlying queries are
  understood, not just abstracted away.

---

## 2026-07-30 — Caching layer: Redis

**Decision:** Redis, using the cache-aside (lazy-loading) pattern

**Reasoning:** Reads (redirects) vastly outnumber writes (new short links
created) for this kind of system. Hitting Postgres on every single redirect
is unnecessary load for data that rarely changes once written. Redis sits
in front of Postgres for the read-hot path (`GET /{short_code}`):

1. Check Redis for the short_code.
2. On hit → return immediately, no DB query.
3. On miss → query Postgres, populate Redis, return.

**Alternatives considered:**
- **No caching** — simpler, but throws away a legitimate opportunity to
  demonstrate understanding of read/write asymmetry, a core system design
  concept.
- **Write-through caching** (populate cache at write time, not on first
  read) — rejected for now because it caches links that may never actually
  be clicked, wasting memory. Cache-aside only caches what's actually
  requested.

**Open problems to solve later (not yet implemented):**
- Cache invalidation — what happens if a short link is deleted/updated?
- TTL (time-to-live) — how long should entries live in Redis before expiring,
  even without an explicit invalidation event?

---

## 2026-07-30 — Local dev environment: Docker Compose

**Decision:** Docker Compose to run Postgres + Redis locally as containers

**Alternatives considered:**
- **Installing Postgres/Redis directly on the machine** — works, but is
  machine-specific, harder to tear down/reset cleanly, and doesn't reflect
  how real teams standardize dev environments. Docker Compose means the
  exact same setup command works on any machine, which is also a legitimate
  resume line ("containerized local dev environment").

**Note:** `docker-compose.yml` (orchestrates multiple containers for local
dev) is distinct from a `Dockerfile` (packages this app itself into a
deployable image). The Dockerfile comes later, once there's real
application code worth packaging — writing it against an empty app would
just be an empty shell with nothing to defend.

---
 
## 2026-07-31 — ID generation: sequential integer + base62 encoding (replacing pure-random codes)
 
**Problem discovered by testing:** The original `generate_short_code()` picked 6
random characters with no uniqueness check against existing codes. Two issues
surfaced from manual testing:
 
1. Shortening the same URL twice produced two different short_codes
   (`25FmYB` vs `RKhYGi`). This is actually a legitimate product decision, not
   a bug — real shorteners (e.g. Bitly) intentionally allow this, since
   separate short links to the same destination may need separate click
   analytics (e.g. tracking an email campaign link separately from a tweet
   link, even if both point to the same page). Decision: keep this behavior —
   every `/shorten` call creates a new, independent short_code.
2. The real risk: pure-random generation has **no collision check**. Two
   different long URLs could, by chance, be assigned the same random code,
   silently overwriting one mapping with another — no error, no warning,
   quiet data loss. With 6 chars over a 62-character alphabet (62^6 ≈ 56
   billion combinations) this feels unlikely at small scale, but the
   **birthday paradox** means collision probability grows much faster than
   intuition suggests as stored URLs scale up. Not safe to rely on chance
   alone in a real system.
**Decision:** Replace random generation with:
1. A **unique, auto-incrementing integer ID** for every new URL (guaranteed
   unique by the database itself — no two rows can ever share an ID).
2. **Base62 encode** that integer (digits 0-9, lowercase a-z, uppercase A-Z —
   62 symbols) to produce a short, URL-safe string.
Since uniqueness comes from the database-guaranteed integer ID, not from
randomness, collisions become structurally impossible rather than just
statistically unlikely.
 
**Alternatives considered:**
- **Random string + check-and-retry-on-collision** — works, but requires an
  extra DB lookup on every write to check for collisions, and still has a
  (shrinking but nonzero) chance of needing multiple retries under load.
  Sequential ID + encoding avoids this entirely by construction.
- **UUID4** — statistically collision-safe, but UUIDs are long (36 chars)
  and not appropriate for something meant to be short and shareable.
- **Base64** — includes `+` and `/` characters that aren't safe in URLs
  without escaping. Base62 avoids this by using only alphanumeric characters.
---

## Template for future entries

```
## YYYY-MM-DD — <Decision title>

**Decision:** <what was chosen>

**Alternatives considered:**
- **<Option A>** — <why rejected>
- **<Option B>** — <why rejected>

**Reasoning:** <why the chosen option wins>
```