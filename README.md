
# 🚀 Task Master 🍅⏰📅

Task Master is a web application that allows users to manage their tasks and schedules using a FastAPI backend and a Streamlit frontend. The application supports user authentication, task creation, and schedule generation by GEMINI AI.

## ✨ Features

- 🔒 **User Authentication:** Secure login and registration.
- 📝 **Task Management:** Create and manage tasks with ease.
- 📅 **Schedule Generation:** Generate schedules based on tasks and constraints.
- ⚡ **Caching:** Powered by Redis for high performance.
- 🐘 **Data Storage:** PostgreSQL integration for reliable storage.
- 🔔 **Notifications:** Telegram integration for timely reminders.
- ⏱️ **Telegram Notifications 10 Minutes Before Meetings:** Receive reminders via Telegram 10 minutes before scheduled tasks.

## 🛠️ Prerequisites

- 🐳 **Docker:** For containerization.
- 🚢 **Docker Compose:** For orchestrating multi-container applications.

## 🏁 Getting Started

### 📥 Clone the Repository

```sh
git clone [https://github.com/yourusername/task-master.git](https://github.com/yourusername/task-master.git)
cd task-master
```

### ⚙️ Environment Variables

Create a `.env` file in the root directory and add the following environment variables:

```properties
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql
REDIS_URL=redis
SECRET_KEY=your_secret_key
TELEGRAM_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### 🚀 Build and Run the Docker Containers

```sh
docker-compose up --build
```

This will build and start the FastAPI, Streamlit, PostgreSQL, and Redis containers.

### 🌐 Access the Application

- 🖥️ **Streamlit Frontend:** [http://localhost:8501](http://localhost:8501)
- ⚙️ **FastAPI Backend:** [http://localhost:1236](http://localhost:1236)

## 📂 Project Structure

```plaintext
.
├── Dockerfile-fastapi      # 🐳 FastAPI backend Dockerfile
├── Dockerfile-streamlit    # 🖥️ Streamlit frontend Dockerfile
├── docker-compose.yml      # 🚢 Docker Compose configuration
├── .envExample             # 📝 Example .env file
├── main.py                 # ⚙️ Main FastAPI application
├── auth.py                 # 🔑 Authentication module
├── moudles.py              # 🧩 SQLAlchemy models and Pydantic schemas
├── database.py             # 🗄️ Database configuration
├── streamlit_app.py        # 📈 Streamlit frontend application
├── requirements.txt        # 📦 Python dependencies
└── README.md               # 📖 Project documentation
```

## 📦 Python Dependencies

The following Python dependencies are required for this project:

```plaintext
fastapi==0.115.8
protobuf==5.29.3
pydantic==2.10.6
pytest==8.3.4
redis==5.2.1
Requests==2.32.3
SQLAlchemy==2.0.38
streamlit==1.41.1
uvicorn==0.34.0
google-generativeai==0.8.4
python-dotenv==1.0.1
psycopg2-binary==2.9.10
openai==1.63.2
python-telegram-bot==20.0
passlib[bcrypt]==1.7.4
PyJWT==2.3.0
python-multipart==0.0.5
python-jose[cryptography]
passlib[bcrypt]
pydantic[email]
bcrypt==3.2.0
```

## 🚀 Usage

### 🔑 User Authentication

- 📝 **Register** a new user.
- 🔐 **Login** with registered user credentials.

### 📝 Task Management

- ➕ **Add** new tasks (name, duration, priority, notes).
- 📋 **View** the list of added tasks.

### 📅 Schedule Generation

- 🛠️ **Configure** scheduling constraints (working hours, days, breaks).
- 🔄 **Generate** a schedule based on tasks and constraints.
- 🔔 **Receive Telegram Notifications 10 Minutes Before Meetings.**
- 🔍 **Fetch** and view a schedule by ID.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
```

