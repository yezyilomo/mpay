from odoo import http, api
from odoo.http import request

class Controller(http.Controller):

#    Just for Demostration
#    @http.route('/auth_usr', type='http', auth='public', website=True, )
#    def render_example_page(self):
#        return http.request.render("Mpay.example__page", {})


    @http.route('/get_transaction_sms', type='http', auth='public', website=True, methods=['POST'])
    def post_method(self, **sms):
        #Here we have to extract important information from SMS sent and store to received.transaction model
        data=request.env['received.transaction'].search([],limit=10)
        return "Info Stored"

    @http.route('/paynow', type='http', auth='public', website=True, methods=['POST'])
    def pay_now(self, **kw):
        data=kw
        return request.render("Mpay.transaction_id_fill",{'amount': data['amount'], 'currency': data['currency']})

    @http.route('/validate', type='http', auth='public', website=True, methods=['POST','GET'])
    def validate_payment(self, **kw):
        transaction=request.env['received.transaction'].search([('transaction_id','=',kw['transaction_id'] ) ],limit=1)
        if not transaction.exists() :  # if invalid transaction_id is provided
            return "No transaction"

        if transaction.transaction_status == 'done' :  # if provided transaction_id has already been used to confirm transaction
           return "Transaction has already been done"

        if transaction.transaction_status == 'pending' : # if transaction is in pending state not yet confirmed

           if transaction.received_amount != kw['amount'] : # if paid amount is not equal to required amount
              transaction.transaction_status='incomplete'
              return "You have paid insufficient money"

           transaction.transaction_status='done'  #Everything is right now we confirm payment
           return "Thank you, You have done your payment successfully, Wait for shipment of your products"
