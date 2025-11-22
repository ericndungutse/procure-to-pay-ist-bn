## Approval Decision + AI Purchase Order Generation Flow

The sequence diagram below illustrates what happens internally when an approver makes a decision (approve or reject) on a purchase request.  
It includes:

- Row-level locking using `select_for_update()`
- Sequential multi-level approval checks
- Decision creation
- Status updates (approved/rejected)
- Triggering an AI service to generate a Purchase Order (PO)
- Uploading the generated PO to a storage provider (e.g., Cloudinary)
- Saving the PO URL back to the database

```mermaid
sequenceDiagram
    participant A as Approver
    participant API as Django API (DecisionManager)
    participant DB as Database
    participant AI as AI PO Generator Service
    participant ST as File Storage (e.g., Cloudinary)

    A->>API: /decide
    API->>DB: select_for_update() lock PR row
    DB-->>API: PR locked and loaded

    API->>DB: Check previous decisions, status, role
    DB-->>API: Validation OK

    API->>DB: Create Decision (APPROVED or REJECTED)
    DB-->>API: Decision saved

    alt Decision = REJECTED
        API->>DB: Update PR.status = REJECTED
        DB-->>API: Saved
        API-->>A: Response: Request Rejected
    else Decision = APPROVED
        API->>DB: Check if all approval levels approved
        DB-->>API: Yes, this is the final approval

        API->>DB: Update PR.status = APPROVED
        DB-->>API: Saved

        %% --- AI PO Creation Trigger ---
        API->>AI: Send PR data + proforma URL
        AI->>ST: Upload generated Purchase Order
        ST-->>AI: PO URL returned

        AI-->>API: PO metadata + URL

        API->>DB: Save PO reference in PurchaseRequest
        DB-->>API: PO saved

        API-->>A: Response: Final Approved + PO generated
    end
```
