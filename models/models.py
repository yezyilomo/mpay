from odoo import models, fields

class MpayAcquirer(models.Model):
    _inherit = 'payment.acquirer'
    
    def _get_providers(self, cr, uid, context=None):
        providers = super(MpayAcquirer, self)._get_providers(cr, uid, context=context)
        providers.append(['Mpay', 'MPay'])
        return providers

    Mpay_account_id = fields.Char('Account Id')
    Mpay_access_tocken = fields.Char('Access Token')


class MpayTransaction(models.Model):
    _inherit = 'payment.transaction'
    Mpay_checkout_id = fields.Char('Mpay Checkout Id')
    acquirer_name = fields.Selection(related='acquirer_id.provider') 
    
    
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
    service_provider=fields.Char('Service Provider', required=True)
    transaction_status=fields.Selection([('pending','pending'),('done','done'),('incomplete','incomplete')],required=True)  
