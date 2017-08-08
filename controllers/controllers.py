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
        data=request.env['received.transaction'].sudo().search([],limit=10)
        return "Info Stored"

    @http.route('/paynow', type='http', auth='public', website=True, methods=['POST'])
    def pay_now(self, **kw):
        data=kw
        error=""
        return request.render("Mpay.transaction_id_fill",{'amount': data['amount'], 'currency': data['currency'],'error': error})

    @http.route('/validate', type='http', auth='public', website=True, methods=['POST','GET'])
    def validate_payment(self, **kw):
        data=kw;
        transaction=request.env['received.transaction'].sudo().search([('transaction_id','=',kw['transaction_id'] ) ],limit=1)
        if not transaction.exists() :  # if invalid transaction_id is provided
            #error="No transaction"
            error="Invalid transaction Id, try again!."
            return request.render("Mpay.transaction_id_fill",{'amount': data['amount'], 'currency': data['currency'], 'error': error})

        if transaction.transaction_status == 'done' :  # if provided transaction_id has already been used to confirm transaction
           #error="Transaction has already been done"
           error="Invalid transaction Id, try again!."
           return request.render("Mpay.transaction_id_fill",{'amount': data['amount'], 'currency': data['currency'], 'error': error})

        if transaction.transaction_status == 'pending' : # if transaction is in pending state not yet confirmed

           if float(transaction.received_amount) != float(kw['amount']) : # if paid amount is not equal to required amount
              transaction.transaction_status='incomplete'
              error= "You have paid insufficient money"
              return request.render("Mpay.transaction_id_fill",{'amount': data['amount'], 'currency': data['currency'], 'error': error})

           transaction.transaction_status='done'  #Everything is right now we confirm payment
           error="none"
           return request.render("Mpay.transaction_id_fill",{'amount': data['amount'], 'currency': data['currency'], 'error': error})
