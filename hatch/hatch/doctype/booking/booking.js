// Copyright (c) 2026, John and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Booking", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Booking", {
    refresh(frm) {
        if (!frm.is_new() &&frm.doc.status !== "Cancelled" && frm.doc.docstatus !== 2) {
            frm.add_custom_button("Cancel Booking", function () {
                let dialog = new frappe.ui.Dialog({
                    title: "Cancel Booking",
                    fields: [
                        {
                            label: "Cancellation Reason",
                            fieldname: "cancellation_reason",
                            fieldtype: "Small Text",
                            reqd: 1
                        }
                    ],
                    primary_action_label: "Cancel Booking",
                    primary_action(values) {
                        frappe.call({
                            method: "hatch.api.cancel_booking",
                            args:{
                                booking_name: frm.doc.name,
                                cancellation_reason:values.cancellation_reason
                            },
                            callback: function (r) {
                                if (!r.exc) {
                                    frappe.show_alert({
                                        message: "Booking cancelled successfully",
                                        indicator: "green"
                                    });
                                    dialog.hide();
                                }
                            }
                        });
                    }
                });
                dialog.show();
            });
        }
        if (!frm.is_new()) {
            frm.add_custom_button("Reassign to Another Member",function () {
                    frappe.prompt(
                        {
                            label: "New Member",
                            fieldname: "new_member",
                            fieldtype: "Link",
                            options: "Member",
                            reqd: 1
                        },
                        function (values){
                            frappe.confirm(
                                `Are you sure you want to reassign this booking to ${values.new_member}?`,
                                function () {
                                    frappe.call({
                                        method:
                                            "hatch.api.reassign_booking",
                                        args: {
                                            booking_name: frm.doc.name,
                                            new_member:values.new_member
                                        },
                                        callback: function (r) {
                                            if (!r.exc) {
                                                frappe.show_alert({
                                                    message: "Booking reassigned successfully",
                                                    indicator: "green"
                                                });
                                            }
                                        }
                                    });
                                },
                                function () {
                                    console.log("Booking reassignment cancelled.");
                                }
                            );
                        },
                        "Reassign Booking","Continue"
                    );
                }
            );
        }
    }
});
