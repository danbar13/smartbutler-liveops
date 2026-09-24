"""
SmartButler Mock Operational Log Generator
Simulates 48 hours of operational data for JAYBEE Systems' SmartButler ecosystem:
- Maintenance Module (Engineering work orders, SLA, parts status)
- Housekeeping Module (Room states, guest requests, deep cleans)
- Logbook Module (Shift handovers, VIP escalations, guest compensations)

Injects 4 deliberate operational anomalies:
1. Room 412 (VIP, Occupied): Recurrent HVAC complaints across shifts.
2. Floor 3: 4 Wi-Fi / SmartTV connection failures in evening peak hours (20:00 - 22:30).
3. Night Shift Handover: 3 open maintenance tasks marked as "WaitingParts".
4. Logbook: 2 critical guest compensation incidents (Room 412 AC & Room 205 ceiling leak).
"""

import os
import json
import csv
from datetime import datetime, timedelta
import random

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "logs")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")

def ensure_directories():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_mock_data():
    ensure_directories()
    # Reference anchor time: Morning standup at 2026-09-23 07:00
    base_time = datetime(2026, 9, 23, 7, 0, 0)
    start_time = base_time - timedelta(hours=48)

    maintenance_tickets = []
    housekeeping_tasks = []
    logbook_entries = []

    # -------------------------------------------------------------
    # 1. MAINTENANCE MODULE
    # -------------------------------------------------------------
    # Deliberate Anomaly 1: Room 412 Recurring HVAC Complaints across shifts
    hvac_412_events = [
        {
            "offset_hours": 36, # Day 1, ~19:40 Evening shift
            "ticket_id": "MNT-7412-1",
            "room_number": 412,
            "floor": 4,
            "category": "HVAC",
            "issue_description": "HVAC blowing warm air, room temp 26C. Guest Dr. E. Ben-Ari requested urgent technician.",
            "priority": "Urgent",
            "status": "Resolved",
            "assigned_technician": "Yossi C. (Senior AC Tech)",
            "shift": "Evening",
            "resolution_time_minutes": 55,
            "vip_flag": True,
            "notes": "Checked refrigerant pressure. Cleaned air filter. Temp set to 21C."
        },
        {
            "offset_hours": 22, # Day 2, ~09:00 Morning shift
            "ticket_id": "MNT-7412-2",
            "room_number": 412,
            "floor": 4,
            "category": "HVAC",
            "issue_description": "HVAC unit vibrating heavily, rattling sound and temperature reset to 27C. Guest irritated.",
            "priority": "High",
            "status": "Resolved",
            "assigned_technician": "Ahmed K. (Mechanic)",
            "shift": "Morning",
            "resolution_time_minutes": 80,
            "vip_flag": True,
            "notes": "Tightened blower fan housing and applied vibration dampeners. Operational test passed."
        },
        {
            "offset_hours": 7, # Day 2 / Night shift, ~23:50
            "ticket_id": "MNT-7412-3",
            "room_number": 412,
            "floor": 4,
            "category": "HVAC",
            "issue_description": "HVAC cooling compressor failed completely. Room warm again. VIP guest demanded Duty Manager and refund.",
            "priority": "Urgent",
            "status": "InProgress",
            "assigned_technician": "David L. (Night Duty Tech)",
            "shift": "Night",
            "resolution_time_minutes": None,
            "vip_flag": True,
            "notes": "Compressor clutch cycling off. Temporary portable fan delivered. Need chiller technician at morning standup."
        }
    ]

    for item in hvac_412_events:
        t_created = base_time - timedelta(hours=item["offset_hours"])
        t_closed = t_created + timedelta(minutes=item["resolution_time_minutes"]) if item["resolution_time_minutes"] else None
        maintenance_tickets.append({
            "ticket_id": item["ticket_id"],
            "created_at": t_created.strftime("%Y-%m-%d %H:%M:%S"),
            "closed_at": t_closed.strftime("%Y-%m-%d %H:%M:%S") if t_closed else "",
            "room_number": str(item["room_number"]),
            "floor": item["floor"],
            "category": item["category"],
            "issue_description": item["issue_description"],
            "priority": item["priority"],
            "status": item["status"],
            "assigned_technician": item["assigned_technician"],
            "shift": item["shift"],
            "resolution_time_minutes": item["resolution_time_minutes"] or "",
            "vip_flag": item["vip_flag"],
            "notes": item["notes"]
        })

    # Deliberate Anomaly 2: Floor 3 Wi-Fi / SmartTV Evening Cluster (4 tickets between 20:00 and 22:30 on Day 2)
    floor3_wifi_events = [
        ("MNT-8304", 304, "SmartTV losing network connection and buffering on hotel portal stream", "20:15:00", 25, "Resolved"),
        ("MNT-8308", 308, "Guest cannot connect smartphone to Wi-Fi portal; authentication timeout", "20:42:00", 35, "Resolved"),
        ("MNT-8315", 315, "Guest reports complete Wi-Fi signal drop in bedroom; SSID disconnects", "21:18:00", 40, "Resolved"),
        ("MNT-8319", 319, "SmartTV offline; error code NET-04 (IP gateway unreachable)", "22:05:00", "", "InProgress")
    ]
    for tid, rnum, desc, time_str, res_min, stat in floor3_wifi_events:
        t_created = datetime.strptime(f"2026-09-22 {time_str}", "%Y-%m-%d %H:%M:%S")
        t_closed = t_created + timedelta(minutes=res_min) if res_min else None
        maintenance_tickets.append({
            "ticket_id": tid,
            "created_at": t_created.strftime("%Y-%m-%d %H:%M:%S"),
            "closed_at": t_closed.strftime("%Y-%m-%d %H:%M:%S") if t_closed else "",
            "room_number": str(rnum),
            "floor": 3,
            "category": "Wi-Fi/Network",
            "issue_description": desc,
            "priority": "High",
            "status": stat,
            "assigned_technician": "Eli R. (IT/AV Specialist)",
            "shift": "Evening",
            "resolution_time_minutes": res_min,
            "vip_flag": False,
            "notes": "Repeated DHCP leases failing on 3rd floor switch Cisco-SW03. IT vendor notified."
        })

    # Deliberate Anomaly 3: 3 Open Maintenance Tasks from Night Shift marked "WaitingParts"
    waiting_parts_events = [
        {
            "ticket_id": "MNT-8491",
            "created_at": "2026-09-23 01:20:00",
            "room_number": "Central Plant",
            "floor": 0,
            "category": "Plumbing",
            "issue_description": "Boiler #2 primary pressure relief valve leaking steam. High pressure safety cutoff engaged.",
            "priority": "Urgent",
            "status": "WaitingParts",
            "assigned_technician": "David L. (Night Duty Tech)",
            "shift": "Night",
            "resolution_time_minutes": "",
            "vip_flag": False,
            "notes": "Valve bypassed to secondary line. New 2-inch safety pressure valve ordered; delivery expected 10:30 AM."
        },
        {
            "ticket_id": "MNT-8495",
            "created_at": "2026-09-23 02:45:00",
            "room_number": "Elevator B",
            "floor": 1,
            "category": "Elevator",
            "issue_description": "Elevator B optic door safety sensor intermittent fault code E-14. Doors reopening repeatedly.",
            "priority": "High",
            "status": "WaitingParts",
            "assigned_technician": "Otis Contractor Hotline",
            "shift": "Night",
            "resolution_time_minutes": "",
            "vip_flag": False,
            "notes": "Elevator B taken Out of Service. Otis service tech scheduled for 09:00 AM with replacement optical curtain."
        },
        {
            "ticket_id": "MNT-8499",
            "created_at": "2026-09-23 04:10:00",
            "room_number": "Service Pantry 2",
            "floor": 2,
            "category": "Equipment",
            "issue_description": "Commercial ice machine compressor locked rotor, tripping 20A breaker in pantry.",
            "priority": "Medium",
            "status": "WaitingParts",
            "assigned_technician": "David L. (Night Duty Tech)",
            "shift": "Night",
            "resolution_time_minutes": "",
            "vip_flag": False,
            "notes": "Unit powered down. Heavy-duty 45uF run capacitor required from central workshop stock."
        }
    ]
    for wpe in waiting_parts_events:
        maintenance_tickets.append({
            "ticket_id": wpe["ticket_id"],
            "created_at": wpe["created_at"],
            "closed_at": "",
            "room_number": wpe["room_number"],
            "floor": wpe["floor"],
            "category": wpe["category"],
            "issue_description": wpe["issue_description"],
            "priority": wpe["priority"],
            "status": wpe["status"],
            "assigned_technician": wpe["assigned_technician"],
            "shift": wpe["shift"],
            "resolution_time_minutes": "",
            "vip_flag": wpe["vip_flag"],
            "notes": wpe["notes"]
        })

    # Background realistic maintenance tickets across 48h
    baseline_maintenance = [
        ("MNT-7201", 104, 1, "Plumbing", "Slow drain in shower basin", "Medium", "Resolved", 45, "Morning", "2026-09-21 09:15:00"),
        ("MNT-7202", 210, 2, "Electrical", "Desk reading lamp flickers", "Low", "Resolved", 20, "Morning", "2026-09-21 11:30:00"),
        ("MNT-7203", 502, 5, "Locks", "Keycard reader red flash, battery low", "High", "Resolved", 15, "Evening", "2026-09-21 16:40:00"),
        ("MNT-7204", 118, 1, "HVAC", "Thermostat display blank", "Medium", "Resolved", 35, "Evening", "2026-09-21 18:20:00"),
        ("MNT-7205", 205, 2, "Plumbing", "Water leak from ceiling above bathroom - pipe riser joint failure", "Urgent", "InProgress", "", "Night", "2026-09-23 02:15:00"),
        ("MNT-7206", 312, 3, "Equipment", "In-room safe error CODE", "Medium", "Resolved", 25, "Morning", "2026-09-22 10:10:00"),
        ("MNT-7207", 405, 4, "Plumbing", "Toilet flush valve running continuously", "Medium", "Resolved", 50, "Morning", "2026-09-22 13:45:00"),
        ("MNT-7208", 516, 5, "Electrical", "Balcony light not turning off with master switch", "Low", "Resolved", 30, "Evening", "2026-09-22 17:15:00")
    ]
    for tid, rnum, fl, cat, desc, pri, stat, res_min, shft, created_str in baseline_maintenance:
        t_cr = datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S")
        t_cl = t_cr + timedelta(minutes=res_min) if res_min else None
        maintenance_tickets.append({
            "ticket_id": tid,
            "created_at": created_str,
            "closed_at": t_cl.strftime("%Y-%m-%d %H:%M:%S") if t_cl else "",
            "room_number": str(rnum),
            "floor": fl,
            "category": cat,
            "issue_description": desc,
            "priority": pri,
            "status": stat,
            "assigned_technician": "Team Duty Tech",
            "shift": shft,
            "resolution_time_minutes": res_min,
            "vip_flag": False,
            "notes": "Routine maintenance task completed." if stat == "Resolved" else "Emergency pipe shutoff active."
        })

    # -------------------------------------------------------------
    # 2. HOUSEKEEPING MODULE
    # -------------------------------------------------------------
    housekeeping_records = [
        # Room 412 VIP stayover touchpoints
        {
            "task_id": "HK-9412-1",
            "timestamp": "2026-09-21 14:15:00",
            "room_number": "412",
            "floor": 4,
            "room_status": "Clean",
            "guest_status": "VIP - Stayover",
            "task_type": "VIP Refresh",
            "housekeeper_name": "Elena S.",
            "shift": "Morning",
            "notes": "VIP amenities refreshed. Guest asked about cooling in the room."
        },
        {
            "task_id": "HK-9412-2",
            "timestamp": "2026-09-22 14:30:00",
            "room_number": "412",
            "floor": 4,
            "room_status": "Clean",
            "guest_status": "VIP - Stayover",
            "task_type": "VIP Refresh",
            "housekeeper_name": "Elena S.",
            "shift": "Morning",
            "notes": "Guest left handwritten note: 'Still too hot in bedroom. Please bring portable fan and ice bucket'."
        },
        {
            "task_id": "HK-9412-3",
            "timestamp": "2026-09-22 20:00:00",
            "room_number": "412",
            "floor": 4,
            "room_status": "Inspected",
            "guest_status": "VIP - Stayover",
            "task_type": "TurnDown & Fan Delivery",
            "housekeeper_name": "Miriam T.",
            "shift": "Evening",
            "notes": "Delivered high-power standing fan and two extra ice buckets. Guest visibly frustrated."
        },
        # Room 205 Emergency Flood Cleanup
        {
            "task_id": "HK-9205-EMERG",
            "timestamp": "2026-09-23 02:40:00",
            "room_number": "205",
            "floor": 2,
            "room_status": "OutOfOrder",
            "guest_status": "Relocated (Was Stayover)",
            "task_type": "Water Extraction / OOO Prep",
            "housekeeper_name": "Night HK Porter Victor",
            "shift": "Night",
            "notes": "Wet vacuum extraction performed. Carpet fans deployed. Room blocked Out of Order."
        },
        # Room 218 Upgrade Preparation
        {
            "task_id": "HK-9218-MOVE",
            "timestamp": "2026-09-23 02:50:00",
            "room_number": "218",
            "floor": 2,
            "room_status": "Inspected",
            "guest_status": "VIP Relocation",
            "task_type": "Emergency VIP Arrival Prep",
            "housekeeper_name": "Night HK Porter Victor",
            "shift": "Night",
            "notes": "Prepared Executive Suite 218 with fresh fruit basket, robe/slippers for moved guest from 205."
        }
    ]

    # Baseline Housekeeping tasks for other rooms
    for fl in range(1, 6):
        for rm in [1, 2, 6, 10, 14]:
            r_num = fl * 100 + rm
            if r_num in (412, 205, 218):
                continue
            housekeeping_records.append({
                "task_id": f"HK-{r_num}-STD",
                "timestamp": f"2026-09-22 {10 + (rm % 4):02d}:{15 + (fl * 5):02d}:00",
                "room_number": str(r_num),
                "floor": fl,
                "room_status": "Clean",
                "guest_status": "Stayover" if rm % 2 == 0 else "Checkout Clean",
                "task_type": "Daily Service",
                "housekeeper_name": f"Attendant Floor {fl}",
                "shift": "Morning",
                "notes": "Standard cleaning completed according to SmartButler checklist."
            })

    # -------------------------------------------------------------
    # 3. LOGBOOK MODULE (Duty Manager / Night Manager / FO Shift Logs)
    # -------------------------------------------------------------
    # Deliberate Anomaly 4: 2 Critical Incidents with Guest Compensation Notes
    logbook_records = [
        # Critical Incident 1: Room 412 VIP Escalation & Compensation
        {
            "log_id": "LOG-20260922-EV01",
            "timestamp": "2026-09-22 23:40:00",
            "shift": "Evening Handover",
            "author_role": "Duty Manager",
            "author_name": "Tomer Sharon",
            "category": "VIP Escalation & Compensation",
            "room_number": "412",
            "vip_guest_name": "Dr. E. Ben-Ari (Diamond Tier VIP)",
            "incident_description": "VIP Guest Dr. Ben-Ari confronted Front Desk in person. HVAC system failed for the 3rd time in 36 hours. Room temperature at 26.5C. Guest stated this ruined his stay before an important medical conference lecture tomorrow. Stated that previous technicians made promises that didn't hold.",
            "compensation_offered": "Complimentary gourmet dinner at Chef Restaurant (450 ILS voucher) + 20% room rate credit on master folio (620 ILS). Free late checkout 16:00.",
            "compensation_amount_ils": 1070.0,
            "escalated_to_gm": True,
            "action_required": "URGENT for Morning Standup: Chief Engineer must personally inspect unit with chiller vendor at 08:30. GM to greet guest at breakfast."
        },
        # Critical Incident 2: Room 205 Ceiling Water Leak & Emergency Relocation
        {
            "log_id": "LOG-20260923-NG01",
            "timestamp": "2026-09-23 03:15:00",
            "shift": "Night Shift Handover",
            "author_role": "Night Manager",
            "author_name": "Shani Mor",
            "category": "Facility Emergency & Room Move",
            "room_number": "205",
            "vip_guest_name": "Mr. & Mrs. R. Cohen",
            "incident_description": "At 02:15 AM guest called panic-stricken due to heavy water cascade through false ceiling above bathtub. Night Tech isolated riser #2. Guests were awake in sleepwear. Handled immediate relocation to Executive Suite 218. Night Porter assisted with baggage. Clean dry clothes provided from laundry emergency stock.",
            "compensation_offered": "Complimentary upgrade to Executive Suite 218 for remainder of stay + 2x Spa Passes + Complimentary Breakfast & mini-bar waived (850 ILS total courtesy package).",
            "compensation_amount_ils": 850.0,
            "escalated_to_gm": True,
            "action_required": "Engineering to repair pipe joint riser 2 by 10:00 AM before pressure restored. Room 205 taken OOO for dehumidification."
        },
        # Standard Logbook Shift Notes
        {
            "log_id": "LOG-20260921-MR01",
            "timestamp": "2026-09-21 15:30:00",
            "shift": "Morning Handover",
            "author_role": "Duty Manager",
            "author_name": "Danielle Levi",
            "category": "Operations Summary",
            "room_number": "Lobby",
            "vip_guest_name": "General",
            "incident_description": "Smooth morning operations. Occupancy at 88%. Corporate group BioMed check-in completed 42 rooms without delays.",
            "compensation_offered": "None",
            "compensation_amount_ils": 0.0,
            "escalated_to_gm": False,
            "action_required": "Prepare VIP arrival gifts for 4th floor Diamond members."
        },
        {
            "log_id": "LOG-20260922-NG01",
            "timestamp": "2026-09-23 06:45:00",
            "shift": "Night to Morning Standup",
            "author_role": "Night Manager",
            "author_name": "Shani Mor",
            "category": "Morning Standup Briefing Handover",
            "room_number": "Hotel Wide",
            "vip_guest_name": "Shift Handover Summary",
            "incident_description": "Challenging night shift. Water leak in 205 contained; 3 open maintenance tasks pending critical spare parts (Boiler 2 valve, Elevator B door sensor, Ice maker capacitor). 3rd floor Wi-Fi cluster resolved partially last night, needs IT morning audit.",
            "compensation_offered": "Shift summary note (Total 1,920 ILS allocated to Rooms 412 & 205)",
            "compensation_amount_ils": 0.0,
            "escalated_to_gm": True,
            "action_required": "Engineering, HK, and FO heads must address Room 412 VIP, Room 205 flood restoration, and the 3 WaitingParts tickets immediately."
        }
    ]

    # Save Maintenance logs (JSON & CSV)
    m_json_path = os.path.join(DATA_DIR, "smartbutler_maintenance_48h.json")
    m_csv_path = os.path.join(DATA_DIR, "smartbutler_maintenance_48h.csv")
    with open(m_json_path, "w", encoding="utf-8") as f:
        json.dump(maintenance_tickets, f, indent=2, ensure_ascii=False)
    with open(m_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=maintenance_tickets[0].keys())
        writer.writeheader()
        writer.writerows(maintenance_tickets)

    # Save Housekeeping logs (JSON & CSV)
    hk_json_path = os.path.join(DATA_DIR, "smartbutler_housekeeping_48h.json")
    hk_csv_path = os.path.join(DATA_DIR, "smartbutler_housekeeping_48h.csv")
    with open(hk_json_path, "w", encoding="utf-8") as f:
        json.dump(housekeeping_records, f, indent=2, ensure_ascii=False)
    with open(hk_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=housekeeping_records[0].keys())
        writer.writeheader()
        writer.writerows(housekeeping_records)

    # Save Logbook logs (JSON & CSV)
    log_json_path = os.path.join(DATA_DIR, "smartbutler_logbook_48h.json")
    log_csv_path = os.path.join(DATA_DIR, "smartbutler_logbook_48h.csv")
    with open(log_json_path, "w", encoding="utf-8") as f:
        json.dump(logbook_records, f, indent=2, ensure_ascii=False)
    with open(log_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=logbook_records[0].keys())
        writer.writeheader()
        writer.writerows(logbook_records)

    print(f"[OK] Generated SmartButler 48h operational logs:")
    print(f"  - Maintenance: {len(maintenance_tickets)} records -> {m_json_path}, {m_csv_path}")
    print(f"  - Housekeeping: {len(housekeeping_records)} records -> {hk_json_path}, {hk_csv_path}")
    print(f"  - Logbook: {len(logbook_records)} records -> {log_json_path}, {log_csv_path}")

if __name__ == "__main__":
    generate_mock_data()
