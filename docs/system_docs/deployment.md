# Procure-to-Pay CI/CD Deployment

This document summarizes the CI/CD workflow for the Procure-to-Pay system.

```mermaid
---
config:
  layout: elk
  look: classic
---
flowchart LR
    subgraph CICD["CI/CD Pipeline"]
        PR["Pull Request Created"]:::prEvent
        Merge["Push to Main"]:::mergeEvent

        %% PR Flow
        TestPR["Test Job"]:::test
        BuildPR["Build Job"]:::build
        DockerHub["Docker Hub"]:::docker
        DeployQA["Deploy QA Job"]:::deploy
        PR --> TestPR --> BuildPR --> DockerHub --> DeployQA

        %% Main Flow
        TestMain["Test Job"]:::test
        BuildMain["Build Job"]:::build
        DockerHub2["Docker Hub"]:::docker
        DeployProd["Deploy Prod Job"]:::deploy
        Merge --> TestMain --> BuildMain --> DockerHub2 --> DeployProd
    end

    %% QA Environment
    subgraph QAEnv["QA Environment"]
        QA["QA Environment<br>Render"]:::qa
    end
    DeployQA --> QA

    %% Production Environment
    subgraph ProdEnv["Production Environment"]
        Prod["Production<br>Azure Container Apps"]:::prod
    end
    DeployProd --> Prod

    %% Backend API
    API["Procure-to-Pay API"]:::api
    QA --> API
    Prod --> API

    %% Class Definitions
    classDef prEvent fill:#8b5cf6,stroke:#6d28d9,color:#fff
    classDef mergeEvent fill:#10b981,stroke:#059669,color:#fff
    classDef test fill:#f59e0b,stroke:#d97706,color:#fff
    classDef build fill:#3b82f6,stroke:#2563eb,color:#fff
    classDef docker fill:#2496ed,stroke:#1d7dc4,color:#fff
    classDef deploy fill:#ec4899,stroke:#db2777,color:#fff
    classDef qa fill:#8b5cf6,stroke:#6d28d9,color:#fff
    classDef prod fill:#0078d4,stroke:#005a9e,color:#fff
    classDef api fill:#047857,stroke:#065f46,color:#fff
```

## Overview

- **Pull Request Flow (QA)**

  - Triggered on PR creation.
  - Test job runs unit tests.
  - Build job creates Docker image.
  - Image pushed to Docker Hub.
  - QA deployment triggers Render environment.

- **Main Branch Flow (Production)**

  - Triggered on merge to main.
  - Test job verifies code.
  - Build job creates Docker image.
  - Image pushed to Docker Hub.
  - Production deployment triggers Azure Container Apps.

- **Backend API**

  - Procure-to-Pay API is accessed by both QA and production environments.
  - Handles staff, approver, and finance user requests.

- **Color Coding**

  - PR Event: Purple
  - Merge Event: Green
  - Test Job: Orange
  - Build Job: Blue
  - Docker Hub: Light Blue
  - Deploy Job: Pink
  - QA Env: Purple
  - Production Env: Blue
  - Procure-to-Pay API: Green
