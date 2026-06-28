/*
 * ============================================================
 *  FileManager.h — File I/O Handler (File Handling)
 * ============================================================
 *  Responsibilities:
 *    - Load booking history from data/history.txt
 *    - Save bookings back to the file
 *    - Auto-create the file and generate 200 sample records
 *      if the file does not exist or is empty
 *  OOP Concepts Used:
 *    - Encapsulation: file path is private
 *    - Composition: used inside BookingManager
 * ============================================================
 */

#ifndef FILEMANAGER_H
#define FILEMANAGER_H

#include "Booking.h"
#include <vector>
#include <fstream>
#include <iostream>
#include <cstdlib>
#include <ctime>
#include <sys/stat.h>
#include <string>

class FileManager {
private:
    std::string filePath;   // Encapsulated file path

    // ---- Helper: check if a file exists ----
    bool fileExists(const std::string& path) const {
        struct stat info;
        return (stat(path.c_str(), &info) == 0);
    }

    // ---- Helper: ensure the data/ directory exists ----
    void ensureDirectoryExists() const {
        // Extract directory part
        std::string dir = filePath.substr(0, filePath.find_last_of("/\\"));
        #ifdef _WIN32
            std::string cmd = "if not exist \"" + dir + "\" mkdir \"" + dir + "\"";
        #else
            std::string cmd = "mkdir -p \"" + dir + "\"";
        #endif
        system(cmd.c_str());
    }

    /*
     * Generate 200 realistic sample records.
     * Data ranges:
     *   UserID : S1001 – S1020 (students)
     *   Room   : 4001  – 4099
     *   Day    : Monday – Saturday
     *   Date   : 2026-03-01 through 2026-03-28
     *   Slot   : 9-11, 11-1, 2-4, 4-6
     *   Status : Pending / Approved
     */
    void generateSampleData(std::vector<Booking>& bookings) const {
        static const char* days[]  = {"Monday","Tuesday","Wednesday",
                                       "Thursday","Friday","Saturday"};
        static const char* slots[] = {"9-11","11-1","2-4","4-6"};
        static const char* stats[] = {"Pending","Approved"};

        srand(static_cast<unsigned>(time(nullptr)));

        for (int i = 0; i < 200; ++i) {
            // Random user ID: S1001 .. S1020
            int uid     = 1001 + rand() % 20;
            std::string userID = "S" + std::to_string(uid);

            // Random room: 4001 .. 4099
            int room    = 4001 + rand() % 99;

            // Random day
            std::string day = days[rand() % 6];

            // Random date: 2026-03-DD
            int dd      = 1 + rand() % 28;
            std::string date = std::string("2026-03-") + (dd < 10 ? "0" : "") + std::to_string(dd);

            // Random slot
            std::string slot = slots[rand() % 4];

            // Random status
            std::string status = stats[rand() % 2];

            bookings.emplace_back(userID, room, day, date, slot, status);
        }
    }

public:
    // Constructor
    explicit FileManager(const std::string& path = "data/history.txt")
        : filePath(path) {}

    /*
     * Load all bookings from the file.
     * If the file doesn't exist or is empty, generate sample data
     * and save it first.
     */
    std::vector<Booking> loadBookings() {
        ensureDirectoryExists();

        std::vector<Booking> bookings;

        if (!fileExists(filePath)) {
            std::cout << "  [INFO] history.txt not found. Generating 200 sample records...\n";
            generateSampleData(bookings);
            saveBookings(bookings);
            return bookings;
        }

        std::ifstream fin(filePath);
        if (!fin.is_open()) {
            std::cout << "  [WARN] Cannot open file. Generating sample data...\n";
            generateSampleData(bookings);
            saveBookings(bookings);
            return bookings;
        }

        std::string line;
        while (std::getline(fin, line)) {
            if (!line.empty()) {
                Booking b = Booking::fromFileString(line);
                if (b.getRoomNo() != 0) {      // skip malformed lines
                    bookings.push_back(b);
                }
            }
        }
        fin.close();

        // If file was empty, seed it
        if (bookings.empty()) {
            std::cout << "  [INFO] File empty. Generating 200 sample records...\n";
            generateSampleData(bookings);
            saveBookings(bookings);
        }

        return bookings;
    }

    /*
     * Save the entire booking vector to the file (overwrite).
     */
    void saveBookings(const std::vector<Booking>& bookings) const {
        ensureDirectoryExists();

        std::ofstream fout(filePath, std::ios::trunc);
        if (!fout.is_open()) {
            std::cerr << "  [ERROR] Cannot write to " << filePath << "\n";
            return;
        }
        for (const auto& b : bookings) {
            fout << b.toFileString() << "\n";
        }
        fout.close();
    }

    /*
     * Append a single booking to the file.
     */
    void appendBooking(const Booking& b) const {
        ensureDirectoryExists();

        std::ofstream fout(filePath, std::ios::app);
        if (!fout.is_open()) {
            std::cerr << "  [ERROR] Cannot append to " << filePath << "\n";
            return;
        }
        fout << b.toFileString() << "\n";
        fout.close();
    }
};

#endif // FILEMANAGER_H
