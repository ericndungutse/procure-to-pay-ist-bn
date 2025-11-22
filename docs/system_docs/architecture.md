# System Architecture Documentation

This document provides an overview of the Procure-to-Pay system architecture, including the high-level design and component interactions.

## Architecture Diagram

![System Architecture](architecture.png)

## Overview

The Procure-to-Pay system is built using a **RESTful API architecture** based on Django and Django REST Framework. The system follows a layered architecture pattern with clear separation of concerns.

## Architecture Layers

### 1. Presentation Layer

The presentation layer consists of REST API endpoints that handle HTTP requests and responses:

- **Authentication Endpoints** (`/api/v1/accounts/`)

  - User login and token generation
  - JWT-based authentication

- **Purchase Request Endpoints** (`/api/v1/requests/`)
  - List and create purchase requests
  - Retrieve individual purchase request details

### 2. Application Layer

The application layer contains business logic organized into services:

- **AuthService** (`accounts/services.py`)

  - Handles authentication business logic
  - Token generation and management

- **PurchaseRequestService** (`purchase_requests/services.py`)
  - Purchase request filtering and access control
  - Role-based query filtering logic

### 3. Domain Layer

The domain layer consists of Django models that represent the business entities:

- **User Model** (`accounts/models.py`)

  - Custom user model with role-based access
  - Roles: Staff, Approver Level 1, Approver Level 2, Finance

- **PurchaseRequest Model** (`purchase_requests/models.py`)
  - Purchase request entity with status workflow
  - Relationships to users and approval levels

### 4. Data Layer

The data layer consists of:

- **PostgreSQL Database**

  - Relational database for persistent data storage
  - Tables for users, purchase requests, and related entities

- **Django ORM**
  - Object-relational mapping layer
  - Database migrations and schema management

## Key Components

### Authentication & Authorization

- **JWT Authentication**: Uses `djangorestframework-simplejwt` for secure token-based authentication
- **Role-Based Access Control**: Implements permission checks based on user roles
- **Custom Permissions**: `IsStaffOrReadOnly` permission class for endpoint access control

### API Design

- **RESTful Principles**: Follows REST conventions for resource-based URLs
- **Serializers**: Data validation and transformation using DRF serializers
- **ViewSets/Generic Views**: Reusable view classes for CRUD operations

### Service Layer

Business logic is separated into service classes to maintain clean architecture:

- Services handle business rules and data access logic
- Views remain thin and delegate to services
- Easy to test and maintain

## Data Flow

1. **Client Request** → HTTP request sent to API endpoint
2. **Authentication Middleware** → Validates JWT token
3. **Permission Check** → Verifies user role and permissions
4. **View Layer** → Receives request and determines action
5. **Service Layer** → Executes business logic and data filtering
6. **Model Layer** → Accesses database through ORM
7. **Database** → Returns data
8. **Serializer** → Transforms data for response
9. **Client Response** → JSON response returned to client

## Technology Stack

- **Framework**: Django 5.2.8
- **API Framework**: Django REST Framework 3.16.1
- **Authentication**: djangorestframework-simplejwt 5.5.1
- **Database**: PostgreSQL
- **ORM**: Django ORM
- **Environment Management**: python-decouple

## Security Considerations

- JWT tokens for stateless authentication
- Password hashing (Django's default hashers)
- Role-based access control at both view and service levels
- SQL injection protection through Django ORM

## Scalability

The architecture supports scalability through:

- Stateless API design (JWT tokens)
- Service layer abstraction for easy extension
