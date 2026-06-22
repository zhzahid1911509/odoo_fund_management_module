# Custom Odoo Module Architecture Explanation (`nn_fund_management`)

This document provides a technical overview of the architectural design, layer responsibilities, and structural constraints implemented within the Odoo 17 custom module `nn_fund_management`.

The architecture follows Odoo’s framework-native **Model-View-Controller (MVC)** design pattern, extended into a **Layered Architecture** that separates institutional capital tracking from operational project execution.

---

## 1. Relational Database & Data Layer (Models)

The database layer isolates financial data at two distinct control points to prevent cross-contamination and ensure precise auditing trail logs:

### A. The Corporate Treasury Layer

- **`nn.fund.account` (Fund Accounts):** Represents physical or cash treasury nodes. It serves as the primary cash ledger, managing overall fluid availability metrics based on incoming transactions and approved allocations.
- **`nn.incoming.fund` (Incoming Funds):** Maps direct institutional inflows into a specific treasury account. It captures metadata (sender, reference, purpose) along with transactional attachments.

### B. The Operational Budget Layer

- **`nn.project` (Projects):** Represents long-running business operational initiatives. It maintains dedicated analytical balance registers to isolate project-level financial health.
- **`nn.expense.head` (Expense Heads):** Tracks generic corporate recurring operating line items (e.g., utilities, marketing). It features identical database tracking metrics to the project model but exists as a completely independent schema table.
- **`nn.fund.allocation` (Fund Allocations):** A specialized polymorphic junction table managing the distribution pipeline moving liquidity down from the _Treasury Layer_ to the _Operational Budget Layer_.
- **`nn.fund.requisition` (Fund Requisitions):** Tracks outward expenses and invoice claims against an active project or expense head budget.
- **`nn.fund.transfer` (Inter-Budget Fund Transfers):** Tracks horizontal movements of unspent capital across operational lines (Project-to-Project or Project-to-Expense Head).

---

## 2. Business Logic Layer & Core Security Constraints

All calculation pipelines and transactional integrity protections are enforced server-side via the Odoo ORM engine layer to ensure absolute data consistency:

- **Autonomous Compute Lifecycles (`@api.depends`):** All financial balance panels are read-only (`readonly=True`) and calculated automatically by background stored compute loops. This structure completely prevents manual user tampering with live accounting calculations.
- **The Exclusive-OR (XOR) Relational Gate:** Implemented via strict Python database intercept parameters on the allocation, requisition, and transfer tables. It ensures that a cash transaction targets _either_ a Project _or_ an Expense Head, but never both simultaneously, protecting relational integrity.
- **Two-Phase State Machine Hold Pipelines:** To completely prevent double-spending vulnerabilities across concurrent user requests, the module implements a temporary hold feature within its state machines:

1. _Submitting an Allocation Request_ freezes bank cash into an `amount_held` category, instantly removing it from the spendable pool while awaiting review.
2. _Submitting a Requisition or Transfer_ places a project-level budget freeze inside a `requisition_hold` or `transfer_hold` register, securing the funds until final management sign-off occurs.

- **Database Reference Uniqueness Firewall:** A low-level PostgreSQL server constraint (`_sql_constraints`) locks down the incoming fund table, ensuring a unique index match per account and preventing duplicate statement reference keys from entering the tracking logs.

---

## 3. Presentation & User Interface Layer (Views)

The frontend interface decouples operational workflows from standard configuration layouts using a clean XML configuration layer (`views/fund_management_views.xml`):

- **Automated Document Sequences:** Integrated Odoo’s native sequence engine (`ir.sequence`) to automatically generate standardized, sequential alphanumeric identifiers (`INC-`, `ALLOC-`, `REQ-`, `XFER-`) when records are created.
- **Embedded Relational Sub-Ledgers:** Uses `One2many` notebook sub-grids embedded directly into the main master configuration forms. This lets users instantly drill down into a bank account's deposit logs or a project's full requisition breakdown from a single view.
- **Dynamic Kanban List badges:** List trees leverage conditional status parameters (`decoration-success`, `decoration-info`) to provide real-time, color-coded visual tracking of workflow stages.

---

## 4. Permission Framework & Audit Logs

- **Native XML Security Modeling:** Access rights are defined using Odoo's native XML records (`security/security.xml`) rather than standard CSV lines, completely avoiding formatting or encoding errors. It cleanly provisions read, write, and create permissions across all tables for the standard internal user group (`base.group_user`).
- **Immutable Transactional Records:** All access rules feature strict `perm_unlink = 0` constraints. Once an entry is committed and posted, the system completely blocks raw data deletion, ensuring an unalterable history trail.
- **Automated Tracking Threads (Chatter):** Every transactional database object inherits Odoo's core communication mixins (`mail.thread` and `mail.activity.mixin`). Combined with the interface chatter widget, the system automatically builds an audit log tracking the creator, submission timestamps, and every management approval signature step.

---

## 5. Deployment Infrastructure (Dockerization)

The application architecture is completely decoupled from the local host system environment using an isolated multi-container runtime blueprint (`docker-compose.yml`):

- **Application Service Node:** Runs an image layer pinned to `Odoo 17.0 Community Edition`, operating on Python 3.10. It utilizes real-time XML developer reloads (`--dev=xml,reload`) to maximize execution transparency.
- **Database Service Node:** Provisions an independent `PostgreSQL 15` instance, completely isolated from the application service container.
- **Persistent Storage Layers:** Uses isolated named Docker volumes (`odoo-web-data` and `odoo-db-data`) to ensure that database rows and uploaded file attachments remain completely secure and persist across container network restarts.
