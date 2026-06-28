

#ifndef STUDENT_H
#define STUDENT_H

#include "User.h"

class Student : public User {
public:
  
    Student(const std::string& id, const std::string& pass)
        : User(id, pass) {}


    void showMenu() const override {
        std::cout << "\n";
        std::cout << "  ╔══════════════════════════════════════╗\n";
        std::cout << "  ║        STUDENT DASHBOARD             ║\n";
        std::cout << "  ╠══════════════════════════════════════╣\n";
        std::cout << "  ║  [1]  Request a Room Booking         ║\n";
        std::cout << "  ║  [2]  View My Bookings               ║\n";
        std::cout << "  ║  [3]  Logout                         ║\n";
        std::cout << "  ╚══════════════════════════════════════╝\n";
        std::cout << "  Enter choice: ";
    }

 
    std::string getRole() const override {
        return "Student";
    }
};

#endif 
