# MSE800_Assessment_2
This project aims to design and develop a Housekeeping Service Management System using modern Python-based backend technologies and a Vue.js frontend. The system simulates a real-world cleaning service platform that connects customers, cleaners, and administrators through a complete and structured business workflow.
The system supports a full business lifecycle, including user registration, service booking, task assignment, service execution, billing, virtual payment, and reporting. Customers can create cleaning requests by specifying service type, time, location, and special requirements. Cleaners can view available tasks, accept assignments, and complete services. Administrators oversee system operations, manage users, assign tasks when necessary, and monitor transactions and system performance.
A virtual payment mechanism is implemented to simulate financial transactions without integrating real-world payment gateways. When a service is completed and confirmed, the system automatically calculates the service fee based on predefined pricing rules. The customer’s virtual balance is deducted, and the cleaner’s balance is increased accordingly. All payment activities are recorded for transparency and reporting purposes.
⸻
Tools and Technology
The project adopts a popular and industry-relevant technology stack, ensuring scalability, maintainability, and alignment with current software development practices:
Backend:

Programming Language: Python
Backend Framework: FastAPI (for high-performance RESTful API development)
Database: MySQL
ORM: SQLAlchemy (for database interaction and data modeling)
Data Validation: Pydantic (schema-based request and response validation)
API Architecture: RESTful APIs
Authentication: Role-based access control (Customer / Cleaner / Admin) with Two-Factor Authentication (2FA) using TOTP during registration and optional login
Documentation: Automatic API documentation using Swagger (FastAPI built-in)

Frontend:

Framework: Vue.js (for responsive and interactive user interface)
HTML5, CSS3, JavaScript (ES6+)
Axios (for API communication)
Vue Router (for client-side routing)
Role-based dashboards for Customers, Cleaners, and Administrators
Optional UI framework: Bootstrap or Vuetify for consistent design

The system follows a clean architecture, separating concerns into models, schemas, services, API routes, and frontend components to improve readability, maintainability, and extensibility.
⸻
Deployment
The application will be deployed as a live full-stack system, simulating a production environment:

Backend: FastAPI application running on a cloud or virtual server environment
Database: MySQL as the persistent storage service
Containerization: Docker for consistent deployment and environment configuration
Frontend: Vue.js application built and served as static files via Nginx or similar server
API Access: HTTP endpoints tested using tools such as Postman or Swagger UI
Configuration: Environment variables for sensitive settings such as database credentials

The entire system will be deployed as a live application using a free or low-cost cloud platform (e.g., Railway.app for full-stack Dockerized apps, Render.com for backend + static frontend, or Vercel for Vue.js frontend combined with a serverless-compatible FastAPI setup). This ensures the project is accessible online for demonstration, testing, and evaluation, showcasing real-world deployment skills including Docker, environment management, and basic CI/CD concepts.
This deployment demonstrates practical knowledge of modern full-stack development and DevOps fundamentals.
⸻
Outcome
The expected outcomes of this project include:

A fully functional Housekeeping Service Management System implementing a complete business workflow.
A structured backend application using FastAPI, MySQL, SQLAlchemy, and Pydantic.
A responsive frontend interface using Vue.js, providing dashboards and interactive features for all user roles.
A simulated billing and virtual payment system, demonstrating transactional logic and data consistency.
Well-documented RESTful APIs suitable for future frontend or mobile application integration.
Enhanced security through implementation of Two-Factor Authentication (2FA) during user registration: users generate a TOTP secret (using libraries like pyotp), scan a QR code with an authenticator app (e.g., Google Authenticator), and verify the code before account activation, significantly reducing risks from credential compromise.
A live deployed version of the full application, hosted on a free cloud platform (e.g., Railway, Render, or Vercel + compatible backend service), allowing real-time interaction, API testing via Swagger, and demonstration of end-to-end functionality in a production-like environment.
Clear project deliverables, including:
Source code repository
Database schema design
API documentation
System architecture and workflow diagrams
Deployment guide (Dockerfiles, docker-compose.yml, platform-specific setup instructions)

Support and maintenance guidelines for future improvements

Overall, this project demonstrates the ability to design, implement, secure, and deploy a real-world inspired full-stack software system using modern Python and JavaScript technologies, meeting both academic and industry expectations.
