

#ifndef FACULTY_H
#define FACULTY_H

#include "User.h"

class Faculty : public User {
public:
   
    Faculty(const std::string& id, const std::string& pass)
        : User(id, pass) {}

   
    void showMenu() const override {
        std::cout << "\n";
        std::cout << "  ╔══════════════════════════════════════╗\n";
        std::cout << "  ║        FACULTY DASHBOARD             ║\n";
        std::cout << "  ╠══════════════════════════════════════╣\n";
        std::cout << "  ║  [1]  View All Bookings              ║\n";
        std::cout << "  ║  [2]  Approve a Booking              ║\n";
        std::cout << "  ║  [3]  Logout                         ║\n";
        std::cout << "  ╚══════════════════════════════════════╝\n";
        std::cout << "  Enter choice: ";
    }


    std::string getRole() const override {
        return "Faculty";
    }
};

#endif 
