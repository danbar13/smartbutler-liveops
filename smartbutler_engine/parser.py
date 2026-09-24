"""
SmartButler Log Parser
Ingests and normalizes operational logs from CSV and JSON files across
SmartButler modules: Maintenance, Housekeeping, and Logbook.
"""

import os
import json
import csv
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import MaintenanceTicket, HousekeepingTask, LogbookEntry

class SmartButlerParser:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "logs")
        else:
            self.data_dir = data_dir

    def load_maintenance(self, file_format: str = "json") -> List[MaintenanceTicket]:
        """Loads maintenance tickets from JSON or CSV."""
        ext = file_format.lower().lstrip(".")
        filename = f"smartbutler_maintenance_48h.{ext}"
        filepath = os.path.join(self.data_dir, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Maintenance log file not found: {filepath}")

        tickets: List[MaintenanceTicket] = []
        if ext == "json":
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    res_time = None
                    if item.get("resolution_time_minutes") not in (None, ""):
                        try:
                            res_time = int(item["resolution_time_minutes"])
                        except ValueError:
                            res_time = None
                    tickets.append(MaintenanceTicket(
                        ticket_id=str(item.get("ticket_id", "")),
                        created_at=str(item.get("created_at", "")),
                        closed_at=str(item.get("closed_at", "")) if item.get("closed_at") else None,
                        room_number=str(item.get("room_number", "")),
                        floor=int(item.get("floor", 0)),
                        category=str(item.get("category", "")),
                        issue_description=str(item.get("issue_description", "")),
                        priority=str(item.get("priority", "Medium")),
                        status=str(item.get("status", "Open")),
                        assigned_technician=str(item.get("assigned_technician", "")),
                        shift=str(item.get("shift", "")),
                        resolution_time_minutes=res_time,
                        vip_flag=bool(item.get("vip_flag", False)),
                        notes=str(item.get("notes", ""))
                    ))
        elif ext == "csv":
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    res_time = None
                    if row.get("resolution_time_minutes"):
                        try:
                            res_time = int(row["resolution_time_minutes"])
                        except ValueError:
                            res_time = None
                    vip = str(row.get("vip_flag", "")).strip().lower() in ("true", "1", "yes")
                    tickets.append(MaintenanceTicket(
                        ticket_id=row.get("ticket_id", ""),
                        created_at=row.get("created_at", ""),
                        closed_at=row.get("closed_at") or None,
                        room_number=row.get("room_number", ""),
                        floor=int(row.get("floor", 0) or 0),
                        category=row.get("category", ""),
                        issue_description=row.get("issue_description", ""),
                        priority=row.get("priority", "Medium"),
                        status=row.get("status", "Open"),
                        assigned_technician=row.get("assigned_technician", ""),
                        shift=row.get("shift", ""),
                        resolution_time_minutes=res_time,
                        vip_flag=vip,
                        notes=row.get("notes", "")
                    ))
        return tickets

    def load_housekeeping(self, file_format: str = "json") -> List[HousekeepingTask]:
        """Loads housekeeping tasks from JSON or CSV."""
        ext = file_format.lower().lstrip(".")
        filename = f"smartbutler_housekeeping_48h.{ext}"
        filepath = os.path.join(self.data_dir, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Housekeeping log file not found: {filepath}")

        tasks: List[HousekeepingTask] = []
        if ext == "json":
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    tasks.append(HousekeepingTask(
                        task_id=str(item.get("task_id", "")),
                        timestamp=str(item.get("timestamp", "")),
                        room_number=str(item.get("room_number", "")),
                        floor=int(item.get("floor", 0)),
                        room_status=str(item.get("room_status", "")),
                        guest_status=str(item.get("guest_status", "")),
                        task_type=str(item.get("task_type", "")),
                        housekeeper_name=str(item.get("housekeeper_name", "")),
                        shift=str(item.get("shift", "")),
                        notes=str(item.get("notes", ""))
                    ))
        elif ext == "csv":
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tasks.append(HousekeepingTask(
                        task_id=row.get("task_id", ""),
                        timestamp=row.get("timestamp", ""),
                        room_number=row.get("room_number", ""),
                        floor=int(row.get("floor", 0) or 0),
                        room_status=row.get("room_status", ""),
                        guest_status=row.get("guest_status", ""),
                        task_type=row.get("task_type", ""),
                        housekeeper_name=row.get("housekeeper_name", ""),
                        shift=row.get("shift", ""),
                        notes=row.get("notes", "")
                    ))
        return tasks

    def load_logbook(self, file_format: str = "json") -> List[LogbookEntry]:
        """Loads duty manager logbook entries from JSON or CSV."""
        ext = file_format.lower().lstrip(".")
        filename = f"smartbutler_logbook_48h.{ext}"
        filepath = os.path.join(self.data_dir, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Logbook file not found: {filepath}")

        entries: List[LogbookEntry] = []
        if ext == "json":
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    comp_amount = 0.0
                    try:
                        comp_amount = float(item.get("compensation_amount_ils", 0.0) or 0.0)
                    except ValueError:
                        comp_amount = 0.0
                    entries.append(LogbookEntry(
                        log_id=str(item.get("log_id", "")),
                        timestamp=str(item.get("timestamp", "")),
                        shift=str(item.get("shift", "")),
                        author_role=str(item.get("author_role", "")),
                        author_name=str(item.get("author_name", "")),
                        category=str(item.get("category", "")),
                        room_number=str(item.get("room_number", "")),
                        vip_guest_name=str(item.get("vip_guest_name", "")),
                        incident_description=str(item.get("incident_description", "")),
                        compensation_offered=str(item.get("compensation_offered", "")),
                        compensation_amount_ils=comp_amount,
                        escalated_to_gm=bool(item.get("escalated_to_gm", False)),
                        action_required=str(item.get("action_required", ""))
                    ))
        elif ext == "csv":
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    comp_amount = 0.0
                    try:
                        comp_amount = float(row.get("compensation_amount_ils", 0.0) or 0.0)
                    except ValueError:
                        comp_amount = 0.0
                    esc = str(row.get("escalated_to_gm", "")).strip().lower() in ("true", "1", "yes")
                    entries.append(LogbookEntry(
                        log_id=row.get("log_id", ""),
                        timestamp=row.get("timestamp", ""),
                        shift=row.get("shift", ""),
                        author_role=row.get("author_role", ""),
                        author_name=row.get("author_name", ""),
                        category=row.get("category", ""),
                        room_number=row.get("room_number", ""),
                        vip_guest_name=row.get("vip_guest_name", ""),
                        incident_description=row.get("incident_description", ""),
                        compensation_offered=row.get("compensation_offered", ""),
                        compensation_amount_ils=comp_amount,
                        escalated_to_gm=esc,
                        action_required=row.get("action_required", "")
                    ))
        return entries
