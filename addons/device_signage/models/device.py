from odoo import fields, models

class Device(models.Model):
    _name = "signage.device"
    _description = "device"
    _order = "name"

    external_id = fields.Integer(
        string="External ID",
        required=True,
        index=True,
    )

    name = fields.Char(
        string = "Name",
        required = True,
        size = 32
    )

    description = fields.Char(
        string = "Description",
        size = 128
    )

    code = fields.Char(
        string = "Code",
        required = True,
        size = 30,
        index = True
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

    _sql_constraints = [
        (
            "UNIQUE(code)",
            "The device code must be unique.",
        ),
    ]

    _external_id_unique = models.Constraint(
        "UNIQUE(external_id)",
        "The external ID must be unique.",
    )