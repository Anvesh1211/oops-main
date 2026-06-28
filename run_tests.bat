@echo off
chcp 65001 >nul

echo ============================================
echo TEST 1: Student new booking (should succeed)
echo ============================================
(
echo 1
echo S9999
echo pass123
echo 1
echo 4050
echo Monday
echo 2026-04-15
echo 9-11
echo 3
echo 3
) | booking_system.exe
echo.
echo ============================================
echo TEST 2: Same booking again (conflict + ML)
echo ============================================
(
echo 1
echo S9999
echo pass123
echo 1
echo 4050
echo Monday
echo 2026-04-15
echo 9-11
echo 3
echo 3
) | booking_system.exe
echo.
echo ============================================
echo TEST 3: Faculty view all bookings
echo ============================================
(
echo 2
echo F001
echo admin
echo 1
echo 3
echo 3
) | booking_system.exe
echo.
echo ============================================
echo TEST 4: Faculty approve a booking
echo ============================================
(
echo 2
echo F001
echo admin
echo 2
echo 1
echo 3
echo 3
) | booking_system.exe
echo.
echo ============================================
echo ALL TESTS COMPLETED
echo ============================================
