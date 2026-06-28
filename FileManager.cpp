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
    std::string filePath;   

  
    bool fileExists(const std::string& path) const {
        struct stat info;
        return (stat(path.c_str(), &info) == 0);
    }

    void ensureDirectoryExists() const {
  
        std::string dir = filePath.substr(0, filePath.find_last_of("/\\"));
        #ifdef _WIN32
            std::string cmd = "if not exist \"" + dir + "\" mkdir \"" + dir + "\"";
        #else
            std::string cmd = "mkdir -p \"" + dir + "\"";
        #endif
        system(cmd.c_str());
    }


    void generateSampleData(std::vector<Booking>& bookings) const {
        static const char* days[]  = {"Monday","Tuesday","Wednesday",
                                       "Thursday","Friday","Saturday"};
        static const char* slots[] = {"9-11","11-1","2-4","4-6"};
        static const char* stats[] = {"Pending","Approved"};

        srand(static_cast<unsigned>(time(nullptr)));

        for (int i = 0; i < 200; ++i) {
       
            int uid     = 1001 + rand() % 20;
            std::string userID = "S" + std::to_string(uid);

            int room    = 4001 + rand() % 99;

     
            std::string day = days[rand() % 6];

   
            int dd      = 1 + rand() % 28;
            std::string date = std::string("2026-03-") + (dd < 10 ? "0" : "") + std::to_string(dd);

 
            std::string slot = slots[rand() % 4];

            std::string status = stats[rand() % 2];

            bookings.emplace_back(userID, room, day, date, slot, status);
        }
    }

public:

    explicit FileManager(const std::string& path = "data/history.txt")
        : filePath(path) {}

  
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
                if (b.getRoomNo() != 0) {      
                    bookings.push_back(b);
                }
            }
        }
        fin.close();

     
        if (bookings.empty()) {
            std::cout << "  [INFO] File empty. Generating 200 sample records...\n";
            generateSampleData(bookings);
            saveBookings(bookings);
        }

        return bookings;
    }


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

#endif 