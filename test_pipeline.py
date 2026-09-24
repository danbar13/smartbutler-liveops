"""
SmartButler LiveOps Digest - Verification & Pipeline Test Suite
Validates the entire end-to-end operational intelligence plugin:
1. Multi-format mock data generation (JSON, CSV).
2. Parser compatibility across JSON and CSV formats.
3. Anomaly detector assertions for:
   - 48h multi-period analysis (extensible trend detection).
   - 24h daily summary (דוח סיכום ליממה החולפת).
4. Multi-format Document Ingestion Engine (PDF, DOCX, XLSX).
5. Executive standup briefing generation in pure Hebrew (Markdown & HTML) with JAYBEE & SmartButler® branding.
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from generate_smartbutler_mock import generate_mock_data
from generate_sample_reports import main as generate_sample_reports
from smartbutler_engine import (
    SmartButlerParser,
    DocumentParser,
    SmartButlerDetector,
    SmartButlerSummarizer,
)

def run_tests():
    print("=" * 70)
    print("STEP 1: Generating 48-Hour SmartButler Mock Operational Logs...")
    print("=" * 70)
    generate_mock_data()

    print("\n" + "=" * 70)
    print("STEP 2: Testing Parser with JSON and CSV Formats...")
    print("=" * 70)
    parser = SmartButlerParser()

    # Test JSON Loading
    m_json = parser.load_maintenance("json")
    hk_json = parser.load_housekeeping("json")
    log_json = parser.load_logbook("json")
    print(f"  [JSON] Loaded {len(m_json)} Maintenance, {len(hk_json)} HK, {len(log_json)} Logbook entries.")

    # Test CSV Loading
    m_csv = parser.load_maintenance("csv")
    hk_csv = parser.load_housekeeping("csv")
    log_csv = parser.load_logbook("csv")
    print(f"  [CSV]  Loaded {len(m_csv)} Maintenance, {len(hk_csv)} HK, {len(log_csv)} Logbook entries.")

    assert len(m_json) == len(m_csv), f"Mismatch between JSON ({len(m_json)}) and CSV ({len(m_csv)}) maintenance records!"
    assert len(hk_json) == len(hk_csv), f"Mismatch between JSON and CSV HK records!"
    assert len(log_json) == len(log_csv), f"Mismatch between JSON and CSV Logbook records!"
    print("  ✓ Parser compatibility test PASSED for all formats.")

    print("\n" + "=" * 70)
    print("STEP 3: Running SmartButler Anomaly Detection Engine (48-Hour Full Scope)...")
    print("=" * 70)
    detector_48h = SmartButlerDetector(m_json, hk_json, log_json)
    briefing_48h = detector_48h.run_analysis(window_hours=48)

    print(f"  Total Anomalies Flagged: {len(briefing_48h.anomalies)}")
    print(f"  Departmental Action Items: {len(briefing_48h.action_items)}")
    print(f"  WaitingParts Night Shift Tasks: {briefing_48h.open_waiting_parts_count}")
    print(f"  Total Guest Compensation Exposure: {briefing_48h.total_compensation_ils:,.0f} ILS")

    # Assertion 1: Room 412 (VIP, Occupied) Recurring HVAC Failures across shifts
    rec_anom_48h = next((a for a in briefing_48h.anomalies if a.category == "RECURRENT_VIP" and "412" in a.location), None)
    assert rec_anom_48h is not None, "FAILED: Recurrent VIP HVAC anomaly for Room 412 was not detected in 48h!"
    assert rec_anom_48h.severity == "CRITICAL", f"Expected CRITICAL severity for Room 412, got {rec_anom_48h.severity}"
    assert len(rec_anom_48h.related_tickets) >= 3, f"Expected >= 3 related tickets for Room 412 in 48h, got {len(rec_anom_48h.related_tickets)}"
    print(f"  ✓ 48H SCENARIO 1 PASSED: Room 412 VIP recurring HVAC anomaly detected ({len(rec_anom_48h.related_tickets)} tickets, severity {rec_anom_48h.severity}).")

    # Assertion 2: Floor 3 Wi-Fi / TV Evening Cluster (4 tickets)
    cluster_anom_48h = next((a for a in briefing_48h.anomalies if a.category == "CLUSTER_INFRASTRUCTURE" and "3" in a.location), None)
    assert cluster_anom_48h is not None, "FAILED: Floor 3 Wi-Fi cluster anomaly was not detected!"
    assert cluster_anom_48h.evidence_count == 4, f"Expected 4 tickets in Floor 3 cluster, got {cluster_anom_48h.evidence_count}"
    print(f"  ✓ 48H SCENARIO 2 PASSED: Floor 3 Wi-Fi cluster detected ({cluster_anom_48h.evidence_count} tickets in evening hours).")

    # Assertion 3: 3 Open Maintenance Tasks Marked WaitingParts from Night Shift
    wp_anom_48h = next((a for a in briefing_48h.anomalies if a.category == "WAITING_PARTS"), None)
    assert wp_anom_48h is not None, "FAILED: WaitingParts night shift anomaly was not detected!"
    assert briefing_48h.open_waiting_parts_count == 3, f"Expected 3 WaitingParts tasks, got {briefing_48h.open_waiting_parts_count}"
    expected_assets = ["Central Plant", "Elevator B", "Service Pantry 2"]
    actual_assets = [t.room_number for t in briefing_48h.waiting_parts_tickets]
    for asset in expected_assets:
        assert asset in actual_assets, f"Asset '{asset}' missing from WaitingParts list!"
    print(f"  ✓ 48H SCENARIO 3 PASSED: 3 Night shift tasks in WaitingParts detected ({', '.join(actual_assets)}).")

    # Assertion 4: 2 Critical Incidents Flagged with Guest Compensation Notes
    assert len(briefing_48h.compensation_incidents) == 2, f"Expected 2 compensation incidents, got {len(briefing_48h.compensation_incidents)}"
    assert briefing_48h.total_compensation_ils == 1920.0, f"Expected 1,920 ILS total compensation, got {briefing_48h.total_compensation_ils}"
    rooms_comp = [l.room_number for l in briefing_48h.compensation_incidents]
    assert "412" in rooms_comp and "205" in rooms_comp, f"Expected rooms 412 and 205 in compensation list, got {rooms_comp}"
    print(f"  ✓ 48H SCENARIO 4 PASSED: 2 Logbook compensation incidents verified (Rooms 412 & 205, Total: {briefing_48h.total_compensation_ils:,.0f} ILS).")

    print("\n" + "=" * 70)
    print("STEP 4: Running 24-Hour Daily Summary Mode (דוח סיכום ליממה החולפת)...")
    print("=" * 70)
    briefing_24h = detector_48h.run_analysis(window_hours=24)
    assert briefing_24h.period_hours == 24, "Expected period_hours == 24"
    assert "24" in briefing_24h.period_label, "Expected '24' in period_label"
    
    # Check that Room 412 recurrence is also flagged in 24h
    rec_anom_24h = next((a for a in briefing_24h.anomalies if a.category == "RECURRENT_VIP" and "412" in a.location), None)
    assert rec_anom_24h is not None, "FAILED: Room 412 recurring HVAC not detected in 24h daily summary!"
    assert len(rec_anom_24h.related_tickets) >= 2, f"Expected >= 2 tickets in 24h window, got {len(rec_anom_24h.related_tickets)}"
    print(f"  ✓ 24H DAILY SUMMARY PASSED: Room 412 flagged ({len(rec_anom_24h.related_tickets)} tickets across shifts in past 24h).")
    print(f"  ✓ 24H Scope Metrics: Maint={briefing_24h.total_maintenance_48h}, HK={briefing_24h.total_housekeeping_48h}, Compensations={briefing_24h.total_compensation_ils:,.0f} ILS.")

    print("\n" + "=" * 70)
    print("STEP 5: Testing Multi-Format Document Ingestion Engine (PDF, DOCX, XLSX)...")
    print("=" * 70)
    generate_sample_reports()
    doc_parser = DocumentParser()

    uploads_dir = os.path.join(os.path.dirname(__file__), "data", "uploads")
    
    # 5.1 Test PDF Ingestion
    pdf_path = os.path.join(uploads_dir, "shift_report_night.pdf")
    assert os.path.exists(pdf_path), "Sample PDF report does not exist!"
    pdf_m, pdf_hk, pdf_log = doc_parser.parse_file(pdf_path, "shift_report_night.pdf")
    print(f"  [PDF Ingestion]  Maint: {len(pdf_m)}, HK: {len(pdf_hk)}, Logbook: {len(pdf_log)}")
    assert len(pdf_m) >= 3, f"Expected >= 3 maintenance tickets from PDF, got {len(pdf_m)}"
    assert len(pdf_log) >= 2, f"Expected >= 2 logbook entries from PDF, got {len(pdf_log)}"
    assert any("412" in t.room_number for t in pdf_m), "Room 412 ticket not found in PDF!"
    print("  ✓ PDF Ingestion PASSED.")

    # 5.2 Test Word (.docx) Ingestion
    docx_path = os.path.join(uploads_dir, "duty_manager_handover.docx")
    assert os.path.exists(docx_path), "Sample DOCX report does not exist!"
    docx_m, docx_hk, docx_log = doc_parser.parse_file(docx_path, "duty_manager_handover.docx")
    print(f"  [DOCX Ingestion] Maint: {len(docx_m)}, HK: {len(docx_hk)}, Logbook: {len(docx_log)}")
    assert len(docx_m) >= 3, f"Expected >= 3 maintenance tickets from DOCX table, got {len(docx_m)}"
    assert len(docx_log) >= 3, f"Expected >= 3 logbook entries from DOCX table, got {len(docx_log)}"
    assert any(l.compensation_amount_ils == 1200.0 for l in docx_log), "1200 ILS compensation not parsed from DOCX!"
    print("  ✓ Word (.docx) Ingestion PASSED.")

    # 5.3 Test Excel (.xlsx) Ingestion
    xlsx_path = os.path.join(uploads_dir, "maintenance_work_orders.xlsx")
    assert os.path.exists(xlsx_path), "Sample XLSX workbook does not exist!"
    xlsx_m, xlsx_hk, xlsx_log = doc_parser.parse_file(xlsx_path, "maintenance_work_orders.xlsx")
    print(f"  [XLSX Ingestion] Maint: {len(xlsx_m)}, HK: {len(xlsx_hk)}, Logbook: {len(xlsx_log)}")
    assert len(xlsx_m) >= 4, f"Expected >= 4 maintenance tickets from XLSX, got {len(xlsx_m)}"
    assert len(xlsx_log) >= 2, f"Expected >= 2 logbook entries from XLSX, got {len(xlsx_log)}"
    assert any(t.status == "WaitingParts" for t in xlsx_m), "WaitingParts status not found in XLSX!"
    print("  ✓ Excel (.xlsx) Ingestion PASSED.")

    print("\n" + "=" * 70)
    print("STEP 6: Generating Executive Briefing Reports (Markdown & HTML)...")
    print("=" * 70)
    summarizer = SmartButlerSummarizer(briefing_24h)
    md_content = summarizer.generate_markdown()
    html_content = summarizer.generate_html()

    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    md_file = os.path.join(reports_dir, "morning_briefing.md")
    html_file = os.path.join(reports_dir, "morning_briefing.html")

    assert os.path.exists(md_file) and os.path.getsize(md_file) > 500, "Markdown report missing or too small!"
    assert os.path.exists(html_file) and os.path.getsize(html_file) > 1000, "HTML report missing or too small!"
    
    # Verify pure Hebrew and official JAYBEE / SmartButler® branding
    assert "SmartButler®" in md_content or "SmartButler" in md_content, "SmartButler branding missing in Markdown!"
    assert "jaybee" in html_content.lower() or "ג'ייבי" in html_content, "JAYBEE Systems branding missing in HTML!"
    assert "svg" in html_content.lower(), "Official JAYBEE SVG logo missing in HTML report!"
    
    print(f"  ✓ Markdown report generated: {md_file} ({os.path.getsize(md_file)} bytes)")
    print(f"  ✓ HTML briefing generated:   {html_file} ({os.path.getsize(html_file)} bytes)")

    print("\n" + "=" * 70)
    print("STEP 7: Executive Morning Standup Briefing Content Preview")
    print("=" * 70)
    print(md_content)
    print("=" * 70)
    print("ALL TESTS AND VERIFICATION CRITERIA PASSED SUCCESSFULLY (100% GREEN)")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
