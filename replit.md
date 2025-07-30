# Galaxy of Consequence - Star Wars RPG API

## Overview

Galaxy of Consequence is a Flask-based REST API for a Star Wars RPG system that integrates with NVIDIA's Nemotron AI for immersive NPC dialogue generation. The system features persistent character management, faction dynamics, Force alignment tracking, and procedural quest generation with real-time canvas saving capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite (default) with PostgreSQL support via environment variables
- **Authentication**: JWT-based with bearer token validation
- **API Documentation**: Swagger UI integration
- **CORS**: Enabled for cross-origin requests

### Database Design
The system uses SQLAlchemy with a declarative base model approach. Key entities include:
- **CanvasEntry**: Stores RPG canvas data (Force HUD, summaries, etc.)
- **PlayerCharacter**: Character sheets with Force alignment tracking
- **FactionState**: Dynamic faction reputation and awareness systems
- **QuestLog**: Procedural quest generation and tracking
- **SessionState**: Session persistence for multiplayer support
- **NPCInteraction**: AI dialogue history logging

## Key Components

### Route Structure
- **Canvas Routes** (`/routes/canvas.py`): Canvas saving/loading with JWT protection
- **Faction Routes** (`/routes/faction.py`): Real-time faction simulation and AI responses
- **Force Routes** (`/routes/force.py`): Force alignment tracking and updates
- **Nemotron Routes** (`/routes/nemotron.py`): NVIDIA AI integration for NPC dialogue
- **Quest Routes** (`/routes/quest.py`): Procedural quest generation
- **Session Routes** (`/routes/session.py`): Session state management

### Service Layer
- **Auth Service**: Bearer token validation with fixed token "Abracadabra"
- **Galaxy Service**: Faction AI logic and procedural quest generation
- **NVIDIA Service**: Nemotron API integration for immersive NPC dialogue

### Security Model
- Simple bearer token authentication ("Abracadabra")
- JWT integration for future scalability
- CORS enabled for frontend integration
- Request validation and error handling

## Data Flow

1. **Authentication**: Requests validate bearer tokens via auth service
2. **Canvas Operations**: Frontend saves/loads RPG canvas data with metadata
3. **Faction Simulation**: Real-time faction AI responses based on player actions
4. **Force Tracking**: Alignment shifts tracked and persisted per character
5. **AI Dialogue**: NVIDIA Nemotron generates lore-accurate NPC responses
6. **Quest Generation**: Procedural quests based on faction states and player history

## External Dependencies

### Core Dependencies
- **Flask**: Web framework with SQLAlchemy, JWT, CORS, Swagger UI
- **OpenAI Client**: For NVIDIA API integration with proper authentication
- **NVIDIA Nemotron API**: AI dialogue generation (configured as environment variable)
- **PostgreSQL**: Database backend via `DATABASE_URL` environment variable

### Environment Variables
- `SESSION_SECRET`: Flask session key (default: "galaxy-of-consequence-secret-key")
- `JWT_SECRET_KEY`: JWT signing key (default: "galaxy-jwt-secret")
- `DATABASE_URL`: Database connection string (default: SQLite)
- `NVIDIA_API_KEY`: Nemotron AI API access

## Deployment Strategy

### Development Setup
- **Entry Point**: `main.py` runs Flask development server on `0.0.0.0:5000`
- **Debug Mode**: Enabled with logging configured to DEBUG level
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies

### Production Considerations
- Environment-based configuration for secrets and database
- Connection pooling with automatic reconnection
- Swagger UI available at `/docs` endpoint
- Static assets served from `/static` directory
- Template rendering for custom Swagger interface

### API Integration
- RESTful endpoints with JSON responses
- OpenAPI/Swagger documentation at `/openapi.yaml`
- CORS enabled for frontend integration
- Bearer token authentication required for protected endpoints
- Real-time faction simulation and AI dialogue capabilities

The system is designed as a modular RPG backend that can support various frontend clients while maintaining persistent game state and providing immersive AI-driven interactions through NVIDIA's Nemotron integration.