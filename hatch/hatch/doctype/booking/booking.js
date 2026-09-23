// Copyright (c) 2026, John and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Booking", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Booking",{
    refresh(frm){
        if(!frm.is_new()){
            frm.add_custom_button('Cancel Booking',()=>{
                let d = new frappe.ui.Dialog({
                    title:'Cancellation of Booking',
                    fields:[
                        {
                            label:"Cancellation Resaon",
                            field_name:"cancellation_reason",
                            field_type:"Small Text"
                        }
                    ],
                    primary_action_label:'Submit',
                    primary_action(values){
                        console.log(values);
                        d.hide();
                    }
                })
            })
            d.show();
        }
    }
})
