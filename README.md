# Molecule Manager

[![CI](https://github.com/KosGeny/molecules-project/actions/workflows/ci.yml/badge.svg)](https://github.com/KosGeny/molecules-project/actions/workflows/ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A web application for managing and searching molecular structures using RDKit.

## Features

- **Molecular CRUD Operations**: Create, read, update, and delete molecular structures with SMILES validation
- **Substructure Search**: Chemical substructure searching using RDKit
- **RESTful API**: Documented FastAPI endpoints
- **Caching**: Redis-based caching
- **Containerized Deployment**: Docker Compose setup with PostgreSQL, Redis, and Nginx
- **Pagination**: Pagination for large molecule datasets

## Technology Stack

### Backend
- **FastAPI**
- **SQLAlchemy**
- **PostgreSQL**
- **Redis**
- **RDKit**
- **Alembic**
- **Pydantic**

### Infrastructure
- **Docker**
- **Docker Compose**
- **Nginx**
- **GitHub Actions**

### Development Tools
- **Black**
- **Flake8**
- **Pytest**

## Architecture

The application follows a microservices-inspired architecture with clear separation of concerns:

```
molecules-project/
├── backend/
│   ├── app/
│   │   ├── config/ 
│   │   ├── db/s
│   │   ├── src/
│   │   │   ├── api/v1/
│   │   │   ├── core/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   └── utils/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
├── nginx/
└── docker-compose.yml
```

### Service Architecture
- **PostgreSQL**: Stores molecular data (SMILES, names, metadata)
- **Redis**: Caches search results and frequently accessed data
- **FastAPI Backend**: Handles API requests and business logic
- **Nginx**: Serves static frontend files and proxies API requests

### Available Endpoints

#### Molecule Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/molecules/` | List all molecules (paginated) |
| `POST` | `/api/v1/molecules/` | Create a new molecule |
| `GET` | `/api/v1/molecules/{id}` | Get molecule by ID |
| `PUT` | `/api/v1/molecules/{id}` | Update molecule |
| `DELETE` | `/api/v1/molecules/{id}` | Delete molecule |
| `POST` | `/api/v1/molecules/upload` | Upload molecules from CSV |
| `POST` | `/api/v1/molecules/search` | Search molecules by substructure |

#### Health & System
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API root with version info |
| `GET` | `/health` | Health check endpoint |

## Installation

```bash
git clone https://github.com/KosGeny/molecules-project.git
cd molecules-project
docker-compose up -d
```