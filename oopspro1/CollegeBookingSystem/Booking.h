/*
 * ============================================================
 *  Booking.h — Booking Entity (Encapsulation)
 * ============================================================
 *  OOP Concepts Used:
 *    - Encapsulation: All data members are private;
 *      access is only through getters and setters.
 *    - Clean separation of data from logic.
 * ============================================================
 */

#ifndef BOOKING_H
#define BOOKING_H

#include <string>
#include <sstream>

class Booking {
private:
    // ---- Encapsulated data members ----
    std::string userID;
    int         roomNo;     // Must be 4 digits (validated externally)
    std::string day;        // e.g. "Monday"
    std::string date;       // e.g. "2026-03-01"
    std::string slot;       // e.g. "9-11"
    std::string status;     // "Pending" or "Approved"

public:
    // Default constructor
    Booking() : roomNo(0), status("Pending") {}

    // Parameterized constructor
    Booking(const std::string& uid, int room,
            const std::string& d, const std::string& dt,
            const std::string& sl, const std::string& st)
        : userID(uid), roomNo(room), day(d), date(dt), slot(sl), status(st) {}

    // ---- Getters (Encapsulation) ----
    std::string getUserID()  const { return userID; }
    int         getRoomNo()  const { return roomNo; }
    std::string getDay()     const { return day; }
    std::string getDate()    const { return date; }
    std::string getSlot()    const { return slot; }
    std::string getStatus()  const { return status; }

    // ---- Setters (Encapsulation) ----
    void setStatus(const std::string& s) { status = s; }

    // Serialize to file format: "UserID RoomNo Day Date Slot Status"
    std::string toFileString() const {
        std::ostringstream oss;
        oss << userID << " " << roomNo << " " << day << " "
            << date   << " " << slot   << " " << status;
        return oss.str();
    }

    // Deserialize from a single line
    static Booking fromFileString(const std::string& line) {
        std::istringstream iss(line);
        std::string uid, d, dt, sl, st;
        int room;
        if (iss >> uid >> room >> d >> dt >> sl >> st) {
            return Booking(uid, room, d, dt, sl, st);
        }
        return Booking(); // fallback
    }

    // Check for conflict: same room, same date, same slot
    bool conflictsWith(int r, const std::string& dt, const std::string& sl) const {
        return (roomNo == r && date == dt && slot == sl);
    }
};

#endif // BOOKING_H
