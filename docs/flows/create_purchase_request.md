# Purchase Request Creation Flow

This sequence diagram shows the process when a `staff` user creates a new purchase request. The user first uploads a proforma document to a storage service (e.g., Cloudinary), then submits the purchase request to the Django API, which saves the request in the database.

```mermaid
sequenceDiagram
    participant U as Staff User
    participant ST as Storage Service (e.g., Cloudinary)
    participant API as Django API
    participant DB as Database

    %% Step 1: Upload proforma to storage
    U->>ST: Upload proforma file
    ST-->>U: Return file URL

    %% Step 2: Submit purchase request with proforma URL
    U->>API: POST /api/requests/ (title, description, amount, proforma URL)

    %% Step 3: API validates request
    API->>API: Validate fields and user authentication

    %% Step 4: API creates PurchaseRequest record
    API->>DB: INSERT PurchaseRequest (status=PENDING, proforma URL, created_by)
    DB-->>API: PurchaseRequest saved

    %% Step 5: API returns response
    API-->>U: Response: PurchaseRequest created (ID, status, details)
```
