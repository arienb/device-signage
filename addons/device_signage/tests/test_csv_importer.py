import os
import tempfile

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCsvImporter(TransactionCase):

    def setUp(self):
        super().setUp()

        self.importer = self.env["signage.csv.importer"]

        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def _create_csv(self, filename, content):
        file_path = os.path.join(self.temp_dir.name, filename)

        with open(file_path, "w", encoding="utf-8") as csv_file:
            csv_file.write(content)

        return file_path

    def test_happy_flow(self):
        device_file = self._create_csv(
            "devices.csv",
            "900001,Test Device,Test description,TEST-900001,"
            "2099-12-31 23:59:59+00:00,enabled\n",
        )

        content_file = self._create_csv(
            "content.csv",
            "900002,Test Content,Test description,900001,"
            "2099-12-31 23:59:59+00:00,enabled\n",
        )

        self.importer._import_devices(device_file, ",")
        self.importer._import_content(content_file, ",")

        device = self.env["signage.device"].search([
            ("external_id", "=", 900001),
        ])

        content = self.env["signage.content"].search([
            ("external_id", "=", 900002),
        ])

        self.assertTrue(device, "The device should have been imported.")
        self.assertTrue(content, "The content should have been imported.")
        self.assertEqual(content.device_id, device)
        self.assertEqual(device.state, "enabled")

    def test_existing_device_is_updated(self):
        first_file = self._create_csv(
            "device_first.csv",
            "900011,Old Device Name,Old description,TEST-900011,"
            "2099-12-31 23:59:59+00:00,enabled\n",
        )

        second_file = self._create_csv(
            "device_second.csv",
            "900011,Updated Device Name,Updated description,TEST-900011,"
            "2099-12-31 23:59:59+00:00,enabled\n",
        )

        self.importer._import_devices(first_file, ",")
        self.importer._import_devices(second_file, ",")

        devices = self.env["signage.device"].search([
            ("external_id", "=", 900011),
        ])

        self.assertEqual(len(devices), 1, "No duplicate device should be created.")
        self.assertEqual(devices.name, "Updated Device Name")
        self.assertEqual(devices.description, "Updated description")

    def test_expired_device_is_disabled(self):
        device_file = self._create_csv(
            "expired_device.csv",
            "900021,Expired Device,Expired description,TEST-900021,"
            "2000-01-01 00:00:00+00:00,enabled\n",
        )

        self.importer._import_devices(device_file, ",")

        device = self.env["signage.device"].search([
            ("external_id", "=", 900021),
        ])

        self.assertTrue(device, "The expired device should still be imported.")
        self.assertEqual(
            device.state,
            "disabled",
            "An expired device should automatically be disabled.",
        )