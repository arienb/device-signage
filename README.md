# Device Signage

An Odoo module for managing digital signage devices and their content.

The module imports device and content data from CSV deliveries, synchronizes existing records, and automatically disables expired records.

## Features

- Import devices and content from CSV files.
- Synchronize existing records using their external IDs.
- Prevent duplicate device codes and external IDs.
- Link content to devices using a Many2one relationship.
- Automatically disable expired records.
- Schedule 1 automatic import per day using Odoo's cron scheduler.
- Configure the CSV folder and delimiter through Odoo settings.
- Log import operations, skipped records, and errors.

## Requirements

- Odoo 20.0 Community
- PostgreSQL 16
- Python packages included with the Odoo installation
- Docker (recommended)

## Installation

1. Clone this repository.
2. Place the `device_signage` module inside your Odoo addons directory.
3. Make sure the addons directory is included in your Odoo configuration.
4. Restart Odoo.
5. Update the Apps list.
6. Search for **Device Signage** and install the module.

## Configuration

After installing the module, configure the CSV import settings in Odoo:

- **CSV Folder Path:** Path to the directory containing the delivery folders.
- **CSV Delimiter:** Character used to separate CSV columns. Defaults to `,`.

The expected folder structure is:

csv/
├── delivery_1/
│   ├── devices.csv
│   └── content.csv
└── delivery_2/
    ├── devices.csv
    └── content.csv

The configured folder path must be accessible from the Odoo server.

## CSV Format

The CSV files do not contain headers.

### devices.csv

| Column | Description |
|---|---|
| 1 | External ID |
| 2 | Name |
| 3 | Description |
| 4 | Code |
| 5 | Expiration date |
| 6 | State |

### content.csv

| Column | Description |
|---|---|
| 1 | External ID |
| 2 | Name |
| 3 | Description |
| 4 | Device external ID |
| 5 | Expiration date |
| 6 | State |

Supported states:

- `enabled`
- `disabled`
- `deleted`

Expiration dates should use ISO 8601 format, for example:

`2028-10-07 23:59:59.000+01:00`

## Automatic Import

The module includes a scheduled action that imports the deliveries automatically once per day.

The import process:

1. Imports devices from all deliveries.
2. Updates existing devices when their external ID already exists.
3. Imports content from all deliveries.
4. Links content to the corresponding device.
5. Skips invalid records and logs the reason.

Expired records are automatically assigned the `disabled` state.

## Testing

The module contains automated tests for:

- Successful import of a device and its associated content.
- Updating an existing device without creating duplicates.
- Automatically disabling expired devices.

Run the tests using Docker Compose:

docker compose exec web odoo -d device_signage --test-enable --stop-after-init --db_host=db --db_user=odoo --db_password=odoo --test-tags /device_signage

## Logging

Import operations and errors are logged through Odoo's logging system.

When using the provided Docker configuration, logs are stored in:

`logs/odoo.log`

## License

LGPL-3