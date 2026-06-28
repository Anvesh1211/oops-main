/*
 * ============================================================
 *  Student.h — Derived Class (Inheritance + Polymorphism)
 * ============================================================
 *  OOP Concepts Used:
 *    - Inheritance: Student inherits from User
 *    - Polymorphism: Overrides showMenu() and getRole()
 * ============================================================
 */

#ifndef STUDENT_H
#define STUDENT_H

#include "User.h"

class Student : public User {
public:
    // Constructor — delegates to base class
    Student(const std::string& id, const std::string& pass)
        : User(id, pass) {}

    // Polymorphic override: Student-specific menu
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

    // Polymorphic override: role identifier
    std::string getRole() const override {
        return "Student";
    }
};

#endif // STUDENT_H
