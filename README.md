# MSE800_Assessment_2
# Housekeeping Service Management System

This project aims to design and develop a **Housekeeping Service Management System** using modern Python-based backend technologies and a Vue.js frontend. The system simulates a real-world cleaning service platform that connects customers, cleaners, and administrators through a complete and structured business workflow.

The system supports a full business lifecycle, including user registration, service booking, task assignment, service execution, billing, virtual payment, and reporting. Customers can create cleaning requests by specifying service type, time, location, and special requirements. Cleaners can view available tasks, accept assignments, and complete services. Administrators oversee system operations, manage users, assign tasks when necessary, and monitor transactions and system performance.

A virtual payment mechanism is implemented to simulate financial transactions without integrating real-world payment gateways. When a service is completed and confirmed, the system automatically calculates the service fee based on predefined pricing rules. The customer’s virtual balance is deducted, and the cleaner’s balance is increased accordingly. All payment activities are recorded for transparency and reporting purposes.

## Tools and Technology

The project adopts a popular and industry-relevant technology stack, ensuring scalability, maintainability, and alignment with current software development practices:

### Backend
- **Programming Language**: Python
- **Backend Framework**: FastAPI (for high-performance RESTful API development)
- **Database**: MySQL
- **ORM**: SQLAlchemy (for database interaction and data modeling)
- **Data Validation**: Pydantic (schema-based request and response validation)
- **API Architecture**: RESTful APIs
- **Authentication**: Role-based access control (Customer / Cleaner / Admin) with **Two-Factor Authentication (2FA)** during user registration for enhanced security
- **Documentation**: Automatic API documentation using Swagger (FastAPI built-in)

### Frontend
- **Framework**: Vue.js (for responsive and interactive user interface)
- **HTML5, CSS3, JavaScript** (ES6+)
- **Axios** (for API communication)
- **Vue Router** (for client-side routing)
- Role-based dashboards for Customers, Cleaners, and Administrators
- Optional UI framework: Bootstrap or Vuetify for consistent design

The system follows a clean architecture, separating concerns into models, schemas, services, API routes, and frontend components to improve readability, maintainability, and extensibility.

## Deployment

The application will be deployed as a live full-stack system, simulating a production environment:

- **Backend**: FastAPI application running on a cloud or virtual server environment
- **Database**: MySQL as the persistent storage service
- **Containerization**: Docker for consistent deployment and environment configuration
- **Frontend**: Vue.js application built and served as static files via Nginx or similar server
- **API Access**: HTTP endpoints tested using tools such as Postman or Swagger UI
- **Configuration**: Environment variables for sensitive settings such as database credentials
- **Live Deployment**: The project will be deployed as a live application using a free hosting service or cloud platform (e.g., Render, Railway, Vercel for frontend + backend integration, or Northflank for full-stack with databases). This demonstrates practical knowledge of modern full-stack development, DevOps fundamentals, and accessible cloud deployment options.

## Outcome

The expected outcomes of this project include:

1. A fully functional Housekeeping Service Management System implementing a complete business workflow.
2. A structured backend application using FastAPI, MySQL, SQLAlchemy, and Pydantic.
3. A responsive frontend interface using Vue.js, providing dashboards and interactive features for all user roles.
4. A simulated billing and virtual payment system, demonstrating transactional logic and data consistency.
5. Well-documented RESTful APIs suitable for future frontend or mobile application integration.
6. **Enhanced Security**: Implementation of a second authenticator (e.g., two-factor authentication using TOTP via libraries like PyOTP) during new user registration to significantly improve account security against unauthorized access.
7. **Live Deployment**: The entire system deployed as a publicly accessible live application on a free cloud platform, showcasing real-world production readiness.
8. Clear project deliverables, including:
   - Source code repository
   - Database schema design
   - API documentation
   - System architecture and workflow diagrams
9. Support and maintenance guidelines for future improvements

Overall, this project demonstrates the ability to design, implement, and deploy a real-world inspired full-stack software system using modern Python and JavaScript technologies, meeting both academic and industry expectations — now with strengthened security (2FA) and live cloud deployment.
