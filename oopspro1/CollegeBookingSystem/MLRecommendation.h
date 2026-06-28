/*
 * ============================================================
 *  MLRecommendation.h — Hybrid ML Recommendation Engine
 * ============================================================
 *  Three models are implemented:
 *
 *  Model 1 — User Preference (frequency-based)
 *    Finds the slot that a given user has booked most often.
 *
 *  Model 2 — Room Popularity (frequency-based)
 *    Finds the slot that is most popular for a given room.
 *
 *  Model 3 — Closest Available Room (KNN-inspired)
 *    Among all rooms that are free on the requested date+slot,
 *    picks the room whose number is numerically closest to the
 *    requested room:
 *        distance = abs(requestedRoom - candidateRoom)
 *
 *  OOP Concepts Used:
 *    - Encapsulation: algorithms operate on const references
 *    - Composition: used inside BookingManager
 * ============================================================
 */

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

    /*
     * Model 1 — User Preference
     * Scans all bookings for the given userID and returns the
     * slot that user has used most frequently.
     * Time complexity: O(n)
     */
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

    /*
     * Model 2 — Room Popularity
     * Scans all bookings for the given room and returns the
     * slot that is most commonly booked for that room.
     * Time complexity: O(n)
     */
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

    /*
     * Model 3 — Closest Available Room (KNN Logic)
     * For the requested date+slot, find all rooms that are
     * currently booked.  Then, among rooms in the valid range
     * (4001–4099) that are NOT booked, pick the one closest
     * to the requested room number.
     *
     * distance = abs(requestedRoom - candidateRoom)
     *
     * Returns 0 if no available room is found.
     * Time complexity: O(n + R) where R = room range size
     */
    int getClosestAvailableRoom(const std::vector<Booking>& bookings,
                                 int requestedRoom,
                                 const std::string& date,
                                 const std::string& slot) const {
        // Collect rooms booked on this date+slot
        std::map<int, bool> occupied;
        for (const auto& b : bookings) {
            if (b.getDate() == date && b.getSlot() == slot) {
                occupied[b.getRoomNo()] = true;
            }
        }

        int closestRoom = 0;
        int minDist     = INT_MAX;

        // Scan room range 4001–4099
        for (int r = 4001; r <= 4099; ++r) {
            if (occupied.find(r) == occupied.end()) {   // room is free
                int dist = std::abs(requestedRoom - r);
                if (dist < minDist) {
                    minDist     = dist;
                    closestRoom = r;
                }
            }
        }
        return closestRoom;
    }

    /*
     * Display all three ML suggestions in a formatted box.
     */
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
        // pad to fill box width
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

#endif // MLRECOMMENDATION_H
