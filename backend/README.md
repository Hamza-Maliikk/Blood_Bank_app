# Blood Bank Backend - Python FastAPI

A modern, scalable backend for the Blood Bank application built with Python FastAPI, MongoDB, and clean architecture principles.

## 🏗️ Architecture

This backend follows **Clean Architecture** principles with clear separation of concerns:

```
backend-python/
├── app/
│   ├── api/              # FastAPI routes/endpoints
│   ├── core/             # Configuration, security, dependencies
│   ├── domain/           # Business entities (TypedDict/dataclasses)
│   ├── services/         # Business logic layer
│   ├── repositories/     # Data access layer (abstract + MongoDB impl)
│   ├── schemas/          # Database schemas
│   └── utils/            # Helpers (logger, validators, etc.)
├── scripts/              # Migration and seeding scripts
├── tests/                # Test files
├── main.py               # FastAPI application entry point
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration
└── docker-compose.yml    # Local development setup
```

## 🚀 Features

- **Authentication**: JWT-based authentication with refresh tokens
- **Real-time**: WebSocket (Socket.IO) for live updates + SSE for AI streaming
- **AI Integration**: Support for both OpenAI and Google Gemini
- **Payments**: Stripe integration for money donations
- **Notifications**: OneSignal push notifications
- **File Storage**: AWS S3 for chat attachments
- **Database**: MongoDB with async Motor driver
- **Clean Architecture**: Repository pattern for easy database switching
- **Type Safety**: Pydantic models with validation
- **Auto Documentation**: FastAPI generates OpenAPI docs

## 🛠️ Tech Stack

- **Framework**: FastAPI (async Python)
- **Database**: MongoDB Atlas
- **Authentication**: JWT tokens
- **Real-time**: Socket.IO + Server-Sent Events
- **AI**: OpenAI API / Google Gemini
- **Payments**: Stripe
- **Notifications**: OneSignal
- **File Storage**: AWS S3
- **Containerization**: Docker

## 📋 Prerequisites

- Python 3.11+
- MongoDB (local or Atlas)
- Docker (optional)
- Environment variables configured

## 🔧 Installation

### 1. Clone and Setup

```bash
git clone <repository-url>
cd backend-python
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example environment file and configure:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```env
# Server Configuration
NODE_ENV=development
PORT=8000
LOG_LEVEL=info
DEBUG=true

# Database Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/bloodbank
MONGODB_DATABASE=bloodbank

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Provider Configuration (choose one)
AI_PROVIDER=openai  # or 'gemini'
OPENAI_API_KEY=sk-your-openai-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=bloodbank-attachments
S3_BASE_URL=https://your-bucket.s3.amazonaws.com

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key

# OneSignal Configuration
ONESIGNAL_APP_ID=your-onesignal-app-id
ONESIGNAL_API_KEY=your-onesignal-api-key

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8081
```

### 4. Run the Application

```bash
# Development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python main.py
```

## 🐳 Docker Setup

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

This will start:
- Python FastAPI backend (port 8000)
- MongoDB (port 27017)
- Redis (port 6379)
- MongoDB Express (port 8081)

### Using Docker Only

```bash
# Build image
docker build -t bloodbank-backend .

# Run container
docker run -p 8000:8000 --env-file .env bloodbank-backend
```

## 🗄️ Database Setup

### Seeding Development Data

```bash
# Run the seeder script
python scripts/seed.py
```

This creates:
- 1 admin user, 1 patient, 6 donors
- 3 blood requests (open, pending, accepted)
- Sample donations, comments, notifications
- Chat sessions and messages

**Default Login Credentials:**
- Admin: `admin@bloodbank.com` / `admin123`
- Patient: `ahmed@example.com` / `password123`
- Donor: `fatima@example.com` / `password123`

### Migration from Firebase

If migrating from Firebase Realtime Database:

```bash
# Set Firebase credentials in .env
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com

# Run migration
python scripts/migrate_firebase_to_mongo.py
```

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/reset-password` - Request password reset
- `POST /api/auth/confirm-reset` - Confirm password reset

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile
- `GET /api/users/donors` - List available donors
- `PUT /api/users/availability` - Toggle donor availability
- `GET /api/users/stats` - Get user statistics

### Requests
- `POST /api/requests` - Create blood request
- `GET /api/requests` - List requests with filters
- `GET /api/requests/{id}` - Get specific request
- `PUT /api/requests/{id}/accept` - Accept request
- `PUT /api/requests/{id}/reject` - Reject request
- `PUT /api/requests/{id}/cancel` - Cancel request
- `GET /api/requests/inbox` - Get donor inbox

### Donations
- `GET /api/donations/blood` - List blood donations
- `PUT /api/donations/blood/{id}` - Update donation status
- `POST /api/donations/money/intent` - Create payment intent
- `POST /api/donations/money/confirm` - Confirm payment
- `GET /api/donations/money` - List money donations

### Comments
- `POST /api/comments` - Add comment to request
- `GET /api/comments/{requestId}` - List request comments
- `DELETE /api/comments/{id}` - Delete comment

### Notifications
- `GET /api/notifications` - Get user notifications
- `PUT /api/notifications/{id}/read` - Mark as read
- `PUT /api/notifications/mark-all-read` - Mark all as read

### Chat & AI
- `POST /api/chat/sessions` - Create chat session
- `GET /api/chat/sessions` - List user sessions
- `POST /api/chat/sessions/{id}/messages` - Send message
- `GET /api/chat/sessions/{id}/messages` - Get chat history
- `POST /api/chat/upload` - Upload file attachment
- `POST /api/ai/search` - AI-enhanced search
- `GET /api/ai/recommendations` - Get recommendations

### Admin
- `GET /api/admin/users` - List all users
- `GET /api/admin/requests` - List all requests
- `GET /api/admin/analytics` - Platform analytics
- `POST /api/admin/announcements` - Create announcement
- `POST /api/admin/seed` - Seed database

### Webhooks
- `POST /api/webhooks/stripe` - Stripe payment webhooks

## 🔌 WebSocket Events

Connect to: `ws://localhost:8000/socket.io/`

### Client Events
- `join_room` - Join a specific room
- `leave_room` - Leave a room
- `send_chat_message` - Send chat message
- `request_update` - Update request status

### Server Events
- `connected` - Connection established
- `notification` - New notification
- `request_notification` - Request-related notification
- `request_status_update` - Request status changed
- `donor_availability_update` - Donor availability changed
- `new_chat_message` - New chat message
- `ai_response` - AI response received

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

## 🚀 Deployment

### Railway
1. Connect your GitHub repository
2. Set environment variables
3. Deploy automatically on push

### Render
1. Create new Web Service
2. Connect repository
3. Configure build and start commands
4. Set environment variables

### AWS ECS
1. Build Docker image
2. Push to ECR
3. Create ECS service
4. Configure load balancer

### Environment Variables for Production

Ensure these are set in production:
- `NODE_ENV=production`
- `DEBUG=false`
- `JWT_SECRET_KEY` (strong secret)
- `MONGODB_URI` (production MongoDB)
- All API keys and secrets

## 🔒 Security

- JWT token authentication
- Password hashing with bcrypt
- CORS configuration
- Input validation with Pydantic
- Rate limiting (recommended)
- HTTPS in production

## 📊 Monitoring

- Health check endpoint: `/health`
- Structured logging
- Error tracking (recommend Sentry)
- Performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation
- Review the logs for errors

## 🔄 Migration Guide

### From Firebase to MongoDB

1. **Backup Firebase data**
2. **Set up MongoDB**
3. **Configure environment variables**
4. **Run migration script**
5. **Update frontend/mobile app**
6. **Test thoroughly**
7. **Switch DNS/environment**

### Key Changes
- Authentication: Firebase Auth → JWT tokens
- Database: Firebase RTDB → MongoDB
- Real-time: Firebase listeners → WebSocket/SSE
- File storage: Firebase Storage → AWS S3
- Payments: Firebase Functions → Direct Stripe integration

---

**Built with ❤️ for the Blood Bank community**
