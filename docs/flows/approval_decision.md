# 💸 Purchase Request Decision Flow (Async PO Generation)

This flow handles approver decisions (Approve/Reject) while offloading heavy Purchase Order (PO) generation to a serverless Lambda function, ensuring the Django API remains fast and responsive by performing the PO creation asynchronously.

## Components

- **A:** Approver (user)
- **API:** Django API (`DecisionManager`)
- **DB:** Stores PRs, Decisions, status
- **LFS:** Lambda File Processor (OCR + OpenAI PO generation)
- **ST:** File Storage (e.g., Cloudinary)
- **MQ:** Message Queue (e.g., RabbitMQ)

## Flow

### 1\. Decision Submission (`/approve` or `/reject`)

1.  **A** submits decision to **API**.
2.  **API** locks PR row (`select_for_update()`), validates request, and creates **Decision** in **DB**.

### 2\. Outcome

#### REJECT

- PR.status → `REJECTED`
- Lock released; API returns `Request Rejected`.

#### APPROVE

- If final approval: PR.status → `APPROVED (Final)`
- Trigger **LFS** with **Full PR Data** (including ID, Amount, Description, and Proforma URL).
- Lock released; API returns `Final Approved (PO Gen in progress)`.

### 3\. Asynchronous PO Generation (Updated)

1.  **LFS** uses the **PR Data** and the **Proforma file** to process and generate the final PO (OCR + OpenAI).
2.  Uploads PO to **ST**, obtains **PO URL**.
3.  Publishes **PO URL** to **MQ**.
4.  **API** consumes message and updates **DB** with PO URL.

## Sequence Diagram (Updated)

```mermaid
sequenceDiagram
    participant A as Approver
    participant API as Django API (DecisionManager)
    participant DB as Database
    participant LFS as Lambda File Processor (OCR/AI)
    participant ST as File Storage (e.g., Cloudinary)
    participant MQ as Message Queue (RabbitMQ)
   
    alt Decision is APPROVE
        A->>API: **/approve**
        API->>DB: select_for_update() lock PR row
        DB-->>API: PR locked and loaded
       
        API->>DB: Check previous decisions, status, role
        DB-->>API: Validation OK
       
        API->>DB: Create Decision (APPROVED)
        DB-->>API: Decision saved
       
        API->>DB: Check if all approval levels approved
        DB-->>API: Yes, this is the final approval
       
        API->>DB: Update PR.status = APPROVED (Final)
        DB-->>API: Saved
       
        %% --- ASYNCHRONOUS PO Creation Trigger ---
        API->>LFS: **Trigger** (Full PR Data: ID, Proforma URL, Amount, Title, etc.)
        API-->>A: Response: Final Approved (PO Gen in progress)
       
        LFS->>LFS: Process File + **Use PR Data** (OCR, Open AI)
        LFS->>ST: **Upload** Generated Purchase Order (PDF)
        ST-->>LFS: PO URL returned
       
        LFS->>MQ: **Publish** PO Metadata + URL (Async Update)
       
        MQ->>API: **Consume** PO Metadata + URL
        API->>DB: Save PO URL to PurchaseRequest
        DB-->>API: PO URL saved
    else Decision is REJECT
        A->>API: **/reject**
        API->>DB: select_for_update() lock PR row
        DB-->>API: PR locked and loaded
       
        API->>DB: Check previous decisions, status, role
        DB-->>API: Validation OK
       
        API->>DB: Create Decision (REJECTED)
        DB-->>API: Decision saved
       
        API->>DB: Update PR.status = REJECTED
        DB-->>API: Saved
        API-->>A: Response: Request Rejected
    end
```
