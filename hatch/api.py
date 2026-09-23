import frappe
from frappe.query_builder import DocType,Order
from frappe.utils import today

@frappe.whitelist()
def share_booking(booking_name,user_email):
    frappe.share.add()


@frappe.whitelist()
def get_upcoming_bookings():
    booking = frappe.qb.DocType('Booking')
    result = (frappe.qb.from_(booking)
        .select(
            booking.name,
            booking.member,
            booking.resource,
            booking.booking_date,
            booking.start_time)
        .where((booking.booking_date >= today())&(booking.status.isin(["Pending Confirmation","Confirmed"])))
        .orderby(booking.booking_date)
        .run(as_dict=True)
    )
    return result











