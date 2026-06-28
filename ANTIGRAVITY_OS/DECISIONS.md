# ResourcePro — Architecture Decisions

## Decision 1: JWT vs Sessions
**Decision:** JWT-based authentication
**Rationale:**
- Stateless — no server-side session storage needed
- Scalable — works across multiple servers without shared session store
- Mobile-ready — tokens work with any client (web, mobile, API)
- Standard — widely supported with robust libraries (PyJWT)

**Implementation:**
- Access token: 60 min expiry (short-lived for security)
- Refresh token: 7 days (30 days with "remember me")
- Payload includes: user_id, role, token type, expiry

## Decision 2: bcrypt for Password Hashing
**Decision:** Use bcrypt (via Python bcrypt library)
**Rationale:**
- Adaptive — cost factor increases with hardware improvements
- Salt included — auto-generated per-password salt
- Battle-tested — industry standard for password hashing
- Resistant to rainbow table and brute-force attacks

**Alternatives considered:**
- SHA-256: Too fast, vulnerable to brute force
- Argon2: Better but less library support in Python
- PBKDF2: Good but bcrypt is more widely adopted

## Decision 3: SQLite for Auth Database
**Decision:** Separate SQLite database for auth (db.sqlite3)
**Rationale:**
- Consistent with existing booking system (uses SQLite)
- No additional infrastructure needed
- Sufficient for expected user scale
- Parameterized queries prevent SQL injection
- Easy to migrate to PostgreSQL later if needed

## Decision 4: Flask Blueprint Architecture
**Decision:** Auth system as a Flask Blueprint
**Rationale:**
- Modular — auth code isolated in its own package
- Maintainable — clear separation of concerns
- Extensible — easy to add new auth features
- Non-disruptive — existing booking API unchanged

## Decision 5: Middleware Decorator Pattern
**Decision:** Python decorators for auth middleware
**Rationale:**
- Pythonic — natural pattern for function wrapping
- Composable — `@verify_token` + `@check_role("faculty")` stack cleanly
- Reusable — any route can be protected with one line
- Testable — decorators are independently testable

## Decision 6: Separate Frontend Directory
**Decision:** Auth pages in FRONTEND/ (separate from frontend/)
**Rationale:**
- Preserves original booking system frontend untouched
- Clear separation between booking UI and auth UI
- Auth pages share consistent design system
- Can be served from same Flask server

## Decision 7: Client-Side Token Storage
**Decision:** localStorage for JWT storage
**Rationale:**
- Simple implementation
- Persistent across page reloads
- Auto-attached via auth.js header injection
- Token refresh handles expiration seamlessly

**Security mitigations:**
- Short-lived access tokens (60 min)
- Refresh token rotation
- Logout invalidates server-side session
- Input sanitization prevents XSS attacks
