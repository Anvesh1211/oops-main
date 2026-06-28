"""
============================================================
 app.py — Flask API Backend (Root Launcher)
============================================================
 This is the main entry point for the Flask server.
 Run: python app.py
 Access: http://localhost:5000
============================================================
"""

import os
import sys
import json
import subprocess
import numpy as np
import joblib
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# ── Path Setup ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Import database manager
sys.path.insert(0, os.path.join(BASE_DIR, 'database'))
from db_manager import (
    check_availability, create_booking, get_all_bookings,
    get_bookings_by_date, get_bookings_by_user, update_booking_status,
    get_booked_rooms_for_slot, get_room_schedule, get_training_data,
    get_booking_stats, VALID_SLOTS, init_db
)

# ── Flask App ──
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

# ── Configuration ──
CPP_ENGINE = os.path.join(BASE_DIR, "backend_cpp", "booking_engine.exe")
ML_MODEL_PATH = os.path.join(BASE_DIR, "ml", "best_model.pkl")

# ── Room Range: 1001 → 4410 ──
ALL_ROOMS = []
for floor in range(1, 5):
    for room in range(1, 411):
        ALL_ROOMS.append(floor * 1000 + room)
ALL_ROOMS_SET = set(ALL_ROOMS)

# ── ML Model Loading ──
ml_model = None
try:
    if os.path.exists(ML_MODEL_PATH):
        ml_model = joblib.load(ML_MODEL_PATH)
        print(f"[ML] Model loaded from {ML_MODEL_PATH}")
    else:
        print(f"[ML] Model not found at {ML_MODEL_PATH}")
except Exception as e:
    print(f"[ML] Error loading model: {e}")

# ── Helper: Call C++ Engine ──
def call_cpp_engine(args):
    """Call the C++ booking engine with arguments and return JSON output."""
    try:
        if not os.path.exists(CPP_ENGINE):
            return None
        cmd = [CPP_ENGINE] + args
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10,
            cwd=os.path.join(BASE_DIR, "backend_cpp")
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout.strip())
        return None
    except Exception as e:
        print(f"[C++] Engine error: {e}")
        return None

# ── Helper: Find closest room ──
def find_closest_room(requested_room, date, slot):
    booked = set(get_booked_rooms_for_slot(date, slot))
    closest = None
    min_dist = float('inf')
    for r in ALL_ROOMS:
        if r not in booked:
            dist = abs(requested_room - r)
            if 0 < dist < min_dist:
                min_dist = dist
                closest = r
    return (closest, min_dist) if closest else (None, None)

# ── Helper: Find next available slot ──
def find_next_slot(room, date):
    for slot in VALID_SLOTS:
        if check_availability(room, date, slot):
            return slot
    return None


# ═══════════════════════════════════════════════════
#                    ROUTES
# ═══════════════════════════════════════════════════

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)


@app.route('/api/check', methods=['POST'])
def check_room():
    data = request.get_json()
    user = data.get('user', '')
    room = int(data.get('room', 0))
    date = data.get('date', '')
    slot = data.get('slot', '')

    if not all([user, room, date, slot]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    if room not in ALL_ROOMS_SET:
        return jsonify({"status": "error", "message": f"Invalid room {room}. Must be 1001-4410"}), 400
    if slot not in VALID_SLOTS:
        return jsonify({"status": "error", "message": f"Invalid slot. Must be one of {VALID_SLOTS}"}), 400

    # Try C++ engine first
    cpp_result = call_cpp_engine(["check", user, str(room), date, slot])

    if check_availability(room, date, slot):
        result = {
            "status": "available",
            "room": room, "date": date, "slot": slot,
            "message": f"Room {room} is available for {slot} on {date}"
        }
    else:
        closest, dist = find_closest_room(room, date, slot)
        next_slot = find_next_slot(room, date)
        result = {
            "status": "unavailable",
            "room": room, "date": date, "slot": slot,
            "message": f"Room {room} is NOT available for {slot} on {date}"
        }
        if closest:
            result["suggested_room"] = closest
            result["suggested_room_distance"] = dist
        if next_slot:
            result["suggested_slot"] = next_slot

    # Add ML prediction
    if ml_model is not None:
        try:
            slot_idx = VALID_SLOTS.index(slot)
            floor_num = room // 1000
            is_student = 1 if user.startswith('S') else 0
            features = np.array([[room, slot_idx, floor_num, is_student]])
            prob = ml_model.predict_proba(features)[0]
            result["ml_booking_probability"] = round(float(max(prob)), 3)
        except Exception as e:
            result["ml_note"] = str(e)

    if cpp_result and "suggested_room" in cpp_result:
        result["cpp_suggested_room"] = cpp_result["suggested_room"]

    return jsonify(result)


@app.route('/api/book', methods=['POST'])
def book_room():
    data = request.get_json()
    user = data.get('user', '')
    room = int(data.get('room', 0))
    date = data.get('date', '')
    slot = data.get('slot', '')

    if not all([user, room, date, slot]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    if room not in ALL_ROOMS_SET:
        return jsonify({"status": "error", "message": f"Invalid room {room}"}), 400

    if not check_availability(room, date, slot):
        closest, dist = find_closest_room(room, date, slot)
        next_slot = find_next_slot(room, date)
        result = {
            "status": "unavailable",
            "message": f"Room {room} is already booked for {slot} on {date}"
        }
        if closest:
            result["suggested_room"] = closest
            result["suggested_room_distance"] = dist
        if next_slot:
            result["suggested_slot"] = next_slot
        return jsonify(result)

    success = create_booking(user, room, date, slot)
    if success:
        call_cpp_engine(["book", user, str(room), date, slot])
        return jsonify({
            "status": "booked",
            "message": f"Room {room} booked for {slot} on {date}",
            "room": room, "date": date, "slot": slot, "user": user
        })
    else:
        return jsonify({"status": "error", "message": "Booking failed (duplicate)"}), 409


@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    date = request.args.get('date', '')
    if not date:
        return jsonify({"status": "error", "message": "Date required"}), 400
    bookings = get_bookings_by_date(date)
    schedule = get_room_schedule(date)
    return jsonify({
        "date": date, "total_bookings": len(bookings),
        "bookings": bookings,
        "schedule": {str(k): v for k, v in schedule.items()},
        "valid_slots": VALID_SLOTS
    })


@app.route('/api/rooms', methods=['GET'])
def get_rooms_status():
    date = request.args.get('date', '')
    if not date:
        return jsonify({"status": "error", "message": "Date required"}), 400
    schedule = get_room_schedule(date)
    rooms_data = []
    for room in sorted(schedule.keys()):
        room_info = {"room": room, "slots": {}}
        for slot in VALID_SLOTS:
            if slot in schedule[room]:
                room_info["slots"][slot] = {
                    "status": "booked",
                    "booked_by": schedule[room][slot]["user"],
                    "approval": schedule[room][slot]["status"]
                }
            else:
                room_info["slots"][slot] = {"status": "available"}
        rooms_data.append(room_info)
    return jsonify({
        "date": date, "rooms": rooms_data,
        "valid_slots": VALID_SLOTS,
        "total_rooms_with_bookings": len(rooms_data)
    })


@app.route('/api/allbookings', methods=['GET'])
def all_bookings():
    bookings = get_all_bookings()
    stats = get_booking_stats()
    return jsonify({"bookings": bookings, "stats": stats})


@app.route('/api/user-bookings', methods=['GET'])
def user_bookings():
    user = request.args.get('user', '')
    if not user:
        return jsonify({"status": "error", "message": "User required"}), 400
    bookings = get_bookings_by_user(user)
    return jsonify({"user": user, "bookings": bookings})


@app.route('/api/approve', methods=['POST'])
def approve_booking():
    data = request.get_json()
    booking_id = data.get('id')
    if not booking_id:
        return jsonify({"status": "error", "message": "ID required"}), 400
    success = update_booking_status(int(booking_id), "Approved")
    if success:
        return jsonify({"status": "success", "message": "Booking approved"})
    return jsonify({"status": "error", "message": "Not found"}), 404


@app.route('/api/reject', methods=['POST'])
def reject_booking():
    data = request.get_json()
    booking_id = data.get('id')
    if not booking_id:
        return jsonify({"status": "error", "message": "ID required"}), 400
    success = update_booking_status(int(booking_id), "Rejected")
    if success:
        return jsonify({"status": "success", "message": "Booking rejected"})
    return jsonify({"status": "error", "message": "Not found"}), 404


@app.route('/api/stats', methods=['GET'])
def stats():
    return jsonify(get_booking_stats())


@app.route('/api/predict', methods=['POST'])
def predict():
    global ml_model
    if ml_model is None:
        try:
            if os.path.exists(ML_MODEL_PATH):
                ml_model = joblib.load(ML_MODEL_PATH)
        except:
            pass
    if ml_model is None:
        return jsonify({"status": "error", "message": "ML model not loaded"}), 503

    data = request.get_json()
    room = int(data.get('room', 0))
    slot = data.get('slot', '')
    user = data.get('user', 'S1001')
    try:
        slot_idx = VALID_SLOTS.index(slot)
        floor_num = room // 1000
        is_student = 1 if user.startswith('S') else 0
        features = np.array([[room, slot_idx, floor_num, is_student]])
        prediction = ml_model.predict(features)[0]
        probabilities = ml_model.predict_proba(features)[0]
        return jsonify({
            "room": room, "slot": slot,
            "prediction": int(prediction),
            "probability": round(float(max(probabilities)), 3),
            "label": "Likely to be booked" if prediction == 1 else "Likely available"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/valid-rooms', methods=['GET'])
def valid_rooms():
    return jsonify({
        "rooms": ALL_ROOMS, "total": len(ALL_ROOMS),
        "range": "1001-4410", "floors": 4, "rooms_per_floor": 410
    })


@app.route('/api/health', methods=['GET'])
def health():
    cpp_status = "connected" if os.path.exists(CPP_ENGINE) else "not found"
    ml_status = "loaded" if ml_model is not None else "not loaded"
    try:
        s = get_booking_stats()
        db_status = "working"
    except:
        db_status = "error"
        s = {}
    return jsonify({
        "status": "running", "cpp_engine": cpp_status,
        "ml_model": ml_status, "database": db_status,
        "booking_stats": s, "valid_room_range": "1001-4410",
        "total_rooms": len(ALL_ROOMS)
    })


# ═══════════════════════════════════════════════════
#                 SERVER STARTUP
# ═══════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  COLLEGE RESOURCE BOOKING SYSTEM")
    print("  Flask Backend Server")
    print("="*60)
    print(f"  Rooms: 1001 -> 4410 ({len(ALL_ROOMS)} total)")
    print(f"  Slots: {', '.join(VALID_SLOTS)}")
    print(f"  C++ Engine: {'Connected' if os.path.exists(CPP_ENGINE) else 'Not found'}")
    print(f"  ML Model: {'Loaded' if ml_model else 'Not loaded'}")
    try:
        s = get_booking_stats()
        print(f"  Database: {s['total']} bookings")
    except:
        print("  Database: Initializing...")
    print("="*60)
    print(f"  Server: http://localhost:5000")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
