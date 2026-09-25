# Copyright (c) 2026, John and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime

class Booking(Document):
    def validate(self):
        self.validate_time()
        self.calculate_amounts()
        self.check_capacity()
        
    def validate_time(self):
        start = get_datetime(f"2000-01-01 {self.start_time}")
        end = get_datetime(f"2000-01-01 {self.end_time}")
        if end <= start:
            frappe.throw("End Time must be After the Start Time.")
            
    def calculate_amounts(self):
        start = get_datetime(f"2000-01-01 {self.start_time}")
        end = get_datetime(f"2000-01-01 {self.end_time}")
        duration_in_hours = (end - start).total_seconds()/3600
        hourly_rate = frappe.db.get_value("Resource",self.resource,"hourly_rate")
        self.base_amount = hourly_rate * duration_in_hours
        
        addons_total = 0
        for addon in self.addons:
            addon.amount = addon.rate * addon.quantity
            addons_total += addon.amount
        self.addons_total = addons_total
        self.total_amount = (self.base_amount + self.addons_total)
        
    def check_capacity(self):
        resource_capacity = frappe.db.get_value("Resource",self.resource,"capacity")
        if resource_capacity is None:
               frappe.throw("Selected Resource does not have a capacity.")
        existing_headcount = frappe.db.sql(
					"""
					SELECT COALESCE(SUM(head_count), 0)
					FROM `tabBooking`
					WHERE resource = %(resource)s
					  AND booking_date = %(booking_date)s
					  AND start_time < %(end_time)s
					  AND end_time > %(start_time)s
					  AND status IN (
						  'Pending Confirmation',
						  'Confirmed',
						  'Checked-In'
					  )
					  AND name != %(booking_name)s
					""",
					{
						"resource": self.resource,
						"booking_date": self.booking_date,
						"start_time": self.start_time,
						"end_time": self.end_time,
						"booking_name": self.name or ""
					}
				)[0][0] or 0
        total_headcount = (existing_headcount + self.head_count)
        seats_free = (resource_capacity - existing_headcount)
        if total_headcount > resource_capacity:
             frappe.throw(
						f"Booking exceeds the resource capacity. "
						f"Only {seats_free} seat(s) are actually free, "
						f"but this booking requires {self.head_count}")
        
        
    def before_submit(self):
        if self.status != "Pending Confirmation":
             frappe.throw("Booking can only be submitted when it is in the pending confirmation status")
        
    def on_submit(self):
        self.db_set("status", "Confirmed")
        frappe.enqueue("hatch.hatch.doctype.booking.booking.send_confirmation_email",booking_name=self.name,queue="short")
        
    def on_cancel(self):
        self.db_set("status", "Cancelled")
        
    def on_trash(self):
        if self.status not in ["Cancelled", "Draft"]:
            frappe.throw("Only Draft or Cancelled bookings can be deleted")
            
    # def on_update(self):
    #     self.total_amount = (sum(row.amount for row in self.addons)+ self.base_amount)
    #     self.save()

    def before_print(self, print_format=None):
        self.print_summary = (f"{self.member} - {self.resource} on {self.booking_date}")

def send_confirmation_email(booking_name):
    booking = frappe.get_doc("Booking",booking_name)
    member_email = frappe.db.get_value("Member",booking.member,"email")
    if not member_email:
        return
    frappe.sendmail(
        recipients=[member_email],
        subject=f"Booking {booking.name} Confirmed",
        message=(f"Your booking {booking.name} has been confirmed"))