from odoo import fields, models

class Device(models.Model):
    _name = "signage.content"
    _description = "content"

    name = fields.Char(
        string = "Name",
        required = True,
        size = 100
    )

    description = fields.Char(
        string = "Description",
        size = 128
    )

    device_id = fields.Many2one(
        comodel_name = "signage.device",
        string = "Device",
        required = True,
        ondelete = "restrict"
    )

    expireDate = fields.Datetime(
        string="Expiration Date",
    )

    state = fields.Selection(
        selection=[
            ("enabled", "Enabled"),
            ("disabled", "Disabled"),
            ("deleted", "Deleted"),
        ],
        string="Status",
        default="enabled",
        required=True,
    )