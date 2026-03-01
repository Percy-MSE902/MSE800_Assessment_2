# Housekeeping Service Management System - Project Specifications

Below is the complete list of core project specifications with one-line descriptions.

1. **Technology Stack – Backend**  
   Developed using Python + FastAPI + SQLAlchemy + Pydantic + MySQL.

2. **RESTful API Architecture**  
   All backend functionality exposed through modern, high-performance RESTful endpoints.

3. **Role-Based Access Control (RBAC)**  
   Three distinct user roles: Customer, Cleaner, Administrator with different permissions.

4. **Two-Factor Authentication (2FA)**  
   Mandatory TOTP-based 2FA implementation during new user registration for enhanced security.

5. **User Registration & Authentication**  
   Secure registration/login流程 with email verification simulation and 2FA setup.

6. **Customer Service Booking**  
   Customers can create cleaning requests specifying type, date/time, location, duration, and special instructions.

7. **Task/Job Listing & Acceptance**  
   Cleaners can view available/open jobs and accept assignments.

8. **Task Assignment & Manual Override**  
   Administrators can manually assign jobs to cleaners when needed.

9. **Service Status Workflow**  
   Full lifecycle: Pending → Assigned → Accepted → In Progress → Completed → Confirmed.

10. **Service Completion & Confirmation**  
    Cleaners mark jobs as completed; customers confirm service quality (or dispute).

11. **Dynamic Pricing Rules**  
    Service fee calculated based on type, duration, location surcharge, and special requirements.

12. **Virtual Payment & Balance System**  
    Simulated wallet: customer balance deducted, cleaner balance credited upon confirmed completion.

13. **Transaction History & Audit Trail**  
    All payment movements and status changes recorded with timestamps for reporting.

14. **Admin Dashboard – User Management**  
    Administrators can view, suspend, activate, or delete user accounts.

15. **Admin Dashboard – Job Oversight**  
    Admins can monitor all jobs, reassign, cancel, or resolve disputes.

16. **Admin Dashboard – Financial & System Reports**  
    Summary reports: total revenue, cleaner earnings, completed jobs, user statistics.

17. **Responsive Vue.js Frontend**  
    Modern single-page application with role-based dashboards for all three user types.

18. **Vue Router & Protected Routes**  
    Client-side routing with authentication guards for role-specific views.

19. **API Client Communication**  
    Frontend uses Axios to securely communicate with FastAPI backend.

20. **API Documentation (Swagger)**  
    Automatic interactive API documentation generated and accessible via /docs.

21. **Data Validation & Serialization**  
    All request/response payloads strictly validated using Pydantic models.

22. **Containerization**  
    Application packaged using Docker (backend + frontend + database possible).

23. **Environment Variable Configuration**  
    Sensitive settings (DB credentials, secret keys, etc.) managed via .env files.

24. **Live Cloud Deployment**  
    Full application deployed to a public URL using a free platform (Render, Railway, Fly.io, Northflank, etc.).

25. **Clean Architecture & Separation of Concerns**  
    Code organized into routers, services, models, schemas, utils layers.

26. **Source Code Version Control**  
    Project hosted in a shared/group GitHub repository with clear commit history.

27. **Project Documentation Deliverables**  
    Includes README, architecture diagram, database schema, API usage examples.
