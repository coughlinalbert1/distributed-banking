# distributed-banking
Building a distributed banking application using a microservice architecture. The tech stack can be React, Python-FastAPI, OAuth2, Redis, Nginx, Docker, Kubernetes

<img width="1116" alt="image" src="https://github.com/coughlinalbert1/distributed-banking/assets/111651444/3ca3b82a-fd44-441a-89b7-1623c2cb98e6">


## Core Services
### User Service
- user account management
- Authentication
- Authorization

### Link to Video Demonstration
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/Cr3XkhOw9xE/0.jpg)](https://www.youtube.com/watch?v=Cr3XkhOw9xE)


## Authorization Service
### Registers users, creates access tokens
The authorization service creates accounts, hashes passwords, and verify credentials. Passwords are hashed and verified using bcrypt from the passlib library. This is done so that passwords are never stored in plain text in the Redis database. This is standard practice for account creation and credential verification. The transaction and account service make calls to this service to handle account creation and credential verification.

## Account Service
#### Handles bank accounts (i.e. account creation, balance tracking, login)
This service handles logging in, account creation, and retrieving account data. To fulfill these tasks, the account service makes calls to the authorization service to make sure it is ok to create the account with the given data, allow logging in, and to retrieve the user data.


## Transaction Service
### Manages all transations (i.e. deposit, withdrawl, and transfers)
This service locks the transactions so that a user must have valid credentials and a JWT session token. Once these have been granted, the user can make transactions.


## Improvements for the Future
Create a React front end and a NGINX API gateway to forward requests from the client to the APIs.


## Supporting Services
### API Gateway
This app will use NGINX for the gateway. The API Gateway acts as an entry point for client requests into the application. It routes the request to the appropriate core service (microservice) and provides load balancing, SSL termination, and authentication.


## Containers and Orchestration
### Container - Docker
Each microservice and some components (like NGINX and Kafka) of the application will be encapsulated into a container. This ensures consistency for development, testing, and production environments.


