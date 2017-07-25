from odoo import models, fields

class MpayAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    Mpay_account_id = fields.Char('Account Id')
    Mpay_access_tocken = fields.Char('Access Token')


class MpayTransaction(models.Model):
    _inherit = 'payment.transaction'
    Mpay_checkout_id = fields.Char('Mpay Checkout Id')
    acquirer_name = fields.Selection(related='acquirer_id.provider') 
