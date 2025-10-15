# Lacos Microcredito API

This is a simple FastAPI application for managing clients, locations, and documents for Lacos Microcredito.

## Features

- Authentication system with JWT tokens
- CRUD operations for clients
- CRUD operations for locations
- CRUD operations for documents with file upload/download capabilities

## Prerequisites

- Python 3.7+
- PostgreSQL database

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd LacosAPI
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   - Make sure PostgreSQL is running
   - Update the DATABASE_URL in the .env file if needed
   - The application will automatically create the funcionarios table and a default admin user

## Running the Application

1. Start the server:
   ```
   uvicorn app.main:app --reload
   ```

2. Access the API documentation at:
   - Interactive API docs: http://localhost:8000/docs
   - Alternative API docs: http://localhost:8000/redoc

## Default Admin User

The application creates a default admin user on startup:

- Username: natalia.massinga
- Email: natalia.massinga@example.com
- Password: Ractis@23

## Complete List of API Routes

### Authentication Routes
- `POST /api/auth/token` - Obtain access token

### Clients Routes
- `POST /api/clientes/create` - Create a new client
- `GET /api/clientes/list` - List all clients
- `GET /api/clientes/get/{cliente_id}` - Get a specific client
- `PUT /api/clientes/update/{cliente_id}` - Update a client
- `DELETE /api/clientes/delete/{cliente_id}` - Delete a client

### Locations Routes
- `POST /api/localizacoes/create` - Create a new location
- `GET /api/localizacoes/list` - List all locations
- `GET /api/localizacoes/get/{localizacao_id}` - Get a specific location
- `PUT /api/localizacoes/update/{localizacao_id}` - Update a location
- `DELETE /api/localizacoes/delete/{localizacao_id}` - Delete a location

### Documents Routes
- `POST /api/documentos/create` - Create a new document with file upload
- `GET /api/documentos/list` - List all documents
- `GET /api/documentos/get/{documento_id}` - Get a specific document
- `GET /api/documentos/get/{documento_id}/download` - Download a document
- `DELETE /api/documentos/delete/{documento_id}` - Delete a document

### Funcionarios Routes
- `POST /api/funcionarios/create` - Create a new funcionario
- `GET /api/funcionarios/list` - List all funcionarios
- `GET /api/funcionarios/get/{funcionario_id}` - Get a specific funcionario
- `PUT /api/funcionarios/update/{funcionario_id}` - Update a funcionario
- `DELETE /api/funcionarios/delete/{funcionario_id}` - Delete a funcionario

## Authentication

All endpoints except `/api/auth/token` require authentication. To authenticate:

1. Send a POST request to `/api/auth/token` with form data:
   - username: natalia.massinga
   - password: Ractis@23

2. Use the returned access token in the Authorization header:
   ```
   Authorization: Bearer <access_token>
   ```

## Database Schema

The application works with the following tables:

1. `clientes` - Client information
2. `localizacao` - Location information
3. `documentos` - Document information with file storage
4. `funcionarios` - Employee information for authentication

These tables should already exist in your PostgreSQL database as per your requirements.