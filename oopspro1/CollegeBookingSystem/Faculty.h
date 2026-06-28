/*
 * ============================================================
 *  Faculty.h — Derived Class (Inheritance + Polymorphism)
 * ============================================================
 *  OOP Concepts Used:
 *    - Inheritance: Faculty inherits from User
 *    - Polymorphism: Overrides showMenu() and getRole()
 * ============================================================
 */

#ifndef FACULTY_H
#define FACULTY_H

#include "User.h"

class Faculty : public User {
public:
    // Constructor — delegates to base class
    Faculty(const std::string& id, const std::string& pass)
        : User(id, pass) {}

    // Polymorphic override: Faculty-specific menu
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

    // Polymorphic override: role identifier
    std::string getRole() const override {
        return "Faculty";
    }
};

#endif // FACULTY_H
