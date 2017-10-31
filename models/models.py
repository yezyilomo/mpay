from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare

import logging
import pprint

_logger = logging.getLogger(__name__)

class MpayAcquirer(models.Model):
    _inherit = 'payment.acquirer'
    provider = fields.Selection(selection_add=[('mpay', 'Mpay')])
    secrete_key = fields.Char("Secrete key", required_if_provider="mpay")
    pending_msg = fields.Html("Pending Message", compute="get_pending_msg")

    @api.depends()
    def get_pending_msg(self):
        if self.provider=="mpay":
            self.pending_msg="""
            <span><font style="font-size: 18px;">Your online payment has been successfully processed.
            But your order is not validated yet, Choose your mobile payment service provider and follow
            instructions to complete payment.</font></span>
            """
        else:
            self.pending_msg="""
            <span><i>Pending,</i> Your online payment has been successfully processed. But your order is not validated yet.</span>
            """

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
    transaction_sender_name = fields.Char("Sender Name")
    payment_procedures=fields.Html("Payment Steps", required=True, default="""
    <ol>
     <li>  piga *150*00#  </li>
     <li>  chagua #4 - Lipa kwa M-Pesa </li>
     <li>  chagua #4 - Weka namba ya kampuni</li>
     <li>  Weka namba ya kumbukumbu ya malipo</li>
     <li>  Weka Kiasi  </li>
     <li>  Weka Namba ya siri  </li>
     <li>  Bonyeza 1 kuthibitisha</li>
    </ol>
    """)
    provider_icon=fields.Char("Image URL", required=True)
    template_sms=fields.Text("Template SMS", required=True,default="\
$transaction_id Imethibitishwa umepokea $received_amount kutoka\
 kwa $name Tarehe $date saa $time kwa kumbukumbu namba $reference")

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
    transaction_status=fields.Selection([('pending','pending'),('done','done'),('incomplete','incomplete'),('cancelled','cancelled')],required=True)
