"""
Generate synthetic test logs for SmartButler LiveOps Digest.
Creates sample files (CSV, JSON) mirroring the structure of SmartButler "Log Report - Providers".
"""

import os
import json
import csv

def generate_samples(output_dir: str = "reports"):
    os.makedirs(output_dir, exist_ok=True)

    # 1. JSON Sample
    json_data = {
        "report_title": "Log Report - Providers",
        "site_name": "Grand Hotel",
        "date_range": "01/Sep/2026 - 23/Sep/2026 (Current Month)",
        "total_tickets": 4,
        "overall_success_rate": 25.0,
        "avg_duration_str": "130:47",
        "avg_duration_minutes": 7847,
        "total_time_str": "523:08",
        "total_time_minutes": 31388,
        "departments": [
            {
                "department": "Housekeeping",
                "total_tickets": 2,
                "avg_duration_str": "190:38",
                "avg_duration_minutes": 11438,
                "total_time_str": "381:15",
                "total_time_minutes": 22875,
                "success_rate": 0.0
            },
            {
                "department": "Maintenance",
                "total_tickets": 1,
                "avg_duration_str": "141:44",
                "avg_duration_minutes": 8504,
                "total_time_str": "141:44",
                "total_time_minutes": 8504,
                "success_rate": 0.0
            },
            {
                "department": "Reception",
                "total_tickets": 1,
                "avg_duration_str": "00:09",
                "avg_duration_minutes": 9,
                "total_time_str": "00:09",
                "total_time_minutes": 9,
                "success_rate": 100.0
            }
        ],
        "tickets": [
            {
                "department": "Housekeeping",
                "task_category": "Cleaning - Shower",
                "received_at": "15/Sep 17:57",
                "creator": "Roman (1)",
                "location": "246",
                "description": "Cleaning - Shower",
                "provided_at": "N/A",
                "duration_str": "N/A",
                "duration_minutes": None,
                "resolver": "-",
                "standard_str": "00:30",
                "standard_minutes": 30,
                "sla_met": False,
                "sla_breach_ratio": 999.0
            },
            {
                "department": "Housekeeping",
                "task_category": "Towel Hand",
                "received_at": "15/Sep 19:24",
                "creator": "Roman (1)",
                "location": "602",
                "description": "Towel Hand (yeşil)",
                "provided_at": "N/A",
                "duration_str": "N/A",
                "duration_minutes": None,
                "resolver": "yeşil",
                "standard_str": "00:15",
                "standard_minutes": 15,
                "sla_met": False,
                "sla_breach_ratio": 999.0
            },
            {
                "department": "Maintenance",
                "task_category": "AC not working",
                "received_at": "09/Sep 20:08",
                "creator": "Roman (1)",
                "location": "246",
                "description": "AC not working (Room 246 cooling malfunction)",
                "provided_at": "15/Sep 17:52",
                "duration_str": "141:44",
                "duration_minutes": 8504,
                "resolver": "Director Maintenance",
                "standard_str": "00:15",
                "standard_minutes": 15,
                "sla_met": False,
                "sla_breach_ratio": 566.93
            },
            {
                "department": "Reception",
                "task_category": "Adaptor delivery",
                "received_at": "09/Sep 19:38",
                "creator": "Roman (1)",
                "location": "242",
                "description": "Adaptor delivery (UK to EU socket)",
                "provided_at": "09/Sep 19:47",
                "duration_str": "00:09",
                "duration_minutes": 9,
                "resolver": "Roman (1)",
                "standard_str": "00:15",
                "standard_minutes": 15,
                "sla_met": True,
                "sla_breach_ratio": 1.0
            }
        ]
    }

    json_path = os.path.join(output_dir, "sample_smartbutler_digest.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    # 2. CSV Sample
    csv_path = os.path.join(output_dir, "sample_smartbutler_digest.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Log Report - Providers", "", "", "", "", "", "", "", "", ""])
        writer.writerow(["Received Date: 01/Sep/2026 - 23/Sep/2026 (Current Month), Sites: Grand Hotel", "", "", "", "", "", "", "", "", ""])
        writer.writerow([])
        writer.writerow([
            "Department", "Task Category", "Received At", "Creator", "Location",
            "Description", "Provided At", "Duration", "Resolver", "Standard"
        ])
        for t in json_data["tickets"]:
            writer.writerow([
                t["department"],
                t["task_category"],
                t["received_at"],
                t["creator"],
                t["location"],
                t["description"],
                t["provided_at"],
                t["duration_str"],
                t["resolver"],
                t["standard_str"]
            ])

    print(f"Generated samples in {output_dir}:")
    print(f" - {json_path}")
    print(f" - {csv_path}")

if __name__ == "__main__":
    generate_samples()
