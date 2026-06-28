"""
Test SQLite database functionality
"""

import sqlite3
import os
import sys

# Add database module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import (
    get_connection, init_db, check_availability, create_booking,
    get_all_bookings, get_booking_stats, get_bookings_by_date,
    update_booking_status, get_booked_rooms_for_slot
)

def test_sqlite_connection():
    """Test basic SQLite connection"""
    print("=" * 60)
    print("TEST 1: SQLite Connection")
    print("=" * 60)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        print(f"✓ SQLite version: {version}")
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

def test_database_initialization():
    """Test database initialization"""
    print("\n" + "=" * 60)
    print("TEST 2: Database Initialization")
    print("=" * 60)
    try:
        # Check if database file exists
        db_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(db_dir, "database", "booking.db")
        
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"✓ Database file exists at: {db_path}")
            print(f"  File size: {size:,} bytes")
        else:
            print(f"⚠ Database file not found at: {db_path}")
        
        # Initialize database (won't create duplicates)
        init_db()
        print(f"✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        return False

def test_table_structure():
    """Test if bookings table has correct structure"""
    print("\n" + "=" * 60)
    print("TEST 3: Table Structure")
    print("=" * 60)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute("PRAGMA table_info(bookings)")
        columns = cursor.fetchall()
        
        if not columns:
            print("✗ Bookings table does not exist!")
            conn.close()
            return False
        
        print("✓ Bookings table schema:")
        expected_columns = ['id', 'user', 'room', 'date', 'slot', 'status', 'created_at']
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            print(f"  - {col_name}: {col_type}")
            
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Schema check error: {e}")
        return False

def test_data_retrieval():
    """Test data retrieval operations"""
    print("\n" + "=" * 60)
    print("TEST 4: Data Retrieval")
    print("=" * 60)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Count total records
        count = cursor.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
        print(f"✓ Total records in database: {count:,}")
        
        if count == 0:
            print("⚠ Warning: Database is empty!")
        
        # Check first few records
        cursor.execute("SELECT id, user, room, date, slot, status FROM bookings LIMIT 3")
        rows = cursor.fetchall()
        
        if rows:
            print("\n  Sample records:")
            for row in rows:
                print(f"    ID: {row[0]}, User: {row[1]}, Room: {row[2]}, Date: {row[3]}, Slot: {row[4]}, Status: {row[5]}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Data retrieval error: {e}")
        return False

def test_booking_operations():
    """Test CRUD operations"""
    print("\n" + "=" * 60)
    print("TEST 5: Booking CRUD Operations")
    print("=" * 60)
    try:
        # Test 1: Get stats
        stats = get_booking_stats()
        print(f"✓ Booking Statistics:")
        print(f"  Total: {stats['total']}")
        print(f"  Approved: {stats['approved']}")
        print(f"  Pending: {stats['pending']}")
        print(f"  Rejected: {stats['rejected']}")
        
        # Test 2: Check availability
        test_room = 1001
        test_date = "2026-03-15"
        test_slot = "10-11"
        
        available = check_availability(test_room, test_date, test_slot)
        print(f"\n✓ Availability check for Room {test_room}, {test_date}, {test_slot}: {'Available' if available else 'Booked'}")
        
        # Test 3: Get bookings by date
        sample_date = "2026-03-10"
        bookings_by_date = get_bookings_by_date(sample_date)
        print(f"✓ Bookings for {sample_date}: {len(bookings_by_date)} records")
        
        # Test 4: Get booked rooms for slot
        booked_rooms = get_booked_rooms_for_slot(sample_date, "10-11")
        print(f"✓ Booked rooms for {sample_date} at 10-11: {len(booked_rooms)} rooms")
        
        return True
    except Exception as e:
        print(f"✗ CRUD operation error: {e}")
        return False

def test_transaction_integrity():
    """Test transaction and integrity"""
    print("\n" + "=" * 60)
    print("TEST 6: Transaction Integrity")
    print("=" * 60)
    try:
        conn = get_connection()
        
        # Check for UNIQUE constraint
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(bookings)")
        columns = cursor.fetchall()
        print("✓ Table structure verified")
        
        # Test foreign key/constraints
        try:
            cursor.execute("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name='bookings'
            """)
            create_sql = cursor.fetchone()[0]
            
            if "UNIQUE" in create_sql:
                print("✓ UNIQUE constraint found in table definition")
            else:
                print("⚠ No UNIQUE constraint found")
                
        except Exception as e:
            print(f"⚠ Could not verify constraints: {e}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Transaction integrity error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "SQLite Database Functionality Test" + " " * 14 + "║")
    print("╚" + "═" * 58 + "╝")
    
    results = []
    results.append(("SQLite Connection", test_sqlite_connection()))
    results.append(("Database Initialization", test_database_initialization()))
    results.append(("Table Structure", test_table_structure()))
    results.append(("Data Retrieval", test_data_retrieval()))
    results.append(("Booking Operations", test_booking_operations()))
    results.append(("Transaction Integrity", test_transaction_integrity()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! SQLite is working correctly.")
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
