# coding=utf-8
from odoo import api, fields, models, _

class LogPaymentNotifications(models.Model):
    _name = "log.payment.notifications"

    # @api.depends('notification_type', 'received_date')
    # def _compute_name(self):
    #     for rec in self:
    #         rec.name = rec.notification_type + ' ' + rec.received_date

    name = fields.Char("Notification")
    received_date = fields.Datetime("Received On")
    notification_type = fields.Selection([('ipn', 'IPN'), ('webhook', 'Webhook')], string="Notification Type")
    notification_id = fields.Char(string="Notification Id")
    notification_data = fields.Text(string="Notification Data")
