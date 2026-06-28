

#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <map>
#include <algorithm>
#include <cmath>
#include <climits>
#include <fstream>
#include <cstdlib>
#include <ctime>
#include <set>
#include "RoomGenerator.h"



static std::string jsonEscape(const std::string& s) {
    std::string out;
    for (char c : s) {
        if (c == '"') out += "\\\"";
        else if (c == '\\') out += "\\\\";
        else if (c == '\n') out += "\\n";
        else out += c;
    }
    return out;
}

static std::string extractJsonValue(const std::string& json, const std::string& key) {
    std::string searchKey = "\"" + key + "\"";
    size_t pos = json.find(searchKey);
    if (pos == std::string::npos) return "";

    pos = json.find(':', pos);
    if (pos == std::string::npos) return "";
    pos++;

    while (pos < json.size() && (json[pos] == ' ' || json[pos] == '\t')) pos++;

    if (pos >= json.size()) return "";

    if (json[pos] == '"') {
  
        pos++;
        size_t end = json.find('"', pos);
        if (end == std::string::npos) return "";
        return json.substr(pos, end - pos);
    } else {
       
        size_t end = pos;
        while (end < json.size() && json[end] != ',' && json[end] != '}' && json[end] != ' ') end++;
        return json.substr(pos, end - pos);
    }
}



struct BookingRecord {
    std::string user;
    int room;
    std::string date;
    std::string slot;
    std::string status;

    std::string toJson() const {
        std::ostringstream oss;
        oss << "{\"user\":\"" << jsonEscape(user) << "\","
            << "\"room\":" << room << ","
            << "\"date\":\"" << jsonEscape(date) << "\","
            << "\"slot\":\"" << jsonEscape(slot) << "\","
            << "\"status\":\"" << jsonEscape(status) << "\"}";
        return oss.str();
    }
};



class BookingEngine {
private:
    RoomGenerator roomGen;
    std::vector<BookingRecord> bookings;
    std::string dbPath;

    const std::vector<std::string> validSlots = {
        "9-10", "10-11", "11-12", "12-1", "2-3", "3-4"
    };

 
    bool isBooked(int room, const std::string& date, const std::string& slot) const {
        for (const auto& b : bookings) {
            if (b.room == room && b.date == date && b.slot == slot &&
                (b.status == "Approved" || b.status == "Pending")) {
                return true;
            }
        }
        return false;
    }

    int findClosestAvailable(int requestedRoom, const std::string& date,
                             const std::string& slot) const {
        const auto& allRooms = roomGen.getRooms();
        std::vector<int> available;

        for (int r : allRooms) {
            if (!isBooked(r, date, slot)) {
                available.push_back(r);
            }
        }

        return roomGen.findClosestRoom(requestedRoom, available);
    }


    std::string findNextSlot(int room, const std::string& date) const {
        for (const auto& s : validSlots) {
            if (!isBooked(room, date, s)) {
                return s;
            }
        }
        return "";
    }


    void loadFromFile() {
        bookings.clear();
        std::ifstream fin(dbPath);
        if (!fin.is_open()) return;

        std::string line;
        while (std::getline(fin, line)) {
            if (line.empty()) continue;
            std::istringstream iss(line);
            BookingRecord b;
            if (iss >> b.user >> b.room >> b.date >> b.slot >> b.status) {
                bookings.push_back(b);
            }
        }
        fin.close();
    }

    void saveToFile() const {
        std::ofstream fout(dbPath, std::ios::trunc);
        if (!fout.is_open()) return;
        for (const auto& b : bookings) {
            fout << b.user << " " << b.room << " " << b.date << " "
                 << b.slot << " " << b.status << "\n";
        }
        fout.close();
    }

public:
    BookingEngine(const std::string& path = "data/bookings.txt")
        : dbPath(path) {
        loadFromFile();
    }

    std::string checkAndBook(const std::string& user, int room,
                             const std::string& date, const std::string& slot,
                             bool doBook) {
                if (!roomGen.isValidRoom(room)) {
            return "{\"status\":\"error\",\"message\":\"Invalid room number\"}";
        }

       
        if (!isBooked(room, date, slot)) {
            if (doBook) {
                BookingRecord b;
                b.user = user;
                b.room = room;
                b.date = date;
                b.slot = slot;
                b.status = "Pending";
                bookings.push_back(b);
                saveToFile();
                return "{\"status\":\"booked\",\"room\":" + std::to_string(room) +
                       ",\"date\":\"" + date + "\",\"slot\":\"" + slot +
                       "\",\"message\":\"Booking created successfully\"}";
            }
            return "{\"status\":\"available\",\"room\":" + std::to_string(room) +
                   ",\"date\":\"" + date + "\",\"slot\":\"" + slot + "\"}";
        }

      
        int closestRoom = findClosestAvailable(room, date, slot);
        std::string nextSlot = findNextSlot(room, date);

        std::ostringstream oss;
        oss << "{\"status\":\"unavailable\","
            << "\"requested_room\":" << room << ","
            << "\"date\":\"" << date << "\","
            << "\"slot\":\"" << slot << "\"";

        if (closestRoom > 0) {
            oss << ",\"suggested_room\":" << closestRoom
                << ",\"suggested_room_distance\":" << std::abs(room - closestRoom);
        }
        if (!nextSlot.empty()) {
            oss << ",\"suggested_slot\":\"" << nextSlot << "\"";
        }
        oss << ",\"message\":\"Room " << room << " is not available for " << slot
            << " on " << date << "\"}";

        return oss.str();
    }

  
    std::string getSchedule(const std::string& date) {
        std::ostringstream oss;
        oss << "{\"date\":\"" << date << "\",\"bookings\":[";

        bool first = true;
        for (const auto& b : bookings) {
            if (b.date == date) {
                if (!first) oss << ",";
                oss << b.toJson();
                first = false;
            }
        }
        oss << "]}";
        return oss.str();
    }

   
    std::string getAllBookings() {
        std::ostringstream oss;
        oss << "{\"total\":" << bookings.size() << ",\"bookings\":[";

        bool first = true;
        for (const auto& b : bookings) {
            if (!first) oss << ",";
            oss << b.toJson();
            first = false;
        }
        oss << "]}";
        return oss.str();
    }

    
    std::string getRoomStatus(const std::string& date) {
        
        std::map<int, std::map<std::string, std::string>> grid;

        for (const auto& b : bookings) {
            if (b.date == date) {
                grid[b.room][b.slot] = b.status;
            }
        }

        std::ostringstream oss;
        oss << "{\"date\":\"" << date << "\",\"rooms\":[";

        const auto& allRooms = roomGen.getRooms();
        bool first = true;

        for (auto& pair : grid) {
            if (!first) oss << ",";
            oss << "{\"room\":" << pair.first << ",\"slots\":{";
            bool sfirst = true;
            for (const auto& s : validSlots) {
                if (!sfirst) oss << ",";
                auto it = pair.second.find(s);
                if (it != pair.second.end()) {
                    oss << "\"" << s << "\":\"booked\"";
                } else {
                    oss << "\"" << s << "\":\"available\"";
                }
                sfirst = false;
            }
            oss << "}}";
            first = false;
        }

        oss << "],\"valid_slots\":[";
        for (size_t i = 0; i < validSlots.size(); i++) {
            if (i > 0) oss << ",";
            oss << "\"" << validSlots[i] << "\"";
        }
        oss << "]}";
        return oss.str();
    }


    std::string updateBookingStatus(const std::string& user, int room,
                                     const std::string& date, const std::string& slot,
                                     const std::string& newStatus) {
        for (auto& b : bookings) {
            if (b.user == user && b.room == room && b.date == date && b.slot == slot) {
                b.status = newStatus;
                saveToFile();
                return "{\"status\":\"updated\",\"message\":\"Booking " + newStatus + "\"}";
            }
        }
        return "{\"status\":\"error\",\"message\":\"Booking not found\"}";
    }

   
    std::string getValidRooms() {
        const auto& rooms = roomGen.getRooms();
        std::ostringstream oss;
        oss << "{\"total\":" << rooms.size() << ",\"rooms\":[";
        for (size_t i = 0; i < rooms.size(); i++) {
            if (i > 0) oss << ",";
            oss << rooms[i];
        }
        oss << "]}";
        return oss.str();
    }
};



int main(int argc, char* argv[]) {

    std::string dataPath = "data/bookings.txt";

   
    #ifdef _WIN32
        system("if not exist \"data\" mkdir \"data\"");
    #else
        system("mkdir -p data");
    #endif

    BookingEngine engine(dataPath);

    if (argc < 2) {
        std::cout << "{\"error\":\"No command provided. Use: check, book, schedule, rooms, status, approve, reject, allrooms\"}" << std::endl;
        return 1;
    }

    std::string command = argv[1];

    if (command == "check" || command == "book") {
        if (argc < 6) {
            std::cout << "{\"error\":\"Usage: " << command << " <user> <room> <date> <slot>\"}" << std::endl;
            return 1;
        }
        std::string user = argv[2];
        int room = std::atoi(argv[3]);
        std::string date = argv[4];
        std::string slot = argv[5];
        bool doBook = (command == "book");

        std::cout << engine.checkAndBook(user, room, date, slot, doBook) << std::endl;

    } else if (command == "schedule") {
        if (argc < 3) {
            std::cout << "{\"error\":\"Usage: schedule <date>\"}" << std::endl;
            return 1;
        }
        std::cout << engine.getSchedule(argv[2]) << std::endl;

    } else if (command == "rooms") {
        if (argc < 3) {
            std::cout << "{\"error\":\"Usage: rooms <date>\"}" << std::endl;
            return 1;
        }
        std::cout << engine.getRoomStatus(argv[2]) << std::endl;

    } else if (command == "all") {
        std::cout << engine.getAllBookings() << std::endl;

    } else if (command == "approve" || command == "reject") {
        if (argc < 6) {
            std::cout << "{\"error\":\"Usage: " << command << " <user> <room> <date> <slot>\"}" << std::endl;
            return 1;
        }
        std::string status = (command == "approve") ? "Approved" : "Rejected";
        std::cout << engine.updateBookingStatus(argv[2], std::atoi(argv[3]),
                                                 argv[4], argv[5], status) << std::endl;

    } else if (command == "allrooms") {
        std::cout << engine.getValidRooms() << std::endl;

    } else {
        std::cout << "{\"error\":\"Unknown command: " << command << "\"}" << std::endl;
        return 1;
    }

    return 0;
}
