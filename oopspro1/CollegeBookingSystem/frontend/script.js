/* ═══════════════════════════════════════════════════════════
   CampusBook — Frontend JavaScript
   College Resource Booking System
   ═══════════════════════════════════════════════════════════ */

const API_BASE = '';  // Same origin

// ── Valid Slot Labels ──
const SLOT_LABELS = {
    '9-10': '9:00 - 10:00',
    '10-11': '10:00 - 11:00',
    '11-12': '11:00 - 12:00',
    '12-1': '12:00 - 1:00',
    '2-3': '2:00 - 3:00',
    '3-4': '3:00 - 4:00'
};

const VALID_SLOTS = ['9-10', '10-11', '11-12', '12-1', '2-3', '3-4'];

// ── All Bookings Cache ──
let allBookingsCache = [];

// ═══════════════════════════════════════════════════
//                INITIALIZATION
// ═══════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    initTabs();
    initDateDefaults();
    populateRoomDropdown();
    checkSystemHealth();
    loadAllBookings();
});

// ── Background Particles ──
function initParticles() {
    const container = document.getElementById('bgParticles');
    const colors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'];
    
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        const size = Math.random() * 4 + 2;
        const color = colors[Math.floor(Math.random() * colors.length)];
        
        particle.style.cssText = `
            width: ${size}px;
            height: ${size}px;
            background: ${color};
            left: ${Math.random() * 100}%;
            animation-duration: ${Math.random() * 20 + 15}s;
            animation-delay: ${Math.random() * 10}s;
        `;
        container.appendChild(particle);
    }
}

// ── Tab Navigation ──
function initTabs() {
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            
            // Update active tab
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Update active panel
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            const panel = document.getElementById(`panel-${target}`);
            if (panel) {
                panel.classList.add('active');
            }
            
            // Load data for specific tabs
            if (target === 'faculty') loadAllBookings();
            if (target === 'analytics') checkSystemHealth();
        });
    });
}

// ── Date Defaults ──
function initDateDefaults() {
    const today = new Date().toISOString().split('T')[0];
    const dateSelect = document.getElementById('dateSelect');
    const scheduleDate = document.getElementById('scheduleDateSelect');
    
    if (dateSelect) dateSelect.value = today;
    if (scheduleDate) scheduleDate.value = today;
}

// ── Populate Room Dropdown ── 
function populateRoomDropdown() {
    const roomSelect = document.getElementById('roomSelect');
    const floorFilter = document.getElementById('floorFilter');
    
    function updateRooms() {
        const floor = parseInt(floorFilter.value);
        roomSelect.innerHTML = '<option value="">Select Room...</option>';
        
        for (let f = 1; f <= 4; f++) {
            if (floor !== 0 && f !== floor) continue;
            
            const optgroup = document.createElement('optgroup');
            optgroup.label = `Floor ${f} (${f}001 - ${f}410)`;
            
            // Add subset of rooms for performance (every 10th room for dropdown)
            for (let r = 1; r <= 410; r += 1) {
                const roomNo = f * 1000 + r;
                // Show key rooms to keep dropdown manageable
                if (r <= 10 || r % 10 === 0 || r === 410) {
                    const opt = document.createElement('option');
                    opt.value = roomNo;
                    opt.textContent = roomNo;
                    optgroup.appendChild(opt);
                }
            }
            roomSelect.appendChild(optgroup);
        }
    }
    
    floorFilter.addEventListener('change', updateRooms);
    updateRooms();
}


// ═══════════════════════════════════════════════════
//              STUDENT ACTIONS
// ═══════════════════════════════════════════════════

async function checkAvailability() {
    const data = getFormData();
    if (!data) return;
    
    showLoading('btnCheck');
    
    try {
        const response = await fetch(`${API_BASE}/api/check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        displayResult(result);
        
        if (result.status === 'available') {
            showToast('Room is available! You can book it.', 'success');
        } else {
            showToast('Room is not available. See suggestions.', 'warning');
        }
    } catch (error) {
        showToast('Error checking availability: ' + error.message, 'error');
        displayError('Failed to check availability. Is the server running?');
    } finally {
        hideLoading('btnCheck');
    }
}

async function bookRoom() {
    const data = getFormData();
    if (!data) return;
    
    showLoading('btnBook');
    
    try {
        const response = await fetch(`${API_BASE}/api/book`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        displayResult(result);
        
        if (result.status === 'booked') {
            showToast(`Room ${data.room} booked successfully!`, 'success');
        } else if (result.status === 'unavailable') {
            showToast('Room unavailable. Check suggestions below.', 'warning');
        } else {
            showToast(result.message || 'Booking failed', 'error');
        }
    } catch (error) {
        showToast('Error booking room: ' + error.message, 'error');
        displayError('Failed to book room. Is the server running?');
    } finally {
        hideLoading('btnBook');
    }
}

async function viewMyBookings() {
    const userId = document.getElementById('studentId').value.trim();
    if (!userId) {
        showToast('Please enter your Student ID', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/user-bookings?user=${encodeURIComponent(userId)}`);
        const result = await response.json();
        
        const container = document.getElementById('myBookingsContainer');
        const tbody = document.getElementById('myBookingsBody');
        tbody.innerHTML = '';
        
        if (result.bookings && result.bookings.length > 0) {
            result.bookings.forEach(b => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${b.room}</td>
                    <td>${b.date}</td>
                    <td>${SLOT_LABELS[b.slot] || b.slot}</td>
                    <td><span class="status-badge ${b.status.toLowerCase()}">${b.status}</span></td>
                `;
                tbody.appendChild(tr);
            });
            container.style.display = 'block';
            showToast(`Found ${result.bookings.length} booking(s)`, 'info');
        } else {
            tbody.innerHTML = '<tr><td colspan="4" class="empty-state">No bookings found</td></tr>';
            container.style.display = 'block';
            showToast('No bookings found for this user', 'info');
        }
    } catch (error) {
        showToast('Error loading bookings: ' + error.message, 'error');
    }
}

// ── Form Data Helper ──
function getFormData() {
    const user = document.getElementById('studentId').value.trim();
    const room = document.getElementById('roomSelect').value;
    const date = document.getElementById('dateSelect').value;
    const slot = document.getElementById('slotSelect').value;
    
    if (!user) { showToast('Please enter your Student ID', 'warning'); return null; }
    if (!room) { showToast('Please select a room', 'warning'); return null; }
    if (!date) { showToast('Please select a date', 'warning'); return null; }
    if (!slot) { showToast('Please select a time slot', 'warning'); return null; }
    
    return { user, room: parseInt(room), date, slot };
}


// ═══════════════════════════════════════════════════
//              DISPLAY RESULTS
// ═══════════════════════════════════════════════════

function displayResult(result) {
    const card = document.getElementById('resultCard');
    const icon = document.getElementById('resultIcon');
    const title = document.getElementById('resultTitle');
    const body = document.getElementById('resultBody');
    
    card.style.display = 'block';
    
    if (result.status === 'available') {
        icon.textContent = '✅';
        title.textContent = 'Room Available';
        title.style.color = 'var(--accent-emerald)';
        body.innerHTML = `
            <p class="result-available">
                <strong>Room ${result.room}</strong> is available on <strong>${result.date}</strong> 
                for <strong>${SLOT_LABELS[result.slot] || result.slot}</strong>.
            </p>
            <p style="margin-top: 8px; color: var(--text-muted)">Click "Book Room" to confirm your reservation.</p>
        `;
    } else if (result.status === 'booked') {
        icon.textContent = '🎉';
        title.textContent = 'Booking Confirmed!';
        title.style.color = 'var(--accent-emerald)';
        body.innerHTML = `
            <p class="result-available">
                <strong>Room ${result.room}</strong> has been booked on <strong>${result.date}</strong> 
                for <strong>${SLOT_LABELS[result.slot] || result.slot}</strong>.
            </p>
            <p style="margin-top: 8px; color: var(--text-muted)">Status: <span class="status-badge pending">Pending Approval</span></p>
        `;
    } else if (result.status === 'unavailable') {
        icon.textContent = '⚠️';
        title.textContent = 'Room Unavailable';
        title.style.color = 'var(--accent-red)';
        
        let suggestionsHtml = '';
        
        if (result.suggested_room) {
            suggestionsHtml += `
                <div class="suggestion">
                    🏠 <strong>Closest Available Room:</strong> Room ${result.suggested_room} 
                    (${result.suggested_room_distance} rooms away)
                </div>
            `;
        }
        
        if (result.suggested_slot) {
            suggestionsHtml += `
                <div class="suggestion">
                    🕐 <strong>Next Available Slot:</strong> ${SLOT_LABELS[result.suggested_slot] || result.suggested_slot}
                </div>
            `;
        }
        
        if (result.ml_booking_probability !== undefined) {
            suggestionsHtml += `
                <div class="suggestion">
                    🤖 <strong>ML Booking Probability:</strong> ${(result.ml_booking_probability * 100).toFixed(1)}%
                </div>
            `;
        }
        
        body.innerHTML = `
            <p class="result-unavailable">${result.message}</p>
            ${suggestionsHtml || '<p style="margin-top: 12px; color: var(--text-muted)">No alternative suggestions available at this time.</p>'}
        `;
    } else {
        icon.textContent = '❌';
        title.textContent = 'Error';
        title.style.color = 'var(--accent-red)';
        body.innerHTML = `<p class="result-unavailable">${result.message || 'An error occurred.'}</p>`;
    }
}

function displayError(msg) {
    const card = document.getElementById('resultCard');
    const icon = document.getElementById('resultIcon');
    const title = document.getElementById('resultTitle');
    const body = document.getElementById('resultBody');
    
    card.style.display = 'block';
    icon.textContent = '❌';
    title.textContent = 'Connection Error';
    title.style.color = 'var(--accent-red)';
    body.innerHTML = `<p class="result-unavailable">${msg}</p>`;
}


// ═══════════════════════════════════════════════════
//              FACULTY ACTIONS
// ═══════════════════════════════════════════════════

async function loadAllBookings() {
    try {
        const response = await fetch(`${API_BASE}/api/allbookings`);
        const result = await response.json();
        
        allBookingsCache = result.bookings || [];
        
        // Update stats
        if (result.stats) {
            document.getElementById('statTotal').textContent = result.stats.total || 0;
            document.getElementById('statApproved').textContent = result.stats.approved || 0;
            document.getElementById('statPending').textContent = result.stats.pending || 0;
            document.getElementById('statRejected').textContent = result.stats.rejected || 0;
        }
        
        renderBookingsTable(allBookingsCache);
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
}

function filterBookings() {
    const filter = document.getElementById('statusFilter').value;
    const filtered = filter === 'all' 
        ? allBookingsCache 
        : allBookingsCache.filter(b => b.status === filter);
    renderBookingsTable(filtered);
}

function renderBookingsTable(bookings) {
    const tbody = document.getElementById('allBookingsBody');
    tbody.innerHTML = '';
    
    if (bookings.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No bookings found</td></tr>';
        return;
    }
    
    // Show max 200 rows for performance
    const displayBookings = bookings.slice(0, 200);
    
    displayBookings.forEach(b => {
        const tr = document.createElement('tr');
        const statusClass = b.status.toLowerCase();
        const isPending = b.status === 'Pending';
        
        tr.innerHTML = `
            <td>#${b.id}</td>
            <td>${b.user}</td>
            <td>${b.room}</td>
            <td>${b.date}</td>
            <td>${SLOT_LABELS[b.slot] || b.slot}</td>
            <td><span class="status-badge ${statusClass}">${b.status}</span></td>
            <td>
                ${isPending ? `
                    <button class="btn btn-sm btn-approve" onclick="approveBooking(${b.id})">✓ Approve</button>
                    <button class="btn btn-sm btn-reject" onclick="rejectBooking(${b.id})">✗ Reject</button>
                ` : '—'}
            </td>
        `;
        tbody.appendChild(tr);
    });
    
    if (bookings.length > 200) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td colspan="7" style="text-align:center; color: var(--text-muted); padding: 12px;">
            Showing 200 of ${bookings.length} bookings
        </td>`;
        tbody.appendChild(tr);
    }
}

async function approveBooking(id) {
    try {
        const response = await fetch(`${API_BASE}/api/approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id })
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            showToast('Booking approved!', 'success');
            loadAllBookings();
        } else {
            showToast(result.message || 'Failed to approve', 'error');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}

async function rejectBooking(id) {
    try {
        const response = await fetch(`${API_BASE}/api/reject`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id })
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            showToast('Booking rejected', 'info');
            loadAllBookings();
        } else {
            showToast(result.message || 'Failed to reject', 'error');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}


// ═══════════════════════════════════════════════════
//              SCHEDULE (SPREADSHEET)
// ═══════════════════════════════════════════════════

async function loadSchedule() {
    const date = document.getElementById('scheduleDateSelect').value;
    if (!date) {
        showToast('Please select a date', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/rooms?date=${date}`);
        const result = await response.json();
        
        renderSpreadsheet(result);
    } catch (error) {
        showToast('Error loading schedule: ' + error.message, 'error');
    }
}

function renderSpreadsheet(data) {
    const tbody = document.getElementById('spreadsheetBody');
    tbody.innerHTML = '';
    
    if (!data.rooms || data.rooms.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">
                    No bookings for this date. All rooms are available!
                </td>
            </tr>
        `;
        return;
    }
    
    data.rooms.forEach(roomData => {
        const tr = document.createElement('tr');
        
        let html = `<td class="room-cell">${roomData.room}</td>`;
        
        VALID_SLOTS.forEach(slot => {
            const slotInfo = roomData.slots[slot];
            if (slotInfo && slotInfo.status === 'booked') {
                const approval = slotInfo.approval || 'Pending';
                const cellClass = approval === 'Approved' ? 'slot-booked' : 'slot-pending';
                const label = approval === 'Approved' ? '🔴 Booked' : '🟡 Pending';
                const bookedBy = slotInfo.booked_by || '';
                html += `<td class="${cellClass}" title="${bookedBy}">${label}<br><small>${bookedBy}</small></td>`;
            } else {
                html += `<td class="slot-available" onclick="quickBook(${roomData.room}, '${slot}')" title="Click to book">🟢 Free</td>`;
            }
        });
        
        tr.innerHTML = html;
        tbody.appendChild(tr);
    });
}

function quickBook(room, slot) {
    // Switch to student tab and pre-fill
    document.querySelector('[data-tab="student"]').click();
    document.getElementById('roomSelect').value = room;
    document.getElementById('slotSelect').value = slot;
    showToast(`Room ${room}, Slot ${SLOT_LABELS[slot]} selected. Click Book to confirm.`, 'info');
}


// ═══════════════════════════════════════════════════
//              SYSTEM HEALTH
// ═══════════════════════════════════════════════════

async function checkSystemHealth() {
    const container = document.getElementById('healthItems');
    
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        const result = await response.json();
        
        container.innerHTML = '';
        
        const items = [
            { label: 'Flask Backend', status: result.status === 'running' ? 'ok' : 'error', text: result.status || 'Unknown' },
            { label: 'C++ Engine', status: result.cpp_engine === 'connected' ? 'ok' : 'warn', text: result.cpp_engine || 'Unknown' },
            { label: 'ML Model', status: result.ml_model === 'loaded' ? 'ok' : 'warn', text: result.ml_model || 'Unknown' },
            { label: 'Database', status: result.database === 'working' ? 'ok' : 'error', text: result.database || 'Unknown' },
            { label: 'Room Range', status: 'ok', text: result.valid_room_range || '1001-4410' },
            { label: 'Total Rooms', status: 'ok', text: (result.total_rooms || 1640).toString() },
        ];
        
        if (result.booking_stats) {
            items.push({
                label: 'Total Bookings',
                status: 'ok',
                text: `${result.booking_stats.total || 0} records`
            });
        }
        
        items.forEach(item => {
            const div = document.createElement('div');
            div.className = `health-item ${item.status}`;
            div.innerHTML = `
                <span class="health-dot"></span>
                <span><strong>${item.label}:</strong> ${item.text}</span>
            `;
            container.appendChild(div);
        });
        
        // Update nav status
        const navStatus = document.getElementById('navStatus');
        navStatus.innerHTML = `<div class="status-dot online"></div><span>System Online</span>`;
        
    } catch (error) {
        container.innerHTML = `
            <div class="health-item error">
                <span class="health-dot"></span>
                <span><strong>Connection Error:</strong> Could not reach backend server</span>
            </div>
        `;
        
        const navStatus = document.getElementById('navStatus');
        navStatus.innerHTML = `<div class="status-dot" style="background: var(--accent-red)"></div><span>Offline</span>`;
    }
}


// ═══════════════════════════════════════════════════
//              UTILITIES
// ═══════════════════════════════════════════════════

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentElement) toast.remove();
    }, 4000);
}

function showLoading(btnId) {
    const btn = document.getElementById(btnId);
    if (btn) {
        btn.disabled = true;
        btn.dataset.originalText = btn.innerHTML;
        btn.innerHTML = '<span class="loading-spinner"></span> Loading...';
    }
}

function hideLoading(btnId) {
    const btn = document.getElementById(btnId);
    if (btn) {
        btn.disabled = false;
        btn.innerHTML = btn.dataset.originalText || btn.innerHTML;
    }
}
