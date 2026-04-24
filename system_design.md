# Agri Platform: System Design & Architecture Documentation

## 1. System Design Overview
The Agri Platform is designed as a centralized digital ecosystem for farmers and agricultural stakeholders. It follows a **Monolithic Architecture** with modularized components for scalability and ease of deployment.

### High-Level System Flow
1.  **Client Layer**: User interacts via a responsive Web Interface (Browser/Mobile via Capacitor).
2.  **Application Layer**: Flask Web Server handles routing, business logic, and session management.
3.  **Intelligence Layer**:
    *   **Local ML Models**: Scikit-learn models for yield and price prediction.
    *   **Cloud AI Services**: Google Gemini Pro for the intelligent chatbot.
    *   **Computer Vision**: OpenCV/Pillow for image processing and disease detection.
4.  **Data Layer**: PostgreSQL (Supabase) or SQLite for structured data (Users, Crops, Predictions).

---

## 2. Architecture
The project follows the **MVC (Model-View-Controller)** pattern:

*   **Models**: SQLAlchemy classes representing database tables (`user.py`, `crop.py`, `marketplace.py`, `scheme.py`, `prediction.py`).
*   **Views**: Jinja2 HTML templates enhanced with TailwindCSS for a modern, responsive UI.
*   **Controllers (Routes)**: Blueprint-based routing logic (`auth.py`, `disease.py`, `chatbot.py`, etc.) that handles user requests and interacts with models.

---

## 3. Workflow

### A. Authentication & User Journey
1.  User registers with an email.
2.  **OTP Verification**: A secure 6-digit OTP is sent via Gmail (Flask-Mail).
3.  Upon verification, the user can access the personal Dashboard.
4.  Profile Management: Users can update their crop preferences and location.

### B. Disease Detection Workflow
1.  Farmer uploads a photo of a diseased leaf.
2.  **Backend Processing**: OpenCV/PIL pre-processes the image.
3.  **AI Analysis**: The system uses a trained ML model or Gemini Vision API to identify the disease.
4.  **Results**: User receives the disease name, confidence score, and recommended treatment.

### C. Marketplace / Supply Chain
1.  **Seller**: Lists surplus crops with price and quantity.
2.  **Buyer**: Browses listings, filters by region, and contacts the seller directly.
3.  **History**: Both parties can view their transaction/listing history.

### D. AI Assistant (AgriBot)
1.  User asks a question (e.g., "Best fertilizer for Rice in Karnataka?").
2.  **Context Injection**: The AI is fed project-specific agricultural data.
3.  **Response**: Gemini AI generates a human-like, accurate response.

---

## 4. Technical Stack

| Component | Technology | Use Case |
| :--- | :--- | :--- |
| **Backend Framework** | Flask (Python) | Core application routing and logic. |
| **Frontend** | HTML5, TailwindCSS, JS | Modern UI and responsive layouts. |
| **Database ORM** | Flask-SQLAlchemy | Database schema management and queries. |
| **Database** | Supabase (PostgreSQL) | Scalable cloud database for persistent storage. |
| **AI Integration** | Google GenAI (Gemini) | Natural language processing and image analysis. |
| **Machine Learning** | Scikit-Learn, NumPy | Yield and price prediction models. |
| **Image Processing** | OpenCV, PIL | Handling and analyzing crop images. |
| **Authentication** | Flask-Login, Bcrypt | Secure user sessions and password hashing. |
| **Communication** | Flask-Mail (SMTP) | OTP delivery and notifications. |
| **Deployment** | Gunicorn + Render/Heroku | Production-ready web server and hosting. |

---

## 5. Requirements

### Functional Requirements
*   **User Management**: Registration, Login, OTP-based password recovery.
*   **Dashboard**: Real-time summary of user activity and agriculture stats.
*   **Crop Disease Analysis**: Image upload and automated diagnosis.
*   **Marketplace**: CRUD (Create, Read, Update, Delete) operations for crop listings.
*   **Yield Prediction**: Input data (Area, Region, Crop Type) to get estimated yield.
*   **Price Prediction**: Forecast crop market prices based on historical data.
*   **Multilingual Support**: Kannada/Hindi translation for regional accessibility.

### Non-Functional Requirements
*   **Security**: CSRF protection (Flask-WTF), password hashing, and secure session cookies.
*   **Performance**: AI responses within < 3 seconds; image processing within < 2 seconds.
*   **Scalability**: Stateless session handling to support multiple concurrent users.
*   **Availability**: 99.9% uptime (hosted on monitored platforms like Render).

---

## 6. Use Cases

### For Farmers
*   **Diagnosis**: "I see brown spots on my Tomato plant. Let me take a photo to find the cure."
*   **Market Insights**: "What is the predicted price for Wheat next month? Should I sell now?"
*   **Planning**: "Which crop is most profitable for my specific soil type this season?"

### For Buyers/Agri-Businesses
*   **Sourcing**: "I need 100 quintals of organic Rice. Who is the nearest seller in the Marketplace?"
*   **Direct Connect**: Reducing middlemen by communicating directly with listed farmers.

### For Students/Researchers
*   **AI Research**: Using the Research Engine to generate academic-level papers on agricultural trends.
*   **Knowledge Base**: Accessing documented government schemes and benefits.
