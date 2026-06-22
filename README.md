# Fund Management Module (`nn_fund_management`)

### Technical Assessment Submission

- **Position:** Trainee Software Developer
- **Assessment Type:** Odoo Custom Module Development
- **Submission Deadline:** 22 June, 2026 at 11:59 PM
- **Module Technical Name:** `nn_fund_management`

---

## 1. Odoo Version

- **Core Framework:** Odoo 17.0 Community Edition (CE)
- **Database Management Engine:** PostgreSQL 15
- **Development Platform Base:** Python 3.10 / 3.11

---

## 2. Required Dependencies

The module specification declares direct framework dependencies on two essential Odoo core components within the `__manifest__.py` file:

- `base`: Provides the foundational Object-Relational Mapping (ORM) framework, relational field logic, and database tracking arrays.
- `mail`: Installs the complete Chatter framework, activity scheduling feeds, message thread mixins, and corporate workflow audit trail logging.

---

## 3. Installation Instructions

### System Prerequisites

Ensure that your local target deployment machine has the following tools installed and active:

- Docker Engine ($\ge$ v24.0.0)
- Docker Compose ($\ge$ v2.20.0)

### Deployment Steps

Execute these terminal commands from your root project repository workspace directory:

1. **Verify Directory Layout:**
   Ensure your project folder structure matches the layout below before starting the container:
   ```text
   odoo_workspace/
   ├── docker-compose.yml
   └── custom_addons/
       └── nn_fund_management/
           ├── __init__.py
           ├── __manifest__.py
           ├── models/
           │   ├── __init__.py
           │   ├── fund_account.py
           │   ├── incoming_fund.py
           │   ├── project.py
           │   ├── expense_head.py
           │   ├── fund_allocation.py
           │   ├── fund_requisition.py
           │   └── fund_transfer.py
           ├── security/
           │   └── security.xml
           └── views/
               └── fund_management_views.xml
   ```


2. **Configure Multi-Container Environment (`docker-compose.yml`):**
   Paste the following orchestration configuration into your root workspace folder:

```yaml
version: "3.8"
services:
  web:
    image: odoo:17.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./custom_addons:/mnt/extra-addons
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo_secure_pass
    command: -u nn_fund_management --dev=xml,reload
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo_secure_pass
    volumes:
      - odoo-db-data:/var/lib/postgresql/data
volumes:
  odoo-web-data:
  odoo-db-data:
```

3. **Wipe Interrupted Cached State (Recommended Clean Boot):**

```bash
docker compose down -v

```

4. **Spin Up the Production Stack Container Network:**

```bash
docker compose up

```

_The Odoo engine bootloader will automatically locate the custom package, execute database migrations, initialize custom models, and sync security parameters smoothly._ 5. **Access the Application Interface:**
Open a web browser tab and navigate to `http://localhost:8069`.

---

## 4. Configuration Steps

Follow these baseline steps within the Odoo UI shell layout to build your master record tracking network before executing live workflows:

1. **Enable Framework Developer System Configurations:**

- Click the top-right user settings wheel panel dropdown menu, select **Settings**, and scroll to click **Activate the developer mode**.
- Click your top-right profile user card layout option, and select **Become Superuser**.

2. **Configure Master Treasury Bank Nodes:**

- Navigate to **Fund Management ➔ Configuration ➔ Bank Accounts**.
- Click **New**. Input Name: `Dutch-Bangla Current Account` and Account Number: `DBBL-4491-2026`.
- Click **Save** (Cloud icon). Verify all balance boxes initialize to exactly `0.00` and are strictly locked as read-only.

3. **Configure Corporate Project Profiles:**

- Navigate to **Fund Management ➔ Configuration ➔ Projects**.
- Click **New**. Name: `Project Alpha (ERP Deployment)`. Click **Save**.
- Click **New**. Name: `Project Beta (Cloud Migration Infrastructure)`. Click **Save**.

4. **Configure Operational Cost Elements:**

- Navigate to **Fund Management ➔ Configuration ➔ Expense Heads**.
- Click **New**. Name: `Corporate Office Internet & Utilities`. Click **Save**.

---

## 5. Testing Instructions

Execute the following 5 integrated test scripts sequentially inside the browser user interface to verify that all transactional firewalls work properly.

### Test Case 1: External Liquidity Ingestion (Section 2)

- **Objective:** Validate automated balance aggregation and transaction reference uniqueness barriers.
- **Procedure:**

1. Go to **Operations ➔ Incoming Funds**. Click **New**.
2. Input: Fund Account = `Dutch-Bangla Current Account`, Received Amount = `2,500,000`, Transaction Reference = `TXN-2026-MARK1`, Sender/Source = `Main Corporate Shareholder Equity`.
3. Click **Save**. The system generates tracking serial sequence number: `INC-2026-0001`.
4. Click **Confirm / Post Amount**. The status badge moves to **Confirmed**.
5. **Verification Check:** Open **Configuration ➔ Bank Accounts**. Confirm that `Total Received` and `Available Unassigned Balance` dynamically calculate to **`2,500,000.00`**.
6. **Security Firewall Test:** Attempt to draft a second deposit targeting the identical transaction reference string `TXN-2026-MARK1` on the same bank account line item. Click Confirm.
7. **Expected System Reaction:** Odoo halts the database execution transaction and returns a strict PostgreSQL integrity constraint intercept block window error: _"Data Integrity Violation! The same transaction reference must not be used twice within the same fund account!"_

### Test Case 2: Fund Allocation Workflow Security (Section 3 & 4)

- **Objective:** Validate that mid-workflow capital remains locked at the treasury layer, eliminating double-allocation vulnerabilities.
- **Procedure:**

1. Go to **Operations ➔ Allocation Requests**. Click **New**.
2. Input: Fund Account = `Dutch-Bangla Current Account`, Allocation Amount = `1,000,000`, Target Project = `Project Alpha (ERP Deployment)`. Leave Target Expense Head empty.
3. Click **Save** (`ALLOC-2026-0001` starts as Draft). Click **Submit Request**. Status switches to **Submitted**.
4. **Verification Check (Mid-State Bank Hold):** Open the **Bank Accounts** dashboard view. Note that `Amount On Hold` displays exactly **`1,000,000.00`** and the spendable `Available Unassigned Balance` drops to **`1,500,000.00`**. This proves the money is safely locked mid-workflow.
5. Return to the allocation form. Complete the multi-tier review sequence: Click **GM Approve** $\rightarrow$ status changes to _GM Approval_. Click **Final MD Approve** $\rightarrow$ status changes to _Approved_.
6. **Verification Check (Project Delivery):** Open **Configuration ➔ Projects**. Select `Project Alpha`. Confirm its `Total Allocated Fund` and `Available Fund` fields dynamically update to exactly **`1,000,000.00`**.

### Test Case 3: Exclusive-OR (XOR) Relational Validation Gates

- **Objective:** Verify the backend rejects multi-destination routing input errors.
- **Procedure:**

1. Open a new **Allocation Request** form. Input an allocation amount of `100,000`.
2. Populate `Project Alpha` **AND** select `Corporate Office Internet & Utilities` simultaneously.
3. Click **Save** or **Submit**.
4. **Expected System Reaction:** The system blocks execution instantly, showing a clear Python validation modal message: _"Business Logic Fault! A transaction must use either a project or an expense head, not both."_

### Test Case 4: Project Expense Requisition Firewalls (Section 6)

- **Objective:** Verify that a submitted bill places a freeze on a project's budget and prevents overspending.
- **Procedure:**

1. Go to **Operations ➔ Project Requisitions**. Click **New**.
2. Input: Source Project = `Project Alpha (ERP Deployment)`, Requisition Amount = `300,000`, Purpose = `AWS Server Array Infrastructure Invoice`.
3. Click **Save** (`REQ-2026-0001` initializes), then click **Submit for Review**. Status turns to **Hold/Review**.
4. **Verification Check (Project Hold):** Navigate to **Configuration ➔ Projects** and select `Project Alpha`. Verify:

- `Total Allocated Fund` remains stably at `1,000,000.00`.
- `Requisition Hold` automatically aggregates to **`300,000.00`**.
- `Available Fund` dynamically drops to **`700,000.00`**.

5. Return to the requisition item. Click **Approve / Pay Bill**. Status turns to **Approved/Paid**.
6. **Verification Check (Permanent Outflow):** Re-examine your project dashboard. `Requisition Hold` clears back to `0.00`, `Total Spent Amount` climbs to **`300,000.00`**, and `Available Fund` stays safely locked at **`700,000.00`**.
7. **Budget Overdraft Firewall Test:** Create a new requisition targeting `Project Alpha` for an amount of **`800,000`** (which exceeds your remaining balance of 700,000). Click Submit.
8. **Expected System Reaction:** The backend blocks submission instantly: _"Budget Violation! Action Aborted. The requested expense exceeds the remaining Available Fund balance."_

### Test Case 5: Inter-Budget Capital Transfers (Section 8)

- **Objective:** Validate Section 8 rules for transferring funds securely between business budgets.
- **Procedure:**

1. Go to **Operations ➔ Internal Transfers**. Click **New**.
2. Input: Source Project = `Project Alpha (ERP Deployment)`, Destination Project = `Project Beta (Cloud Migration Infrastructure)`, Transfer Amount = `200,000`, Reason = `Re-assigning extra infrastructure buffer cash`.
3. Click **Save** (`XFER-2026-0001` initializes), then click **Submit Transfer Hold**. Status turns to **Hold/Review**.
4. **Verification Check (Pending Transfer Hold):** View your **Projects Dashboard**:

- `Project Alpha`'s `Transfer Hold` field updates to **`200,000.00`**, and its net spendable `Available Fund` line drops to **`500,000.00`**.
- `Project Beta`'s balance tracks at `0.00` (proves pending transfer cash cannot be double-spent).

5. Return to the transfer document. Click **Approve & Execute**. Status changes to **Approved**.
6. **Verification Check (Multi-Node Routing):** Examine both project profiles:

- **Project Alpha:** `Transfer Hold` clears to `0.00`, `Outgoing Transfers` logs **`200,000.00`**, and `Available Fund` stays locked at **`500,000.00`**.
- **Project Beta:** `Incoming Transfers` logs **`200,000.00`**, and its spendable `Available Fund` ledger scales cleanly to **`200,000.00`**.

---

## 6. Assumptions

During module construction, the following technical and operational logic assumptions were made:

- **Single Operational Currency:** System architecture ledger processing tracking loops operate under a single global currency index wrapper (configured as Bangladeshi Taka - BDT). Multi-currency automatic conversion pipelines were omitted to prioritize calculation loops.
- **Single-Company Isolation:** To avoid multi-company analytics cross-leaks under default installation rules, the workspace is configured to execute within a single active corporate wrapper instance (`res.company`).
- **The Authorized Role Rule:** The implementation assumes that the users interacting with the system form elements are properly trained internal accounting employees with operational access privileges. User profile tracking lookups are globally granted access permissions via Odoo's default base user profile group (`base.group_user`).

---

## 7. Known Limitations

- **Section 7 (Bill Control System) Omission:** Section 7 requires an advanced vendor invoice-matching layer. As Page 2 of the assessment specifications explicitly notes that _full task completion is not mandatory_, this component was strategically omitted to focus development on the core ledger calculation models, cross-model hold systems, and double-spending protection rules.
- **Workflow Phase Variation:** Allocation Requests utilize the full multi-tier approval states (_Submitted $\rightarrow$ GM Approval $\rightarrow$ MD Approval $\rightarrow$ Approved_). Requisitions and Transfers use a simplified sequence (_Submitted $\rightarrow$ Approved_), which can be easily expanded using reusable approval logic during the live technical evaluation.
- **Static Access Assignment:** All custom security permission maps are aggregated under a single global group (`base.group_user`). Granular row-isolation record rules (`ir.rule`) were omitted, meaning that role separation must be managed directly using visual form control configurations during technical walkthroughs.

```

```
