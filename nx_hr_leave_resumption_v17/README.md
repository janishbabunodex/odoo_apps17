# HR Leave Resumption Date — Odoo 17

## Overview
This module extends Odoo 17's **HR Holidays** (`hr_holidays`) to allow HR teams to record and track an employee's expected **Resumption (Rejoin) Date** after an approved leave.

---

## Features

| Feature | Description |
|---|---|
| **Resumption Date field** | Date field added to every leave request form (employee & manager views) |
| **Create Resumption Leave** | Button creates a linked single-day leave record on the resumption date |
| **View Resumption Leave** | Button opens the linked resumption leave form directly |
| **Onchange Warning** | Advisory popup when the resumption date is set, showing leave end date for confirmation |
| **Date Validation** | Server-side constraint prevents resumption date being earlier than the leave end date |
| **Tracking** | Resumption Date changes are logged in the chatter |
| **Tree column** | Optional "Resumption Date" column in the list view |

---

## Installation

1. Copy `hr_leave_resumption/` into your Odoo addons path.
2. Update the apps list: **Settings → Apps → Update Apps List**.
3. Search for **"HR Leave Resumption Date"** and click **Install**.

---

## Dependencies

- `hr_holidays` (standard Odoo Time Off module)

---

## Usage

### Setting a Resumption Date
1. Open a leave request (your own or as HR Manager).
2. Fill in the **Resumption Date** field — an advisory warning will appear showing the leave end date.
3. Save the record.

### Creating a Resumption Leave
1. Once a Resumption Date is saved, the **Create Resumption Leave** button appears in the header.
2. Click it and confirm — a linked single-day leave (Unpaid type) is created for the resumption date.
3. The button changes to **View Resumption Leave** for easy navigation.

---

## Technical Notes

### Model: `hr.leave` (inherited)

| Field | Type | Description |
|---|---|---|
| `resumption_date` | `Date` | Expected return-to-work date; tracked in chatter |
| `nx_resumption_leave_id` | `Many2one → hr.leave` | Linked resumption leave record |
| `has_resumption_leave` | `Boolean` (computed) | Used to toggle button visibility |

### Methods

| Method | Description |
|---|---|
| `create_resumption_leave()` | Creates and links a resumption `hr.leave` record |
| `action_view_resumption()` | Returns window action to open the linked leave form |
| `_onchange_resumption_date()` | Advisory warning when resumption date is entered |
| `_check_resumption_date()` | Constrains resumption date ≥ leave end date |

---

## Changelog

### v17.0.1.0.0
- Initial release
- Resumption Date field with chatter tracking
- Create / View Resumption Leave buttons
- Onchange warning and server-side date constraint
- Employee and Manager form view inheritance
- Optional tree view column

---

## License
LGPL-3
