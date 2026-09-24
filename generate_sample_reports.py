"""
Generate Sample Operational Uploads for SmartButler LiveOps Digest.
Creates sample files in data/uploads/ covering PDF, Word (.docx), and Excel (.xlsx):
1. data/uploads/shift_report_night.pdf - Operational Night Shift Handover Brief
2. data/uploads/duty_manager_handover.docx - Word report with Duty Manager Logbook & Guest Compensations
3. data/uploads/maintenance_work_orders.xlsx - Excel workbook with open maintenance tickets & WaitingParts
"""

import os
import sys
from datetime import datetime
import pandas as pd
import docx
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Ensure console utf-8
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "data", "uploads")

def ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)

def generate_pdf_report():
    pdf_path = os.path.join(UPLOAD_DIR, "shift_report_night.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "SmartButler - Night Shift Operational Summary (2026-09-23)")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, "Generated: 2026-09-23 06:45:00 | Facility: SmartButler Grand Hotel | Shift: Night")
    c.line(50, height - 75, width - 50, height - 75)

    y = height - 100
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Section 1: Critical Maintenance Work Orders")
    y -= 20

    c.setFont("Helvetica", 10)
    lines = [
        "MNT-7412-3 | Room 412 (VIP) | Category: HVAC | Status: WaitingParts | Priority: Urgent",
        "  Issue: HVAC cooling compressor clutch failure. Room warm at 26C. Guest VIP Dr. Ben-Ari irritated.",
        "  Assigned: David L. (Night Tech) | Notes: Fan provided. WaitingParts Chiller compressor valve.",
        "",
        "MNT-801 | Room 205 | Category: Plumbing | Status: WaitingParts | Priority: Urgent",
        "  Issue: Pipe burst in bathroom ceiling. Flooding into corridor. Room taken out of order.",
        "  Assigned: Yossi C. | Notes: WaitingParts replacement 1/2-inch copper pipe joiner.",
        "",
        "MNT-802 | Room 304 | Category: Electrical | Status: WaitingParts | Priority: High",
        "  Issue: Main breaker tripping repeatedly under load. Suspected coil degradation.",
        "  Assigned: Ahmed K. | Notes: WaitingParts 40A Schneider breaker module.",
        "",
        "MNT-803 | Boiler Room | Category: Plumbing | Status: WaitingParts | Priority: Urgent",
        "  Issue: Secondary boiler circulation pump seal leaking hot water.",
        "  Assigned: David L. | Notes: WaitingParts mechanical pump seal model Grundfos B2.",
    ]

    for line in lines:
        c.drawString(50, y, line)
        y -= 15

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Section 2: Duty Manager Incident Logbook & Compensations")
    y -= 20

    c.setFont("Helvetica", 10)
    log_lines = [
        "LOG-501 | Room 412 | Guest: Dr. E. Ben-Ari (VIP) | Compensation: 1,200 ILS (Spa & Dinner Credits)",
        "  Incident: Third AC failure in 36 hours. Duty Manager personal intervention and executive apology.",
        "",
        "LOG-502 | Room 205 | Guest: Mr. Sharon Cohen | Compensation: 850 ILS (Room Upgrade + Wine)",
        "  Incident: Severe ceiling leak and carpet water damage. Emergency guest relocation to Suite 601.",
        "",
        "LOG-503 | Floor 3 | Guest: Multi-room guests | Compensation: 0 ILS",
        "  Incident: Wi-Fi gateway packet drops on floor 3 access point. Escalated to telecom provider.",
    ]

    for line in log_lines:
        c.drawString(50, y, line)
        y -= 15

    c.save()
    print(f"Generated PDF report: {pdf_path}")

def generate_docx_report():
    docx_path = os.path.join(UPLOAD_DIR, "duty_manager_handover.docx")
    doc = docx.Document()

    doc.add_heading("SmartButler® - Duty Manager Handover Report", level=1)
    doc.add_paragraph("Period: Past 24 Hours (Night & Evening Handover) | Author: Ronen S., Night Duty Manager")

    doc.add_heading("אירועי יומן מנהל תורן ופיצוי אורחים", level=2)
    
    # Table for Logbook entries
    table = doc.add_table(rows=1, cols=6)
    table.style = "Table Grid"
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "מס' יומן"
    hdr_cells[1].text = "מועד ומשמרת"
    hdr_cells[2].text = "חדר / מיקום"
    hdr_cells[3].text = "אורח אח\"מ"
    hdr_cells[4].text = "תיאור התקרית"
    hdr_cells[5].text = "עלות (₪)"

    logs_data = [
        ("LOG-901", "2026-09-23 00:15:00", "412", "ד\"ר א. בן-ארי", "תקלת מיזוג אוויר חוזרת ונשנית - פעם שלישית. האורח זעם וביקש שיחה עם מנכ\"ל המלון.", "1200"),
        ("LOG-902", "2026-09-22 23:40:00", "205", "שרון כהן", "פיצוץ צינור מים בתקרת חדר הרחצה והצפה. בוצעה העברה לחדר 601 ושדרוג.", "850"),
        ("LOG-903", "2026-09-22 21:30:00", "קומה 3", "אורחי קומה 3", "תקלות ניתוקי רשת אלחוטית וטלוויזיות חכמות בקומה 3 בין 20:00 ל-22:30.", "0"),
    ]

    for lid, ts, rm, vip, desc, cost in logs_data:
        row_cells = table.add_row().cells
        row_cells[0].text = lid
        row_cells[1].text = ts
        row_cells[2].text = rm
        row_cells[3].text = vip
        row_cells[4].text = desc
        row_cells[5].text = cost

    doc.add_heading("קריאות אחזקה דחופות במשמרת לילה", level=2)
    maint_table = doc.add_table(rows=1, cols=6)
    maint_table.style = "Table Grid"
    m_hdr = maint_table.rows[0].cells
    m_hdr[0].text = "מספר קריאה"
    m_hdr[1].text = "חדר"
    m_hdr[2].text = "סיווג"
    m_hdr[3].text = "תיאור"
    m_hdr[4].text = "סטטוס"
    m_hdr[5].text = "חלק חסר"

    m_data = [
        ("MNT-910", "412", "מיזוג אוויר", "מדחס מיזוג אוויר כשל. נמסר מאוורר זמני לאורח.", "WaitingParts", "שסתום ומצמד מדחס"),
        ("MNT-911", "205", "אינסטלציה", "פיצוץ צנרת מים מעל תקרת גבס חדר רחצה.", "WaitingParts", "מחבר צנרת נחושת חצי צול"),
        ("MNT-912", "דוד מרכזי", "מערכות מרכזיות", "משאבת סחרור דוד 2 דולפת מים חמים.", "WaitingParts", "אטם מכני גרונדפוס"),
    ]

    for tid, rm, cat, desc, stat, note in m_data:
        r = maint_table.add_row().cells
        r[0].text = tid
        r[1].text = rm
        r[2].text = cat
        r[3].text = desc
        r[4].text = stat
        r[5].text = note

    doc.save(docx_path)
    print(f"Generated DOCX report: {docx_path}")

def generate_excel_report():
    xlsx_path = os.path.join(UPLOAD_DIR, "maintenance_work_orders.xlsx")

    # Maintenance Sheet
    maintenance_records = [
        {
            "ticket_id": "MNT-7412-3",
            "created_at": "2026-09-23 00:05:00",
            "room_number": "412",
            "floor": 4,
            "category": "מיזוג אוויר",
            "issue_description": "כשל מדחס יחידת מיזוג אוויר בחדר 412 (אורח אח\"מ)",
            "priority": "Urgent",
            "status": "WaitingParts",
            "assigned_technician": "דוד ל. (טכנאי לילה)",
            "shift": "Night",
            "notes": "ממתין לשסתום לחץ ומצמד. צפי הגעת ספק 10:30."
        },
        {
            "ticket_id": "MNT-801",
            "created_at": "2026-09-22 23:45:00",
            "room_number": "205",
            "floor": 2,
            "category": "אינסטלציה",
            "issue_description": "נזילה פעילה ופיצוץ צינור אספקת מים קומה 2",
            "priority": "Urgent",
            "status": "WaitingParts",
            "assigned_technician": "יוסי כ. (אינסטלטור)",
            "shift": "Night",
            "notes": "ממתין למחבר צנרת נחושת 1/2 אינץ'. מים סגורים לחדר."
        },
        {
            "ticket_id": "MNT-802",
            "created_at": "2026-09-23 01:20:00",
            "room_number": "304",
            "floor": 3,
            "category": "חשמל",
            "issue_description": "מפסק ראשי קופץ בלוח חדר 304 תחת עומס",
            "priority": "High",
            "status": "WaitingParts",
            "assigned_technician": "אחמד ק. (חשמלאי)",
            "shift": "Night",
            "notes": "ממתין למאמ\"ת 40 אמפר שניידר אלקטריק."
        },
        {
            "ticket_id": "MNT-803",
            "created_at": "2026-09-23 02:40:00",
            "room_number": "חדר משאבות",
            "floor": 0,
            "category": "מערכות מרכזיות",
            "issue_description": "דליפת מים חמים באטם משאבת סחרור ראשית דוד 2",
            "priority": "Urgent",
            "status": "WaitingParts",
            "assigned_technician": "דוד ל. (טכנאי לילה)",
            "shift": "Night",
            "notes": "ממתין לאטם מכני Grundfos B2. משאבת גיבוי הופעלה."
        },
        {
            "ticket_id": "MNT-804",
            "created_at": "2026-09-22 20:30:00",
            "room_number": "301",
            "floor": 3,
            "category": "תקשורת",
            "issue_description": "ניתוק רשת אלחוטית וטלוויזיה חכמה",
            "priority": "Medium",
            "status": "Resolved",
            "assigned_technician": "אבי ר.",
            "shift": "Evening",
            "notes": "אותחל מתג תקשורת ארוניית קומה 3."
        }
    ]

    # Logbook Sheet
    logbook_records = [
        {
            "log_id": "LOG-880",
            "timestamp": "2026-09-23 00:20:00",
            "room_number": "412",
            "vip_guest_name": "ד\"ר א. בן-ארי",
            "incident_description": "תקלת מיזוג אוויר חוזרת - הוענק שובר ארוחת ערב וטיפול ספא",
            "compensation_offered": "ארוחת ערב זוגית + זיכוי 1,200 ₪",
            "compensation_amount_ils": 1200.0,
            "shift": "Night",
            "author_name": "רונן ש. (מנהל תורן)"
        },
        {
            "log_id": "LOG-881",
            "timestamp": "2026-09-22 23:55:00",
            "room_number": "205",
            "vip_guest_name": "שרון כהן",
            "incident_description": "נזילה בתקרה - שודרג לסוויטה 601 וניתן בקבוק יין",
            "compensation_offered": "שדרוג סוויטה + יין בשווי 850 ₪",
            "compensation_amount_ils": 850.0,
            "shift": "Night",
            "author_name": "רונן ש. (מנהל תורן)"
        }
    ]

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        pd.DataFrame(maintenance_records).to_excel(writer, sheet_name="Maintenance", index=False)
        pd.DataFrame(logbook_records).to_excel(writer, sheet_name="Logbook", index=False)

    print(f"Generated Excel workbook: {xlsx_path}")

def main():
    ensure_upload_dir()
    print("Generating sample operational upload reports...")
    generate_pdf_report()
    generate_docx_report()
    generate_excel_report()
    print("Sample report generation complete!")

if __name__ == "__main__":
    main()
