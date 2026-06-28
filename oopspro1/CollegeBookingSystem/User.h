/*
 * ============================================================
 *  User.h — Abstract Base Class (Abstraction + Polymorphism)
 * ============================================================
 *  OOP Concepts Used:
 *    - Abstraction: Pure virtual functions (showMenu, getRole)
 *    - Polymorphism: Virtual dispatch via base-class pointer
 *    - Encapsulation: Private data with public accessors
 * ============================================================
 */

#ifndef USER_H
#define USER_H

#include <string>
#include <iostream>

// Abstract base class — cannot be instantiated directly
class User {
private:
    std::string userID;   // Encapsulated: accessed only via getter
    std::string password;

public:
    // Constructor
    User(const std::string& id, const std::string& pass)
        : userID(id), password(pass) {}

    // Virtual destructor for proper cleanup of derived objects
    virtual ~User() {}

    // ---- Pure virtual functions (Abstraction) ----
    virtual void showMenu() const = 0;          // Each role has its own menu
    virtual std::string getRole() const = 0;    // Returns "Student" or "Faculty"

    // ---- Accessors (Encapsulation) ----
    std::string getUserID() const { return userID; }

    // Authenticate against stored credentials
    bool authenticate(const std::string& pass) const {
        return password == pass;
    }
};

#endif // USER_H
