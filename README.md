# distributed-banking
Building a distributed banking application using a microservice architecture. The tech stack can be React, Python-FastAPI, OAuth2, Redis, Nginx, Docker, Kubernetes

## Core Services
### User Service
- user account management
- Authentication
- Authorization

### Account Service
- Handles bank accounts (i.e. account creation, balance tracking, and account closure)

### Transaction Service
- Manages all transations (i.e. deposit, withdrawl, and transfers)
- Ensure transactional integrity and consistency

### Authorization Service
- Registers user
- creates tokens

### Notification Service
- Sends transaction alerts, loan reminders, and other notifications to users via email, SMS, or in-app

## Supporting Services
### API Gateway
This app will use NGINX for the gateway. The API Gateway acts as an entry point for client requests into the application. It routes the request to the appropriate core service (microservice) and provides load balancing, SSL termination, and authentication.

### Config Service
Centralizes and manages external configurations for services in different environments.

### Circuit Breaker Service
Prevents failures from cascading to the other services. The circuit breaker does this by managing and isolating failures in the system.

## Containers and Orchestration
### Container - Docker
Each microservice and some components (like NGINX and Kafka) of the application will be encapsulated into a container. This ensures consistency for development, testing, and production environments.

### Orchestration - Kubernetes (K8s)
Manages the lifecycle of containers, including deployment, scaling, and management of containerized applications.
