import frappe
from frappe.utils import now_datetime,add_to_date
def release_expired_holds():
    run_key = f"release_holds:{now_datetime().strftime('%Y%m%d%H')}"
    if frappe.cache().get_value(run_key):
        return
    frappe.cache().set_value(run_key,True,expires_in_sec=3500)
    expiry_hours = frappe.db.get_value(
        "Hatch Settings",
        None,
        "pending_confirmation_expiry_hours"
    )
    if not expiry_hours:
        return
    expiry_time = add_to_date(now_datetime(),hours=-expiry_hours)
    expired_bookings = frappe.get_all(
        "Booking",
        filters={"status": "Pending Confirmation","creation":["<=","expiry_time"]},
        pluck="name"
    )
    for booking_name in expired_bookings:
        booking = frappe.get_doc("Booking",booking_name)
        booking.status = "Cancelled"
        booking.save(ignore_permissions=True)

