from flask import Flask, render_template_string, request, jsonify, session
from datetime import datetime, timedelta
import json
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

#SAMPLE DATA, REPLACE WITH ACTUAL DATABASE ON PROD.
faculty_members = [
    {'id': 1, 'name': 'Dr. Maria Santos', 'department': 'Computer Science', 'email': 'msantos@university.edu'},
    {'id': 2, 'name': 'Prof. Juan Reyes', 'department': 'Mathematics', 'email': 'jreyes@university.edu'},
    {'id': 3, 'name': 'Dr. Ana Cruz', 'department': 'Physics', 'email': 'acruz@university.edu'},
]

available_slots = [
    {'id': 1, 'faculty_id': 1, 'date': '2026-01-10', 'time': '10:00', 'duration': 30, 'is_booked': False},
    {'id': 2, 'faculty_id': 1, 'date': '2026-01-10', 'time': '11:00', 'duration': 30, 'is_booked': False},
    {'id': 3, 'faculty_id': 1, 'date': '2026-01-10', 'time': '14:00', 'duration': 30, 'is_booked': False},
    {'id': 4, 'faculty_id': 2, 'date': '2026-01-10', 'time': '13:00', 'duration': 30, 'is_booked': False},
    {'id': 5, 'faculty_id': 2, 'date': '2026-01-11', 'time': '09:00', 'duration': 30, 'is_booked': False},
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
            color: #fff;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 50px;
            animation: fadeInDown 0.6s ease;
        }
        
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .header h1 {
            font-size: 3em;
            font-weight: 700;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p {
            font-size: 1.2em;
            color: rgba(255, 255, 255, 0.8);
        }
        
        .role-switcher {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 30px;
        }
        
        .role-btn {
            padding: 14px 40px;
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 50px;
            font-size: 1.05em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background: rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
        }
        
        .role-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-color: transparent;
            color: white;
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .role-btn:hover:not(.active) {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
        }
        
        .content {
            display: grid;
            grid-template-columns: 350px 1fr;
            gap: 30px;
            animation: fadeIn 0.8s ease;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            color: #2d3748;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 25px 70px rgba(0, 0, 0, 0.35);
        }
        
        .card h2 {
            font-size: 1.6em;
            margin-bottom: 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }
        
        .faculty-item {
            padding: 18px;
            margin-bottom: 12px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 2px solid transparent;
            background: linear-gradient(135deg, #f6f8fb 0%, #f0f2f5 100%);
        }
        
        .faculty-item:hover {
            background: linear-gradient(135deg, #e8ecf4 0%, #dde2ea 100%);
            transform: translateX(5px);
        }
        
        .faculty-item.selected {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-color: transparent;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }
        
        .faculty-item.selected h3,
        .faculty-item.selected p {
            color: white;
        }
        
        .faculty-item h3 {
            color: #2d3748;
            margin-bottom: 6px;
            font-size: 1.1em;
            font-weight: 600;
        }
        
        .faculty-item p {
            color: #718096;
            font-size: 0.9em;
        }
        
        .slot-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }
        
        .slot-item {
            padding: 25px;
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background: white;
            position: relative;
            overflow: hidden;
        }
        
        .slot-item::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .slot-item:hover {
            border-color: #667eea;
            transform: translateY(-8px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
        }
        
        .slot-item:hover::before {
            opacity: 0.05;
        }
        
        .slot-date {
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 1.15em;
            position: relative;
            z-index: 1;
        }
        
        .slot-time {
            color: #718096;
            font-size: 0.95em;
            position: relative;
            z-index: 1;
        }
        
        .btn {
            padding: 14px 28px;
            border: none;
            border-radius: 12px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
        }
        
        .btn-primary:active {
            transform: translateY(-1px);
        }
        
        .btn-secondary {
            background: #e2e8f0;
            color: #4a5568;
        }
        
        .btn-secondary:hover {
            background: #cbd5e0;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(8px);
            justify-content: center;
            align-items: center;
            z-index: 1000;
            animation: fadeIn 0.3s ease;
        }
        
        .modal.show {
            display: flex;
        }
        
        .modal-content {
            background: white;
            padding: 40px;
            border-radius: 24px;
            width: 90%;
            max-width: 550px;
            box-shadow: 0 30px 90px rgba(0, 0, 0, 0.4);
            animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        
        .modal-header h3 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 1.8em;
            font-weight: 700;
        }
        
        .close-btn {
            background: #f7fafc;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-size: 1.5em;
            cursor: pointer;
            color: #718096;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .close-btn:hover {
            background: #e2e8f0;
            color: #2d3748;
            transform: rotate(90deg);
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 10px;
            color: #2d3748;
            font-weight: 600;
            font-size: 0.95em;
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 14px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 1em;
            font-family: inherit;
            background: #f7fafc;
            color: #2d3748;
            transition: all 0.3s ease;
        }
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
            background: white;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .appointment-item {
            padding: 25px;
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            border-left: 5px solid #667eea;
            border-radius: 16px;
            margin-bottom: 18px;
            transition: all 0.3s ease;
        }
        
        .appointment-item:hover {
            transform: translateX(5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        }
        
        .appointment-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .appointment-time {
            font-weight: 700;
            color: #2d3748;
            font-size: 1.2em;
        }
        
        .status-badge {
            padding: 8px 18px;
            border-radius: 50px;
            font-size: 0.85em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-confirmed {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
        }
        
        .empty-state {
            text-align: center;
            padding: 80px 30px;
            color: #a0aec0;
        }
        
        .empty-state p {
            font-size: 1.1em;
            line-height: 1.6;
        }
        
        .analytics {
            margin-top: 40px;
            padding-top: 40px;
            border-top: 2px solid #e2e8f0;
        }
        
        .analytics h3 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 1.4em;
            margin-bottom: 25px;
            font-weight: 700;
        }
        
        .analytics-item {
            margin-bottom: 20px;
        }
        
        .analytics-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            color: #2d3748;
            font-weight: 600;
        }
        
        .analytics-bar {
            background: #e2e8f0;
            height: 32px;
            border-radius: 16px;
            overflow: hidden;
        }
        
        .analytics-fill {
            background: linear-gradient(90deg, #667eea, #764ba2);
            height: 100%;
            transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
        }
        
        .meeting-type {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: white;
            border-radius: 50px;
            font-size: 0.9em;
            margin-top: 12px;
            color: #4a5568;
            font-weight: 600;
            border: 2px solid #e2e8f0;
        }
        
        .info-box {
            background: linear-gradient(135deg, #edf2f7 0%, #e2e8f0 100%);
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 25px;
            border-left: 4px solid #667eea;
        }
        
        .info-box p {
            color: #2d3748;
            margin: 8px 0;
            font-size: 0.95em;
        }
        
        .info-box strong {
            color: #667eea;
            font-weight: 700;
        }
        
        .faculty-slot-item {
            padding: 20px;
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            border-radius: 16px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
            border-left: 5px solid transparent;
        }
        
        .faculty-slot-item:hover {
            transform: translateX(5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        }
        
        .faculty-slot-item.booked {
            opacity: 0.7;
            border-left-color: #a0aec0;
        }
        
        .faculty-slot-item.available {
            border-left-color: #48bb78;
        }
        
        .slot-info {
            flex: 1;
        }
        
        .slot-info-time {
            color: #2d3748;
            font-weight: 700;
            margin-bottom: 6px;
            font-size: 1.1em;
        }
        
        .slot-info-date {
            color: #718096;
            font-size: 0.9em;
        }
        
        .slot-status {
            padding: 6px 16px;
            border-radius: 50px;
            font-size: 0.85em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .slot-status.available {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
        }
        
        .slot-status.booked {
            background: #cbd5e0;
            color: #4a5568;
        }
        
        .btn-delete {
            background: linear-gradient(135deg, #fc8181 0%, #f56565 100%);
            color: white;
            padding: 10px 18px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 0.9em;
            margin-left: 15px;
            transition: all 0.3s ease;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(252, 129, 129, 0.3);
        }
        
        .btn-delete:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(252, 129, 129, 0.4);
        }
        
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
        }
        
        .card-header h2 {
            margin: 0;
        }
        
        @media (max-width: 1200px) {
            .content {
                grid-template-columns: 1fr;
            }
            
            .grid-2 {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 768px) {
            .slot-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .role-switcher {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Faculty Consultation System</h1>
            <p>Schedule appointments with faculty members effortlessly</p>
            <div class="role-switcher">
                <button class="role-btn active" id="student-btn" onclick="switchRole('student')">
                    Student View
                </button>
                <button class="role-btn" id="faculty-btn" onclick="switchRole('faculty')">
                    Faculty View
                </button>
            </div>
        </div>
        
        <!-- Student interface -->
        <div id="student-view" class="content">
            <div class="card">
                <h2>Select Faculty</h2>
                <div id="faculty-list"></div>
            </div>
            
            <div class="card">
                <h2>Available Time Slots</h2>
                <div id="slots-container">
                    <div class="empty-state">
                        <p>Select a faculty member to view their available consultation times</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Faculty interface -->
        <div id="faculty-view" style="display: none;">
            <div class="content">
                <div class="card">
                    <div class="card-header">
                        <h2>Select Your Profile</h2>
                        <button class="btn btn-primary" onclick="showAddFacultyModal()">+ Add Faculty</button>
                    </div>
                    <div id="faculty-profiles"></div>
                </div>
                
                <div style="display: flex; flex-direction: column; gap: 30px;">
                    <div class="card">
                        <div class="card-header">
                            <h2>Today's Schedule</h2>
                            <button class="btn btn-primary" onclick="showAddSlotModal()">+ Add Slot</button>
                        </div>
                        <div id="appointments-container"></div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h2>My Available Slots</h2>
                            <button class="btn btn-primary" onclick="showAddSlotModal()">+ Add New Slot</button>
                        </div>
                        <div id="faculty-slots-container"></div>
                    </div>
                </div>
            </div>
            
            <div class="card" style="margin-top: 30px;">
                <div class="analytics">
                    <h3>Consultation Topics Analytics</h3>
                    <div id="analytics-container"></div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Booking modal -->
    <div id="booking-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Book Appointment</h3>
                <button class="close-btn" onclick="closeModal('booking-modal')">&times;</button>
            </div>
            <div id="booking-info" class="info-box"></div>
            <form onsubmit="bookAppointment(event)">
                <div class="form-group">
                    <label>Your Name *</label>
                    <input type="text" id="student-name" required>
                </div>
                <div class="form-group">
                    <label>Consultation Concern *</label>
                    <textarea id="concern" rows="4" required placeholder="Briefly describe what you'd like to discuss..."></textarea>
                </div>
                <div class="form-group">
                    <label>Meeting Type</label>
                    <select id="meeting-type">
                        <option value="in-person">In-person</option>
                        <option value="online">Online</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%;">
                    Confirm Booking
                </button>
            </form>
        </div>
    </div>
    
    <!-- Add slot modal -->
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
    
    <!-- Add Faculty Modal -->
    <div id="faculty-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Add Faculty Member</h3>
                <button class="close-btn" onclick="closeModal('faculty-modal')">&times;</button>
            </div>
            <form onsubmit="addFaculty(event)">
                <div class="form-group">
                    <label>Name *</label>
                    <input type="text" id="faculty-name" placeholder="Dr. John Doe" required>
                </div>
                <div class="form-group">
                    <label>Department *</label>
                    <input type="text" id="faculty-department" placeholder="Computer Science" required>
                </div>
                <div class="form-group">
                    <label>Email *</label>
                    <input type="email" id="faculty-email" placeholder="jdoe@university.edu" required>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%;">
                    Add Faculty Member
                </button>
            </form>
        </div>
    </div>
    
    <!-- Manage Appointment Modal -->
    <div id="manage-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Manage Appointment</h3>
                <button class="close-btn" onclick="closeModal('manage-modal')">&times;</button>
            </div>
            <div id="manage-info" class="info-box"></div>
            
            <!-- Action Selection -->
            <div id="action-selection">
                <p style="margin-bottom: 20px; color: #2d3748; font-weight: 600;">What would you like to do?</p>
                <button type="button" class="btn btn-primary" onclick="showCancelWithReason()" style="width: 100%; margin-bottom: 12px;">
                    Cancel with Reason
                </button>
                <button type="button" class="btn btn-secondary" onclick="showCancelWithoutReason()" style="width: 100%;">
                    Cancel without Reason
                </button>
            </div>
            
            <!-- Cancel with Reason Form -->
            <div id="cancel-reason-form" style="display: none;">
                <form onsubmit="cancelAppointmentWithReason(event)">
                    <div class="form-group">
                        <label>Cancellation Reason *</label>
                        <textarea id="cancel-reason" rows="4" required placeholder="Please provide a reason for cancelling this appointment..."></textarea>
                    </div>
                    <div style="display: flex; gap: 12px;">
                        <button type="button" class="btn btn-secondary" style="flex: 1;" onclick="showActionSelection()">Back</button>
                        <button type="submit" class="btn btn-primary" style="flex: 1; background: linear-gradient(135deg, #fc8181 0%, #f56565 100%);">
                            Confirm Cancellation
                        </button>
                    </div>
                </form>
            </div>
            
            <!-- Cancel without Reason Confirmation -->
            <div id="cancel-confirm" style="display: none;">
                <p style="color: #e53e3e; margin-bottom: 20px; padding: 15px; background: #fff5f5; border-radius: 12px; border-left: 4px solid #fc8181;">
                    <strong>Warning:</strong> You are about to cancel this appointment without providing a reason. The student will be notified of the cancellation.
                </p>
                <div style="display: flex; gap: 12px;">
                    <button type="button" class="btn btn-secondary" style="flex: 1;" onclick="showActionSelection()">Back</button>
                    <button type="button" class="btn btn-primary" onclick="cancelAppointmentWithoutReason()" style="flex: 1; background: linear-gradient(135deg, #fc8181 0%, #f56565 100%);">
                        Confirm Cancellation
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentRole = 'student';
        let selectedFaculty = null;
        let selectedSlot = null;
        let selectedAppointment = null;
        let facultyMembers = [];
        let availableSlots = [];
        let appointments = [];
        
        // Load initial data when page loads
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
        
        // Switch between student and faculty views
        function switchRole(role) {
            currentRole = role;
            document.getElementById('student-btn').classList.toggle('active', role === 'student');
            document.getElementById('faculty-btn').classList.toggle('active', role === 'faculty');
            document.getElementById('student-view').style.display = role === 'student' ? 'grid' : 'none';
            document.getElementById('faculty-view').style.display = role === 'faculty' ? 'block' : 'none';
            
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
        
        // Handle faculty selection in student view
        function selectFaculty(facultyId) {
            selectedFaculty = facultyMembers.find(f => f.id === facultyId);
            document.querySelectorAll('#faculty-list .faculty-item').forEach((item, idx) => {
                item.classList.toggle('selected', facultyMembers[idx].id === facultyId);
            });
            renderSlots();
        }
        
        // Handle faculty profile selection in faculty view
        function selectFacultyProfile(facultyId) {
            selectedFaculty = facultyMembers.find(f => f.id === facultyId);
            document.querySelectorAll('#faculty-profiles .faculty-item').forEach((item, idx) => {
                item.classList.toggle('selected', facultyMembers[idx].id === facultyId);
            });
            renderAppointments();
            renderAnalytics();
            renderFacultySlots();
        }
        
        // Display available slots for selected faculty
        function renderSlots() {
            const container = document.getElementById('slots-container');
            const facultySlots = availableSlots.filter(s => s.faculty_id === selectedFaculty.id && !s.is_booked);
            
            if (facultySlots.length === 0) {
                container.innerHTML = '<div class="empty-state"><p>No available slots at the moment</p></div>';
                return;
            }
            
            container.innerHTML = '<div class="slot-grid">' + facultySlots.map(slot => `
                <div class="slot-item" onclick='selectSlot(${JSON.stringify(slot)})'>
                    <div class="slot-date">${slot.date}</div>
                    <div class="slot-time">${slot.time} (${slot.duration} min)</div>
                </div>
            `).join('') + '</div>';
        }
        
        // Open booking modal with selected slot info
        function selectSlot(slot) {
            selectedSlot = slot;
            document.getElementById('booking-info').innerHTML = `
                <p><strong>Faculty:</strong> ${selectedFaculty.name}</p>
                <p><strong>Date:</strong> ${slot.date}</p>
                <p><strong>Time:</strong> ${slot.time} (${slot.duration} min)</p>
            `;
            document.getElementById('booking-modal').classList.add('show');
        }
        
        // Submit appointment booking
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
                // Clear form fields
                document.getElementById('student-name').value = '';
                document.getElementById('concern').value = '';
            }
        }
        
        // Display appointments for selected faculty
        function renderAppointments() {
            const container = document.getElementById('appointments-container');
            const facultyAppts = appointments.filter(a => a.faculty_id === selectedFaculty.id && a.status !== 'cancelled');
            
            if (facultyAppts.length === 0) {
                container.innerHTML = '<div class="empty-state"><p>No appointments scheduled</p></div>';
                return;
            }
            
            container.innerHTML = facultyAppts.map(apt => `
                <div class="appointment-item">
                    <div class="appointment-header">
                        <div class="appointment-time">${apt.time}</div>
                        <div style="display: flex; gap: 10px; align-items: center;">
                            <span class="status-badge status-confirmed">Confirmed</span>
                            <button class="btn" onclick='manageAppointment(${JSON.stringify(apt).replace(/'/g, "&apos;")})' style="padding: 8px 16px; background: linear-gradient(135deg, #f6ad55 0%, #ed8936 100%); color: white; border: none; border-radius: 8px; font-size: 0.85em; font-weight: 600; cursor: pointer;">
                                Manage
                            </button>
                        </div>
                    </div>
                    <p style="font-weight: 600; color: #2d3748; margin-bottom: 8px;">${apt.student_name}</p>
                    <p style="color: #718096; margin: 5px 0;">${apt.concern}</p>
                    <span class="meeting-type">
                        ${apt.meeting_type === 'online' ? 'Online' : 'In-person'}
                    </span>
                </div>
            `).join('');
        }
        
        // Show analytics of consultation topics
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
        
        // Add new time slot for faculty
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
                renderFacultySlots();
                // Reset form
                document.getElementById('slot-date').value = '';
                document.getElementById('slot-time').value = '';
            }
        }
        
        // Display all slots for the faculty member
        function renderFacultySlots() {
            const container = document.getElementById('faculty-slots-container');
            const facultySlots = availableSlots.filter(s => s.faculty_id === selectedFaculty.id);
            
            if (facultySlots.length === 0) {
                container.innerHTML = '<div class="empty-state"><p>No time slots created yet. Click "Add New Slot" to get started.</p></div>';
                return;
            }
            
            // Sort slots by date and time
            facultySlots.sort((a, b) => {
                const dateCompare = a.date.localeCompare(b.date);
                if (dateCompare !== 0) return dateCompare;
                return a.time.localeCompare(b.time);
            });
            
            container.innerHTML = facultySlots.map(slot => `
                <div class="faculty-slot-item ${slot.is_booked ? 'booked' : 'available'}">
                    <div class="slot-info">
                        <div class="slot-info-time">${slot.time} - ${slot.duration} minutes</div>
                        <div class="slot-info-date">${slot.date}</div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span class="slot-status ${slot.is_booked ? 'booked' : 'available'}">
                            ${slot.is_booked ? 'Booked' : 'Available'}
                        </span>
                        ${!slot.is_booked ? `<button class="btn-delete" onclick="deleteSlot(${slot.id})">Delete</button>` : ''}
                    </div>
                </div>
            `).join('');
        }
        
        // Delete an available slot
        async function deleteSlot(slotId) {
            if (!confirm('Are you sure you want to delete this time slot?')) {
                return;
            }
            
            const response = await fetch('/api/delete-slot', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ slot_id: slotId })
            });
            
            if (response.ok) {
                alert('Time slot deleted successfully!');
                await loadSlots();
                renderFacultySlots();
            }
        }
        
        // Show add faculty modal
        function showAddFacultyModal() {
            document.getElementById('faculty-modal').classList.add('show');
        }
        
        // Add new faculty member
        async function addFaculty(event) {
            event.preventDefault();
            
            const data = {
                name: document.getElementById('faculty-name').value,
                department: document.getElementById('faculty-department').value,
                email: document.getElementById('faculty-email').value
            };
            
            const response = await fetch('/api/add-faculty', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                alert('Faculty member added successfully!');
                closeModal('faculty-modal');
                await loadFacultyMembers();
                renderFacultyProfiles();
                renderFacultyList();
                // Reset form
                document.getElementById('faculty-name').value = '';
                document.getElementById('faculty-department').value = '';
                document.getElementById('faculty-email').value = '';
            }
        }
        
        // Manage appointment
        function manageAppointment(apt) {
            selectedAppointment = apt;
            document.getElementById('manage-info').innerHTML = `
                <p><strong>Student:</strong> ${apt.student_name}</p>
                <p><strong>Date:</strong> ${apt.date}</p>
                <p><strong>Time:</strong> ${apt.time}</p>
                <p><strong>Concern:</strong> ${apt.concern}</p>
                <p><strong>Type:</strong> ${apt.meeting_type === 'online' ? 'Online' : 'In-person'}</p>
            `;
            showActionSelection();
            document.getElementById('manage-modal').classList.add('show');
        }
        
        // Show action selection
        function showActionSelection() {
            document.getElementById('action-selection').style.display = 'block';
            document.getElementById('cancel-reason-form').style.display = 'none';
            document.getElementById('cancel-confirm').style.display = 'none';
        }
        
        // Show cancel with reason form
        function showCancelWithReason() {
            document.getElementById('action-selection').style.display = 'none';
            document.getElementById('cancel-reason-form').style.display = 'block';
            document.getElementById('cancel-confirm').style.display = 'none';
        }
        
        // Show cancel without reason confirmation
        function showCancelWithoutReason() {
            document.getElementById('action-selection').style.display = 'none';
            document.getElementById('cancel-reason-form').style.display = 'none';
            document.getElementById('cancel-confirm').style.display = 'block';
        }
        
        // Cancel appointment with reason
        async function cancelAppointmentWithReason(event) {
            event.preventDefault();
            
            const reason = document.getElementById('cancel-reason').value;
            
            const response = await fetch('/api/cancel-appointment', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    appointment_id: selectedAppointment.id,
                    reason: reason
                })
            });
            
            if (response.ok) {
                alert('Appointment cancelled successfully. Student has been notified with your reason.');
                closeModal('manage-modal');
                await loadAppointments();
                await loadSlots();
                renderAppointments();
                document.getElementById('cancel-reason').value = '';
            }
        }
        
        // Cancel appointment without reason
        async function cancelAppointmentWithoutReason() {
            const response = await fetch('/api/cancel-appointment', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    appointment_id: selectedAppointment.id,
                    reason: null
                })
            });
            
            if (response.ok) {
                alert('Appointment cancelled successfully. Student has been notified.');
                closeModal('manage-modal');
                await loadAppointments();
                await loadSlots();
                renderAppointments();
            }
        }
        
        function closeModal(modalId) {
            document.getElementById(modalId).classList.remove('show');
        }
        
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
    
    # Mark the slot as booked
    for slot in available_slots:
        if slot['id'] == data['slot_id']:
            slot['is_booked'] = True
            break
    
    # create a new appointment 
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
    
    # email notification
    faculty = next(f for f in faculty_members if f['id'] == data['faculty_id'])
    print(f"\nEmail confirmation sent to: {data['student_name']}")
    print(f"Appointment with {faculty['name']}")
    print(f"Date: {appointment['date']} at {appointment['time']}")
    print(f"Type: {data['meeting_type']}")
    print(f"Topic: {data['concern']}\n")
    
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

@app.route('/api/delete-slot', methods=['POST'])
def delete_slot():
    data = request.json
    slot_id = data['slot_id']
    
    # find name and remove slot 
    global available_slots
    available_slots = [slot for slot in available_slots if slot['id'] != slot_id]
    
    return jsonify({'success': True})

@app.route('/api/add-faculty', methods=['POST'])
def add_faculty():
    data = request.json
    
    faculty = {
        'id': len(faculty_members) + 1,
        'name': data['name'],
        'department': data['department'],
        'email': data['email']
    }
    faculty_members.append(faculty)
    
    print(f"\nNew faculty member added:")
    print(f"Name: {faculty['name']}")
    print(f"Department: {faculty['department']}")
    print(f"Email: {faculty['email']}\n")
    
    return jsonify({'success': True, 'faculty': faculty})

@app.route('/api/cancel-appointment', methods=['POST'])
def cancel_appointment():
    data = request.json
    appointment_id = data['appointment_id']
    reason = data.get('reason')
    
    #find appointment and mark cacnnel
    for apt in appointments:
        if apt['id'] == appointment_id:
            apt['status'] = 'cancelled'
            apt['cancellation_reason'] = reason
            
            # Free up the slot
            for slot in available_slots:
                if slot['date'] == apt['date'] and slot['time'] == apt['time']:
                    slot['is_booked'] = False
                    break
            
            #send notif 
            print(f"\nAppointment Cancelled:")
            print(f"Student: {apt['student_name']}")
            print(f"Date: {apt['date']} at {apt['time']}")
            if reason:
                print(f"Reason: {reason}")
            else:
                print("Reason: Not provided")
            print(f"Email notification sent to student\n")
            
            break
    
    return jsonify({'success': True})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Faculty Consultation Appointment System")
    print("="*60)
    print("\nStarting server...")
    print("Access the application at: http://127.0.0.1:5000")
    print("\nFeatures:")
    print("  - Student appointment booking")
    print("  - Faculty schedule management")
    print("  - Email confirmations (console output)")
    print("  - Consultation analytics")
    print("\nPress Ctrl+C to stop the server\n")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)