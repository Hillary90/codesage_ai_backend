# CodeSage AI - Backend

AI-Powered Code Review and Developer Portfolio Builder - REST API

**Live API:** https://codesage-ai-backend-oke3.onrender.com

## Features

- **AI Code Analysis**: Integration with OpenAI and Gemini for intelligent code review
- **Code Quality Metrics**: Pylint, Radon, and Bandit integration
- **User Authentication**: JWT-based secure authentication
- **GitHub Integration**: Fetch and analyze repositories
- **RESTful API**: Clean and documented API endpoints
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Rate Limiting**: Redis-based API rate limiting
- **Security**: CORS, encryption, and secure password hashing

## Tech Stack

- **Flask 3.0** - Web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **Redis** - Caching and rate limiting
- **JWT** - Authentication
- **OpenAI & Gemini** - AI code analysis
- **PyGithub** - GitHub API integration
- **Gunicorn** - Production server

## Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Redis 6+ (optional)
- OpenAI or Gemini API key
- GitHub Personal Access Token

## Local Installation

1. Clone the repository:
```bash
git clone https://github.com/Hillary90/codesage_ai_backend.git
cd codesage_ai_backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Configure environment variables in `.env`:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/codesage_db
JWT_SECRET_KEY=your-jwt-secret-key
GEMINI_API_KEY=your-gemini-api-key
AI_MODEL=gemini-1.5-flash
CORS_ORIGINS=http://localhost:5173
```

6. Initialize database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Running Locally
 
### Development Mode
```bash
flask run
```
API available at `http://localhost:5000`

### Production Mode
```bash
gunicorn wsgi:app
```

## Project Structure

```
codesage_ai_backend/
├── models/          # Database models
├── routes/          # API endpoints
├── services/        # Business logic
├── utils/           # Helper functions
├── migrations/      # Database migrations
├── app.py           # Application factory
├── wsgi.py          # WSGI entry point
├── config.py        # Configuration
├── database.py      # Database setup
└── requirements.txt # Dependencies
```

## API Endpoints

### Health Check
- `GET /health` - Check API status

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user

### Code Review
- `POST /api/reviews/analyze` - Analyze code
- `GET /api/reviews/history` - Get review history
- `GET /api/reviews/:id` - Get specific review
- `DELETE /api/reviews/:id` - Delete review

### Portfolio
- `GET /api/portfolio` - Get user portfolio
- `POST /api/portfolio/project` - Add project
- `PUT /api/portfolio/project/:id` - Update project
- `DELETE /api/portfolio/project/:id` - Delete project

### Notifications
- `GET /api/notifications` - Get user notifications
- `PUT /api/notifications/:id/read` - Mark as read

##  Testing

```bash
pytest
pytest --cov=. --cov-report=html
```

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Rate limiting per IP/user
- CORS protection
- SQL injection prevention
- XSS protection
- Input validation and sanitization

##  Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License.

##  Author

**Hillary**
- GitHub: [@Hillary90](https://github.com/Hillary90)

##  Acknowledgments

- Flask community
- OpenAI and Google Gemini for AI capabilities
- PostgreSQL and Redis teams
- Render for hosting
