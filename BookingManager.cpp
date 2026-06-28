#ifndef BOOKINGMANAGER_H
#define BOOKINGMANAGER_H

#include "Booking.h"
#include "FileManager.h"
#include "MLRecommendation.h"
#include <vector>
#include <string>
#include <iostream>
#include <iomanip>
#include <algorithm>
#include <set>

class BookingManager {
private:
   
    FileManager      fileManager;   
    MLRecommendation mlEngine;      
    
    std::vector<Booking> bookings;

  
    const std::vector<std::string> validSlots = {"9-11", "11-1", "2-4", "4-6"};

  
    bool isValidRoom(const std::string& input, int& roomOut) const {
        if (input.size() != 4) return false;
        for (char c : input) {
            if (!isdigit(c)) return false;
        }
        roomOut = std::stoi(input);
        return (roomOut >= 1000 && roomOut <= 9999);
    }

   
    bool isValidDate(const std::string& input) const {
        if (input.size() != 10) return false;
        if (input[4] != '-' || input[7] != '-') return false;
        for (int i = 0; i < 10; ++i) {
            if (i == 4 || i == 7) continue;
            if (!isdigit(input[i])) return false;
        }
        int month = std::stoi(input.substr(5, 2));
        int day   = std::stoi(input.substr(8, 2));
        return (month >= 1 && month <= 12 && day >= 1 && day <= 31);
    }

    
    bool isValidSlot(const std::string& input) const {
        return std::find(validSlots.begin(), validSlots.end(), input) != validSlots.end();
    }

    
    bool isDuplicate(const std::string& uid, int room,
                     const std::string& date, const std::string& slot) const {
        for (const auto& b : bookings) {
            if (b.getUserID() == uid && b.getRoomNo() == room &&
                b.getDate() == date && b.getSlot() == slot) {
                return true;
            }
        }
        return false;
    }

public:
    
    BookingManager() {
        bookings = fileManager.loadBookings();
    }

    
    int getTotalBookings() const {
        return static_cast<int>(bookings.size());
    }

    
    void requestBooking(const std::string& userID) {
        std::string roomInput, day, date, slot;
        int roomNo = 0;

       
        while (true) {
            std::cout << "  Enter Room Number (4 digits, e.g. 4050): ";
            std::cin >> roomInput;
            if (isValidRoom(roomInput, roomNo)) break;
            std::cout << "  [!] Invalid room. Must be exactly 4 digits.\n";
        }

        
        std::cout << "  Enter Day (e.g. Monday): ";
        std::cin >> day;

       
        while (true) {
            std::cout << "  Enter Date (YYYY-MM-DD): ";
            std::cin >> date;
            if (isValidDate(date)) break;
            std::cout << "  [!] Invalid date format. Use YYYY-MM-DD.\n";
        }

        
        while (true) {
            std::cout << "  Enter Time Slot (9-11 / 11-1 / 2-4 / 4-6): ";
            std::cin >> slot;
            if (isValidSlot(slot)) break;
            std::cout << "  [!] Invalid slot. Choose from: 9-11, 11-1, 2-4, 4-6\n";
        }

        
        if (isDuplicate(userID, roomNo, date, slot)) {
            std::cout << "\n  [!] You already have this exact booking.\n";
            return;
        }

       
        bool conflict = false;
        for (const auto& b : bookings) {
            if (b.conflictsWith(roomNo, date, slot)) {
                conflict = true;
                break;
            }
        }

        if (conflict) {
            
            mlEngine.showSuggestions(bookings, userID, roomNo, date, slot);
        } else {
           
            Booking newBooking(userID, roomNo, day, date, slot, "Pending");
            bookings.push_back(newBooking);
            fileManager.appendBooking(newBooking);

            std::cout << "\n  ╔══════════════════════════════════════╗\n";
            std::cout << "  ║  ✓  Booking Created Successfully!    ║\n";
            std::cout << "  ╠══════════════════════════════════════╣\n";
            std::cout << "  ║  Room : " << roomNo << "                          ║\n";
            std::cout << "  ║  Date : " << date;
            for (int i = static_cast<int>(date.size()); i < 28; ++i) std::cout << " ";
            std::cout << "║\n";
            std::cout << "  ║  Slot : " << slot;
            for (int i = static_cast<int>(slot.size()); i < 28; ++i) std::cout << " ";
            std::cout << "║\n";
            std::cout << "  ║  Status: Pending                      ║\n";
            std::cout << "  ╚══════════════════════════════════════╝\n";
        }
    }

    
    void viewMyBookings(const std::string& userID) const {
        std::cout << "\n  ── Your Bookings ─────────────────────────────────────────\n";
        std::cout << "  " << std::left
                  << std::setw(10) << "Room"
                  << std::setw(12) << "Day"
                  << std::setw(14) << "Date"
                  << std::setw(10) << "Slot"
                  << std::setw(10) << "Status" << "\n";
        std::cout << "  ──────────────────────────────────────────────────────────\n";

        int count = 0;
        for (const auto& b : bookings) {
            if (b.getUserID() == userID) {
                std::cout << "  " << std::left
                          << std::setw(10) << b.getRoomNo()
                          << std::setw(12) << b.getDay()
                          << std::setw(14) << b.getDate()
                          << std::setw(10) << b.getSlot()
                          << std::setw(10) << b.getStatus() << "\n";
                ++count;
            }
        }
        if (count == 0) {
            std::cout << "  (no bookings found)\n";
        }
        std::cout << "  ──────────────────────────────────────────────────────────\n";
        std::cout << "  Total: " << count << " booking(s)\n";
    }

    
    void viewAllBookings() const {
        std::cout << "\n  ── All Bookings ──────────────────────────────────────────────────────\n";
        std::cout << "  " << std::left
                  << std::setw(8)  << "#"
                  << std::setw(10) << "UserID"
                  << std::setw(8)  << "Room"
                  << std::setw(12) << "Day"
                  << std::setw(14) << "Date"
                  << std::setw(10) << "Slot"
                  << std::setw(10) << "Status" << "\n";
        std::cout << "  ─────────────────────────────────────────────────────────────────────────\n";

        for (int i = 0; i < static_cast<int>(bookings.size()); ++i) {
            const auto& b = bookings[i];
            std::cout << "  " << std::left
                      << std::setw(8)  << (i + 1)
                      << std::setw(10) << b.getUserID()
                      << std::setw(8)  << b.getRoomNo()
                      << std::setw(12) << b.getDay()
                      << std::setw(14) << b.getDate()
                      << std::setw(10) << b.getSlot()
                      << std::setw(10) << b.getStatus() << "\n";
        }
        std::cout << "  ─────────────────────────────────────────────────────────────────────────\n";
        std::cout << "  Total bookings: " << bookings.size() << "\n";
    }

    
    void approveBooking() {
        
        std::vector<int> pendingIndices;
        std::cout << "\n  ── Pending Bookings ──────────────────────────────────────\n";
        std::cout << "  " << std::left
                  << std::setw(6)  << "#"
                  << std::setw(10) << "UserID"
                  << std::setw(8)  << "Room"
                  << std::setw(12) << "Day"
                  << std::setw(14) << "Date"
                  << std::setw(10) << "Slot" << "\n";
        std::cout << "  ──────────────────────────────────────────────────────────\n";

        for (int i = 0; i < static_cast<int>(bookings.size()); ++i) {
            if (bookings[i].getStatus() == "Pending") {
                pendingIndices.push_back(i);
                std::cout << "  " << std::left
                          << std::setw(6)  << pendingIndices.size()
                          << std::setw(10) << bookings[i].getUserID()
                          << std::setw(8)  << bookings[i].getRoomNo()
                          << std::setw(12) << bookings[i].getDay()
                          << std::setw(14) << bookings[i].getDate()
                          << std::setw(10) << bookings[i].getSlot() << "\n";
            }
        }

        if (pendingIndices.empty()) {
            std::cout << "  (no pending bookings)\n";
            return;
        }

        std::cout << "  ──────────────────────────────────────────────────────────\n";
        std::cout << "  Enter booking # to approve (0 to cancel): ";

        int choice = 0;
        std::cin >> choice;
        if (std::cin.fail()) {
            std::cin.clear();
            std::cin.ignore(10000, '\n');
            std::cout << "  [!] Invalid input.\n";
            return;
        }

        if (choice < 1 || choice > static_cast<int>(pendingIndices.size())) {
            std::cout << "  [!] Cancelled or invalid selection.\n";
            return;
        }

        int idx = pendingIndices[choice - 1];
        bookings[idx].setStatus("Approved");
        fileManager.saveBookings(bookings);      

        std::cout << "  ✓ Booking #" << choice << " approved successfully!\n";
    }
};

#endif 
