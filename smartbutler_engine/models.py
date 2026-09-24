"""
SmartButler Domain Models
Represents entities from JAYBEE Systems' SmartButler modules:
- Maintenance
- Housekeeping
- Logbook
- Document Ingestion Tracking
- Detected Anomalies & Executive Briefing
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class MaintenanceTicket:
    ticket_id: str
    created_at: str
    closed_at: Optional[str]
    room_number: str
    floor: int
    category: str
    issue_description: str
    priority: str
    status: str
    assigned_technician: str
    shift: str
    resolution_time_minutes: Optional[int]
    vip_flag: bool
    notes: str
    source_file: Optional[str] = None
    source_type: Optional[str] = None

@dataclass
class HousekeepingTask:
    task_id: str
    timestamp: str
    room_number: str
    floor: int
    room_status: str
    guest_status: str
    task_type: str
    housekeeper_name: str
    shift: str
    notes: str
    source_file: Optional[str] = None
    source_type: Optional[str] = None

@dataclass
class LogbookEntry:
    log_id: str
    timestamp: str
    shift: str
    author_role: str
    author_name: str
    category: str
    room_number: str
    vip_guest_name: str
    incident_description: str
    compensation_offered: str
    compensation_amount_ils: float
    escalated_to_gm: bool
    action_required: str
    source_file: Optional[str] = None
    source_type: Optional[str] = None

@dataclass
class Anomaly:
    anomaly_id: str
    category: str # "RECURRENT_VIP", "CLUSTER_INFRASTRUCTURE", "WAITING_PARTS", "CRITICAL_COMPENSATION"
    title: str
    title_he: str
    severity: str # "CRITICAL", "HIGH", "MEDIUM"
    location: str
    description: str
    description_he: str
    evidence_count: int
    related_tickets: List[str] = field(default_factory=list)
    action_item: str = ""
    action_item_he: str = ""
    responsible_dept: str = ""
    financial_impact_ils: float = 0.0

@dataclass
class DepartmentActionItem:
    department: str
    department_he: str
    priority: str
    owner: str
    target_time: str
    action: str
    action_he: str
    room_or_asset: str

@dataclass
class ExecutiveBriefing:
    generated_at: str
    hotel_name: str
    total_maintenance_48h: int # Total maintenance tickets analyzed
    total_housekeeping_48h: int # Total housekeeping tasks analyzed
    total_logbook_entries_48h: int # Total logbook entries analyzed
    open_waiting_parts_count: int
    total_compensation_ils: float
    vip_at_risk_count: int
    anomalies: List[Anomaly] = field(default_factory=list)
    action_items: List[DepartmentActionItem] = field(default_factory=list)
    waiting_parts_tickets: List[MaintenanceTicket] = field(default_factory=list)
    compensation_incidents: List[LogbookEntry] = field(default_factory=list)
    period_label: str = "יממה אחרונה (24 שעות)"
    period_hours: int = 24
    sources_ingested: List[str] = field(default_factory=list)
