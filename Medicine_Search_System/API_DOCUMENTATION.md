# Medicine Search System API Documentation

## Base URL
```
http://localhost:5000/api/v1
```

## Authentication

The API uses JWT (JSON Web Token) for authentication. Include the token in the `Authorization` header:
```
Authorization: Bearer <your_token>
```

## Endpoints

### Authentication

#### Register New User
```
POST /api/v1/auth/register

Request Body:
{
    "username": "string",
    "email": "string",
    "password": "string"
}

Response: 201 Created
{
    "token": "jwt_token_string",
    "user": {
        "id": 1,
        "username": "string",
        "email": "string",
        "created_at": "2025-11-18T12:00:00"
    }
}
```

#### Login
```
POST /api/v1/auth/login

Request Body:
{
    "username": "string",
    "password": "string"
}

Response: 200 OK
{
    "token": "jwt_token_string",
    "user": {
        "id": 1,
        "username": "string",
        "email": "string",
        "created_at": "2025-11-18T12:00:00"
    }
}
```

### Medicine Search

#### Search Medicines
```
GET /api/v1/medicines/search?q=paracetamol&manufacturer=cipla&discontinued=active&limit=50

Query Parameters:
- q: Search query (optional)
- manufacturer: Filter by manufacturer (optional)
- discontinued: Filter by status - 'active', 'discontinued', or 'all' (optional, default: 'all')
- limit: Maximum number of results (optional, default: 50)

Response: 200 OK
{
    "count": 10,
    "medicines": [
        {
            "name": "string",
            "manufacturer": "string",
            "composition": "string",
            "uses": "string",
            "side_effects": "string",
            "pack_size_label": "string",
            "is_discontinued": "Yes/No"
        }
    ]
}
```

#### Get Medicine Details
```
GET /api/v1/medicines/{index}

Response: 200 OK
{
    "medicine": {
        "name": "string",
        "manufacturer": "string",
        "composition": "string",
        "uses": "string",
        "side_effects": "string",
        "pack_size_label": "string",
        "is_discontinued": "Yes/No"
    }
}
```

### Saved Searches (Requires Authentication)

#### Get Saved Searches
```
GET /api/v1/saved-searches
Headers: Authorization: Bearer <token>

Response: 200 OK
{
    "saved_searches": [
        {
            "id": 1,
            "query": "string",
            "filters": "string",
            "created_at": "2025-11-18T12:00:00"
        }
    ]
}
```

#### Create Saved Search
```
POST /api/v1/saved-searches
Headers: Authorization: Bearer <token>

Request Body:
{
    "query": "string",
    "filters": "string (optional)"
}

Response: 201 Created
{
    "saved_search": {
        "id": 1,
        "query": "string",
        "filters": "string",
        "created_at": "2025-11-18T12:00:00"
    }
}
```

#### Delete Saved Search
```
DELETE /api/v1/saved-searches/{search_id}
Headers: Authorization: Bearer <token>

Response: 200 OK
{
    "message": "Saved search deleted"
}
```

### Medicine Comparisons (Requires Authentication)

#### Get Comparisons
```
GET /api/v1/comparisons
Headers: Authorization: Bearer <token>

Response: 200 OK
{
    "comparisons": [
        {
            "id": 1,
            "medicine_indices": "0,1,2",
            "title": "string",
            "created_at": "2025-11-18T12:00:00"
        }
    ]
}
```

#### Create Comparison
```
POST /api/v1/comparisons
Headers: Authorization: Bearer <token>

Request Body:
{
    "medicine_indices": "0,1,2",
    "title": "string (optional)"
}

Response: 201 Created
{
    "comparison": {
        "id": 1,
        "medicine_indices": "0,1,2",
        "title": "string",
        "created_at": "2025-11-18T12:00:00"
    }
}
```

### Drug Interaction Checker

#### Check Interactions
```
POST /api/v1/interactions/check

Request Body:
{
    "medicine_indices": [0, 1, 2]
}

Response: 200 OK
{
    "medicines": [...],
    "interactions": [
        {
            "medicine1": "string",
            "medicine2": "string",
            "type": "duplicate_ingredient|known_interaction|no_interactions",
            "warning": "string",
            "severity": "high|medium|none",
            "recommendation": "string",
            "ingredients": ["string"] (optional)
        }
    ]
}
```

### Statistics

#### Get Database Statistics
```
GET /api/v1/stats

Response: 200 OK
{
    "total_medicines": 100,
    "total_manufacturers": 50,
    "discontinued_count": 10,
    "active_count": 90
}
```

## Error Responses

All endpoints may return the following error responses:

```
400 Bad Request
{
    "error": "Error message"
}

401 Unauthorized
{
    "error": "Token is missing|Invalid token|Token has expired"
}

404 Not Found
{
    "error": "Resource not found"
}

500 Internal Server Error
{
    "error": "Internal server error"
}
```

## Rate Limiting

Currently, there are no rate limits implemented. In production, consider implementing rate limiting to prevent abuse.

## CORS

CORS is not enabled by default. For mobile applications, you may need to enable CORS in the Flask application.

## Example Usage (Python)

```python
import requests

# Register
response = requests.post('http://localhost:5000/api/v1/auth/register', json={
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'password123'
})
token = response.json()['token']

# Search medicines
response = requests.get('http://localhost:5000/api/v1/medicines/search?q=paracetamol')
medicines = response.json()['medicines']

# Create saved search (authenticated)
headers = {'Authorization': f'Bearer {token}'}
response = requests.post(
    'http://localhost:5000/api/v1/saved-searches',
    headers=headers,
    json={'query': 'paracetamol'}
)

# Check drug interactions
response = requests.post(
    'http://localhost:5000/api/v1/interactions/check',
    json={'medicine_indices': [0, 1, 2]}
)
interactions = response.json()['interactions']
```

## Example Usage (cURL)

```bash
# Register
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
TOKEN=$(curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}' \
  | jq -r '.token')

# Search medicines
curl http://localhost:5000/api/v1/medicines/search?q=paracetamol

# Create saved search
curl -X POST http://localhost:5000/api/v1/saved-searches \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"paracetamol"}'

# Check interactions
curl -X POST http://localhost:5000/api/v1/interactions/check \
  -H "Content-Type: application/json" \
  -d '{"medicine_indices":[0,1,2]}'
```
