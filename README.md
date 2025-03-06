# Distributed Banking System

A Microservices-based banking backend built with FastAPI, Redis, and Docker.

[Link to repository](https://github.com/coughlinalbert1/distributed-banking)

<img width="1116" alt="image" src="https://github.com/coughlinalbert1/distributed-banking/assets/111651444/3ca3b82a-fd44-441a-89b7-1623c2cb98e6">


The Distributed Banking System is a microservices-based backend designed for secure financial transactions, including user authentication, account management, and transaction processing. It utilizes FastAPI, Redis, OAuth2, JWT, and Docker to ensure scalability, security, and efficiency.


## Features
✔ Microservices Architecture – Modular services for authentication, accounts, and transactions.

✔ JWT-based Authentication – Secure user login with OAuth2.

✔ Redis as a Database & Message Broker – Fast, in-memory data storage and inter-service communication.

✔ Containerized with Docker – Simplifies deployment and scaling.

✔ Asynchronous API Calls – Optimized performance with Uvicorn and Redis Streams.

✔ Planned API Gateway (NGINX) – Future support for load balancing and improved security.


## How it Works
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/Cr3XkhOw9xE/0.jpg)](https://www.youtube.com/watch?v=Cr3XkhOw9xE)


## 🛠️ Tech Stack

| **Category**          | **Technology Used**      |
|----------------------|------------------------|
| **Backend**          | FastAPI, Python        |
| **Database**         | Redis                  |
| **Authentication**   | OAuth2, JWT            |
| **Service Communication** | Redis Streams  |
| **Containerization** | Docker                 |
| **Planned Enhancements** | NGINX API Gateway, Deployment |

## 📂 Microservices
The system consists of three main microservices:

### 1️⃣ Authentication Service
- Manages **user registration, login, and password hashing** using bcrypt.
- Issues **JWT tokens** for authentication.
- Uses **OAuth2** for secure access.

### 2️⃣ Account Service
- Handles **account creation, balance tracking, and user identity verification**.
- Interacts with **Redis for account data storage**.
- Requires **JWT authentication** for security.

### 3️⃣ Transaction Service
- Manages **deposits, withdrawals, and transfers** securely.
- Utilizes **Redis Streams** for inter-service communication.
- Verifies **account balance before processing transactions**.

---

## 📦 Setup & Installation
### 🔹 Prerequisites
Ensure you have:
- **Python 3.9+**
- **Docker & Docker Compose**
- **Redis installed locally** (or use Docker)

### 🔹 Clone the Repository
```bash
git clone https://github.com/coughlinalbert1/distributed-banking.git
cd distributed-banking
```


### 🔹 Install Dependencies
```bash
pip install -r requirements.txt
```

### 🔹 Configure Environment Variables  
Before running the project, ensure you have the necessary environment variables set up:  

1. **Create the required environment files** (`.env` or config files) for each service.  
2. **Set up a Redis instance** (either locally or using a cloud provider like RedisLabs).  
3. **Add your Redis database connection URL** to the environment variables.  

Failure to configure these variables may result in connection issues between services.

### 🔹 Run with Docker
```bash
pip install -r requirements.txt
```

### 🔹 Run Services Manually (Without Docker)
```bash
uvicorn auth_service.main:app --host 0.0.0.0 --port 8001
uvicorn account_service.main:app --host 0.0.0.0 --port 8002
uvicorn transaction_service.main:app --host 0.0.0.0 --port 8003
```

## 📖 API Documentation
Once running, FastAPI provides an interactive API UI at:
-	**Authentication Service → http://localhost:8001/docs**
-	**Account Service → http://localhost:8002/docs**
-	**Transaction Service → http://localhost:8003/docs**

## 🔮 Future Enhancements

| Feature | Description |
|---------|------------|
| 🚧 **NGINX API Gateway** | Implement load balancing, request routing, and security improvements. |
| 🚧 **Frontend UI (React-based dashboard)** | Develop a user-friendly interface for account management and transactions. |
| 🚧 **Database Upgrade** | Move from Redis to PostgreSQL for persistent data storage. |
| 🚧 **Advanced Monitoring** | Integrate Prometheus & Grafana for real-time system monitoring. |
| 🚧 **Kubernetes Deployment** | Improve scalability by deploying microservices using Kubernetes. |
| 🚧 **Event-Driven Architecture** | Implement Kafka or RabbitMQ for more scalable inter-service communication. |

## 👨‍💻 Contributors
Albert Coughlin – Backend Engineer

## 📜 License
This project is licensed under the MIT License – feel free to use and modify.
