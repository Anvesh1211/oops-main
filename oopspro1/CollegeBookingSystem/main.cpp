/*
 * ============================================================
 *  main.cpp — College Resource Booking & Hybrid ML
 *             Recommendation System
 * ============================================================
 *
 *  OOP Concepts Demonstrated:
 *  ─────────────────────────────────────────────────────────
 *  1. Abstraction      — User is an abstract base class with
 *                         pure virtual functions.
 *  2. Inheritance       — Student and Faculty inherit from User.
 *  3. Encapsulation     — Booking data is private; accessed
 *                         only through getters/setters.
 *  4. Polymorphism      — showMenu() and getRole() are
 *                         dispatched via virtual functions.
 *  5. Composition       — BookingManager composes FileManager
 *                         and MLRecommendation.
 *  6. Dynamic Objects   — Bookings stored in std::vector and
 *                         managed at runtime.
 *  7. File Handling     — Persistent storage in data/history.txt
 *
 *  ML Models:
 *  ─────────────────────────────────────────────────────────
 *  1. User Preference   — Most frequent slot per user.
 *  2. Room Popularity   — Most frequent slot per room.
 *  3. Closest Room (KNN)— Nearest numerically-available room.
 *
 *  Build:
 *    g++ main.cpp -o booking_system
 *    ./booking_system        (Linux/Mac)
 *    booking_system.exe      (Windows)
 * ============================================================
 */

#include <iostream>
#include <string>
#include <limits>
#include <memory>       // for unique_ptr (dynamic objects)

#include "User.h"
#include "Student.h"
#include "Faculty.h"
#include "BookingManager.h"

// ──────────────────────────────────────────────────────────────
//  Helper: safely read an integer from cin, clearing bad state
// ──────────────────────────────────────────────────────────────
static int safeIntInput() {
    int val;
    std::cin >> val;
    if (std::cin.fail()) {
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        return -1;
    }
    return val;
}

// ──────────────────────────────────────────────────────────────
//  Display the main welcome banner
// ──────────────────────────────────────────────────────────────
static void showBanner() {
    std::cout << "\n";
    std::cout << "  ╔══════════════════════════════════════════════════════╗\n";
    std::cout << "  ║   COLLEGE RESOURCE BOOKING & HYBRID ML SYSTEM       ║\n";
    std::cout << "  ║   ────────────────────────────────────────────────   ║\n";
    std::cout << "  ║   OOP + ML Recommendation + File Handling           ║\n";
    std::cout << "  ╚══════════════════════════════════════════════════════╝\n";
}

// ──────────────────────────────────────────────────────────────
//  Login screen — returns a polymorphic User pointer
//  Demonstrates: Polymorphism (base-class pointer to derived)
// ──────────────────────────────────────────────────────────────
static std::unique_ptr<User> loginScreen() {
    std::cout << "\n";
    std::cout << "  ╔══════════════════════════════════════╗\n";
    std::cout << "  ║            LOGIN PORTAL              ║\n";
    std::cout << "  ╠══════════════════════════════════════╣\n";
    std::cout << "  ║  [1]  Login as Student               ║\n";
    std::cout << "  ║  [2]  Login as Faculty               ║\n";
    std::cout << "  ║  [3]  Exit                           ║\n";
    std::cout << "  ╚══════════════════════════════════════╝\n";
    std::cout << "  Enter choice: ";

    int choice = safeIntInput();

    if (choice == 3) {
        return nullptr;  // exit signal
    }

    std::string uid, pass;
    std::cout << "  Enter User ID  : ";
    std::cin >> uid;
    std::cout << "  Enter Password : ";
    std::cin >> pass;

    if (choice == 1) {
        // Polymorphism: Student* stored as User*
        return std::make_unique<Student>(uid, pass);
    } else if (choice == 2) {
        // Polymorphism: Faculty* stored as User*
        return std::make_unique<Faculty>(uid, pass);
    }

    std::cout << "  [!] Invalid selection.\n";
    return nullptr;
}

// ──────────────────────────────────────────────────────────────
//  Student session loop
// ──────────────────────────────────────────────────────────────
static void studentSession(User* user, BookingManager& manager) {
    while (true) {
        user->showMenu();  // Polymorphic call

        int choice = safeIntInput();
        switch (choice) {
            case 1:
                manager.requestBooking(user->getUserID());
                break;
            case 2:
                manager.viewMyBookings(user->getUserID());
                break;
            case 3:
                std::cout << "  Logging out...\n";
                return;
            default:
                std::cout << "  [!] Invalid choice. Try again.\n";
        }
    }
}

// ──────────────────────────────────────────────────────────────
//  Faculty session loop
// ──────────────────────────────────────────────────────────────
static void facultySession(User* user, BookingManager& manager) {
    while (true) {
        user->showMenu();  // Polymorphic call

        int choice = safeIntInput();
        switch (choice) {
            case 1:
                manager.viewAllBookings();
                break;
            case 2:
                manager.approveBooking();
                break;
            case 3:
                std::cout << "  Logging out...\n";
                return;
            default:
                std::cout << "  [!] Invalid choice. Try again.\n";
        }
    }
}

// ──────────────────────────────────────────────────────────────
//  MAIN ENTRY POINT
// ──────────────────────────────────────────────────────────────
int main() {
    showBanner();

    // Composition: BookingManager owns FileManager + MLRecommendation
    // File is loaded automatically in constructor
    BookingManager manager;

    std::cout << "  [INFO] System loaded. Total bookings: "
              << manager.getTotalBookings() << "\n";

    // Main loop
    while (true) {
        // Login — returns a polymorphic User pointer
        std::unique_ptr<User> user = loginScreen();

        if (!user) {
            // Exit or invalid
            std::cout << "\n  ╔══════════════════════════════════════╗\n";
            std::cout << "  ║  Thank you for using the system!     ║\n";
            std::cout << "  ║  Goodbye!                            ║\n";
            std::cout << "  ╚══════════════════════════════════════╝\n\n";
            break;
        }

        std::cout << "\n  Welcome, " << user->getUserID()
                  << " (" << user->getRole() << ")\n";  // Polymorphic call

        // Dispatch to role-specific session
        if (user->getRole() == "Student") {
            studentSession(user.get(), manager);
        } else if (user->getRole() == "Faculty") {
            facultySession(user.get(), manager);
        }
    }

    return 0;
}
