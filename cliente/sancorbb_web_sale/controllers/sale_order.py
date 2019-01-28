from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_tx_state = fields.Selection(related='payment_tx_id.state', string='Payment State')

