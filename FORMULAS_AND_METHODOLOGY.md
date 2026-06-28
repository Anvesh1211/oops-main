# 🧮 Formulas & Methodology - College Resource Booking System

## 📋 Table of Contents
1. [System Architecture](#system-architecture)
2. [Conflict Detection Algorithm](#conflict-detection-algorithm)
3. [ML Models & Training Methodology](#ml-models--training-methodology)
4. [Hybrid Recommendation System](#hybrid-recommendation-system)
5. [Feature Engineering](#feature-engineering)
6. [Distance Metrics](#distance-metrics)
7. [Database Schema](#database-schema)
8. [Probability Calculations](#probability-calculations)
9. [Synthetic Data Generation](#synthetic-data-generation)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Request Flow                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. User Input: (UserID, Room, Date, Slot)                     │
│          ↓                                                      │
│  2. Validation Layer                                            │
│     ├─ Room: 1000-9999 (valid 4-digit range)                   │
│     ├─ Date: YYYY-MM-DD format                                 │
│     ├─ Slot: ["9-10", "10-11", "11-12", "12-1", "2-3", "3-4"]│
│     └─ User: Starts with 'S' (Student) or 'F' (Faculty)       │
│          ↓                                                      │
│  3. Conflict Detection                                          │
│     ├─ Check: room == existing.room AND                        │
│     │          date == existing.date AND                       │
│     │          slot == existing.slot                           │
│     ├─ If NO conflict → Create Booking                         │
│     └─ If CONFLICT → Trigger ML Suggestions                    │
│          ↓                                                      │
│  4. ML Prediction Pipeline (3 Models Ensemble)                 │
│     ├─ Model 1: User Preference (Frequency-based)              │
│     ├─ Model 2: Room Popularity (Frequency-based)              │
│     ├─ Model 3: KNN Closest Room (Distance-based)              │
│     └─ Model 4: Random Forest/Decision Tree/Logistic Reg       │
│          ↓                                                      │
│  5. Return Suggestions + Probability                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Conflict Detection Algorithm

### 1. **Exact Match Conflict Detection**

**Formula:**
```
Conflict = (room_requested == room_booked) 
          ∧ (date_requested == date_booked) 
          ∧ (slot_requested == slot_booked)
```

**Implementation (C++):**
```cpp
bool conflictsWith(int r, const std::string& dt, const std::string& sl) const {
    return (roomNo == r && date == dt && slot == sl);
}
```

**Implementation (Python - SQLite):**
```python
def check_availability(room, date, slot):
    result = cursor.execute(
        "SELECT * FROM bookings 
         WHERE room = ? AND date = ? AND slot = ? 
         AND status != 'Rejected'",
        (room, date, slot)
    ).fetchone()
    return result is None
```

**Status Filter:** Only `Rejected` bookings are excluded from conflict checking. `Pending` and `Approved` bookings count as conflicts.

---

## ML Models & Training Methodology

### **Dataset Configuration**

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Total Samples** | 1,500 | Synthetic data generated |
| **Training Set** | 80% (1,200) | With stratification |
| **Test Set** | 20% (300) | Stratified split |
| **Random State** | 42 | Reproducible results |
| **Target Classes** | 2 (Binary) | 0=Available, 1=Booked |

---

### **Model 1: Random Forest Classifier**

**Configuration:**
```python
RandomForestClassifier(
    n_estimators=100,      # 100 decision trees
    random_state=42,       # Fixed seed
    max_depth=10           # Tree depth limit
)
```

**Formula (Ensemble):**
```
Prediction = MODE(Tree_1(X), Tree_2(X), ..., Tree_100(X))

Probability = Mean(Probability_from_each_tree)
```

**Features Used:**
- Room number (continuous)
- Slot index (0-5, ordinal)
- Floor number (1-4, categorical)
- Is Student (0/1, binary)

**Output:**
```
P(booked) = probability from majority voting
```

---

### **Model 2: Decision Tree Classifier**

**Configuration:**
```python
DecisionTreeClassifier(
    random_state=42,
    max_depth=8            # Pruning depth
)
```

**Decision Logic:**
```
Each split: if (feature <= threshold) then left_branch else right_branch

Final prediction: leaf_node class
```

**Split Criterion:** Gini impurity or entropy (default: gini)

```
Gini(node) = 1 - Σ(p_i)²

where p_i = proportion of class i at node
```

---

### **Model 3: Logistic Regression**

**Configuration:**
```python
LogisticRegression(
    random_state=42,
    max_iter=1000          # Iteration limit
)
```

**Mathematical Formula:**
```
P(booked = 1 | X) = 1 / (1 + e^(-z))

where z = β₀ + β₁·room + β₂·slot_idx + β₃·floor + β₄·is_student

e = 2.71828 (Euler's number)
```

**Output:** Probability score between 0 and 1

---

### **Model Selection Criteria**

```
best_model = argmax(accuracy_score(y_test, model.predict(X_test)))
```

**Evaluation Metric:**
```
Accuracy = (TP + TN) / (TP + TN + FP + FN)

where:
  TP = True Positives (correctly predicted booked)
  TN = True Negatives (correctly predicted available)
  FP = False Positives (incorrectly predicted booked)
  FN = False Negatives (incorrectly predicted available)
```

---

## Hybrid Recommendation System

### **3-Model Ensemble (C++ Console & Initial Conflict)**

When a booking conflict occurs, **three independent models** suggest alternatives:

---

### **Model 1: User Preference Slot** 
**Methodology:** Frequency-based recommendation

**Formula:**
```
preferred_slot(user) = argmax(count(slot_i)) 
                       for all user's historical bookings

∀ booking ∈ user_bookings:
    frequency[booking.slot] += 1

best_slot = slot with maximum frequency
```

**Implementation:**
```cpp
std::string getUserPreferredSlot(const std::vector<Booking>& bookings,
                                  const std::string& userID) const {
    std::map<std::string, int> slotFreq;
    
    for (const auto& b : bookings) {
        if (b.getUserID() == userID) {
            slotFreq[b.getSlot()]++;  // Count occurrences
        }
    }
    
    std::string bestSlot = "N/A";
    int maxCount = 0;
    for (const auto& p : slotFreq) {
        if (p.second > maxCount) {
            maxCount = p.second;
            bestSlot = p.first;  // Select most frequent
        }
    }
    return bestSlot;
}
```

**Logic:**
- Count all time slots user has previously booked
- Return the slot with highest count
- If no history, return "N/A"

---

### **Model 2: Room Popularity Slot**
**Methodology:** Frequency-based popularity analysis

**Formula:**
```
popular_slot(room) = argmax(count(slot_i)) 
                     for all bookings of that room

∀ booking ∈ all_bookings where booking.room == room:
    frequency[booking.slot] += 1

best_slot = slot with maximum frequency
```

**Implementation:**
```cpp
std::string getRoomPopularSlot(const std::vector<Booking>& bookings,
                                int roomNo) const {
    std::map<std::string, int> slotFreq;
    
    for (const auto& b : bookings) {
        if (b.getRoomNo() == roomNo) {
            slotFreq[b.getSlot()]++;  // Count by room
        }
    }
    
    std::string bestSlot = "N/A";
    int maxCount = 0;
    for (const auto& p : slotFreq) {
        if (p.second > maxCount) {
            maxCount = p.second;
            bestSlot = p.first;
        }
    }
    return bestSlot;
}
```

**Logic:**
- Analyze all bookings for the requested room
- Find the time slot with most bookings
- Suggests that popular slot for same room
- Useful for predictable usage patterns

---

### **Model 3: Closest Available Room (KNN)**
**Methodology:** Euclidean distance in room number space

**Formula:**
```
closest_room(r_req, date, slot) = argmin(|r_req - r|)
                                  ∀ r ∈ available_rooms(date, slot)

distance = |room_requested - room_candidate|
```

**Implementation:**
```cpp
int getClosestAvailableRoom(const std::vector<Booking>& bookings,
                            int requestedRoom,
                            const std::string& date,
                            const std::string& slot) const {
    
    // Mark occupied rooms
    std::map<int, bool> occupied;
    for (const auto& b : bookings) {
        if (b.getDate() == date && b.getSlot() == slot) {
            occupied[b.getRoomNo()] = true;
        }
    }
    
    int closestRoom = 0;
    int minDist = INT_MAX;
    
    // Search all available rooms on same floor/range
    for (int r = 4001; r <= 4099; ++r) {
        if (occupied.find(r) == occupied.end()) {  // If available
            int dist = std::abs(requestedRoom - r);
            if (dist < minDist) {
                minDist = dist;
                closestRoom = r;
            }
        }
    }
    return closestRoom;
}
```

**Distance Metric:**
```
d(r_req, r_cand) = |r_req - r_cand|

Example:
  Requested: 2050
  Available: 2049, 2051, 2052
  
  d(2050, 2049) = 1  ← Minimum, selected
  d(2050, 2051) = 1
  d(2050, 2052) = 2
```

**Search Space:** Iterates through room range (4001-4099 in code, but can be 1001-4410)

---

## Feature Engineering

### **Input Features for ML Models**

| Feature | Type | Range | Encoding | Purpose |
|---------|------|-------|----------|---------|
| **room** | Continuous | 1001-4410 | As-is (int) | Room number absolute value |
| **slot_idx** | Ordinal | 0-5 | Index mapping | Time slot order (0=9-10, 5=3-4) |
| **floor** | Categorical | 1-4 | Derived from room | Floor number (room // 1000) |
| **is_student** | Binary | 0/1 | Boolean → int | User type (1=Student, 0=Faculty) |

### **Slot Index Mapping**

```python
VALID_SLOTS = ["9-10", "10-11", "11-12", "12-1", "2-3", "3-4"]

slot_idx = VALID_SLOTS.index(slot)

Mapping:
  "9-10"  → 0
  "10-11" → 1
  "11-12" → 2
  "12-1"  → 3
  "2-3"   → 4
  "3-4"   → 5
```

### **Floor Extraction**

```python
floor_num = room // 1000

Example:
  Room 1050 → Floor 1
  Room 2500 → Floor 2
  Room 3999 → Floor 3
  Room 4050 → Floor 4
```

### **User Type Encoding**

```python
is_student = 1 if user.startswith('S') else 0

Student: "S1001", "S1002", ... → is_student = 1
Faculty: "F001", "F002", ... → is_student = 0
```

---

## Distance Metrics

### **1. Euclidean Distance (Room Selection)**

**Formula:**
```
d_euclidean(room_req, room_cand) = √((room_req - room_cand)²)
                                  = |room_req - room_cand|  (1D space)
```

**Python Implementation:**
```python
def find_closest_room(requested_room, date, slot):
    booked = set(get_booked_rooms_for_slot(date, slot))
    closest = None
    min_dist = float('inf')
    
    for r in ALL_ROOMS:
        if r not in booked:
            dist = abs(requested_room - r)  # 1D Euclidean
            if 0 < dist < min_dist:
                min_dist = dist
                closest = r
    
    return (closest, min_dist) if closest else (None, None)
```

**Example:**
```
Request: Room 2050, Date: 2026-04-15, Slot: 9-10
Booked: {2050, 2051, 2052}
Available: {2000, 2001, ..., 2049, 2053, ...}

Distances:
  |2050 - 2049| = 1  ← Minimum
  |2050 - 2048| = 2
  |2050 - 2053| = 3
  |2050 - 2000| = 50

Recommendation: Room 2049
```

---

## Database Schema

### **Bookings Table (SQLite)**

```sql
CREATE TABLE bookings (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user         TEXT NOT NULL,
    room         INTEGER NOT NULL,
    date         TEXT NOT NULL,
    slot         TEXT NOT NULL,
    status       TEXT DEFAULT 'Pending',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(room, date, slot)
)
```

### **Key Constraints**

| Constraint | Type | Purpose |
|-----------|------|---------|
| **PRIMARY KEY (id)** | Unique Identifier | Auto-increment booking ID |
| **UNIQUE(room, date, slot)** | Composite Unique | Prevent double-booking |
| **NOT NULL (user, room, date, slot)** | Mandatory Fields | Data integrity |
| **DEFAULT 'Pending'** | Status | New bookings start pending |
| **PRAGMA journal_mode=WAL** | Write-Ahead Logging | Concurrency support |

### **Status Values**

```
Pending   → Awaiting faculty approval
Approved  → Faculty approved (counts as booked)
Rejected  → Faculty rejected (excluded from conflicts)
```

---

## Probability Calculations

### **1. ML Model Probability Output**

**For Binary Classification:**
```
P(booked = 1 | X) = model.predict_proba(X)[0, 1]

Where:
  [0, 0] = probability of class 0 (available)
  [0, 1] = probability of class 1 (booked)
```

**Example:**
```python
features = np.array([[2050, 0, 2, 1]])  # Room 2050, slot 9-10, floor 2, student
proba = ml_model.predict_proba(features)[0]
# Output: [0.35, 0.65]

ml_booking_probability = max(proba) = 0.65
```

### **2. Synthetic Data Generation Probability**

**Probability Calculation for Training Data:**

```python
prob = 0.5  # Base probability

# Early slots (9-10, 10-11, 11-12) more popular
if slot_idx < 3:
    prob += 0.15

# Lower floors more accessible
prob += (5 - floor_num) * 0.03
# Floor 1: (5-1)*0.03 = 0.12
# Floor 2: (5-2)*0.03 = 0.09
# Floor 3: (5-3)*0.03 = 0.06
# Floor 4: (5-4)*0.03 = 0.03

# Students book slightly more
if is_student:
    prob += 0.05

# Random variation (-0.2 to +0.2)
prob += random.uniform(-0.2, 0.2)

# Clamp to [0, 1]
prob = max(0, min(1, prob))

booked = 1 if random.random() < prob else 0
```

**Example Probabilities:**
```
Scenario 1: Student, Room 1050 (Floor 1), Slot 9-10
  Base:    0.50
  Slot:   +0.15
  Floor:  +0.12
  Student:+0.05
  Random: ±0.2
  Range:   [0.32, 0.72]

Scenario 2: Faculty, Room 4099 (Floor 4), Slot 3-4
  Base:    0.50
  Slot:   +0.00  (slot_idx=5, not <3)
  Floor:  +0.03
  Student:+0.00
  Random: ±0.2
  Range:   [0.33, 0.73]
```

---

## Synthetic Data Generation

### **Dataset Composition**

```
Total Records: 1,500

Users:
  ├─ Students: 50 users (S1001 to S1050)
  └─ Faculty:  20 users (F101 to F120)

Rooms:
  ├─ Total Unique: 300 (subset of 1640 available)
  └─ Distribution: Stratified across 4 floors

Dates:
  ├─ Base Date: 2026-03-01
  ├─ Range: 0-30 days forward
  └─ Total: ~31 unique dates

Slots:
  ├─ Options: ["9-10", "10-11", "11-12", "12-1", "2-3", "3-4"]
  └─ Distribution: 250 per slot (approximately)

Statuses:
  ├─ Approved: 75% of bookings
  ├─ Pending:  25% of bookings
  └─ Rejected: 0% (not generated, only from user actions)
```

### **Uniqueness Constraint**

```python
# Prevent duplicate (room, date, slot) combinations
booked_slots = set()

while len(records) < 1200 and attempts < 5000:
    key = (room, date, slot)
    if key not in booked_slots:
        booked_slots.add(key)
        records.append((user, room, date, slot, status))
```

**Guarantee:** Maximum 1 booking per (room, date, slot) tuple

---

## Algorithm Complexity Analysis

| Operation | Algorithm | Time Complexity | Space Complexity |
|-----------|-----------|-----------------|------------------|
| **Conflict Detection** | Linear Search | O(n) | O(1) |
| **Find Closest Room** | Linear Scan | O(m) | O(m) |
| **User Preference** | Hash Map Count | O(n) | O(s) |
| **Room Popularity** | Hash Map Count | O(n) | O(s) |
| **RF Prediction** | Ensemble Voting | O(100 × d) | O(100 × nodes) |
| **DT Prediction** | Tree Traversal | O(depth) | O(depth) |
| **LR Prediction** | Linear Eval | O(f) | O(f) |

Where: n=bookings, m=rooms, s=slots, d=tree depth, f=features

---

## File I/O Operations

### **C++ Console App - File Format**

**File: data/history.txt**

```
Format: UserID RoomNo Day Date Slot Status

Example:
S1001 2050 Monday 2026-04-15 9-11 Pending
F001 3010 Tuesday 2026-04-16 11-1 Approved
S1002 1050 Wednesday 2026-04-17 2-4 Approved
```

**Parsing Logic:**
```cpp
static Booking fromFileString(const std::string& line) {
    std::istringstream iss(line);
    std::string uid, d, dt, sl, st;
    int room;
    if (iss >> uid >> room >> d >> dt >> sl >> st) {
        return Booking(uid, room, d, dt, sl, st);
    }
    return Booking();
}
```

---

## Summary: Decision Making Flow

```
┌─ Request Validation ─┐
│ Room, Date, Slot     │
└──────────┬───────────┘
           ↓
┌─ Check Availability ─┐
│ Query: (room, date, slot) exists?
└──────────┬───────────┘
           ├─→ YES: CONFLICT ─┐
           │                  ↓
           │          ┌─ Suggest Alternatives ─┐
           │          │ 1. User Preferred Slot │
           │          │ 2. Room Popular Slot   │
           │          │ 3. Closest Room (KNN)  │
           │          │ 4. ML Probability      │
           │          └─────────────────────────┘
           │
           └─→ NO: AVAILABLE ─┐
                               ↓
                      ┌─ Create Booking ─┐
                      │ INSERT INTO DB   │
                      └──────────────────┘
```

---

**Document Version:** 1.0  
**Last Updated:** April 2026  
**Project:** College Resource Booking & Hybrid ML Recommendation System
