# Copyright (c) 2026, John and contributors
# For license information, please see license.txt

# import frappe
from frappe import _


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns()
	data = get_data()

	return columns, data

def execute_snapshot_report(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for snapshot report. When 'Synced
	Report' is enabled in report, framework will call this method
	every time the report is refreshed or a filter is updated. It
	accepts the same filters as normal execute. But a utility method -
	get_latest_sync, is also imported.

	"""
	from frappe.database.duckdb.database import get_latest_sync

	columns = get_columns()
	data = get_data()

	return columns, data

def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
        {
            "label": _("Resource"),
            "fieldname": "resource",
            "fieldtype": "Link",
            "options": "Resource",
            "width": 180,
        },
        {
            "label": _("Total Bookings"),
            "fieldname": "total_bookings",
            "fieldtype": "Int",
            "width": 130,
        },
        {
            "label": _("Total Hours Booked"),
            "fieldname": "total_hours_booked",
            "fieldtype": "Float",
            "width": 160,
        },
        {
            "label": _("Utilization %"),
            "fieldname": "utilization",
            "fieldtype": "Percent",
            "width": 130,
        },
        {
            "label": _("Revenue"),
            "fieldname": "revenue",
            "fieldtype": "Currency",
            "width": 130,
        },
    ]


def get_data() -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	return [
		["Row 1", 1],
		["Row 2", 2],
	]
