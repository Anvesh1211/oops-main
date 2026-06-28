

#ifndef BOOKING_H
#define BOOKING_H

#include <string>
#include <sstream>

class Booking {
private:
   std::string userID;
    int         roomNo;     
    std::string day;        
    std::string date;       
    std::string slot;       
    std::string status;     
public:
  
    Booking() : roomNo(0), status("Pending") {}

  
    Booking(const std::string& uid, int room,
            const std::string& d, const std::string& dt,
            const std::string& sl, const std::string& st)
        : userID(uid), roomNo(room), day(d), date(dt), slot(sl), status(st) {}

    
    std::string getUserID()  const { return userID; }
    int         getRoomNo()  const { return roomNo; }
    std::string getDay()     const { return day; }
    std::string getDate()    const { return date; }
    std::string getSlot()    const { return slot; }
    std::string getStatus()  const { return status; }

   
    void setStatus(const std::string& s) { status = s; }


    std::string toFileString() const {
        std::ostringstream oss;
        oss << userID << " " << roomNo << " " << day << " "
            << date   << " " << slot   << " " << status;
        return oss.str();
    }

    
    static Booking fromFileString(const std::string& line) {
        std::istringstream iss(line);
        std::string uid, d, dt, sl, st;
        int room;
        if (iss >> uid >> room >> d >> dt >> sl >> st) {
            return Booking(uid, room, d, dt, sl, st);
        }
        return Booking(); 
    }

    bool conflictsWith(int r, const std::string& dt, const std::string& sl) const {
        return (roomNo == r && date == dt && slot == sl);
    }
};

#endif 
