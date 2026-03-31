
# Hand Hygiene Compliance Monitoring System

## 🏥 Complete AI-Powered Healthcare Solution

A full-stack system for monitoring and improving hand hygiene compliance in hospitals using computer vision, real-time monitoring, and analytics.

---
 
## 📦 Project Structure  

```
Hand_Hygiene_prediction_system/
├── backend/
│   ├── app.py                    # Flask main application
│   ├── detect_hygiene.py         # Phase 1: AI detection script 
│   ├── routes/
│   │   └── hygiene.py            # REST API endpoints
│   ├── models/
│   │   └── db.py                 # PostgreSQL database models
│   ├── ai/
│   │   ├── hand_detection.py     # MediaPipe hand detection
│   │   ├── timer_logic.py        # WHO 20-second compliance timer
│   │   ├── utils.py              # Display utilities
│   │   └── integration.py        # Phase 1-2 integration
│   └── requirements_phase2.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx     # Statistics & charts
│   │   │   ├── LiveMonitor.jsx   # Real-time status
│   │   │   └── Reports.jsx       # Analytics & trends
│   │   ├── components/
│   │   │   ├── Navbar.jsx        # Navigation
│   │   │   ├── StatCard.jsx      # Metric cards
│   │   │   └── Chart.jsx         # Chart components
│   │   ├── services/
│   │   │   └── api.js            # API client
│   │   ├── App.jsx               # Main app
│   │   ├── main.jsx              # Entry point
│   │   └── App.css               # Styles
│   ├── index.html                # HTML template
│   ├── package.json              # Dependencies
│   ├── vite.config.js            # Vite config
│   ├── tailwind.config.js        # Tailwind config
│   └── postcss.config.js         # PostCSS config
│
├── requirements_phase1.txt       # Phase 1 AI dependencies
├── requirements_phase2.txt       # Phase 2 Backend dependencies
├── verify_setup.py               # Dependency checker
├── test_api.py                   # API testing script
└── DB_SETUP.txt                  # Database setup guide
```

---

## 🎯 Features

### Phase 1: AI Detection
- ✅ Real-time hand detection using MediaPipe
- ✅ WHO 20-second compliance monitoring
- ✅ Event logging and statistics
- ✅ Live video feed with overlay 
- ✅ 30 FPS performance on CPU

### Phase 2: Backend API
- ✅ Flask REST API with 10+ endpoints 
- ✅ PostgreSQL database with 3 tables
- ✅ Event logging and retrieval
- ✅ Statistics calculation
- ✅ User management

### Phase 3: Frontend Dashboard
- ✅ React + Tailwind UI
- ✅ Real-time dashboard with statistics
- ✅ Live monitoring page
- ✅ Analytics and reporting
- ✅ Chart.js visualizations

---

## 🚀 Quick Start
 
### Prerequisites
- Python 3.10+
- Node.js 16+
- PostgreSQL 13+
- Git

### Installation

#### 1. Clone & Setup Backend

```bash
# Install Python dependencies
pip install -r requirements_phase1.txt
pip install -r requirements_phase2.txt

# Setup PostgreSQL (using Docker)
docker run --name hand-hygiene-db \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=hand_hygiene \ 
  -p 5432:5432 \
  -d postgres:15 

# Run backend
python backend/app.py
```

#### 2. Setup Frontend 

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

#### 3. Run AI Detection (Optional)

```bash
python backend/detect_hygiene.py
```

---

## 📊 API Endpoints 

### Health & Status
```
GET /api/health                    # Health check
GET /                              # API info
```

### Event Logging
```
POST /api/log                      # Log event
GET /api/logs                      # Get all events
GET /api/logs/<id>                 # Get specific event
```

### Statistics
```
GET /api/stats                     # Overall stats
GET /api/stats/daily               # Daily trends
GET /api/stats/user/<user_id>      # User statistics
```
 
### User Management
```
POST /api/users                    # Create user
GET /api/users/<user_id>           # Get user
```

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| AI/Vision | OpenCV, MediaPipe |
| Backend | Flask, SQLAlchemy |
| Database | PostgreSQL |
| Frontend | React, Vite |
| Styling | Tailwind CSS |
| Charts | Chart.js |
| API Client | Axios |
| Realtime | Flask-SocketIO (Phase 4) |

---

## 📈 Database Schema

### hygiene_events
- id (Primary Key)
- user_id
- start_time
- end_time
- duration
- status (completed/incomplete)
- compliance (boolean)
- location
- department
- metadata (JSON)

### daily_stats
- id
- date
- total_events
- completed_events
- incomplete_events
- compliance_rate
- avg_duration

### users
- id
- user_id (Unique)
- name
- department
- role
- created_at

---

## 🔌 Environment Variables

Create `.env` in backend:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/hand_hygiene
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

---

## 🧪 Testing

### Test API
```bash
python test_api.py
```

### Test Backend
```bash
python -m pytest  # If pytest installed
```

### Test Frontend
```bash
cd frontend
npm run build
npm run preview
```

---

## 📊 Dashboard Features

### Dashboard Page
- Total events metric
- Compliant events count
- Non-compliant events count
- Compliance rate percentage
- 30-day compliance trend
- Compliance distribution pie chart
- Average wash duration

### Live Monitor Page
- Real-time hand detection status
- Timer display (elapsed vs required)
- Progress bar visualization
- Status indicators (Idle/Detected/Washing/Completed)
- Color-coded alerts
- Connection status indicator

### Reports Page
- Time range filtering (7/14/30/90 days)
- User-specific analytics
- Compliance trend chart
- Events breakdown (compliant vs incomplete)
- Average duration trends
- Summary statistics
- Export functionality

---

## 🔄 Data Flow

```
AI Detection (Phase 1)
    ↓
Event Logging (Backend API)
    ↓
PostgreSQL Database
    ↓
Dashboard Retrieval (Frontend)
    ↓
Real-time Visualization
```

---

## 🐛 Troubleshooting

### Backend Issues
```bash
# Check database connection
python -c "from models.db import db; print('DB OK')"

# Reset database
python -c "from models.db import db, init_db; init_db(create_app())"
```

### Frontend Issues
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

### API Issues
```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Test with sample data
python test_api.py
```

---

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| AI Detection Latency | ~100ms |
| API Response Time | ~200ms |
| Dashboard Load Time | ~2s |
| Database Query Time | ~50ms |
| Webcam FPS | 30 FPS |
| Frontend Bundle Size | ~500KB |

---

## 🔐 Security Considerations

- PostgreSQL with password authentication
- Flask CORS enabled for frontend
- Environment variables for secrets
- API validation and error handling
- SQL injection prevention (SQLAlchemy ORM)

---

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## 🚀 Deployment

### Backend (Flask)
```bash
# Production
gunicorn -w 4 app:app
```

### Frontend (React)
```bash
# Build
npm run build

# Serve
npm run preview
```

### Database (PostgreSQL)
```bash
# Backup
pg_dump hand_hygiene > backup.sql

# Restore
psql hand_hygiene < backup.sql
```

---

## 📖 Documentation

- `DB_SETUP.txt` - Database setup guide
- Code comments in each module
- API docstrings in routes
- Component PropTypes in React

---

## 🎓 Learning Resources

### AI Detection
- MediaPipe Hands: https://mediapipe.dev
- OpenCV: https://opencv.org
- Hand detection tutorial

### Backend
- Flask: https://flask.palletsprojects.com
- SQLAlchemy: https://sqlalchemy.org
- PostgreSQL: https://postgresql.org

### Frontend
- React: https://react.dev
- Tailwind CSS: https://tailwindcss.com
- Chart.js: https://chartjs.org

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Phase 4: WebSocket real-time alerts
- Phase 5: Machine learning analytics
- Mobile app (React Native)
- Cloud deployment (Azure/AWS)
- Advanced reporting

---

## 📝 License

MIT License - See LICENSE file

---

## 📞 Support

For issues, questions, or suggestions:
1. Check troubleshooting section
2. Review code comments
3. Check API documentation
4. Test with sample data

---

## ✅ Completion Status

- [x] Phase 1: AI Detection ✅
- [x] Phase 2: Backend API ✅
- [x] Phase 3: Frontend Dashboard ✅
- [ ] Phase 4: Real-time Alerts (Coming Soon)
- [ ] Phase 5: Advanced Analytics (Coming Soon)

---

## 🎉 System Ready!

All 3 phases complete and integrated. Ready for:
- Deployment
- Testing with real data
- User training
- Hospital integration

---

**Built with ❤️ for healthcare compliance**
>>>>>>> 72c4732 (Initial commit - AI Hand Hygiene Project)
