import frappe
def booking_query(user):
    if not user:
        user = frappe.session.user
    member = frappe.db.get_value("Member",{"user": user},"name")
    if not member:
        return "0=1"
    return f"`tabBooking`.`member` = {frappe.db.escape(member)}"
