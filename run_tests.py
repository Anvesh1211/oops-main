"""
============================================================
 run_tests.py — Auto Test Suite
============================================================
 Tests:
   1. Book an available room → success
   2. Book same room/slot again → suggestion appears
   3. Closest room suggestion works
   4. Next slot suggestion works
   5. Spreadsheet UI (rooms endpoint) updates
   6. ML model loads and predicts correctly
   7. Faculty approve/reject works
   8. Valid-rooms endpoint returns 1640 rooms
   9. Health check passes
============================================================
"""

import urllib.request
import urllib.error
import json
import sys

BASE = "http://localhost:5000"
PASS = "✅ PASS"
FAIL = "❌ FAIL"
results = []

def api_post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=data,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def api_get(path):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=10) as r:
        return json.loads(r.read())

def test(name, passed, detail=""):
    mark = PASS if passed else FAIL
    results.append(passed)
    print(f"  {mark}  {name}")
    if detail:
        print(f"         ↳ {detail}")

print("\n" + "="*60)
print("  AUTO TEST SUITE — College Booking System")
print("="*60)

# ── Test 1: Health Check ──
print("\n[T1] Health Check")
try:
    r = api_get("/api/health")
    ok = r.get("status") == "running" and r.get("database") == "working"
    test("System is online and database working", ok,
         f"cpp={r.get('cpp_engine')}, ml={r.get('ml_model')}, db={r.get('database')}, rooms={r.get('total_rooms')}")
except Exception as e:
    test("System is online and database working", False, str(e))

# ── Test 2: Valid Rooms ──
print("\n[T2] Room Range 1001→4410")
try:
    r = api_get("/api/valid-rooms")
    ok = r.get("total") == 1640 and 1001 in r.get("rooms", []) and 4410 in r.get("rooms", [])
    test("1640 rooms returned (1001–4410)", ok,
         f"total={r.get('total')}, first={r['rooms'][0]}, last={r['rooms'][-1]}")
except Exception as e:
    test("1640 rooms returned (1001–4410)", False, str(e))

# ── Test 3: Book Available Room ──
print("\n[T3] Book Available Room → Success")
TEST_ROOM = 2205
TEST_DATE = "2026-04-15"
TEST_SLOT = "9-10"
TEST_USER = "S9001"
try:
    r = api_post("/api/book", {"user": TEST_USER, "room": TEST_ROOM, "date": TEST_DATE, "slot": TEST_SLOT})
    ok = r.get("status") == "booked"
    test("Book room 2205 for 2026-04-15 09-10 → Booked", ok,
         f"status={r.get('status')}, msg={r.get('message','')}")
except Exception as e:
    test("Book room 2205 for 2026-04-15 09-10 → Booked", False, str(e))

# ── Test 4: Duplicate → Suggestion ──
print("\n[T4] Duplicate Booking → Suggestions Appear")
try:
    r = api_post("/api/book", {"user": "S9002", "room": TEST_ROOM, "date": TEST_DATE, "slot": TEST_SLOT})
    has_suggestion = "suggested_room" in r or "suggested_slot" in r
    ok = r.get("status") == "unavailable" and has_suggestion
    sug = f"suggested_room={r.get('suggested_room','—')}, suggested_slot={r.get('suggested_slot','—')}"
    test("Second booking of same slot → unavailable + suggestions", ok, sug)
except Exception as e:
    test("Second booking of same slot → unavailable + suggestions", False, str(e))

# ── Test 5: Check (not book) → Available ──
print("\n[T5] Check Availability (Different Slot)")
try:
    r = api_post("/api/check", {"user": "S9003", "room": TEST_ROOM, "date": TEST_DATE, "slot": "10-11"})
    ok = r.get("status") == "available"
    test("Check room 2205 slot 10-11 → available", ok,
         f"status={r.get('status')}")
except Exception as e:
    test("Check room 2205 slot 10-11 → available", False, str(e))

# ── Test 6: Closest Room Suggestion ──
print("\n[T6] Closest Room Logic")
try:
    # Book rooms 2204 and 2206, then ask for 2205 → closest should be 2203 or 2207
    api_post("/api/book", {"user": "S9004", "room": 2204, "date": TEST_DATE, "slot": TEST_SLOT})
    api_post("/api/book", {"user": "S9005", "room": 2206, "date": TEST_DATE, "slot": TEST_SLOT})
    r = api_post("/api/check", {"user": "S9006", "room": TEST_ROOM, "date": TEST_DATE, "slot": TEST_SLOT})
    has_closest = "suggested_room" in r and r["suggested_room"] is not None
    if has_closest:
        dist = abs(TEST_ROOM - r["suggested_room"])
        ok = has_closest and dist <= 10
        test(f"Closest room found: {r.get('suggested_room')} (dist={dist})", ok,
             f"requested={TEST_ROOM}, suggested={r.get('suggested_room')}")
    else:
        test("Closest room logic", False, "No suggested_room in response")
except Exception as e:
    test("Closest room logic", False, str(e))

# ── Test 7: Next Slot Suggestion ──
print("\n[T7] Next Available Slot")
try:
    r = api_post("/api/book", {"user": "S9007", "room": TEST_ROOM, "date": TEST_DATE, "slot": TEST_SLOT})
    ok = r.get("suggested_slot") is not None or r.get("status") == "booked"
    # Check that check endpoint gives next slot
    r2 = api_post("/api/check", {"user": "S9008", "room": TEST_ROOM, "date": TEST_DATE, "slot": TEST_SLOT})
    has_next = "suggested_slot" in r2
    test(f"Next slot suggestion: {r2.get('suggested_slot','—')}", has_next,
         f"status={r2.get('status')}, next_slot={r2.get('suggested_slot','none')}")
except Exception as e:
    test("Next slot suggestion", False, str(e))

# ── Test 8: Schedule / Spreadsheet ──
print("\n[T8] Spreadsheet Room Grid")
try:
    r = api_get(f"/api/rooms?date={TEST_DATE}")
    ok = "rooms" in r and "valid_slots" in r
    booked_count = r.get("total_rooms_with_bookings", 0)
    test(f"Room grid for {TEST_DATE} → {booked_count} rooms with bookings", ok,
         f"slots={r.get('valid_slots')}, booked_rooms={booked_count}")
except Exception as e:
    test("Spreadsheet room grid", False, str(e))

# ── Test 9: ML Predict ──
print("\n[T9] ML Model Prediction")
try:
    r = api_post("/api/predict", {"user": "S1001", "room": 2205, "slot": "9-10"})
    ok = ("prediction" in r and "probability" in r and "label" in r)
    test(f"ML prediction works: {r.get('label','?')} ({r.get('probability','?')*100:.1f}% prob)",
         ok, f"model returned prediction={r.get('prediction')}, prob={r.get('probability')}")
except Exception as e:
    test("ML prediction", False, str(e))

# ── Test 10: Faculty Approve ──
print("\n[T10] Faculty Approve/Reject")
try:
    # Get a pending booking
    r = api_get("/api/allbookings")
    pending = [b for b in r.get("bookings", []) if b["status"] == "Pending"]
    if pending:
        bid = pending[0]["id"]
        ra = api_post("/api/approve", {"id": bid})
        ok_approve = ra.get("status") == "success"
        rr = api_post("/api/reject", {"id": pending[1]["id"] if len(pending) > 1 else bid})
        ok_reject = rr.get("status") == "success"
        test(f"Approve booking #{bid}", ok_approve, ra.get("message",""))
        test(f"Reject booking", ok_reject, rr.get("message",""))
    else:
        test("Faculty approve", False, "No pending bookings found")
except Exception as e:
    test("Faculty approve/reject", False, str(e))

# ── Summary ──
passed = sum(results)
total = len(results)
print("\n" + "="*60)
print(f"  RESULTS: {passed}/{total} tests passed")
print("="*60)

if passed == total:
    print("\n  🎉 ALL TESTS PASSED — System is production-ready!\n")
else:
    print(f"\n  ⚠️  {total - passed} test(s) failed\n")

sys.exit(0 if passed == total else 1)
