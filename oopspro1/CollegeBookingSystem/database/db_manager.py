"""
============================================================
 db_manager.py — SQLite Database Manager
============================================================
 Handles all database CRUD operations for the booking system.
 
 Table Schema:
   id     - INTEGER PRIMARY KEY AUTOINCREMENT
   user   - TEXT NOT NULL
   room   - INTEGER NOT NULL
   date   - TEXT NOT NULL
   slot   - TEXT NOT NULL
   status - TEXT DEFAULT 'Pending'
 
 Valid Slots: 9-10, 10-11, 11-12, 12-1, 2-3, 3-4
============================================================
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "booking.db")

VALID_SLOTS = ["9-10", "10-11", "11-12", "12-1", "2-3", "3-4"]

def get_connection():
    """Get a database connection, creating DB if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            room INTEGER NOT NULL,
            date TEXT NOT NULL,
            slot TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(room, date, slot)
        )
    """)
    
    conn.commit()
    
    # Check if we need to seed data
    count = cursor.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    if count == 0:
        seed_data(conn)
    
    conn.close()

def seed_data(conn):
    """Generate 1000+ synthetic booking records for ML training."""
    cursor = conn.cursor()
    
    users = [f"S{i}" for i in range(1001, 1051)] + [f"F{i}" for i in range(101, 121)]
    
    # Generate rooms in valid range 1001-4410
    rooms = []
    for floor in range(1, 5):
        for room in range(1, 411):
            rooms.append(floor * 1000 + room)
    
    # Pick a subset of rooms to make data more realistic
    popular_rooms = random.sample(rooms, min(200, len(rooms)))
    
    base_date = datetime(2026, 3, 1)
    records = []
    attempts = 0
    booked_slots = set()
    
    while len(records) < 1200 and attempts < 5000:
        attempts += 1
        user = random.choice(users)
        room = random.choice(popular_rooms)
        day_offset = random.randint(0, 30)
        date = (base_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        slot = random.choice(VALID_SLOTS)
        status = random.choice(["Pending", "Approved", "Approved", "Approved"])
        
        key = (room, date, slot)
        if key not in booked_slots:
            booked_slots.add(key)
            records.append((user, room, date, slot, status))
    
    cursor.executemany(
        "INSERT OR IGNORE INTO bookings (user, room, date, slot, status) VALUES (?, ?, ?, ?, ?)",
        records
    )
    conn.commit()
    print(f"[DB] Seeded {len(records)} booking records")

def check_availability(room, date, slot):
    """Check if a room is available for a specific date and slot."""
    conn = get_connection()
    cursor = conn.cursor()
    result = cursor.execute(
        "SELECT * FROM bookings WHERE room = ? AND date = ? AND slot = ? AND status != 'Rejected'",
        (room, date, slot)
    ).fetchone()
    conn.close()
    return result is None

def create_booking(user, room, date, slot, status="Pending"):
    """Create a new booking. Returns True if successful, False if duplicate."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO bookings (user, room, date, slot, status) VALUES (?, ?, ?, ?, ?)",
            (user, room, date, slot, status)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_all_bookings():
    """Get all bookings."""
    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT id, user, room, date, slot, status FROM bookings ORDER BY date, slot"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_bookings_by_date(date):
    """Get all bookings for a specific date."""
    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT id, user, room, date, slot, status FROM bookings WHERE date = ? ORDER BY room, slot",
        (date,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_bookings_by_user(user):
    """Get all bookings for a specific user."""
    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT id, user, room, date, slot, status FROM bookings WHERE user = ? ORDER BY date, slot",
        (user,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_booking_status(booking_id, new_status):
    """Update a booking's status (Approve/Reject)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE bookings SET status = ? WHERE id = ?",
        (new_status, booking_id)
    )
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_booked_rooms_for_slot(date, slot):
    """Get all rooms that are booked for a specific date and slot."""
    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT DISTINCT room FROM bookings WHERE date = ? AND slot = ? AND status != 'Rejected'",
        (date, slot)
    ).fetchall()
    conn.close()
    return [row['room'] for row in rows]

def get_room_schedule(date):
    """Get the full room schedule grid for a date."""
    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT room, slot, status, user FROM bookings WHERE date = ? AND status != 'Rejected' ORDER BY room, slot",
        (date,)
    ).fetchall()
    conn.close()
    
    schedule = {}
    for row in rows:
        room = row['room']
        if room not in schedule:
            schedule[room] = {}
        schedule[room][row['slot']] = {
            "status": row['status'],
            "user": row['user']
        }
    
    return schedule

def get_training_data():
    """Get data formatted for ML model training."""
    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT user, room, slot, status FROM bookings"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_booking_stats():
    """Get booking statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    total = cursor.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    approved = cursor.execute("SELECT COUNT(*) FROM bookings WHERE status='Approved'").fetchone()[0]
    pending = cursor.execute("SELECT COUNT(*) FROM bookings WHERE status='Pending'").fetchone()[0]
    rejected = cursor.execute("SELECT COUNT(*) FROM bookings WHERE status='Rejected'").fetchone()[0]
    
    conn.close()
    return {
        "total": total,
        "approved": approved,
        "pending": pending,
        "rejected": rejected
    }

# Initialize on import
init_db()
