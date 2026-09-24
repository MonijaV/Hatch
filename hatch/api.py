import frappe
from frappe.query_builder import DocType,Order
from frappe.utils import today

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

@frappe.whitelist()
def reassign_bookings(from_member, to_member):
    try:
        result = frappe.db.sql("""
            UPDATE `tabBooking`
            SET member = %(to_member)s
            WHERE member = %(from_member)s
              AND booking_date >= %(today)s
              AND status != 'Cancelled' """,
            {
                "from_member": from_member,
                "to_member": to_member,
                "today": today()
            })
        frappe.db.commit()
        return {
            "success": True,
            "message": "Bookings reassigned successfully",
        }
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(),"Booking Reassignment Failed")
        frappe.throw("Unable to reassign bookings")

@frappe.whitelist()
def rename_member(old, new):
    frappe.rename_doc( "Member",old,new,merge=False)
    return {
        "message": "Member renamed successfully",
        "old_name": old,
        "new_name": new
    }

@frappe.whitelist()
def cancel_booking(booking_name, cancellation_reason):
    booking = frappe.get_doc("Booking", booking_name)
    if booking.status == "Cancelled":
        frappe.throw("Booking is already cancelled")
    if not cancellation_reason:
        frappe.throw("Cancellation reason is required")
    booking.status = "Cancelled"
    booking.save(ignore_permissions=True)
    return {
        "success": True,
        "message": "Booking cancelled successfully"
    }


@frappe.whitelist()
def reassign_booking(booking_name, new_member):
    booking = frappe.get_doc("Booking", booking_name)
    if not frappe.db.exists("Member", new_member):
        frappe.throw("Selected Member does not exist")
    if booking.status == "Cancelled":
        frappe.throw("Cancelled bookings cannot be reassigned")
    booking.member = new_member
    booking.save(ignore_permissions=True)
    return {
        "success": True,
        "message": "Booking reassigned successfully",
        "booking": booking.name,
        "new_member": new_member
    }











