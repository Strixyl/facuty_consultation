from flask import Flask, render_template_string, request, jsonify, session
from datetime import datetime, timedelta
import json
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# In-memory database (use SQLite/PostgreSQL in production)
faculty_members = [
    {'id': 1, 'name': 'Dr. Maria Santos', 'department': 'Computer Studies', 'email': 'msantos@university.edu'},
    {'id': 2, 'name': 'Prof. Juan Reyes', 'department': 'Mathematics', 'email': 'jreyes@university.edu'},
    {'id': 3, 'name': 'Dr. Ana Cruz', 'department': 'Physics', 'email': 'acruz@university.edu'},
    {'id': 4, 'name': 'Dr. Gwen Alison', 'department': 'Engineering', 'email': 'gwena@university.edu'},
]

available_slots = [
    {'id': 1, 'faculty_id': 1, 'date': '2026-01-10', 'time': '10:00', 'duration': 30, 'is_booked': False},
    {'id': 2, 'faculty_id': 1, 'date': '2026-01-10', 'time': '11:00', 'duration': 30, 'is_booked': False},
    {'id': 3, 'faculty_id': 1, 'date': '2026-01-10', 'time': '14:00', 'duration': 30, 'is_booked': False},
    {'id': 4, 'faculty_id': 2, 'date': '2026-01-10', 'time': '13:00', 'duration': 30, 'is_booked': False},
    {'id': 5, 'faculty_id': 2, 'date': '2026-01-11', 'time': '09:00', 'duration': 30, 'is_booked': False},
    {'id': 6, 'faculty_id': 3, 'date': '2026-01-13', 'time': '09:00', 'duration': 30, 'is_booked': False},
    {'id': 7, 'faculty_id': 4, 'date': '2026-01-12', 'time': '09:00', 'duration': 30, 'is_booked': False},
    {'id': 8, 'faculty_id': 4, 'date': '2026-01-15', 'time': '09:00', 'duration': 30, 'is_booked': False},
    {'id': 9, 'faculty_id': 4, 'date': '2026-01-16', 'time': '09:00', 'duration': 30, 'is_booked': False},
    {'id': 10, 'faculty_id': 1, 'date': '2026-01-14', 'time': '09:00', 'duration': 30, 'is_booked': False},
    {'id': 11, 'faculty_id': 3, 'date': '2026-01-13', 'time': '09:00', 'duration': 30, 'is_booked': False},
]
appointments = []
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Faculty Consultation System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        
        .role-switcher {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        .role-btn {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .role-btn.active {
            background: #667eea;
            color: white;
        }
        
        .role-btn:not(.active) {
            background: #e0e0e0;
            color: #666;
        }
        
        .role-btn:hover:not(.active) {
            background: #d0d0d0;
        }
        
        .content {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 30px;
        }
        
        .card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .card h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        
        .faculty-item {
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid transparent;
        }
        
        .faculty-item:hover {
            background: #f5f5f5;
        }
        
        .faculty-item.selected {
            background: #e8eaf6;
            border-color: #667eea;
        }
        
        .faculty-item h3 {
            color: #333;
            margin-bottom: 5px;
        }
        
        .faculty-item p {
            color: #666;
            font-size: 0.9em;
        }
        
        .slot-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .slot-item {
            padding: 20px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .slot-item:hover {
            border-color: #667eea;
            background: #f5f7ff;
        }
        
        .slot-date {
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
        }
        
        .slot-time {
            color: #666;
            font-size: 0.95em;
        }
        
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
        }
        
        .btn-secondary {
            background: #e0e0e0;
            color: #666;
        }
        
        .btn-secondary:hover {
            background: #d0d0d0;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        
        .modal.show {
            display: flex;
        }
        
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 15px;
            width: 90%;
            max-width: 500px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .modal-header h3 {
            color: #667eea;
            font-size: 1.5em;
        }
        
        .close-btn {
            background: none;
            border: none;
            font-size: 1.5em;
            cursor: pointer;
            color: #999;
        }
        
        .close-btn:hover {
            color: #333;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: bold;
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            font-family: inherit;
        }
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .appointment-item {
            padding: 20px;
            background: #f0f4ff;
            border-left: 4px solid #667eea;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        .appointment-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .appointment-time {
            font-weight: bold;
            color: #333;
            font-size: 1.1em;
        }
        
        .status-badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }
        
        .status-confirmed {
            background: #4caf50;
            color: white;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }
        
        .empty-state svg {
            width: 80px;
            height: 80px;
            margin-bottom: 20px;
            opacity: 0.5;
        }
        
        .analytics {
            margin-top: 20px;
        }
        
        .analytics-item {
            margin-bottom: 15px;
        }
        
        .analytics-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            color: #333;
        }
        
        .analytics-bar {
            background: #e0e0e0;
            height: 25px;
            border-radius: 12px;
            overflow: hidden;
        }
        
        .analytics-fill {
            background: linear-gradient(90deg, #667eea, #764ba2);
            height: 100%;
            transition: width 0.5s;
        }
        
        .meeting-type {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 5px 12px;
            background: white;
            border-radius: 20px;
            font-size: 0.85em;
            margin-top: 10px;
        }
        
        @media (max-width: 768px) {
            .content {
                grid-template-columns: 1fr;
            }
            
            .slot-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 Faculty Consultation System</h1>
            <p>Book appointments with your professors easily</p>
            <div class="role-switcher">
                <button class="role-btn active" id="student-btn" onclick="switchRole('student')">
                    👨‍🎓 Student View
                </button>
                <button class="role-btn" id="faculty-btn" onclick="switchRole('faculty')">
                    👨‍🏫 Faculty View
                </button>
            </div>
        </div>
        
        <!-- Student View -->
        <div id="student-view" class="content">
            <div class="card">
                <h2>Select Faculty</h2>
                <div id="faculty-list"></div>
            </div>
            
            <div class="card">
                <h2>Available Slots</h2>
                <div id="slots-container">
                    <div class="empty-state">
                        <p>Select a faculty member to view available slots</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Faculty View -->
        <div id="faculty-view" class="content" style="display: none;">
            <div class="card">
                <h2>Select Your Profile</h2>
                <div id="faculty-profiles"></div>
            </div>
            
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2 style="margin: 0;">Today's Schedule</h2>
                    <button class="btn btn-primary" onclick="showAddSlotModal()">➕ Add Slot</button>
                </div>
                <div id="appointments-container"></div>
                
                <div class="analytics">
                    <h3 style="color: #667eea; margin-bottom: 15px;">📊 Consultation Topics</h3>
                    <div id="analytics-container"></div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Booking Modal -->
    <div id="booking-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Book Appointment</h3>
                <button class="close-btn" onclick="closeModal('booking-modal')">&times;</button>
            </div>
            <div id="booking-info" style="background: #f5f7ff; padding: 15px; border-radius: 8px; margin-bottom: 20px;"></div>
            <form onsubmit="bookAppointment(event)">
                <div class="form-group">
                    <label>Your Name *</label>
                    <input type="text" id="student-name" required>
                </div>
                <div class="form-group">
                    <label>Consultation Concern *</label>
                    <textarea id="concern" rows="4" required placeholder="Briefly describe your concern..."></textarea>
                </div>
                <div class="form-group">
                    <label>Meeting Type</label>
                    <select id="meeting-type">
                        <option value="in-person">🏢 In-person</option>
                        <option value="online">💻 Online</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%;">
                    ✓ Confirm Booking
                </button>
            </form>
        </div>
    </div>
    
    <!-- Add Slot Modal -->
    <div id="slot-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Add Available Slot</h3>
                <button class="close-btn" onclick="closeModal('slot-modal')">&times;</button>
            </div>
            <form onsubmit="addSlot(event)">
                <div class="form-group">
                    <label>Date</label>
                    <input type="date" id="slot-date" required>
                </div>
                <div class="form-group">
                    <label>Time</label>
                    <input type="time" id="slot-time" required>
                </div>
                <div class="form-group">
                    <label>Duration</label>
                    <select id="slot-duration">
                        <option value="15">15 minutes</option>
                        <option value="30">30 minutes</option>
                        <option value="45">45 minutes</option>
                        <option value="60">60 minutes</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%;">
                    Add Slot
                </button>
            </form>
        </div>
    </div>

    <script>
        let currentRole = 'student';
        let selectedFaculty = null;
        let selectedSlot = null;
        let facultyMembers = [];
        let availableSlots = [];
        let appointments = [];
        
        // Initialize
        async function init() {
            await loadFacultyMembers();
            await loadSlots();
            await loadAppointments();
            renderFacultyList();
        }
        
        async function loadFacultyMembers() {
            const response = await fetch('/api/faculty');
            facultyMembers = await response.json();
        }
        
        async function loadSlots() {
            const response = await fetch('/api/slots');
            availableSlots = await response.json();
        }
        
        async function loadAppointments() {
            const response = await fetch('/api/appointments');
            appointments = await response.json();
        }
        
        function switchRole(role) {
            currentRole = role;
            document.getElementById('student-btn').classList.toggle('active', role === 'student');
            document.getElementById('faculty-btn').classList.toggle('active', role === 'faculty');
            document.getElementById('student-view').style.display = role === 'student' ? 'grid' : 'none';
            document.getElementById('faculty-view').style.display = role === 'faculty' ? 'grid' : 'none';
            
            if (role === 'faculty') {
                renderFacultyProfiles();
            }
        }
        
        function renderFacultyList() {
            const container = document.getElementById('faculty-list');
            container.innerHTML = facultyMembers.map(faculty => `
                <div class="faculty-item" onclick="selectFaculty(${faculty.id})">
                    <h3>${faculty.name}</h3>
                    <p>${faculty.department}</p>
                </div>
            `).join('');
        }
        
        function renderFacultyProfiles() {
            const container = document.getElementById('faculty-profiles');
            container.innerHTML = facultyMembers.map(faculty => `
                <div class="faculty-item" onclick="selectFacultyProfile(${faculty.id})">
                    <h3>${faculty.name}</h3>
                    <p>${faculty.department}</p>
                </div>
            `).join('');
        }
        
        function selectFaculty(facultyId) {
            selectedFaculty = facultyMembers.find(f => f.id === facultyId);
            document.querySelectorAll('#faculty-list .faculty-item').forEach((item, idx) => {
                item.classList.toggle('selected', facultyMembers[idx].id === facultyId);
            });
            renderSlots();
        }
        
        function selectFacultyProfile(facultyId) {
            selectedFaculty = facultyMembers.find(f => f.id === facultyId);
            document.querySelectorAll('#faculty-profiles .faculty-item').forEach((item, idx) => {
                item.classList.toggle('selected', facultyMembers[idx].id === facultyId);
            });
            renderAppointments();
            renderAnalytics();
        }
        
        function renderSlots() {
            const container = document.getElementById('slots-container');
            const facultySlots = availableSlots.filter(s => s.faculty_id === selectedFaculty.id && !s.is_booked);
            
            if (facultySlots.length === 0) {
                container.innerHTML = '<div class="empty-state"><p>No available slots at the moment</p></div>';
                return;
            }
            
            container.innerHTML = '<div class="slot-grid">' + facultySlots.map(slot => `
                <div class="slot-item" onclick='selectSlot(${JSON.stringify(slot)})'>
                    <div class="slot-date">📅 ${slot.date}</div>
                    <div class="slot-time">🕐 ${slot.time} (${slot.duration} min)</div>
                </div>
            `).join('') + '</div>';
        }
        
        function selectSlot(slot) {
            selectedSlot = slot;
            document.getElementById('booking-info').innerHTML = `
                <p><strong>Faculty:</strong> ${selectedFaculty.name}</p>
                <p><strong>Date:</strong> ${slot.date}</p>
                <p><strong>Time:</strong> ${slot.time} (${slot.duration} min)</p>
            `;
            document.getElementById('booking-modal').classList.add('show');
        }
        
        async function bookAppointment(event) {
            event.preventDefault();
            
            const data = {
                faculty_id: selectedFaculty.id,
                slot_id: selectedSlot.id,
                student_name: document.getElementById('student-name').value,
                concern: document.getElementById('concern').value,
                meeting_type: document.getElementById('meeting-type').value
            };
            
            const response = await fetch('/api/book', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                alert('Appointment booked successfully! Confirmation email sent.');
                closeModal('booking-modal');
                await loadSlots();
                await loadAppointments();
                renderSlots();
                document.getElementById('student-name').value = '';
                document.getElementById('concern').value = '';
            }
        }
        
        function renderAppointments() {
            const container = document.getElementById('appointments-container');
            const facultyAppts = appointments.filter(a => a.faculty_id === selectedFaculty.id);
            
            if (facultyAppts.length === 0) {
                container.innerHTML = '<div class="empty-state"><p>No appointments scheduled</p></div>';
                return;
            }
            
            container.innerHTML = facultyAppts.map(apt => `
                <div class="appointment-item">
                    <div class="appointment-header">
                        <div class="appointment-time">🕐 ${apt.time}</div>
                        <span class="status-badge status-confirmed">Confirmed</span>
                    </div>
                    <p><strong>${apt.student_name}</strong></p>
                    <p style="color: #666; margin: 5px 0;">${apt.concern}</p>
                    <span class="meeting-type">
                        ${apt.meeting_type === 'online' ? '💻 Online' : '🏢 In-person'}
                    </span>
                </div>
            `).join('');
        }
        
        function renderAnalytics() {
            const topics = {};
            appointments.filter(a => a.faculty_id === selectedFaculty.id).forEach(apt => {
                topics[apt.concern] = (topics[apt.concern] || 0) + 1;
            });
            
            const sortedTopics = Object.entries(topics).sort((a, b) => b[1] - a[1]).slice(0, 5);
            const maxCount = Math.max(...sortedTopics.map(t => t[1]), 1);
            
            const container = document.getElementById('analytics-container');
            container.innerHTML = sortedTopics.map(([topic, count]) => `
                <div class="analytics-item">
                    <div class="analytics-label">
                        <span>${topic}</span>
                        <span>${count}</span>
                    </div>
                    <div class="analytics-bar">
                        <div class="analytics-fill" style="width: ${(count / maxCount) * 100}%"></div>
                    </div>
                </div>
            `).join('');
        }
        
        function showAddSlotModal() {
            document.getElementById('slot-modal').classList.add('show');
        }
        
        async function addSlot(event) {
            event.preventDefault();
            
            const data = {
                faculty_id: selectedFaculty.id,
                date: document.getElementById('slot-date').value,
                time: document.getElementById('slot-time').value,
                duration: parseInt(document.getElementById('slot-duration').value)
            };
            
            const response = await fetch('/api/add-slot', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                alert('Time slot added successfully!');
                closeModal('slot-modal');
                await loadSlots();
                document.getElementById('slot-date').value = '';
                document.getElementById('slot-time').value = '';
            }
        }
        
        function closeModal(modalId) {
            document.getElementById(modalId).classList.remove('show');
        }
        
        // Initialize on page load
        init();
    </script>
</body>
</html>
'''
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/faculty')
def get_faculty():
    return jsonify(faculty_members)

@app.route('/api/slots')
def get_slots():
    return jsonify(available_slots)

@app.route('/api/appointments')
def get_appointments():
    return jsonify(appointments)

@app.route('/api/book', methods=['POST'])
def book_appointment():
    data = request.json
    
    # Mark slot as booked
    for slot in available_slots:
        if slot['id'] == data['slot_id']:
            slot['is_booked'] = True
            break
    
    # Create appointment
    appointment = {
        'id': len(appointments) + 1,
        'faculty_id': data['faculty_id'],
        'student_name': data['student_name'],
        'date': next(s['date'] for s in available_slots if s['id'] == data['slot_id']),
        'time': next(s['time'] for s in available_slots if s['id'] == data['slot_id']),
        'duration': next(s['duration'] for s in available_slots if s['id'] == data['slot_id']),
        'concern': data['concern'],
        'meeting_type': data['meeting_type'],
        'status': 'confirmed'
    }
    appointments.append(appointment)
    
    # Simulate sending email
    faculty = next(f for f in faculty_members if f['id'] == data['faculty_id'])
    print(f"\n📧 EMAIL SENT TO: {data['student_name']}")
    print(f"Subject: Appointment Confirmed with {faculty['name']}")
    print(f"Date: {appointment['date']} at {appointment['time']}")
    print(f"Meeting Type: {data['meeting_type']}")
    print(f"Concern: {data['concern']}\n")
    
    return jsonify({'success': True, 'appointment': appointment})

@app.route('/api/add-slot', methods=['POST'])
def add_slot():
    data = request.json
    
    slot = {
        'id': len(available_slots) + 1,
        'faculty_id': data['faculty_id'],
        'date': data['date'],
        'time': data['time'],
        'duration': data['duration'],
        'is_booked': False
    }
    available_slots.append(slot)
    
    return jsonify({'success': True, 'slot': slot})

if __name__ == '__main__':
    print("🎓 Faculty Consultation Appointment System")
    print("📍 Open your browser and go to: http://127.0.0.1:5000")
    print("   • Students can browse faculty and book appointments")
    print("   • Faculty can manage their schedule and add time slots")
    print("\n⚠️  Press Ctrl+C to stop the server\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
    
    
    