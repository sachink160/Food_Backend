# Food Finder Backend API

A comprehensive FastAPI backend for food delivery and restaurant management platform. Features phone-based authentication, multi-role user management, restaurant operations, and public search capabilities.

## 🚀 Features

### Authentication & User Management
- **Phone-based login** with automatic user creation
- **Multi-role support**: Users can have multiple roles (customer, restaurant_owner, admin, delivery_person)
- **JWT token authentication** with access and refresh tokens
- **Automatic profile backfill**: Missing fields are auto-populated during login
- **User profile management** with full CRUD operations
- **Address management** with default address support

### Restaurant Management (Owner Features)
- **Restaurant profile management** with comprehensive business details
- **Category management** for menu organization
- **Menu item management** with detailed food information
- **Special items management** for featured dishes
- **Delivery settings** (radius, fees, minimum order amounts)
- **Business hours and location management**

### Public Features
- **Restaurant discovery** with filtering by city and cuisine
- **Location-based search** with radius support
- **Popular and new restaurant listings**
- **Unique restaurant code search**
- **Comprehensive restaurant information display**

### Technical Features
- **SQLAlchemy 2.x ORM** with connection pooling
- **Pydantic v2 schemas** for data validation
- **Automatic table creation** on startup
- **Comprehensive logging** with file rotation
- **CORS support** for frontend integration
- **Request ID tracking** for debugging
- **Error handling** with structured responses

## 📋 Requirements

- **Python 3.11+**
- **PostgreSQL** (recommended) or **SQLite**
- **FastAPI 0.110.0+**
- **SQLAlchemy 2.0+**
- **Pydantic 2.4+**

## ⚙️ Environment Setup

Create `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/food_db
# or for SQLite: DATABASE_URL=sqlite:///./food.db

# Security
SECRET_KEY=your-super-secret-key-here

# Optional: OpenAI API Key for future AI features
OPENAI_API_KEY=your-openai-api-key
```

### Quick Start with SQLite
```env
DATABASE_URL=sqlite:///./food.db
SECRET_KEY=dev_secret_key_change_in_production
```

## 🛠️ Installation & Running

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access Documentation
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **API Root**: http://127.0.0.1:8000/

## 🔐 Authentication

### Login Endpoint
```http
POST /auth/login
Content-Type: application/json

{
  "phone_number": "9999999999",
  "user_type": "customer" | "restaurant_owner"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "active_role": "customer",
    "roles": ["customer"],
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "profile_incomplete": false
  }
}
```

### Using Authentication
Include the access token in the Authorization header:
```http
Authorization: Bearer <access_token>
```

## 📚 API Endpoints

### 🔑 Authentication
- `POST /auth/login` - Phone-based login with role selection

### 👤 User Management
- `GET /user/me` - Get current user profile
- `PATCH /user/me` - Update user profile

#### Address Management
- `GET /user/me/addresses` - List user addresses
- `POST /user/me/addresses` - Create new address
- `PATCH /user/me/addresses/{address_id}` - Update address
- `DELETE /user/me/addresses/{address_id}` - Delete address

### 🏪 Restaurant Owner Features
#### Restaurant Management
- `GET /owner/restaurant` - Get my restaurant details
- `POST /owner/restaurant` - Create or update restaurant

#### Category Management
- `GET /owner/restaurant/categories` - List all categories
- `POST /owner/restaurant/categories` - Create category
- `PATCH /owner/restaurant/categories/{category_id}` - Update category
- `DELETE /owner/restaurant/categories/{category_id}` - Delete category

#### Menu Management
- `GET /owner/restaurant/menu` - List menu items
- `POST /owner/restaurant/menu` - Create menu item
- `PATCH /owner/restaurant/menu/{item_id}` - Update menu item
- `DELETE /owner/restaurant/menu/{item_id}` - Delete menu item

#### Special Items
- `GET /owner/restaurant/specials` - Get special items
- `POST /owner/restaurant/specials` - Set special items (array of menu item IDs)

### 🍽️ Public Restaurant Data
- `GET /restaurants` - List restaurants (with optional city/cuisine filters)
- `GET /restaurants/{restaurant_id}` - Get restaurant details
- `POST /restaurants` - Create restaurant (admin only)
- `PATCH /restaurants/{restaurant_id}` - Update restaurant (admin only)
- `DELETE /restaurants/{restaurant_id}` - Delete restaurant (admin only)

### 🔍 Search & Discovery
- `GET /search/nearby?lat={lat}&lng={lng}&radius_km={radius}` - Find nearby restaurants
- `GET /search/popular?limit={limit}` - Get popular restaurants
- `GET /search/new?limit={limit}` - Get newest restaurants
- `GET /search/code/{unique_code}` - Find restaurant by unique code

## 🏗️ Project Structure

```
Backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration and environment variables
│   ├── database.py            # Database connection and session management
│   ├── models.py              # SQLAlchemy models
│   ├── schemas.py             # Pydantic schemas for validation
│   ├── auth.py                # Authentication and JWT utilities
│   ├── middleware.py          # CORS and request ID middleware
│   ├── logger.py              # Logging configuration
│   └── routes/
│       ├── auth_routes.py     # Authentication endpoints
│       ├── user.py            # User profile and address management
│       ├── owner.py           # Restaurant owner features
│       ├── restaurants.py     # Public restaurant endpoints
│       └── search.py          # Search and discovery endpoints
├── logs/                      # Application logs
├── uploads/                   # File uploads directory
├── chroma_db/                 # Vector database for AI features
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔧 Configuration

### Database Configuration
- **Connection Pooling**: QueuePool with 10 base connections, 20 overflow
- **Connection Recycling**: Every 3600 seconds
- **Pre-ping**: Enabled for connection health checks
- **SQLite Optimizations**: Foreign keys, WAL mode, NORMAL sync

### Logging Configuration
- **Log Level**: INFO
- **File Rotation**: 1MB max file size, 5 backup files
- **Log Format**: `%(asctime)s | %(levelname)s | %(name)s | %(message)s`
- **Output**: Both console and file (`logs/app.log`)

### Security Configuration
- **JWT Algorithm**: HS256
- **Token Expiry**: 3000 minutes (50 hours)
- **Password Hashing**: bcrypt
- **CORS**: Enabled for all origins (configure for production)

## 🚀 Deployment

### Production Considerations
1. **Change SECRET_KEY** to a strong, random value
2. **Configure CORS** to allow only your frontend domain
3. **Use PostgreSQL** instead of SQLite
4. **Set up proper logging** and monitoring
5. **Configure reverse proxy** (nginx) for production
6. **Use environment variables** for all sensitive data

### Docker Deployment (Optional)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🧪 Testing

### Manual Testing with cURL

#### Login
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"9999999999","user_type":"restaurant_owner"}'
```

#### Get User Profile
```bash
curl http://127.0.0.1:8000/user/me \
  -H "Authorization: Bearer <access_token>"
```

#### Search Restaurants
```bash
curl "http://127.0.0.1:8000/search/popular?limit=10"
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Error**: `app.main:app` → Ensure you're running from the Backend directory
2. **Database Connection**: Check `DATABASE_URL` and database server status
3. **Port Already in Use**: Change port with `--port 8001`
4. **CORS Issues**: Verify frontend URL is allowed in middleware
5. **Token Expired**: Use refresh token or re-login

### Debug Mode
Enable SQL query logging by setting `echo=True` in `database.py`:
```python
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Enable SQL query logging
    # ... other options
)
```

### Logs Location
- Application logs: `logs/app.log`
- Console output: Real-time in terminal
- Request IDs: Available in response headers (`X-Request-ID`)

## 📈 Performance

### Database Optimizations
- Connection pooling reduces connection overhead
- Pre-ping ensures healthy connections
- SQLite pragmas optimize performance
- Proper indexing on frequently queried fields

### API Response Format
All API responses follow this structure:
```json
{
  "success": true,
  "data": { /* actual response data */ }
}
```

Error responses:
```json
{
  "success": false,
  "error": "Error message or validation details"
}
```

## 🔄 Future Enhancements

- **Alembic migrations** for database schema management
- **Redis caching** for frequently accessed data
- **File upload** for restaurant and menu images
- **Real-time notifications** with WebSockets
- **Payment integration** for order processing
- **AI-powered recommendations** using OpenAI API
- **Order management** system
- **Review and rating** system

## 📄 License

This project is part of the Food Finder platform. Please refer to the main project documentation for licensing information.
