

#ifndef MLRECOMMENDATION_H
#define MLRECOMMENDATION_H

#include "Booking.h"
#include <vector>
#include <map>
#include <string>
#include <climits>
#include <cstdlib>
#include <iostream>
#include <algorithm>

class MLRecommendation {
public:

   
    std::string getUserPreferredSlot(const std::vector<Booking>& bookings,
                                     const std::string& userID) const {
        std::map<std::string, int> slotFreq;

        for (const auto& b : bookings) {
            if (b.getUserID() == userID) {
                slotFreq[b.getSlot()]++;
            }
        }

        std::string bestSlot = "N/A";
        int maxCount = 0;
        for (const auto& p : slotFreq) {
            if (p.second > maxCount) {
                maxCount = p.second;
                bestSlot = p.first;
            }
        }
        return bestSlot;
    }

   
    std::string getRoomPopularSlot(const std::vector<Booking>& bookings,
                                    int roomNo) const {
        std::map<std::string, int> slotFreq;

        for (const auto& b : bookings) {
            if (b.getRoomNo() == roomNo) {
                slotFreq[b.getSlot()]++;
            }
        }

        std::string bestSlot = "N/A";
        int maxCount = 0;
        for (const auto& p : slotFreq) {
            if (p.second > maxCount) {
                maxCount = p.second;
                bestSlot = p.first;
            }
        }
        return bestSlot;
    }

   
    int getClosestAvailableRoom(const std::vector<Booking>& bookings,
                                 int requestedRoom,
                                 const std::string& date,
                                 const std::string& slot) const {
        
        std::map<int, bool> occupied;
        for (const auto& b : bookings) {
            if (b.getDate() == date && b.getSlot() == slot) {
                occupied[b.getRoomNo()] = true;
            }
        }

        int closestRoom = 0;
        int minDist     = INT_MAX;

        
        for (int r = 4001; r <= 4099; ++r) {
            if (occupied.find(r) == occupied.end()) {   
                int dist = std::abs(requestedRoom - r);
                if (dist < minDist) {
                    minDist     = dist;
                    closestRoom = r;
                }
            }
        }
        return closestRoom;
    }

   
    void showSuggestions(const std::vector<Booking>& bookings,
                         const std::string& userID,
                         int roomNo,
                         const std::string& date,
                         const std::string& slot) const {
        std::string preferred   = getUserPreferredSlot(bookings, userID);
        std::string popular     = getRoomPopularSlot(bookings, roomNo);
        int         closestRoom = getClosestAvailableRoom(bookings, roomNo, date, slot);

        std::cout << "\n";
        std::cout << "  ╔══════════════════════════════════════════════╗\n";
        std::cout << "  ║   ⚠  BOOKING CONFLICT — ML SUGGESTIONS     ║\n";
        std::cout << "  ╠══════════════════════════════════════════════╣\n";
        std::cout << "  ║  Booking not available!                     ║\n";
        std::cout << "  ║                                              ║\n";
        std::cout << "  ║  Suggestions:                                ║\n";
        std::cout << "  ║  ▸ User preferred slot : " << preferred;
       
        for (int i = static_cast<int>(preferred.size()); i < 20; ++i) std::cout << " ";
        std::cout << "║\n";
        std::cout << "  ║  ▸ Popular slot (room) : " << popular;
        for (int i = static_cast<int>(popular.size()); i < 20; ++i) std::cout << " ";
        std::cout << "║\n";
        if (closestRoom > 0) {
            std::string roomStr = std::to_string(closestRoom);
            std::cout << "  ║  ▸ Closest avail. room: " << roomStr;
            for (int i = static_cast<int>(roomStr.size()); i < 20; ++i) std::cout << " ";
            std::cout << "║\n";
        } else {
            std::cout << "  ║  ▸ Closest avail. room: None available   ║\n";
        }
        std::cout << "  ╚══════════════════════════════════════════════╝\n";
    }
};

#endif