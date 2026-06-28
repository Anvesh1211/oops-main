/*
 * ============================================================
 *  RoomGenerator.h — Dynamic Room Generator (OOP)
 * ============================================================
 *  OOP Concepts Used:
 *    - Encapsulation: Room list is private
 *    - Abstraction: generateRooms() hides implementation
 *    - Dynamic Objects: vector managed at runtime
 *
 *  Room Range: 1001 → 4410
 *    Floors: 1–4
 *    Rooms per floor: 001–410
 *    Format: floor * 1000 + room_number
 * ============================================================
 */

#ifndef ROOMGENERATOR_H
#define ROOMGENERATOR_H

#include <vector>
#include <string>
#include <algorithm>
#include <cmath>

class RoomGenerator {
private:
    std::vector<int> rooms;

    void generateRooms() {
        rooms.clear();
        for (int floor = 1; floor <= 4; ++floor) {
            for (int room = 1; room <= 410; ++room) {
                int roomNo = floor * 1000 + room;
                rooms.push_back(roomNo);
            }
        }
        // Sort numerically (already sorted by construction)
        std::sort(rooms.begin(), rooms.end());
    }

public:
    RoomGenerator() {
        generateRooms();
    }

    const std::vector<int>& getRooms() const {
        return rooms;
    }

    int getTotalRooms() const {
        return static_cast<int>(rooms.size());
    }

    bool isValidRoom(int roomNo) const {
        return std::binary_search(rooms.begin(), rooms.end(), roomNo);
    }

    // Find closest room to requested room from a list of available rooms
    int findClosestRoom(int requestedRoom, const std::vector<int>& availableRooms) const {
        if (availableRooms.empty()) return 0;

        int closest = 0;
        int minDist = INT_MAX;
        for (int r : availableRooms) {
            int dist = std::abs(requestedRoom - r);
            if (dist < minDist) {
                minDist = dist;
                closest = r;
            }
        }
        return closest;
    }

    // Lexicographical comparison of room numbers as strings
    static bool lexCompare(int a, int b) {
        return std::to_string(a) < std::to_string(b);
    }

    // Get rooms sorted lexicographically
    std::vector<int> getRoomsLexSorted() const {
        std::vector<int> sorted = rooms;
        std::sort(sorted.begin(), sorted.end(), lexCompare);
        return sorted;
    }
};

#endif // ROOMGENERATOR_H
