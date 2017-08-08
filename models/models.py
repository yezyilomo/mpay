from odoo import models, fields, api

class MpayAcquirer(models.Model):
     _inherit = 'payment.acquirer'
     provider = fields.Selection(selection_add=[('mpay', 'Mpay')])

     def _get_feature_support(self):
        res = super(MpayAcquirer, self)._get_feature_support()
        res['tokenize'].append('mpay')
        return res

class MpayTransaction(models.Model):
    _inherit = 'payment.transaction'

class PaymentService(models.Model):
    _name='payment.service'
    _description='This store Service provider informations'
    service_provider=fields.Char('Service Provider', required=True)
    service_number=fields.Char('Service Number', required=True)

class ReceivedTransaction(models.Model):
    _name='received.transaction'
    _description='This store all details from synchronised SMS'
    sender_name=fields.Char('Sender Name', required=True)
    sender_phone=fields.Char('Sender Phone', required=True)
    transaction_id=fields.Char('Transaction Id', required=True)
    received_amount=fields.Float('Received Amount', required=True)
    transaction_currency=fields.Char('Currency', required=True)
    service_provider=fields.Char('Service Provider', required=True)
    transaction_status=fields.Selection([('pending','pending'),('done','done'),('incomplete','incomplete')],required=True)
