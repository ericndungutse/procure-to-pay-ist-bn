# 🧾 Receipt Upload Flow (Asynchronous Audit with Direct Notification)

This flow details the asynchronous process triggered when a **Staff User** uploads a product receipt.

1.  The user first uploads the receipt file to the **Storage Service (ST)** and sends the resulting URL to the **Django API**.
2.  The **API** validates the request, saves the `receipt_url` in the database, and immediately responds to the user.
3.  The **API** then asynchronously triggers the **Lambda File Processor (LFS)**, providing the Receipt URL, the corresponding **Purchase Order (PO) URL**, and the PR data.
4.  The **LFS** uses **OCR/AI** to compare the contents of the Receipt against the PO.
5.  If a mismatch is detected, the **LFS** publishes a `Discrepancy Report` to the **Message Queue (MQ)**.
6.  The **API** consumes this message, saves the report to the `DiscrepancyReports` table in the **DB**, and directly sends an **email notification** to the Purchase Request creator.

## Sequence Diagram

```mermaid
sequenceDiagram
    participant U as Staff User
    participant ST as Storage Service (e.g., Cloudinary)
    participant API as Django API
    participant DB as Database
    participant LFS as Lambda File Processor (OCR/AI)
    participant MQ as Message Queue (RabbitMQ)

    %% Step 1: Staff uploads receipt file
    U->>ST: Upload receipt file
    ST-->>U: Return receipt URL

    %% Step 2: Staff submits receipt URL
    U->>API: POST /api/requests/{id}/upload-receipt (Receipt URL)

    %% Step 3: API validates request and saves URL
    API->>DB: Load PurchaseRequest by ID (to get PO URL & Creator's Email)
    DB-->>API: PurchaseRequest loaded

    API->>API: Validate user, status, etc.

    API->>DB: Update PurchaseRequest.receipt_url = URL
    DB-->>API: Receipt URL saved

    %% Step 4: API triggers asynchronous audit
    API->>LFS: **Trigger Audit** (PR ID, Receipt URL, PO URL)
    API-->>U: Response: Receipt uploaded (Audit in progress)

    %% Step 5: LFS performs comparison (Asynchronous)
    LFS->>LFS: Extract data from Receipt & PO (OCR/AI)
    LFS->>LFS: **Compare** Receipt vs PO (OpenAI)

    alt Discrepancy Found
        LFS->>LFS: Generate Discrepancy Report dict
        LFS->>MQ: **Publish** Discrepancy Report
        MQ->>API: **Consume** Discrepancy Report
        API->>DB: Insert into DiscrepancyReports table
        DB-->>API: Report saved
        API->>API: **Send Discrepancy Alert Email** (to PR creator)
    else No Discrepancy
        LFS->>LFS: Audit complete (No further action)
    end
```
