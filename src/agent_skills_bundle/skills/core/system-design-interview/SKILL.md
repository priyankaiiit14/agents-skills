---
name: system-design-interview
description: Use this skill when preparing for or walking through a system design interview for a web service, API, or distributed backend system (e.g., 'design Ticketmaster', 'design a URL shortener', 'design an Uber-like ride matching system', 'design a rate limiter'). Provides a repeatable 5-step framework — requirements, core entities, API design, high-level design, deep dives — covering tradeoffs like consistency vs. availability, contention/locking patterns (reserve-and-confirm flows, distributed locks with TTL), caching layers, and surge handling (SSE/WebSockets, virtual waiting queues). Do NOT use this for data pipeline, ETL, or data platform design questions — use the data-engineering system design skill for those instead.
---

# System Design Interview Framework

A repeatable 5-step process for any system design interview, generalized from a Ticketmaster-style breakdown. Timebox: ~35-45 min interview → roughly 5 / 5 / 5 / 15 / 15 minutes across the steps below.

---

## 0. Before You Start
- Don't jump straight to drawing boxes. Spend the first ~10 minutes on requirements + entities + API — this is where most candidates lose points by skipping ahead.
- Treat the interviewer as a collaborator, not an examiner. Ask questions out loud; state assumptions explicitly so they can correct you.
- Explicitly draw a line between **in scope** and **out of scope**. Say it out loud: "I'm going to treat X as out of scope unless you'd like me to go deeper there." This signals maturity and gives the interviewer a hook to redirect you.

---

## 1. Requirements (~5 min)

### Functional Requirements
Phrase these as "Users should be able to ___." Ask clarifying questions to narrow scope — don't assume. Aim for 3-5 core features; anything else goes in "out of scope."

### Non-Functional Requirements
Qualities of the system, not features. Standard menu to pull from:
- **Consistency vs. Availability** — this is the single highest-leverage question to ask early. Frame it from the problem's perspective: *"Is there a part of this system where we cannot tolerate incorrect data (e.g., double-booking, double-charging)? If so, that part needs strong consistency even at the cost of availability."*
  - Different subsystems can make different tradeoffs. E.g., booking/payment → strong consistency; search/browsing → high availability, eventual consistency is fine.
- **Read/write ratio** — is this read-heavy or write-heavy? Most consumer systems are read >> write.
- **Query access pattern** — is load steady or spiky? (e.g., ticket sales spike around a popular event drop, a flash sale, a viral post). This determines whether you need queueing, rate limiting, or a waiting-room pattern later.
- **Scalability** — expected scale (users, QPS, data volume) — enough to justify design decisions, not full BOTEC yet.
- **Latency** — which operations need to feel instant vs. can be async?
- **Durability / fault tolerance** — what can never be lost (payments, bookings) vs. what can be regenerated/re-fetched (a cache, a search index)?

**Tip:** Don't do back-of-envelope math here just to show you can. Only calculate numbers when they directly change a design decision later (e.g., "at this QPS we need to shard" or "this justifies a cache").

---

## 2. Core Entities (~2-3 min)

- List the nouns your system persists or exchanges — usually 3-6 entities (e.g., User, Event, Venue, Order, Ticket).
- Don't over-invest in fields yet. It's fine to say: *"I'll flesh out fields as the design evolves, since I don't yet know what the API and data flow will require."*
- This step exists purely to make the next step (API) concrete — you need names for the things flowing through your endpoints.

---

## 3. API Design (~5 min)

For **each functional requirement**, define the endpoint(s) that satisfy it. Default to REST unless there's a clear reason for GraphQL/gRPC (e.g., flexible client-driven queries, internal service-to-service calls).

Patterns worth reusing:
- **Reads** — `GET /resource/:id` → return the entity plus whatever nested/related data the client needs to render (avoid N+1 client calls).
- **Search/browse** — `GET /search?term=&filter1=&filter2=...` with optional query params → return partial/lightweight representations, not full objects.
- **Multi-step write flows with contention** (booking, checkout, auction bidding) — split into two calls:
  1. `POST /resource/reserve` — acquire a temporary hold, short TTL.
  2. `PUT /resource/confirm` — finalize (payment, commit) before TTL expires.
- **Security hygiene** — don't put `userId` in the request body; derive identity from the auth token/session server-side so a client can't spoof another user's ID.

Say what each response shape is, even loosely (e.g., `Event & Venue & Ticket[]`) — this signals you're thinking about payload cost and client rendering, not just routes.

---

## 4. High-Level Design (~15 min)

Walk through your API list one endpoint (or flow) at a time, and draw the components that satisfy it. Don't design the whole diagram silently — narrate as you go.

### Default architecture choices (state your reasoning, don't just declare it)
- **Monolith vs. microservices** — default to microservices for interviews above entry-level, since it lets you reason about independent scaling/failure domains. Justify by service ownership boundaries (e.g., Booking Service, Search Service, Notification Service), not by "it's more modern."
- **SQL vs. NoSQL** — pick based on relationships and consistency needs, not dogma. If entities have foreign keys / 1:many / transactional needs → SQL. Don't get pulled into a SQL-vs-NoSQL religious debate in the interview; what matters is which *properties* (ACID, schema flexibility, query patterns) you need.
- **Naive-first, then optimize** — it's fine to say "a naive `SELECT` here would work but will be slow at scale — I'll come back to this in deep dives." This shows you know where the bottleneck is without prematurely over-engineering.

### Handling contention / write conflicts (generalizes beyond ticketing — applies to inventory, seat/slot booking, auctions, limited drops)
Walk through the maturity ladder of solutions and pick the best one — this progression itself is a strong signal in interviews:
1. **Status column only** (`available/reserved/booked`) — simple, but a reserved-and-abandoned item stays stuck forever.
2. **Status + timestamp, queried with a time filter** — works, but complicates every read query and couples read logic to write timing.
3. **Status + timestamp, reaped by a cron job** — decouples reads from cleanup, but introduces lag: if the cron job runs every N minutes and misses a cycle, effective hold time balloons to ~2N instead of N.
4. **Distributed lock with TTL (e.g., Redis key per resource ID, TTL = hold duration)** — best of both: no polling, no stale reads, and expiry is automatic and precise. On confirm, the app releases the lock manually before TTL; on abandonment, Redis expires it for free.
   - **Failure mode to call out:** if the lock store goes down, you temporarily lose the "soft hold" UX, but you never get true double-booking/double-allocation because the source-of-truth DB still enforces correctness via ACID transactions + optimistic concurrency control (OCC) or row-level locking. Explicitly say: *"Losing the lock store degrades UX (a user might get a payment-time conflict), but it's strictly better than the cron-job failure mode, where all items could appear falsely unavailable."*

### Talking points that impress interviewers here
- Name the concurrency mechanism your database actually uses (e.g., Postgres uses MVCC — transactions see a consistent snapshot, avoiding read/write blocking) rather than hand-waving "the database handles it."
- Explicitly separate "the lock/cache layer" (optimizes the happy path) from "the database" (guarantees correctness) — interviewers want to see you know which layer is truly load-bearing for consistency.

---

## 5. Deep Dives (~15 min)

Go back to your non-functional requirements list and ask: *what's still unsatisfied?* Pick 1-3 to go deep on — depth beats breadth here.

Common deep-dive themes to have ready (pick whichever match the problem):

### A. Making search/browse fast
- Full table scans on the primary DB don't scale for text/filter-heavy search → introduce a search-optimized store (Elasticsearch/OpenSearch) using inverted indexes; mention geospatial query support if location filtering is relevant.
- **Keeping it in sync with the primary DB** (this is the actual hard part, not the search index itself):
  - App-code dual-write on every mutation — simple, but risks drift if one write fails.
  - Change Data Capture (CDC) streaming primary DB changes into the search index — more resilient, decouples services, standard answer for "how do you keep two stores consistent."
  - If write volume is high, put a queue between CDC and the search index, since search indexes often have update-rate ceilings.
  - Note explicitly: never use the search index as the system of record — it typically lacks durability guarantees and transactional support.
- **Caching repeated queries** — layer options depending on the failure mode you're solving:
  - Search engine's own built-in shard-level query/result caching.
  - Redis/Memcached in front of the search layer for normalized query strings.
  - CDN in front of the API gateway for very short TTLs (~30-60s) — great for identical high-frequency queries (e.g., a trending search term), but useless once query cardinality is high (many filter permutations) or results are personalized.

### B. Handling surges / hot spots (viral event, flash sale, popular drop)
- **Keeping clients in sync with fast-changing state:**
  - Long polling — simplest, but wasteful and higher latency.
  - Server-Sent Events (SSE) — good default for one-way server→client push (e.g., "this seat just got taken"); simpler than WebSockets when you don't need client→server messages over the same channel.
  - WebSockets — only justified if you genuinely need bidirectional real-time communication.
- **Virtual waiting queue / "chokepoint"** for extreme demand spikes:
  - Sits in front of the contended service, admitting users at a controlled rate instead of letting everyone hit the hot path at once.
  - Implement with a sorted set (e.g., Redis ZSET keyed by timestamp) for queue ordering.
  - Maintain a persistent connection (SSE/WebSocket) so users can see live queue position without polling.
  - On admission, add the session to an `admitted:{resourceId}` set with a TTL; the downstream service checks this set and rejects any request not present in it — this is what actually enforces the queue, not just the UI.

### C. Other deep-dive levers worth having in your back pocket
- **Sharding/partitioning** the primary DB once single-node write throughput becomes the bottleneck.
- **Read replicas** for read-heavy, eventually-consistent-ok paths (browsing, viewing).
- **Rate limiting** at the API gateway to protect backends from abusive or accidental traffic spikes.
- **Idempotency keys** for any write endpoint that a client might retry (payments, reservations) to avoid duplicate side effects.
- **Back-of-envelope math** — only pull this out when it changes a decision (e.g., "at 50K QPS, a single Postgres instance won't keep up, so here's how I'd shard/read-replica it"). Don't do math as a performance for its own sake.

---

## Quick Checklist to Run Through Live

- [ ] Asked clarifying questions before assuming scope
- [ ] Named functional requirements as user-facing capabilities
- [ ] Identified the consistency-vs-availability tradeoff and *where in the system* it applies
- [ ] Listed 3-6 core entities without over-specifying fields early
- [ ] Mapped every functional requirement to at least one API call
- [ ] Avoided leaking user identity into request bodies where auth context should be used instead
- [ ] Chose SQL/NoSQL and monolith/microservices with a stated reason, not by default habit
- [ ] Identified the one place where correctness matters most (no double-booking / no double-charging) and solved it with a real mechanism (lock + TTL + DB-level guarantee), not just "the database handles it"
- [ ] Picked 1-3 deep dives tied directly back to an unmet non-functional requirement
- [ ] Used back-of-envelope numbers only where they changed a decision
- [ ] Explicitly called out what's out of scope
