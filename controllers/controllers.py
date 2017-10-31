from odoo import http, api
from odoo.http import request
import logging
import pprint
import werkzeug
import odoo

_logger = logging.getLogger(__name__)

class MpayController(http.Controller):
    _accept_url = '/payment/mpay/feedback'

    @http.route([
        '/payment/mpay/feedback',
    ], type='http', auth='none', csrf=False)
    def mpay_form_feedback(self, **post):
        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(post))  # debug
        print(post)
        request.env['payment.transaction'].sudo().form_feedback(post, 'transfer')
        return werkzeug.utils.redirect(post.pop('return_url', '/'))

    @http.route('/shop/confirmation', type='http', auth='public', website=True, )   #
    def payment_confirmation(self, **post):
        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :

         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """

        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            providers=request.env['payment.service'].sudo().search([])
            return request.render("Mpay.example__page", {'order': order, 'providers': providers})
        else:
            return request.redirect('/shop')             

    def extract_data(self,template,message):
       tokenized_message=message.split()
       tokenized_template=template.split()
       data={}
       try:
            if( len(tokenized_message) != len(tokenized_template) ):
             for i in range(0,len(tokenized_message)):
               if(tokenized_message[i] != tokenized_template[i]) and tokenized_template[i][0:1] == "$" and len(tokenized_template)!= (i+1):
                  data.update( {tokenized_template[i][1:] : tokenized_message[i]} )

               elif (tokenized_message[i] != tokenized_template[i]) and tokenized_template[i][0:1] != "$" and len(tokenized_template)!= (i+1):
                  while True:
                    if (tokenized_message[i] != tokenized_template[i]) and tokenized_template[i][0:1] != "$":
                       data[tokenized_template[i-1][1:]]=data[tokenized_template[i-1][1:]]+" "+tokenized_message[i]
                       del tokenized_message[i]
                    else:
                       break;
               elif (tokenized_message[i] != tokenized_template[i]) and tokenized_template[i][0:1] == "$" and len(tokenized_template)== (i+1):
                  help_message=""
                  iterator=iter(tokenized_message[i:])
                  for p in iterator:
                    test=next(iterator,True)
                    if test==True:
                       help_message=help_message+p+""
                    else:
                       help_message=help_message+p+" "
                  data.update({tokenized_template[i][1:]:help_message})
                  break;
             return data

            else:
              for i in range(0,len(tokenized_message)):
                 if(tokenized_message[i] != tokenized_template[i]) and tokenized_template[i][0:1] == "$" :
                    data.update( {tokenized_template[i][1:] : tokenized_message[i]} )

              return data
       except Exception as e:
         print("Error 001: Invalid formating of template\nCheck if your message corresponds with the template\n")


    @http.route('/get_transaction_sms', type='http', auth='public', website=True, methods=['POST'], csrf=False)
    def post_method(self, **sms):
          #Here we have to extract important information from SMS sent and store to "received.transaction" model
          mpay_secret_key=request.env['payment.acquirer'].sudo().search([("provider","=","mpay")]).ensure_one().secrete_key
          if sms['secret'] != mpay_secret_key:
              return "Error 404."

          received_sms=sms["message"]
          provider_sending_name=sms["from"]
          template=""
          provider=request.env['payment.service'].sudo().search([("transaction_sender_name","=",provider_sending_name)])
          if not provider.exists():
              print('\033[1m'+'\033[91m'+"\nOooops!, Provider with the name '"+provider_sending_name+"' is not defined in your database!..\n"+'\033[0m')
              return "Error 405"
          else:
              template=provider.ensure_one().template_sms

          try :
            transaction_sms=self.extract_data(template,received_sms)
          except Exception as e:
             print(e)
             print('\033[1m'+'\033[91m'+"\nOooops!, it seems like your SMS does not involve payment transaction!.\n"+'\033[0m')

          data=request.env['received.transaction'].sudo().create({
           'reference': transaction_sms['reference'],
           'sender_name': transaction_sms['name'],
           'sender_phone': transaction_sms['name'],
           'transaction_id': transaction_sms['transaction_id'],
           'transaction_status': 'pending',
           'transaction_currency': transaction_sms['received_amount'][0:3],
           'received_amount': float(transaction_sms['received_amount'][3:].replace(",", "")),
           'service_provider': sms['from']
           } )
          order=request.env['payment.transaction'].sudo().search( [('reference','=',transaction_sms['reference'] )] )

          if order.exists():
              if order.state!='done' and data.transaction_status!='done' and  data.received_amount >= order.amount: ##If paid amount is equal or greater than expected amount
                 order.write({'state':'done'})
                 data.write({'transaction_status': 'done'})
                 print('\033[1m'+'\033[92m'+"\nMpay payment for order # "+transaction_sms['reference']+ " confirmed\n"+'\033[0m')
              elif  order.state!='done' and data.transaction_status!='done' and data.received_amount < order.amount: ##If paid amount is less than expected amount
                data.write({'transaction_status': 'incomplete'})
                print('\033[1m'+'\033[91m'+"\nIncomplete payment.\n"+'\033[0m')
              else :
               data.write({'transaction_status': 'cancelled'})
               print('\033[1m'+'\033[1m'+'\033[1m'+'\033[91m'+"\nOrder "+transaction_sms['reference']+ " has already been processed.\n"+'\033[0m')#Order with the same  order number exist
          else:
             print('\033[1m'+'\033[91m'+"\nOrder "+transaction_sms['reference']+" does not exist.\n" +'\033[0m')
