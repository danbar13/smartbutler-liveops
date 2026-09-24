"""
SmartButler LiveOps Digest - Data Models (parsers/models.py)
Defines standard models for parsed SmartButler "Log Report - Providers" documents.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

def parse_duration_to_minutes(d_str: str) -> Optional[int]:
    """Converts duration string formatted as 'HH:MM' or 'HHH:MM' to total minutes."""
    if not d_str or d_str.strip() in ("N/A", "-", "", "None"):
        return None
    try:
        parts = d_str.strip().split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 60 + int(parts[1])  # Ignore seconds
    except (ValueError, AttributeError):
        pass
    return None

def format_minutes_to_duration(minutes: Optional[int]) -> str:
    """Converts integer minutes to 'HH:MM' string format."""
    if minutes is None:
        return "N/A"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

@dataclass
class TicketItem:
    department: str
    task_category: str
    received_at: str
    creator: str
    location: str
    description: str
    provided_at: str = "N/A"
    duration_str: str = "N/A"
    duration_minutes: Optional[int] = None
    resolver: str = "-"
    standard_str: str = "00:15"
    standard_minutes: int = 15
    sla_met: bool = False
    sla_breach_ratio: float = 0.0

    def __post_init__(self):
        if self.duration_minutes is None and self.duration_str != "N/A":
            self.duration_minutes = parse_duration_to_minutes(self.duration_str)
        if self.standard_minutes == 15 and self.standard_str != "00:15":
            std_min = parse_duration_to_minutes(self.standard_str)
            if std_min is not None:
                self.standard_minutes = std_min

        # Compute SLA Met
        if self.duration_minutes is not None and self.standard_minutes > 0:
            self.sla_met = (self.duration_minutes <= self.standard_minutes)
            if not self.sla_met:
                self.sla_breach_ratio = round(self.duration_minutes / self.standard_minutes, 2)
            else:
                self.sla_breach_ratio = 1.0
        else:
            # If duration is N/A (unresolved), it is an SLA breach
            self.sla_met = False
            self.sla_breach_ratio = 999.0

@dataclass
class DepartmentSummary:
    department: str
    total_tickets: int
    avg_duration_str: str
    avg_duration_minutes: int
    total_time_str: str
    total_time_minutes: int
    success_rate: float

@dataclass
class ParsedLogReport:
    report_title: str
    site_name: str
    date_range: str
    raw_filename: str
    file_format: str
    total_tickets: int
    overall_success_rate: float
    avg_duration_str: str
    avg_duration_minutes: int
    total_time_str: str
    total_time_minutes: int
    tickets: List[TicketItem] = field(default_factory=list)
    departments: List[DepartmentSummary] = field(default_factory=list)

    def to_report_dict(self) -> Dict[str, Any]:
        return {
            "report_title": self.report_title,
            "site_name": self.site_name,
            "date_range": self.date_range,
            "raw_filename": self.raw_filename,
            "file_format": self.file_format,
            "total_tickets": self.total_tickets,
            "overall_success_rate": self.overall_success_rate,
            "avg_duration_str": self.avg_duration_str,
            "avg_duration_minutes": self.avg_duration_minutes,
            "total_time_str": self.total_time_str,
            "total_time_minutes": self.total_time_minutes
        }

    def tickets_as_dicts(self) -> List[Dict[str, Any]]:
        return [asdict(t) for t in self.tickets]

    def departments_as_dicts(self) -> List[Dict[str, Any]]:
        return [asdict(d) for d in self.departments]
