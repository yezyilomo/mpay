from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare

import logging
import pprint

_logger = logging.getLogger(__name__)

class MpayAcquirer(models.Model):
    _inherit = 'payment.acquirer'
    provider = fields.Selection(selection_add=[('mpay', 'Mpay')])

    post_msg = fields.Html('Thanks Message', compute="funct")

    @api.depends()
    def funct (self):
     first=self.env['payment.service'].sudo().search([("service_provider","=","Vodacom")]);
     if first.exists():
         first=first.service_number
     else:
         first="1500"
     second=self.env['payment.service'].sudo().search([("service_provider","=","Tigo")]);
     if second.exists():
         first=second.service_number
     else:
         second="1400"

     self.post_msg=_('''<div>
      <h3>Please use the following details for payment</h3>
        <div class="mpay">
        <span >  <img src="http://www.vodafone.com/content/dam/vodafone-images/M-Pesa/map/m-pesa-drc-tanz-les-moz.jpg" alt=""  width="200" height="100">
                    <ol>
                     <li>  piga *150*00#  </li>
                    <li>  chagua #4 - Lipa kwa M-Pesa </li>
                    <li>  chagua #4 - Weka namba ya kampuni %(ref_first)s </li>
                    <li>  Weka namba ya kumbukumbu ya malipo</li>
                    <li>  Weka Kiasi  </li>
                    <li>  Weka Namba ya siri  </li>
                    <li>  Bonyeza 1 kuthibitisha</li>
                    </ol>
        </span>
        <span > <img src="http://www.ocode.or.tz/wp-content/uploads/2014/02/tigo_pesa_tutashinda.png" alt=""  width="200" height="100">
                  <ol>
                   <li>  piga *150*01#  </li>
                  <li>  chagua #4 - Lipa kwa M-Pesa </li>
                  <li>  chagua #4 - Weka namba ya kampuni %(ref_second)s </li>
                  <li>  Weka Kiasi  </li>
                  <li>  Weka Namba ya siri  </li>
                  <li>  Bonyeza 1 kuthibitisha</li>
                  </ol>
        </span>
        </div>
      <b>Please use the order name as reference number(kumbukumbu namba).</b>
      </div>''')%{
      'ref_first': first,
      'ref_second': second
      }


    def mpay_get_form_action_url(self):
        return '/payment/mpay/feedback'

class MpayPaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _mpay_form_get_tx_from_data(self, data):
        reference, amount, currency_name = data.get('reference'), data.get('amount'), data.get('currency_name')
        tx = self.search([('reference', '=', reference)])

        if not tx or len(tx) > 1:
            error_msg = _('received data for reference %s') % (pprint.pformat(reference))
            if not tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        return tx

    def _mpay_form_get_invalid_parameters(self, data):
        invalid_parameters = []

        if float_compare(float(data.get('amount', '0.0')), self.amount, 2) != 0:
            invalid_parameters.append(('amount', data.get('amount'), '%.2f' % self.amount))
        if data.get('currency') != self.currency_id.name:
            invalid_parameters.append(('currency', data.get('currency'), self.currency_id.name))

        return invalid_parameters

    def _mpay_form_validate(self, data):
        _logger.info('Validated mpay payment for tx %s: set as pending' % (self.reference))
        return self.write({'state': 'pending'})

class PaymentService(models.Model):
    _name='payment.service'
    _description='This store Service provider informations'
    service_provider=fields.Char('Service Provider', required=True)
    service_number=fields.Char('Service Number', required=True)
    template_sms=fields.Text("Template SMS", required=True,default="$transaction_id Imethibitishwa umepokea $received_amount kutoka kwa $name Tarehe $date saa $time kwa kumbukumbu namba $reference")


class ReceivedTransaction(models.Model):
    _name='received.transaction'
    _description='This store all details from synchronised SMS'
    reference=fields.Char('Reference', required=True)
    sender_name=fields.Char('Sender Name', required=True)
    sender_phone=fields.Char('Sender Phone', required=True)
    transaction_id=fields.Char('Transaction Id', required=True)
    received_amount=fields.Float('Received Amount', required=True)
    transaction_currency=fields.Char('Currency', required=True)
    service_provider=fields.Char('Service Provider', required=True)
    transaction_status=fields.Selection([('pending','pending'),('done','done'),('incomplete','incomplete')],required=True)
