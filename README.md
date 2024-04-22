# distributed-banking
Building a distributed banking application using a microservice architecture. The tech stack can be React, Python-FastAPI, OAuth2, Redis, Nginx, Docker, Kubernetes

<img width="1116" alt="image" src="https://github.com/coughlinalbert1/distributed-banking/assets/111651444/3ca3b82a-fd44-441a-89b7-1623c2cb98e6">


## Core Services
### User Service
- user account management
- Authentication
- Authorization

## Authorization Service
### Registers users, creates access tokens
<img width="1067" alt="image" src="https://github.com/coughlinalbert1/distributed-banking/assets/111651444/770e444e-358c-47e8-b432-c3d1f1f2dfab">


This is the main service. Tokens, which are used to give a user who has valid credentials access to endpoints in the transaction service, are created in this service. This service handles the encryption of passwords and stores them in the Redis and decrypts the password in order to check if the user inputted the right password. This protects the user's private passowrd in case of attack. This service also has an endpoint for creating an account. If the username is unique, the user can create an account by following the schema provided in the request body.
<img width="1067" alt="image" src="https://github.com/coughlinalbert1/distributed-banking/assets/111651444/b8434024-7ecd-488a-a242-5bfd9a7f3420">
This is the endpoint for creating an account. The user will not directly make a call here, but it handles the authorization parts of this process. The text box is the request body and it requires a unique username and a password. If a username is taken, the API will return a HTTP 400 response code and a message that the username is already taken. If not, this will be the response:
<img width="1067" alt="image" src="https://github.com/coughlinalbert1/distributed-banking/assets/111651444/8a323c14-1b31-444d-92c7-68f8c1d24c9b">
The other endpoint is a login endpoint. This endpoint checks the database for valid login credentials then returns the username, userid, and access token information. For the access token creation, validation, and password hashing, we followed standard protocol for this. Oauth2 and JWT tokens are standard ways to sercure accounts.
<img width="1067" alt="image" src="https://github.com/coughlinalbert1/distributed-banking/assets/111651444/ba15354d-3fd5-4d95-b623-19ccba64f9dc">
<img width="1067" alt="image" src="https://github.com/coughlinalbert1/distributed-banking/assets/111651444/4f246df5-5da3-4cec-84fa-028cc65bf4df">


## Account Service
#### Handles bank accounts (i.e. account creation, balance tracking, login)
<img width="705" alt="image" src="https://github.com/coughlinalbert1/distributed-banking/assets/111651444/a7a4f55d-8f8f-4753-b8ab-b8e5d04ca836">

### Create a New Account
<img width="1067" alt="image" src="https://github.com/coughlinalbert1/distributed-banking/assets/111651444/35b5c950-f5b9-4fa4-baa3-801e5ae678a7">
<img width="1067" alt="image" src="https://github.com/coughlinalbert1/distributed-banking/assets/111651444/afde2e07-4b45-4b02-94f3-892bfcedb8a5">
<img width="1067" alt="image" src="https://github.com/coughlinalbert1/distributed-banking/assets/111651444/8fca8be1-1551-41f1-962e-2ac9db670441">





## Transaction Service
<img width="705" alt="image" src="https://github.com/coughlinalbert1/distributed-banking/assets/111651444/466fd310-e1fe-4823-a22e-4ce00933cbd8">
- Manages all transations (i.e. deposit, withdrawl, and transfers)
- Ensure transactional integrity and consistency


## Supporting Services
### API Gateway
This app will use NGINX for the gateway. The API Gateway acts as an entry point for client requests into the application. It routes the request to the appropriate core service (microservice) and provides load balancing, SSL termination, and authentication.


## Containers and Orchestration
### Container - Docker
Each microservice and some components (like NGINX and Kafka) of the application will be encapsulated into a container. This ensures consistency for development, testing, and production environments.


