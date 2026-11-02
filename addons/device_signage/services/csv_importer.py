
import csv
import logging
import os

from datetime import datetime, timezone
from odoo import fields, models

_logger = logging.getLogger(__name__)


class CsvImporter(models.AbstractModel):
    _name = "signage.csv.importer"
    _description = "Digital Signage CSV Importer"


    def _get_import_settings(self):

        settings = self.env["res.config.settings"].sudo().create({})

        csv_folder = settings.csv_folder or "/mnt/csv"
        csv_delimiter = settings.csv_delimiter or ","

        csv_folder = csv_folder.strip()
        csv_delimiter = csv_delimiter.strip()

        if not csv_folder:
            _logger.error("CSV folder path is not configured")
            return None

        if len(csv_delimiter) != 1:
            _logger.error(
                "Invalid CSV delimiter '%s'. Expected exactly one character.",
                csv_delimiter,
            )
            return None

        if not os.path.isdir(csv_folder):
            _logger.error("CSV folder does not exist: %s", csv_folder)
            return None

        return csv_folder, csv_delimiter


    def _import_devices(self, file_path, delimiter):

        _logger.info("Starting device import: %s", file_path)

        if not os.path.isfile(file_path):
            _logger.error("Device CSV file not found: %s", file_path)
            return

        imported = 0
        updated = 0
        skipped = 0

        try:
            with open(
                file_path,
                mode="r",
                encoding="utf-8-sig",
                newline="",
            ) as csv_file:

                for row_number, line in enumerate(csv_file, start=1):
                    try:
                        row = next(
                            csv.reader(
                                [line],
                                delimiter=delimiter,
                                strict=True,
                            )
                        )
                    except csv.Error as error:
                        skipped += 1
                        _logger.warning(
                            "Skipping malformed CSV row %s: %s",
                            row_number,
                            error,
                        )
                        continue

                    try:
                        if len(row) != 6:
                            raise ValueError(
                                f"Expected 6 columns, received {len(row)}"
                            )

                        row = [value.strip() for value in row]
                        external_id, name, description, code, expire_date, state = row
                        external_id = int(external_id)

                        if not name:
                            raise ValueError("Device name is missing")

                        if not code:
                            raise ValueError("Device code is missing")

                        if len(name) > 32:
                            raise ValueError("Device name exceeds 32 characters")

                        if len(description) > 128:
                            raise ValueError("Device description exceeds 128 characters")

                        if len(code) > 30:
                            raise ValueError("Device code exceeds 30 characters")

                        if state not in ("enabled", "disabled", "deleted"):
                            raise ValueError(f"Invalid device state: {state}")

                        expiration = datetime.fromisoformat(expire_date)

                        if expiration.tzinfo is None:
                            expiration = expiration.replace(tzinfo=timezone.utc)
                        else:
                            expiration = expiration.astimezone(timezone.utc)

                        expiration = expiration.replace(tzinfo=None)

                        if expiration < fields.Datetime.now():
                            state = "disabled"

                        values = {
                            "external_id": external_id,
                            "name": name,
                            "description": description,
                            "code": code,
                            "expire_date": expiration,
                            "state": state,
                        }

                        # savepoint om  de import door te laten gaan bij fouten
                        with self.env.cr.savepoint():

                            device = self.env["signage.device"].search(
                                [("external_id", "=", external_id)],
                                limit=1,
                            )

                            if device:
                                device.write(values)
                                updated += 1
                                _logger.info(
                                    "Updated device %s (%s)",
                                    external_id,
                                    name,
                                )
                            else:
                                self.env["signage.device"].create(values)
                                imported += 1
                                _logger.info(
                                    "Created device %s (%s)",
                                    external_id,
                                    name,
                                )

                    except (ValueError, TypeError) as error:
                        skipped += 1
                        _logger.warning(
                            "Skipping device row %s: %s. Data: %s",
                            row_number,
                            error,
                            row,
                        )

                    except Exception:
                        skipped += 1
                        _logger.exception(
                            "Unexpected error processing device row %s",
                            row_number,
                        )

            _logger.info(
                "Device import finished. Created: %s, Updated: %s, Skipped: %s",
                imported,
                updated,
                skipped,
            )

        except (OSError, csv.Error):
            _logger.exception("Could not read device CSV file: %s", file_path)


    def _import_content(self, file_path, delimiter):

        _logger.info("Starting content import: %s", file_path)

        if not os.path.isfile(file_path):
            _logger.error("Content CSV file not found: %s", file_path)
            return

        imported = 0
        updated = 0
        skipped = 0

        try:
            with open(
                file_path,
                mode="r",
                encoding="utf-8-sig",
                newline="",
            ) as csv_file:

                for row_number, line in enumerate(csv_file, start=1):
                    try:
                        row = next(
                            csv.reader(
                                [line],
                                delimiter=delimiter,
                                strict=True,
                            )
                        )
                    except csv.Error as error:
                        skipped += 1
                        _logger.warning(
                            "Skipping malformed content CSV row %s: %s",
                            row_number,
                            error,
                        )
                        continue

                    try:
                        if len(row) != 6:
                            raise ValueError(
                                f"Expected 6 columns, received {len(row)}"
                            )

                        row = [value.strip() for value in row]

                        external_id, name, description, device_external_id, expire_date, state = row

                        external_id = int(external_id)
                        device_external_id = int(device_external_id)

                        if not name:
                            raise ValueError("Content name is missing")

                        if len(name) > 100:
                            raise ValueError("Content name exceeds 100 characters")

                        if len(description) > 128:
                            raise ValueError("Content description exceeds 128 characters")

                        if state not in ("enabled", "disabled", "deleted"):
                            raise ValueError(f"Invalid content state: {state}")

                        expiration = datetime.fromisoformat(expire_date)

                        if expiration.tzinfo is None:
                            expiration = expiration.replace(tzinfo=timezone.utc)
                        else:
                            expiration = expiration.astimezone(timezone.utc)

                        expiration = expiration.replace(tzinfo=None)

                        if expiration < fields.Datetime.now():
                            state = "disabled"

                        device = self.env["signage.device"].search(
                            [("external_id", "=", device_external_id)],
                            limit=1,
                        )

                        if not device:
                            raise ValueError(
                                f"Referenced device {device_external_id} does not exist"
                            )

                        values = {
                            "external_id": external_id,
                            "name": name,
                            "description": description,
                            "device_id": device.id,
                            "expire_date": expiration,
                            "state": state,
                        }

                        with self.env.cr.savepoint():

                            content = self.env["signage.content"].search(
                                [("external_id", "=", external_id)],
                                limit=1,
                            )

                            if content:
                                content.write(values)
                                updated += 1
                                _logger.info(
                                    "Updated content %s (%s)",
                                    external_id,
                                    name,
                                )
                            else:
                                self.env["signage.content"].create(values)
                                imported += 1
                                _logger.info(
                                    "Created content %s (%s)",
                                    external_id,
                                    name,
                                )

                    except (ValueError, TypeError) as error:
                        skipped += 1
                        _logger.warning(
                            "Skipping content row %s: %s. Data: %s",
                            row_number,
                            error,
                            row,
                        )

                    except Exception:
                        skipped += 1
                        _logger.exception(
                            "Unexpected error processing content row %s",
                            row_number,
                        )

            _logger.info(
                "Content import finished. Created: %s, Updated: %s, Skipped: %s",
                imported,
                updated,
                skipped,
            )

        except (OSError, csv.Error):
            _logger.exception("Could not read content CSV file: %s", file_path)


    def action_import_all_deliveries(self):

        _logger.info("Starting complete signage CSV import")

        # settings nakijken
        settings = self._get_import_settings()

        if not settings:
            _logger.error("CSV import aborted due to invalid settings")
            return

        csv_folder, delimiter = settings

        _logger.info(
            "Using CSV folder: %s with delimiter: '%s'",
            csv_folder,
            delimiter,
        )

        deliveries = ["delivery_1", "delivery_2"]

        # import devices
        for delivery in deliveries:
            file_path = os.path.join(
                csv_folder,
                delivery,
                "devices.csv",
            )

            _logger.info("Processing device delivery: %s", delivery)
            self._import_devices(file_path, delimiter)

        # import content
        for delivery in deliveries:
            file_path = os.path.join(
                csv_folder,
                delivery,
                "content.csv",
            )

            _logger.info("Processing content delivery: %s", delivery)
            self._import_content(file_path, delimiter)

        _logger.info("Complete signage CSV import finished")