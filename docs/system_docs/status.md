# System Status & Integration Notes

This page documents the current integration and endpoint status for the Procure-to-Pay system. It lists the deployed frontend, source repo, and the state of key API endpoints and features.

## Frontend

- Deployed frontend (demo): https://procure-to-pay-sigma.vercel.app/
- Frontend repository: https://github.com/ericndungutse/procure-to-pay-fn-frontend

## Endpoint & Feature Status

The project is under active development. The table below summarizes implemented, partially implemented, and not-yet-integrated features.

### Authentication
- `POST /api/v1/accounts/login/` — Implemented

### Purchase Requests
- `GET /api/v1/requests/` — Implemented (server-side role filtering exists; advanced query filtering by params is NOT implemented)
- `POST /api/v1/requests/` — Implemented
- `GET /api/v1/requests/{id}/` — Implemented
- `PATCH /api/v1/requests/{id}/` — NOT implemented (update endpoint not available)
- `PATCH /api/v1/requests/{id}/upload-receipt` — Implemented (saves receipt URL and triggers verification call)

### Decisions / Approvals
- `POST /api/v1/requests/{id}/approve` — Decision creation implemented (concurrency-safe manager exists)
- `POST /api/v1/requests/{id}/reject` — Implemented
- Integration note: Decision logic (the `DecisionManager`) is implemented; UI integration and some downstream hooks may be pending.

### Purchase Order / Receipt Mismatch
- Verification workflow is implemented in the file-processor service and emits mismatch messages when a discrepancy is detected.
- This repo contains a `PurchaseOrderReceiptMismatch` model and a consumer that records incoming mismatch messages, but the end-to-end UI/workflow integration is NOT complete.

## Notes & Next Steps
- If you rely on the update purchase request endpoint or advanced filtering, treat those as TODO items.
- Consider adding pagination and filtering to the mismatches endpoint if you expect many records.
- For production, restrict the mismatches listing endpoint (current implementation is unprotected). Implement authentication/authorization for any admin or sensitive endpoints.
