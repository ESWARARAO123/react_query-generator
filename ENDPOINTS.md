# API Endpoints Documentation

## Backend Endpoints

### 1. Query Processing
- **Endpoint**: `/api/execute`
- **Method**: POST
- **Description**: Processes natural language queries and converts them to SQL
- **Request Body**: 
  ```json
  {
    "query": "string"
  }
  ```
- **Response**: 
  ```json
  {
    "sql": "string",
    "data": "array of objects",
    "columns": ["string"]
  }
  ```

### 2. Database Schema
- **Endpoint**: `/api/schema`
- **Method**: GET
- **Description**: Retrieves the complete database schema
- **Response**: 
  ```json
  {
    "schema": {
      "table_name": {
        "columns": [
          {
            "name": "string",
            "type": "string"
          }
        ]
      }
    }
  }
  ```

### 3. Available Tables
- **Endpoint**: `/api/tables`
- **Method**: GET
- **Description**: Retrieves list of available tables
- **Response**: 
  ```json
  {
    "tables": ["table1", "table2", ...]
  }
  ```

### 4. CSV Download
- **Endpoint**: `/api/download-csv`
- **Method**: POST
- **Description**: Generates and returns a CSV file for download
- **Request Body**: 
  ```json
  {
    "data": "array of objects",
    "columns": ["string"],
    "filename": "string"
  }
  ```
- **Response**: 
  ```json
  {
    "filename": "string",
    "content": "base64 encoded string"
  }
  ```

## Frontend Routes

### 1. Main Application
- **Route**: `/`
- **Description**: Main application interface with query input and results display

### 2. Table Selection
- **Route**: `/tables`
- **Description**: Interface for selecting and viewing available tables

### 3. Query History
- **Route**: `/history`
- **Description**: View and manage query history

## Port Configuration
- Frontend: `http://localhost:3121`
- Backend: `http://localhost:5000`

## File Structure
```
chat2sql/
├── backend/
│   ├── main.py
│   ├── model.py
│   ├── database.py
│   └── config.py
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   └── index.js
│   └── public/
└── myenv/
```

## Development Setup
1. Backend:
   ```bash
   cd backend
   python main.py
   ```

2. Frontend:
   ```bash
   cd frontend
   npm start
   ```

The frontend will be available at `http://localhost:3121` and will communicate with the backend at `http://localhost:5000`. 