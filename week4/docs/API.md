# API Documentation

## Overview

This document describes the REST API for the Notes and Action Items service. The API is built with FastAPI and uses JSON for request/response bodies.

## Base URL

```
http://localhost:8000
```

---

## Notes

### List Notes

**GET** `/notes/`

Returns all notes.

**Response** `200 OK`
```json
[
  {
    "id": 1,
    "title": "string",
    "content": "string"
  }
]
```

---

### Create Note

**POST** `/notes/`

Creates a new note.

**Request Body**
```json
{
  "title": "string (required, min 1, max 200 chars)",
  "content": "string (required, min 1 char)"
}
```

**Response** `201 Created`
```json
{
  "id": 1,
  "title": "string",
  "content": "string"
}
```

**Errors**
- `422 Unprocessable Entity` - Validation error

---

### Search Notes

**GET** `/notes/search/?q={query}`

Searches notes by query string (case-insensitive).

**Query Parameters**
- `q` (required): Search query string

**Response** `200 OK`
```json
[
  {
    "id": 1,
    "title": "string",
    "content": "string"
  }
]
```

---

### Get Note

**GET** `/notes/{note_id}`

Returns a single note by ID.

**Path Parameters**
- `note_id` (required): Note ID (integer)

**Response** `200 OK`
```json
{
  "id": 1,
  "title": "string",
  "content": "string"
}
```

**Errors**
- `404 Not Found` - Note does not exist

---

### Update Note

**PUT** `/notes/{note_id}`

Updates an existing note.

**Path Parameters**
- `note_id` (required): Note ID (integer)

**Request Body**
```json
{
  "title": "string (required, min 1, max 200 chars)",
  "content": "string (required, min 1 char)"
}
```

**Response** `200 OK`
```json
{
  "id": 1,
  "title": "string",
  "content": "string"
}
```

**Errors**
- `404 Not Found` - Note does not exist
- `422 Unprocessable Entity` - Validation error

---

### Delete Note

**DELETE** `/notes/{note_id}`

Deletes a note.

**Path Parameters**
- `note_id` (required): Note ID (integer)

**Response** `204 No Content`

**Errors**
- `404 Not Found` - Note does not exist

---

### Extract Action Items

**POST** `/notes/{note_id}/extract`

Extracts action items from note content using LLM. Creates action items and returns them.

**Path Parameters**
- `note_id` (required): Note ID (integer)

**Response** `201 Created`
```json
[
  {
    "id": 1,
    "description": "string",
    "completed": false
  }
]
```

---

## Action Items

### List Action Items

**GET** `/action-items/`

Returns all action items.

**Response** `200 OK`
```json
[
  {
    "id": 1,
    "description": "string",
    "completed": false
  }
]
```

---

### Create Action Item

**POST** `/action-items/`

Creates a new action item.

**Request Body**
```json
{
  "description": "string (required, min 1 char)"
}
```

**Response** `201 Created`
```json
{
  "id": 1,
  "description": "string",
  "completed": false
}
```

**Errors**
- `422 Unprocessable Entity` - Validation error

---

### Mark Action Item Complete

**PUT** `/action-items/{item_id}/complete`

Marks an action item as complete.

**Path Parameters**
- `item_id` (required): Action item ID (integer)

**Errors**
- `404 Not Found` - Action item does not exist

**Response** `200 OK`
```json
{
  "id": 1,
  "description": "string",
  "completed": true
}
```

---

## Error Responses

| Status Code | Description |
|-------------|-------------|
| `204 No Content` | Request succeeded with no response body (e.g., DELETE) |
| `404 Not Found` | Resource does not exist |
| `422 Unprocessable Entity` | Request validation failed (invalid body or parameters) |
| `500 Internal Server Error` | Server-side error |

---

## OpenAPI Schema

The full OpenAPI 3.0 schema is available at:
```
GET /openapi.json
```

Interactive API documentation (Swagger UI) is available at:
```
GET /docs
```
