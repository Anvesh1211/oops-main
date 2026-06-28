#include <iostream>
#include <string>
#include <limits>
#include <memory>       

#include "User.h"
#include "Student.h"
#include "Faculty.h"
#include "BookingManager.h"

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

static void showBanner() {
    std::cout << "\n";
    std::cout << "  ╔══════════════════════════════════════════════════════╗\n";
    std::cout << "  ║   COLLEGE RESOURCE BOOKING & HYBRID ML SYSTEM       ║\n";
    std::cout << "  ║   ────────────────────────────────────────────────   ║\n";
    std::cout << "  ║   OOP + ML Recommendation + File Handling           ║\n";
    std::cout << "  ╚══════════════════════════════════════════════════════╝\n";
}


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
        return nullptr; 
    }

    std::string uid, pass;
    std::cout << "  Enter User ID  : ";
    std::cin >> uid;
    std::cout << "  Enter Password : ";
    std::cin >> pass;

    if (choice == 1) {
     
        return std::make_unique<Student>(uid, pass);
    } else if (choice == 2) {
      
        return std::make_unique<Faculty>(uid, pass);
    }

    std::cout << "  [!] Invalid selection.\n";
    return nullptr;
}


static void studentSession(User* user, BookingManager& manager) {
    while (true) {
        user->showMenu(); 

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


static void facultySession(User* user, BookingManager& manager) {
    while (true) {
        user->showMenu();  

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


int main() {
    showBanner();

  
    BookingManager manager;

    std::cout << "  [INFO] System loaded. Total bookings: "
              << manager.getTotalBookings() << "\n";

    
    while (true) {
     
        std::unique_ptr<User> user = loginScreen();

        if (!user) {
 
            std::cout << "\n  ╔══════════════════════════════════════╗\n";
            std::cout << "  ║  Thank you for using the system!     ║\n";
            std::cout << "  ║  Goodbye!                            ║\n";
            std::cout << "  ╚══════════════════════════════════════╝\n\n";
            break;
        }

        std::cout << "\n  Welcome, " << user->getUserID()
                  << " (" << user->getRole() << ")\n";

     
        if (user->getRole() == "Student") {
            studentSession(user.get(), manager);
        } else if (user->getRole() == "Faculty") {
            facultySession(user.get(), manager);
        }
    }

    return 0;
}
