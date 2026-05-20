# AI-Native JSON CMS with FastAPI + MCP

## Vision

Build a dynamic JSON-driven CMS platform using FastAPI and PostgreSQL where entities are defined using configuration files and CRUD APIs are generated automatically.

The platform will later expose all operations through an MCP server, making the backend directly operable by AI agents.

This project serves as:

- A FastAPI architecture playground
- A dynamic metadata-driven backend
- A foundation for AI-native SaaS products
- A reusable business application boilerplate

---

# Core Tech Stack

## Backend
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Pydantic
- Alembic

## Infrastructure
- Docker
- Docker Compose

## Future Integrations
- MCP Server
- Redis
- Celery/RQ
- JWT Authentication
- RBAC

---

# High-Level Architecture

```text
JSON Entity Definitions
        ↓
Dynamic Model Generator
        ↓
Dynamic CRUD API Generator
        ↓
FastAPI REST APIs
        ↓
PostgreSQL Database
        ↓
MCP Layer
        ↓
AI Agents / LLMs
```

---

# Project Goals

## Functional Goals
- Dynamic entity definitions
- Automatic CRUD generation
- Filtering & pagination
- Validation system
- Authentication & authorization
- MCP integration
- AI operability

## Learning Goals
- Python fundamentals
- Async programming
- FastAPI architecture
- SQLAlchemy ORM
- Dynamic Python patterns
- Metaprogramming
- MCP ecosystem

---

# Cycle 1 — Dynamic FastAPI CMS Foundation

## Goal
Build the core dynamic CMS engine with FastAPI and PostgreSQL.

---

## Features

### Project Setup
- [x] Setup FastAPI project structure
- [x] Configure virtual environment
- [x] Setup dependency management
- [x] Setup Docker & Docker Compose
- [x] Configure PostgreSQL container
- [x] Setup environment variables

---

### Database Layer
- [x] Setup SQLAlchemy 2.0
- [x] Configure database session handling
- [x] Setup Alembic migrations
- [x] Create base ORM model
- [x] Implement database connection lifecycle

---

### Dynamic Entity System
- [x] Create JSON entity schema format
- [x] Implement entity loader
- [x] Parse entity definitions dynamically
- [x] Generate SQLAlchemy models dynamically
- [x] Generate Pydantic schemas dynamically
- [x] Register entities at startup

---

### CRUD Engine
- [x] Create generic CRUD service
- [x] Generate CRUD routes dynamically
- [x] Auto-register FastAPI routers
- [x] Implement:
  - [x] Create
  - [x] Read
  - [x] Update
  - [x] Delete

---

### Swagger & API Docs
- [x] Ensure generated APIs appear in Swagger
- [ ] Add entity metadata documentation
- [x] Validate generated schemas

---

### Example Entities
- [x] Tasks
- [x] Posts
- [ ] Users
- [ ] Candidates

---

## Learning Outcomes

### Python
- Classes
- Typing
- Dynamic imports
- Reflection
- Dataclasses
- File parsing

### FastAPI
- Routing
- Dependency injection
- Lifespan hooks
- Request validation

### SQLAlchemy
- ORM basics
- Sessions
- Model generation
- Relationships

---

# Cycle 2 — Advanced Query Engine

## Goal
Make the CMS production-grade with querying, filtering, validations, and developer experience improvements.

---

## Features

### Pagination
- [ ] Offset pagination
- [ ] Cursor pagination
- [ ] Configurable page sizes

---

### Filtering
- [ ] Exact match filters
- [ ] Partial string matching
- [ ] Numeric filters
- [ ] Date range filters
- [ ] Boolean filters
- [ ] Dynamic query builder

Example:
```http
GET /tasks?status=completed&priority=high
```

---

### Sorting
- [ ] Ascending sorting
- [ ] Descending sorting
- [ ] Multi-field sorting

---

### Validation System
- [ ] Required fields
- [ ] Min/max validation
- [ ] Regex validation
- [ ] Enum validation
- [ ] Custom validators

Example:
```json
{
  "name": "email",
  "type": "string",
  "required": true,
  "regex": "email"
}
```

---

### Relationships
- [ ] One-to-many
- [ ] Many-to-many
- [ ] Nested entity loading

---

### Developer Experience
- [ ] Better error handling
- [ ] Structured API responses
- [ ] Logging
- [ ] Configurable entity loading
- [ ] Hot reload for entity configs

---

### Performance
- [ ] Async database support
- [ ] Query optimization
- [ ] Connection pooling

---

## Learning Outcomes

### Python
- Advanced typing
- Asyncio
- Generic programming
- Decorators

### Backend Architecture
- Query builders
- Validation pipelines
- API design patterns

---

# Cycle 3 — MCP Integration Layer

## Goal
Expose the CMS as an MCP-compatible AI-operable platform.

---

## Features

### MCP Server Setup
- [ ] Setup MCP server project
- [ ] Connect MCP server with CMS
- [ ] Define MCP tool registry

---

### Dynamic MCP Tool Generation
Generate tools automatically for every entity.

Example:
- create_task
- update_task
- delete_task
- search_tasks

---

### MCP Operations
- [ ] List entities
- [ ] Read entity metadata
- [ ] Create records
- [ ] Update records
- [ ] Delete records
- [ ] Query records

---

### AI Features
- [ ] Structured outputs
- [ ] Tool descriptions
- [ ] Schema-aware tools
- [ ] Dynamic prompt generation

---

### Security
- [ ] Tool-level permissions
- [ ] Safe query handling
- [ ] Input sanitization

---

## Learning Outcomes

### AI Infrastructure
- MCP architecture
- Tool calling
- AI interoperability
- Structured schemas

### Python
- Async systems
- Protocol handling
- Dynamic tool generation

---

# Cycle 4 — Authentication & RBAC

## Goal
Make the platform SaaS-ready and secure.

---

## Features

### Authentication
- [ ] JWT authentication
- [ ] Login endpoint
- [ ] Refresh tokens
- [ ] Password hashing
- [ ] Session management

---

### Middleware
- [ ] Authentication middleware
- [ ] Request logging middleware
- [ ] Error middleware
- [ ] Tenant middleware

---

### RBAC
- [ ] Roles
- [ ] Permissions
- [ ] Entity-level permissions
- [ ] Field-level permissions

Example:
- Admin
- Editor
- Viewer

---

### Multi-Tenancy
- [ ] Tenant identification
- [ ] Tenant isolation
- [ ] Subdomain tenancy

---

### Audit System
- [ ] Audit logs
- [ ] Change tracking
- [ ] User activity logs

---

### Security Enhancements
- [ ] Rate limiting
- [ ] CORS policies
- [ ] API key support
- [ ] Secure headers

---

## Learning Outcomes

### Security
- Authentication flows
- Authorization systems
- Middleware architecture

### SaaS Architecture
- Multi-tenancy
- Permission systems
- Production backend patterns

---

# Future Cycles (Optional)

## Admin Dashboard
- React admin UI
- Dynamic forms
- Entity editor

---

## Workflow Engine
- Triggers
- Automations
- Event pipelines

---

## Realtime Features
- WebSockets
- Live updates
- Notifications

---

## AI Enhancements
- AI-generated forms
- AI querying
- AI report generation

---

# Suggested Folder Structure

```text
app/
├── core/
├── database/
├── entities/
├── generators/
├── middleware/
├── models/
├── routes/
├── schemas/
├── services/
├── utils/
└── main.py
```

---

# MVP Definition

The MVP is complete when:

- JSON entity definitions work
- CRUD APIs are generated dynamically
- Data persists in PostgreSQL
- APIs appear in Swagger automatically
- Basic filtering works

---

# Final Vision

A reusable AI-native backend platform where:

- Developers define entities in JSON
- APIs are generated automatically
- AI agents can interact with the system through MCP
- The platform becomes a foundation for rapidly building business applications
