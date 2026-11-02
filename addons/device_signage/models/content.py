from odoo import fields, models

class Device(models.Model):
    _name = "signage.content"
    _description = "content"

    name = fields.Char(
        string = "Name",
        required = True,
        size = 100
    )

    external_id = fields.Integer(
        string="External ID",
        required=True,
        index=True,
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

    expire_date = fields.Datetime(
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

    _external_id_unique = models.Constraint(
        "UNIQUE(external_id)",
        "The external ID must be unique.",
    )    