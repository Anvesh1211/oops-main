# ResourcePro — Project Documentation

## Overview
ResourcePro is a College Resource Booking System with ML-powered suggestions, C++ OOP backend engine, Flask API layer, SQLite database, and a premium web frontend.

## Architecture
```
┌─────────────────────────────────────────────────┐
│                  Web Frontend                    │
│  (HTML/CSS/JS + Auth Pages + Dashboards)         │
├─────────────────────────────────────────────────┤
│              Flask Backend (Python)              │
│    ┌──────────────┐  ┌───────────────────┐      │
│    │  Booking API  │  │  Auth API (JWT)   │      │
│    └──────────────┘  └───────────────────┘      │
├─────────────────────────────────────────────────┤
│         C++ OOP Engine  │  ML Models             │
├─────────────────────────────────────────────────┤
│              SQLite Database                     │
│    ┌──────────────┐  ┌───────────────────┐      │
│    │  booking.db   │  │  db.sqlite3 (auth)│      │
│    └──────────────┘  └───────────────────┘      │
└─────────────────────────────────────────────────┘
```

## Key Components
- **AUTH/** — Authentication module (JWT, bcrypt, RBAC)
- **FRONTEND/** — Auth frontend pages (login, register, dashboards)
- **frontend/** — Original booking system frontend
- **database/** — Booking database manager
- **DATABASE/** — Auth database (auto-created)
- **backend_cpp/** — C++ booking engine
- **ml/** — Machine learning models

## Tech Stack
| Component | Technology |
|-----------|-----------|
| Backend | Flask (Python) |
| Auth | JWT + bcrypt |
| Database | SQLite |
| Frontend | HTML/CSS/JS |
| ML | scikit-learn |
| C++ Engine | OOP booking logic |

## Running
```bash
python app.py
# Server: http://localhost:5000
# Login:  http://localhost:5000/login.html
```

## Testing
```bash
python AUTH/test_auth.py
```
