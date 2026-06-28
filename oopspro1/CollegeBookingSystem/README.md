# 🎓 College Resource Booking & Hybrid ML Recommendation System

> A full-stack, production-ready college room booking system featuring a **C++ OOP console engine**, a **Flask REST API**, an **SQLite database**, a **scikit-learn ML prediction module**, and a **modern spreadsheet-style Web UI**.

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [System Architecture](#-system-architecture)
3. [OOP Concepts Demonstrated](#-oop-concepts-demonstrated)
4. [Project Structure](#-project-structure)
5. [Prerequisites](#-prerequisites)
6. [Step-by-Step Setup Guide](#-step-by-step-setup-guide)
   - [Part A — C++ Console Application](#part-a--c-console-application-standalone)
   - [Part B — Full-Stack Web Application](#part-b--full-stack-web-application)
7. [Running the Application](#-running-the-application)
8. [Testing](#-testing)
9. [API Reference](#-api-reference)
10. [ML Module Details](#-ml-module-details)
11. [Valid Room Ranges & Time Slots](#-valid-room-ranges--time-slots)
12. [Troubleshooting](#-troubleshooting)

---

## 📌 Project Overview

This project is a **dual-mode booking system** for college resources (rooms, labs, etc.):

| Mode | Technology | Entry Point |
|------|-----------|-------------|
| **Console App** | C++ (OOP, File I/O) | `booking_system.exe` |
| **Web App** | Flask + SQLite + ML + HTML/CSS/JS | `python app.py` |

**Key Features:**
- 🏫 Room booking with conflict detection
- 🤖 Hybrid ML suggestions (User Preference + Room Popularity + KNN Closest Room)
- 📊 Spreadsheet-style web dashboard for room schedules
- 🔒 Student and Faculty roles with separate menus
- ✅ Faculty approval workflow
- 📦 Persistent storage (file-based for C++, SQLite for web)
- 🔌 C++ engine integrated into Flask via subprocess JSON I/O

---

## 🏗 System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                        Web Browser                       │
│               frontend/index.html + script.js            │
└──────────────────────┬───────────────────────────────────┘
                       │ HTTP (REST API)
┌──────────────────────▼───────────────────────────────────┐
│                   Flask Server (app.py)                   │
│              Runs on http://localhost:5000                │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐   │
│  │  database/ │  │    ml/     │  │   backend_cpp/   │   │
│  │  SQLite DB │  │  sklearn   │  │  booking_engine  │   │
│  │ db_manager │  │  best_model│  │  (subprocess)    │   │
│  └────────────┘  └────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│           C++ Console Application (standalone)           │
│   main.cpp → BookingManager → FileManager + MLEngine     │
│                  data/history.txt                        │
└──────────────────────────────────────────────────────────┘
```

---

## 🧬 OOP Concepts Demonstrated

| Concept | Where Used |
|---|---|
| **Abstraction** | `User` is an abstract base class with pure virtual `showMenu()` and `getRole()` |
| **Inheritance** | `Student` and `Faculty` both inherit from `User` |
| **Encapsulation** | `Booking` data is private; accessed only through getters/setters |
| **Polymorphism** | `showMenu()` and `getRole()` dispatched via virtual functions through `User*` pointer |
| **Composition** | `BookingManager` composes `FileManager` (HAS-A) and `MLRecommendation` (HAS-A) |
| **Dynamic Objects** | Bookings stored in `std::vector<Booking>` and managed at runtime |
| **File Handling** | Persistent storage in `data/history.txt` and SQLite DB |

---

## 📁 Project Structure

```
CollegeBookingSystem/
│
├── 📄 main.cpp                  # C++ console app entry point
├── 📄 User.h                    # Abstract base class (Abstraction + Polymorphism)
├── 📄 Student.h                 # Inherits User — student role
├── 📄 Faculty.h                 # Inherits User — faculty role
├── 📄 Booking.h                 # Booking entity (Encapsulation)
├── 📄 BookingManager.h          # Central controller (Composition)
├── 📄 FileManager.h             # File I/O subsystem
├── 📄 MLRecommendation.h        # Hybrid ML engine (3 models)
│
├── 📄 app.py                    # Flask API server (root launcher)
├── 📄 run_tests.bat             # Automated test script (Windows)
├── 📄 run_tests.py              # Python test runner
│
├── 📁 backend/
│   └── app.py                   # Alternative Flask backend
│
├── 📁 backend_cpp/
│   ├── booking_engine.cpp        # C++ engine with JSON I/O (Flask integration)
│   ├── booking_engine.exe        # Prebuilt C++ engine binary
│   ├── RoomGenerator.h           # Room generation utility
│   └── data/                     # Runtime booking data for C++ engine
│
├── 📁 database/
│   ├── db_manager.py             # SQLite ORM & query layer
│   ├── booking.db                # SQLite database file
│   └── __init__.py
│
├── 📁 frontend/
│   ├── index.html                # Main web UI (spreadsheet-style)
│   ├── script.js                 # Frontend logic & API calls
│   └── style.css                 # Modern UI styling
│
├── 📁 ml/
│   ├── train_model.py            # ML training script (3 models)
│   ├── best_model.pkl            # Saved best model (joblib)
│   ├── training_data.csv         # Synthetic training dataset
│   ├── training_results.json     # Model comparison results
│   └── room_prediction.ipynb     # Jupyter notebook analysis
│
└── 📁 data/
    └── history.txt               # C++ console app booking history
```

---

## ✅ Prerequisites

Make sure the following are installed before proceeding:

### For C++ Console Application
| Tool | Version | Download |
|------|---------|----------|
| **g++ / MinGW-w64** | GCC 10+ | [winlibs.com](https://winlibs.com/) or [MSYS2](https://www.msys2.org/) |

Verify installation:
```bash
g++ --version
```

### For Web Application (Flask)
| Tool | Version | Download |
|------|---------|----------|
| **Python** | 3.8+ | [python.org](https://www.python.org/downloads/) |
| **pip** | Latest | Comes with Python |

Verify installation:
```bash
python --version
pip --version
```

---

## 🚀 Step-by-Step Setup Guide

### Part A — C++ Console Application (Standalone)

> This is a pure C++ terminal application. No Python or Flask needed.

---

#### Step 1: Open a Terminal

Open **Command Prompt** or **PowerShell** and navigate to the project folder:
```powershell
cd d:\oopspro1\CollegeBookingSystem
```

---

#### Step 2: Compile the C++ Source

```bash
g++ main.cpp -o booking_system -std=c++17
```

> ✅ This generates `booking_system.exe` in the current directory.

If you see errors about missing headers, ensure MinGW is properly installed and on your `PATH`.

---

#### Step 3: Run the Console Application

```bash
.\booking_system.exe
```

You will see the welcome banner:
```
  ╔══════════════════════════════════════════════════════╗
  ║   COLLEGE RESOURCE BOOKING & HYBRID ML SYSTEM       ║
  ║   ────────────────────────────────────────────────   ║
  ║   OOP + ML Recommendation + File Handling           ║
  ╚══════════════════════════════════════════════════════╝
```

---

#### Step 4: Login and Use the System

**As a Student:**
1. Choose `[1] Login as Student`
2. Enter any User ID (e.g., `S1001`) and any password
3. Select:
   - `[1]` Request a Booking
   - `[2]` View My Bookings
   - `[3]` Logout

**Booking input prompts:**
```
  Enter Room Number (4 digits, e.g. 4050): 4050
  Enter Day (e.g. Monday): Monday
  Enter Date (YYYY-MM-DD): 2026-04-15
  Enter Time Slot (9-11 / 11-1 / 2-4 / 4-6): 9-11
```

**As Faculty:**
1. Choose `[2] Login as Faculty`
2. Enter any User ID (e.g., `F001`) and any password
3. Select:
   - `[1]` View All Bookings
   - `[2]` Approve a Booking
   - `[3]` Logout

---

#### Step 5: ML Recommendations (Conflict Detection)

If a room is already booked, the system automatically triggers Hybrid ML suggestions:
```
  ╔══════════════════════════════════════════════╗
  ║   ⚠  BOOKING CONFLICT — ML SUGGESTIONS     ║
  ╠══════════════════════════════════════════════╣
  ║  Booking not available!                     ║
  ║  Suggestions:                               ║
  ║  ▸ User preferred slot : 9-11              ║
  ║  ▸ Popular slot (room) : 11-1              ║
  ║  ▸ Closest avail. room: 4049              ║
  ╚══════════════════════════════════════════════╝
```

---

### Part B — Full-Stack Web Application

> This includes the Flask API, SQLite DB, Python ML model, C++ engine integration, and web frontend.

---

#### Step 1: Navigate to the Project Directory

```powershell
cd d:\oopspro1\CollegeBookingSystem
```

---

#### Step 2: Install Python Dependencies

Install all required Python packages:
```bash
python -m pip install flask flask-cors numpy scikit-learn joblib pandas
```

Or install individually:
```bash
pip install flask
pip install flask-cors
pip install numpy
pip install scikit-learn
pip install joblib
pip install pandas
```

Verify key packages:
```bash
python -c "import flask, sklearn, joblib, numpy, pandas; print('All packages OK')"
```

---

#### Step 3: (Optional) Compile the C++ Backend Engine

The C++ engine enhances availability checking. A prebuilt binary (`booking_engine.exe`) is already included. To recompile:

```bash
cd backend_cpp
g++ booking_engine.cpp -o booking_engine -std=c++17
cd ..
```

> ⚠️ If compilation fails, the Flask app gracefully falls back to the Python-only mode.

---

#### Step 4: (Optional) Retrain the ML Model

A pre-trained model (`ml/best_model.pkl`) is already included. To retrain:

```bash
python ml/train_model.py
```

This will:
- Generate 1,500 synthetic booking samples
- Train 3 models: Random Forest, Decision Tree, Logistic Regression
- Compare accuracies and save the best model as `ml/best_model.pkl`
- Output results to `ml/training_results.json`

---

#### Step 5: Start the Flask Server

From the project root directory:

```bash
python app.py
```

You should see:
```
============================================================
  COLLEGE RESOURCE BOOKING SYSTEM
  Flask Backend Server
============================================================
  Rooms: 1001 -> 4410 (1640 total)
  Slots: 9-10, 10-11, 11-12, 12-1, 2-3, 3-4
  C++ Engine: Connected
  ML Model: Loaded
  Database: 0 bookings
============================================================
  Server: http://localhost:5000
============================================================
```

---

#### Step 6: Open the Web UI

Open your browser and navigate to:
```
http://localhost:5000
```

The spreadsheet-style dashboard will load with:
- 📅 Date selector
- 🏫 Room grid with color-coded slot availability
- 🔍 Check room availability
- 📝 Book rooms directly from the UI
- 📊 View all bookings and statistics
- ✅ Faculty can approve/reject bookings

---

## 🧪 Testing

### Automated Tests (Windows Batch)

Run the pre-defined test scenarios:
```bash
.\run_tests.bat
```

This runs 4 automated tests:
1. **TEST 1**: Student creates a new booking (should succeed)
2. **TEST 2**: Same booking again — triggers conflict detection + ML suggestions
3. **TEST 3**: Faculty views all bookings
4. **TEST 4**: Faculty approves a booking

### Python Test Runner

```bash
python run_tests.py
```

### Manual API Testing (using curl or browser)

**Check health:**
```bash
curl http://localhost:5000/api/health
```

**Check room availability:**
```bash
curl -X POST http://localhost:5000/api/check \
  -H "Content-Type: application/json" \
  -d "{\"user\":\"S1001\", \"room\":2050, \"date\":\"2026-04-15\", \"slot\":\"9-10\"}"
```

**Book a room:**
```bash
curl -X POST http://localhost:5000/api/book \
  -H "Content-Type: application/json" \
  -d "{\"user\":\"S1001\", \"room\":2050, \"date\":\"2026-04-15\", \"slot\":\"9-10\"}"
```

**Get schedule for a date:**
```bash
curl "http://localhost:5000/api/schedule?date=2026-04-15"
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serve web UI |
| `GET` | `/api/health` | System health check |
| `POST` | `/api/check` | Check room availability + ML prediction |
| `POST` | `/api/book` | Create a booking |
| `GET` | `/api/schedule?date=YYYY-MM-DD` | Get full schedule for a date |
| `GET` | `/api/rooms?date=YYYY-MM-DD` | Get room status grid for a date |
| `GET` | `/api/allbookings` | Get all bookings + stats |
| `GET` | `/api/user-bookings?user=S1001` | Get bookings by user ID |
| `POST` | `/api/approve` | Approve a booking by ID |
| `POST` | `/api/reject` | Reject a booking by ID |
| `POST` | `/api/predict` | ML prediction for room/slot |
| `GET` | `/api/valid-rooms` | List all valid rooms |
| `GET` | `/api/stats` | Booking statistics |

### Request/Response Examples

**POST `/api/check`**
```json
// Request
{ "user": "S1001", "room": 2050, "date": "2026-04-15", "slot": "9-10" }

// Response (available)
{
  "status": "available",
  "room": 2050,
  "date": "2026-04-15",
  "slot": "9-10",
  "ml_booking_probability": 0.623
}

// Response (unavailable)
{
  "status": "unavailable",
  "suggested_room": 2051,
  "suggested_room_distance": 1,
  "suggested_slot": "10-11",
  "ml_booking_probability": 0.841
}
```

---

## 🤖 ML Module Details

Three models are trained and the best one is automatically selected:

| # | Model | Description |
|---|-------|-------------|
| **Model 1** | **User Preference** (C++ + Python) | Finds the slot a given user has booked most often (frequency-based) |
| **Model 2** | **Room Popularity** (C++ + Python) | Finds the most popular time slot for a given room (frequency-based) |
| **Model 3** | **Closest Room — KNN** (C++ + Python) | Among free rooms, picks the numerically closest to the requested room |
| **Model 4** | **Random Forest** (sklearn) | Predicts booking probability from room, slot, floor, user type |
| **Model 5** | **Decision Tree** (sklearn) | Alternative tree-based classifier |
| **Model 6** | **Logistic Regression** (sklearn) | Linear baseline classifier |

**Features used for sklearn models:**
- `room` — Room number (1001–4410)
- `slot_idx` — Time slot index (0–5)
- `floor` — Floor number (1–4)
- `is_student` — 1 if Student, 0 if Faculty

---

## 🏫 Valid Room Ranges & Time Slots

### Room Numbers
| Floor | Range | Count |
|-------|-------|-------|
| Floor 1 | 1001 – 1410 | 410 rooms |
| Floor 2 | 2001 – 2410 | 410 rooms |
| Floor 3 | 3001 – 3410 | 410 rooms |
| Floor 4 | 4001 – 4410 | 410 rooms |
| **Total** | **1001 – 4410** | **1,640 rooms** |

### Time Slots (Web App)
| Slot | Hours |
|------|-------|
| `9-10` | 9:00 AM – 10:00 AM |
| `10-11` | 10:00 AM – 11:00 AM |
| `11-12` | 11:00 AM – 12:00 PM |
| `12-1` | 12:00 PM – 1:00 PM |
| `2-3` | 2:00 PM – 3:00 PM |
| `3-4` | 3:00 PM – 4:00 PM |

### Time Slots (C++ Console App)
| Slot |
|------|
| `9-11` |
| `11-1` |
| `2-4` |
| `4-6` |

---

## 🛠 Troubleshooting

### `g++: command not found`
- Install **MinGW-w64** from [winlibs.com](https://winlibs.com/)
- Add the `bin/` folder to your system `PATH`
- Restart your terminal and try again

### `ModuleNotFoundError: No module named 'flask'`
```bash
pip install flask flask-cors numpy scikit-learn joblib pandas
```

### `booking_engine.exe` not found warning
> The Flask app will still work using Python-only mode. The C++ engine is optional.
> To compile: `cd backend_cpp && g++ booking_engine.cpp -o booking_engine -std=c++17`

### Port 5000 already in use
```bash
# Find and kill the process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

### Database issues / no bookings showing
```bash
# Delete and recreate the database
del database\booking.db
python app.py   # Database auto-initializes on startup
```

### ML model not loading
```bash
# Retrain the model
python ml/train_model.py
```

---

## 👥 User Roles

| Role | Login Format | Capabilities |
|------|-------------|---|
| **Student** | Any ID starting with `S` (e.g., `S1001`) | Request bookings, view own bookings, get ML suggestions |
| **Faculty** | Any ID starting with `F` (e.g., `F001`) | View all bookings, approve/reject pending bookings |

> **Note:** The C++ console app does not implement credential validation — any User ID and password combination is accepted. Authentication is based solely on role selection (Student/Faculty).

---

## 📜 License

This project was developed as an academic OOP demonstration project using C++, Python (Flask), SQLite, and Machine Learning.

---

*Built with ❤️ using C++17 · Python 3 · Flask · SQLite · scikit-learn*
