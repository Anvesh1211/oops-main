
 
#ifndef USER_H
#define USER_H

#include <string>
#include <iostream>


class User {
private:
    std::string userID;   
    std::string password;

public:
    
    User(const std::string& id, const std::string& pass)
        : userID(id), password(pass) {}

    
    virtual ~User() {}

   
    virtual void showMenu() const = 0;         
    virtual std::string getRole() const = 0;    

   
    std::string getUserID() const { return userID; }

    
    bool authenticate(const std::string& pass) const {
        return password == pass;
    }
};

#endif 
