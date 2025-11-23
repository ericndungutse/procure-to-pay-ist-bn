# Receipt Upload Flow (URL Update Only)

This sequence diagram describes the process when the staff user uploads the receipt for an approved purchase request.  
The front-end first uploads the file to the storage provider (Cloudinary or similar), then submits the file URL to the Django API.  
The API simply updates the `receipt` field of the PurchaseRequest.

```mermaid
sequenceDiagram
    participant U as Staff User
    participant ST as Storage Service (e.g., Cloudinary)
    participant API as Django API
    participant DB as Database

    %% Step 1: Staff uploads receipt file
    U->>ST: Upload receipt file
    ST-->>U: Return receipt URL

    %% Step 2: Staff submits receipt URL
    U->>API: POST /api/requests/{id}/upload-receipt (receipt URL)

    %% Step 3: API validates request
    API->>DB: Load PurchaseRequest by ID
    DB-->>API: PurchaseRequest loaded

    API->>API: Validate user owns PR + PR is approved or ready for receipt upload

    %% Step 4: Save receipt URL
    API->>DB: Update PurchaseRequest.receipt_url = URL
    DB-->>API: Receipt saved

    %% Step 5: API returns success response
    API-->>U: Response: Receipt uploaded (URL saved)
```
