import frappe
def after_install():
    create_default_resources()
    create_default_settings()
    frappe.msgprint("Hatch installation completed successfully")
def create_default_resources():
    resources=[
        {
            "resource_name":"Room A",
            "resource_type":"Meeting Room",
            "capacity":6,
            "hourly_rate":500,
            "is_active":1,
        },
        {
            "resource_name":"Room B",
            "resource_type":"Meeting Room",
            "capacity":3,
            "hourly_rate":300,
            "is_active":1,
        },
        {
            "resource_name":"Hot Desk Zone",
            "resource_type":"Hot Desk Zone",
            "capacity":12,
            "hourly_rate":100,
            "is_active":1,
        },
    ]
    for data in resources:
        if not frappe.db.exists("Resource",{"resource_name": data["resource_name"]}):
            frappe.get_doc({
                "doctype": "Resource",
                "resource_name":data["resource_name"],
                "resource_type":data["resource_type"],
                "capacity":data["capacity"],
                "hourly_rate":data["hourly_rate"],
                "is_active":data["is_active"]
            }).insert(ignore_permissions=True)

def create_default_settings():
    if not frappe.db.exists("Hatch Settings"):
        frappe.get_doc({
            "doctype": "Hatch Settings",
            "manager_email": frappe.session.user,
            "pending_confirmation_expiry_hours": 2,
            "cancellation_window_hours": 4,
            "waitlist_enabled": 1
        }).insert(ignore_permissions=True)