# ResourcePro — Issues Log

## Resolved Issues

### Issue #1: Module Import Path
**Problem:** AUTH module couldn't be imported from app.py due to Python path configuration
**Fix:** Added `sys.path.insert(0, BASE_DIR)` and used absolute imports for AUTH package
**Status:** ✅ Resolved

### Issue #2: Database Auto-Creation
**Problem:** DATABASE/ directory didn't exist on first run
**Fix:** Added `os.makedirs(DB_DIR, exist_ok=True)` in models.py `get_auth_connection()`
**Status:** ✅ Resolved

### Issue #3: Static File Routing Conflict
**Problem:** Flask's catch-all `/<path:path>` route conflicted with explicit auth page routes
**Fix:** Added explicit routes for login.html, register.html, dashboard pages before catch-all, and check FRONTEND dir first in catch-all
**Status:** ✅ Resolved

### Issue #4: CORS with Auth Headers
**Problem:** Browser blocked Authorization header in cross-origin requests
**Fix:** Flask-CORS handles this automatically with `CORS(app)`
**Status:** ✅ Resolved

### Issue #5: Token Refresh Race Condition
**Problem:** Multiple simultaneous requests could trigger multiple refresh attempts
**Fix:** Client-side auth.js uses single authFetch wrapper that serializes refresh attempts
**Status:** ✅ Resolved

## Known Limitations

### Limitation #1: Email Verification
**Description:** No email verification on registration (no SMTP configured)
**Mitigation:** Manual verification via activity logs
**Priority:** Low (enhancement for production)

### Limitation #2: Rate Limiting
**Description:** No rate limiting on login attempts
**Mitigation:** Could add flask-limiter for production deployment
**Priority:** Medium

### Limitation #3: HTTPS
**Description:** Development server uses HTTP, not HTTPS
**Mitigation:** Deploy behind reverse proxy (Nginx) with SSL for production
**Priority:** High (for production)
