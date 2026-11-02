from odoo import fields, models


class SignageSettings(models.TransientModel):
    _inherit = "res.config.settings"

    csv_folder = fields.Char(
        string="CSV Folder Path",
        config_parameter="device_signage.csv_folder",
        default="/mnt/csv",
    )

    csv_delimiter = fields.Char(
        string="CSV Delimiter",
        config_parameter="device_signage.csv_delimiter",
        default=",",
    )