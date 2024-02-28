# distributed-banking
Building a mock banking application using a microservice architecture. The tech stack will be React (maybe can skip building a front end to save time), Python-FastAPI, OAuth2, PostgreSQL + Citus, Nginx, Kafka, Docker, Kubernetes, + maybe something for logging?

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

### Loan Service (We can probably skip this service bc it sounds like a pain)
- Manages loan application (i.e. approvals, disburments, and repayments)

### Payment Service (maybe skip this too for same reasons)
- external payments, direct debits, and payment gateways

### Notification Service
- Sends transaction alerts, loan reminders, and other notifications to users via email, SMS, or in-app

## Supporting Services
### API Gateway
This app will use NGINX for the gateway. The API Gateway acts as an entry point for client requests into the application. It routes the request to the appropriate core service (microservice) and provides load balancing, SSL termination, and authentication.

### Servcice Discovery
Consul or Eureka will be used for this supporting service. This will handle service registration, discovery, and will enable the services to communicate with eachother.

### Config Service
Centralizes and manages external configurations for services in different environments.

### Circuit Breaker Service
Prevents failures from cascading to the other services. The circuit breaker does this by managing and isolating failures in the system.

## Data Management
### Distributed Database
This app will use PostgreSQL with the Citus extension. Citus horizontally scales PostgreSQL to distribute data and queries across multiple nodes. Citus allows the app to utilize true distribution and access more processing power due to the nature of horizontal scaling. Each service having its own node (database) increase the fault tolerance of the app. 

## Event Driven Architecture
### Message Broker
We can use Kafka for this. It facilitates asynchronous communication between services via events, which ensures loose coupling, enhances scalability, and improves the overall system's resilience.

## Containers and Orchestration
### Container - Docker
Each microservice and some components (like NGINX and Kafka) of the application will be encapsulated into a container. This ensures consistency for development, testing, and production environments.

### Orchestration - Kubernetes (K8s)
Manages the lifecycle of containers, including deployment, scaling, and management of containerized applications.
