# Procure-to-Pay System

A web-based purchase request management system that streamlines the procurement process from request creation to approval and finance processing.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Create a Virtual Environment](#2-create-a-virtual-environment)
  - [3. Install Dependencies](#3-install-dependencies)
  - [4. Set Up Environment Variables](#4-set-up-environment-variables)
  - [5. Create PostgreSQL Database](#5-create-postgresql-database)
  - [6. Run Database Migrations](#6-run-database-migrations)
  - [7. Create Initial Users (Optional)](#7-create-initial-users-optional)
  - [8. Start the Development Server](#8-start-the-development-server)
- [API Documentation](#api-documentation)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Additional Documentation](#additional-documentation)
- [Need Help?](#need-help)

## Overview

This system helps organizations manage purchase requests efficiently. Staff members can create purchase requests, which then go through an approval workflow before being processed by the finance team. The system supports different user roles with appropriate access levels:

- **Staff**: Create and view their own purchase requests
- **Approvers**: Review and approve purchase requests from all staff
- **Finance**: Access all purchase requests for payment processing

## Features

- User authentication and authorization
- Purchase request creation and management
- Role-based access control
- Approval workflow support
- Secure RESTful API

## Prerequisites

Before setting up the project, make sure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **PostgreSQL** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **pip** - Python package manager (usually comes with Python)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd procure-to-pay-ist-bn
```

### 2. Create a Virtual Environment

Create and activate a virtual environment to isolate project dependencies:

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root directory with the following variables:

```env
SECRET_KEY=your-secret-key-here
DB_NAME=procure_to_pay_ist
DB_USER=postgres
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432
```

Replace the values with your actual configuration. The `SECRET_KEY` should be a long random string (Django can generate one for you).

### 5. Create PostgreSQL Database

Create a new PostgreSQL database:

```bash
# Login to PostgreSQL
psql -U postgres

# Create the database
CREATE DATABASE procure_to_pay_ist;

# Exit PostgreSQL
\q
```

Make sure the database name matches the `DB_NAME` in your `.env` file.

### 6. Run Database Migrations

Apply database migrations to set up the required tables:

```bash
python manage.py migrate
```

### 7. Create Initial Users (Optional)

Seed the database with initial user accounts:

```bash
python manage.py seed_users
```

This creates sample users for testing (staff, approvers, and finance admin).

### 8. Start the Development Server

Run the Django development server:

```bash
python manage.py runserver
```

The server will start at `http://localhost:8000/`. You can now test the API endpoints locally.

## API Documentation

### Using the API

Once your development server is running, you can interact with the API in several ways:

1. **Postman Collection** (Recommended): Use the interactive Postman documentation with pre-configured requests and examples:

   - **[Postman API Documentation](https://documenter.getpostman.com/view/50243263/2sB3dHVYGG)**
   - Import the collection into Postman and update the base URL to `http://localhost:8000` for local testing

2. **API Endpoints**: The main endpoints available are:

   - `POST /api/v1/accounts/login/` - User login
   - `GET /api/v1/requests/` - List purchase requests
   - `POST /api/v1/requests/` - Create a purchase request
   - `GET /api/v1/requests/{id}/` - Get purchase request details

3. **Testing Tools**: You can also use tools like curl, HTTPie, or any REST client to test the endpoints.

**Note**: The Postman documentation shows example requests. When testing locally, make sure your development server is running and use `http://localhost:8000` as the base URL.

For additional technical documentation and architecture details, see the `/docs` folder.

## Running Tests

Run the test suite to verify everything is working:

```bash
pytest
```

## Project Structure

- `/accounts` - User authentication and management
- `/purchase_requests` - Purchase request functionality
- `/config` - Django project configuration
- `/docs` - Additional documentation and diagrams

## Additional Documentation

- **Technical Documentation**: For architecture diagrams and database design, check the `/docs` folder

## Need Help?

If you encounter any issues during setup, please check:

1. All prerequisites are installed correctly
2. PostgreSQL is running and accessible
3. Environment variables are set correctly
4. Database migrations have been applied
5. The development server is running before testing API endpoints

For technical documentation and detailed guides, refer to the `/docs` folder. For API request examples and testing, use the [Postman API Documentation](https://documenter.getpostman.com/view/50243263/2sB3dHVYGG).
