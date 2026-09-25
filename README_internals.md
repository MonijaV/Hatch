### B2c — Dangerous Patterns

The given code has two bugs related to the document lifecycle,
def validate(self):
    self.total_amount = sum(r.amount for r in self.addons) + self.base_amount
    self.save()
    resource = frappe.get_doc("Resource", self.resource)
    resource.times_booked += 1
    resource.save()
BUG1:
   validate() runs as part of the document save lifecycle. Calling self.save() inside validate() starts another save operation, which invokes validate() again. This can recursively trigger the same code and lead to a recursion error
BUG2:
   A specific document can be validated using validate method multiple number of times even when other document is being updated..so by doing so the times_booked field increments every time even for the other documents in the doctype.

Corrected Version:
  def validate(self):
    self.total_amount = sum(r.amount for r in self.addons) + self.base_amount

def on_submit(self):
    resource = frappe.get_doc("Resource", self.resource)
    resource.times_booked += 1
    resource.save()

### B2d — Concurrency

When two users open the same document and both try to save it,Frappe uses optimistic concurrency control.It compares the document's modification timestamp/version.If another user has already modified the document,Frappe raises Document has been modified after you have opened it instead of silently overwriting the other user's changes.

### C3 — Booking Add-on Entry & Child Table Internals

The DB Table name for Booking Add-on Entry is `tabBooking Add-on Entry`.

### D2 Row-Level Filtering & Data Leaks

frappe.get_all is dangerous,because it bypasses the user permissions(The user who doesnt have permission ,can also view the document using frappe.get_all). Whereas the frappe.get_list,before retrieving the document checks the permissions and restricts the user from seeing the records,if he doesnt have access to the document.

### E1 — Complete Lifecycle

on_update is triggered by saving an existing document. If I call self.save() inside on_update, that save triggers on_update again, causing recursive updates. For calculated fields, I should calculate them in validate().


### E2 — Naming & Renaming

so while renaming a document from old name to new name we can specify merge=True or merge=False.When we specify
merge=False,if there is an existing document that already exist with the new name will not be merged as the same document.whereas when we specify merge=True,if there is an existing document that already exist with the new name ,the document will merge and become a single same document.

### E3 — One Performance Judgment Call

doc = frappe.get_doc("Hatch Settings", "Hatch Settings")
hours = doc.pending_confirmation_expiry_hours

hours = frappe.db.get_value("Hatch Settings", None, "pending_confirmation_expiry_hours")

get_doc() loads the document as a Frappe Document object which is useful when I need the document itself or multiple fields and document methods. frappe.db.get_value() is more appropriate when I only need one specific field because I don't need to construct the full Document object

### H1 — Booking Form Script


### I1 — Query Report

With an f-string,the value becomes part of the SQL string itself.With a parameterized query,the SQL structure and the data are passed separately.This reduces SQL injection risk and makes dynamic queries safer and easier to maintain

### J1 — Booking Confirmation


### K2 — Spot the N+1

import frappe
def print_booking_members():
    bookings = frappe.get_all("Booking",fields=["name", "member"])
    member_names = list({bk.member for bk in bookings if bk.member})
    if not member_names:
        return
    members = frappe.get_all("Member",
        filters={
            "name": ["in", member_names]
        },
        fields=[
            "name",
            "member_name",
            "email"
        ])
    member_map = {member.name: member for member in members}
    for bk in bookings:
        mem = member_map.get(bk.member)
        if mem:
            print(mem.member_name,mem.email)

### L1 — Availability Check Endpoint

curl http://127.0.0.1:8000/api/resource/Booking -H "Authorization: token 873e26370386ec1:3e584042e16abc8"
{"data":[{"name":"BOOK-2026-0001"},{"name":"BOOK-2026-0001-1"},{"name":"BOOK-2026-0002"},{"name":"BOOK-2026-0003"},{"name":"BOOK-2026-0004"},{"name":"BOOK-2026-0005"},{"name":"BOOK-2026-0006"},{"name":"BOOK-2026-0007"},{"name":"BOOK-2026-0008"},{"name":"BOOK-2026-0009"}]}%

curl -X post "http://127.0.0.1:8000/api/resource/Booking" -H "Authorization: token 873e26370386ec1:3e584042e16abc8" -H "Content-Type: application/json" -d '{"member":"MEM-0006","resource":"Room A","booking_date":"2026-09-26","start_time":"10:00:00","end_time":"11:00:00","head_count":2}' 
{"data":{"name":"BOOK-2026-0010","owner":"Administrator","creation":"2026-09-25 16:36:54.249421","modified":"2026-09-25 16:36:54.249421","modified_by":"Administrator","docstatus":0,"idx":0,"member":"MEM-0006","resource":"Room A","booking_date":"2026-09-26","start_time":"10:00:00","end_time":"11:00:00","head_count":2,"base_amount":500.0,"addons_total":0.0,"total_amount":500.0,"payment_status":"Unpaid","status":"Draft","doctype":"Booking","addons":[]}}%    

### N1 — ignore_permissions Audit & JS-Hiding Pitfall

1.cancel_booking()
booking.save(ignore_permissions=True)
The whitelisted cancellation method performs the controlled server-side cancellation operation after validating the booking,so the method bypasses normal document permissions for this operation

2.Audit Log creation
The audit hook must be able to create an Audit Log entry even when the triggering user does not have normal create permission on the Audit Log DocType.

### Video Clip

https://drive.google.com/file/d/1peRz6Em8yDLuoW1danxFJbYs1G0L93ud/view?usp=sharing













