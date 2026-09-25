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
def share_booking(booking_name, user_email):
    if not frappe.db.exists("Booking", booking_name): 
        frappe.throw("Booking does not exist") 
    if not frappe.db.exists("User", user_email): 
        frappe.throw("User does not exist")
    frappe.share.add( "Booking", booking_name, user_email, read=1) 
    return { "message": "Booking shared successfully","booking": booking_name,"user": user_email }

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


@frappe.whitelist()
def get_availability():
    resource = frappe.form_dict.get("resource")
    booking_date = frappe.form_dict.get("booking_date")
    start_time = frappe.form_dict.get("start_time")
    end_time = frappe.form_dict.get("end_time")
    if not resource or not booking_date or not start_time or not end_time:
        frappe.throw("Resource, booking date, start time and end time are required.")
    capacity = frappe.db.get_value("Resource",resource,"capacity")
    if capacity is None:
        frappe.throw("Resource does not exist.")
    booked = frappe.db.sql(
        """
        SELECT COALESCE(SUM(head_count), 0)
        FROM `tabBooking`
        WHERE resource = %(resource)s
          AND booking_date = %(booking_date)s
          AND status NOT IN ('Cancelled', 'Completed')
          AND docstatus < 2
          AND start_time < %(end_time)s
          AND end_time > %(start_time)s
        """,
        {
            "resource": resource,
            "booking_date": booking_date,
            "start_time": start_time,
            "end_time": end_time
        }
    )[0][0]
    available = max(capacity - booked, 0)
    return {
        "capacity": capacity,
        "booked": booked,
        "available": available
    }











