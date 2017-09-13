from odoo import http, api
from odoo.http import request
import logging
import pprint
import werkzeug

_logger = logging.getLogger(__name__)

class OgoneController(http.Controller):
    _accept_url = '/payment/mpay/feedback'

    @http.route([
        '/payment/mpay/feedback',
    ], type='http', auth='none', csrf=False)
    def mpay_form_feedback(self, **post):
        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(post))  # debug
        print(post)
        request.env['payment.transaction'].sudo().form_feedback(post, 'transfer')
        return werkzeug.utils.redirect(post.pop('return_url', '/'))

#####Just for Demostration #################################################
    @http.route('/auth_usr', type='http', auth='public', website=True, )   #
    def render_demo_page(self):                                            #
        return http.request.render("Mpay.example__page", {})               #
####Just for Demostration ##################################################

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
        if sms['secret'] !='ilomoyezy':
            return "Error 404."

        received_sms=sms['message']
        get_record=request.env['payment.service'].sudo().search([("service_provider","=","Vodacom")]);
        if get_record.exists():
           template=get_record.template_sms;
        else:
            template="$transaction_id Imethibitishwa umepokea $received_amount kutoka kwa $name Tarehe $date saa $time kwa kumbukumbu namba $reference"

        try :
          transaction_sms=self.extract_data(template,received_sms)
          data=request.env['received.transaction'].sudo().create({'reference': transaction_sms['reference'],'sender_name': transaction_sms['name'], 'sender_phone': transaction_sms['name'], 'transaction_id': transaction_sms['transaction_id'], 'transaction_status': 'pending', 'transaction_currency': transaction_sms['received_amount'][0:3], 'received_amount': float(transaction_sms['received_amount'][3:].replace(",", "")), 'service_provider': sms['from'] }  )
          trs=request.env['payment.transaction'].sudo().search( [('reference','=',transaction_sms['reference'] )] )
          print(len(transaction_sms['reference']));
          print(received_sms)
          if trs.exists(): ##########If the order exists
              if trs.state!='done' and data.transaction_status!='done' and trs.amount <= data.received_amount: ##If paid amount is equal or greater than expected amount
                 trs.write({'state':'done'})
                 data.write({'transaction_status': 'done'})
                 print('\033[1m'+'\033[92m'+"\nMpay payment for order # "+transaction_sms['reference']+ " confirmed\n"+'\033[0m')
              elif  trs.state!='done' and data.transaction_status!='done' and trs.amount > data.received_amount: ##If paid amount is less than expected amount
                data.write({'transaction_status': 'incomplete'})
                print('\033[1m'+'\033[91m'+"\nIncomplete payment.\n"+'\033[0m')
              else :
               data.write({'transaction_status': 'cancelled'})
               print('\033[1m'+'\033[1m'+'\033[1m'+'\033[91m'+"\nOrder "+transaction_sms['reference']+ " has already been processed.\n"+'\033[0m')#Order with the same  order number exist
          else:  ###########If the order doesn't exist
            print('\033[1m'+'\033[91m'+"\nOrder "+transaction_sms['reference']+" does not exist.\n" +'\033[0m')

        except Exception as e:
            print(e)
            print('\033[1m'+'\033[91m'+"\nOooop!, it seems like your SMS does not involve payment transaction!.\n"+'\033[0m')
