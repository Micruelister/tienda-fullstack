# Tienda Full-Stack E-commerce

### 🚧 **Current Status: Work in Progress** 🚧
**This is a live learning project and is currently under active development. New features are being added and existing code is being refined.**

---

This is a full-stack e-commerce web application built to showcase skills in modern web development. The project leverages a Python-based back-end and a dynamic React front-end.

## 🚀 Features

*   **User Authentication:** Secure user registration and login functionality.
*   **Product Catalog:** Browse and view a list of available products.
*   **Shopping Cart:** Add products to a cart and manage its contents.
*   **RESTful API:** A well-structured back-end API built with Flask to handle all business logic.

## 🛠️ Tech Stack

*   **Front-end:** React, Vite, JavaScript, HTML5, CSS3
*   **Back-end:** Python, Flask, SQLAlchemy
*   **Database:** SQLite (for development), PostgreSQL-ready
*   **Deployment:** Docker, Docker Compose, Nginx

---

## 🌟 Project Structure Overhaul 🌟

This project has undergone a significant refactoring to improve its structure, security, and maintainability.

*   **Backend:** The Flask backend has been restructured from a single file into a scalable, modular application using the **Application Factory pattern** and **Blueprints**. This separates concerns and makes the codebase much easier to manage.
*   **Frontend:** The React frontend's authentication flow has been hardened to remove critical security vulnerabilities. It now relies on secure, server-side session validation instead of unsafe `localStorage`.
*   **Security:** Major security vulnerabilities have been addressed, including **Cross-Site Request Forgery (CSRF)**, **insecure file uploads**, and client-side authorization flaws.

---

## 🚀 Getting Started with Docker (Recommended)

This project is fully containerized, which is the easiest and most reliable way to get it running.

### Prerequisites

*   [Docker](https://docs.docker.com/get-docker/) installed on your machine.
*   [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop).

### 1. Configuration

Before you start, you need to create a `.env` file at the root of the project to configure the application. You can copy the example file:

```bash
cp .env.example .env
```

Now, open the `.env` file and fill in the required values:

*   `SECRET_KEY`: A long, random string for Flask's security features.
*   `DATABASE_URL`: The connection string for your database. For local testing, you can leave it as the default SQLite setting. For production, you should point it to a PostgreSQL or other production-ready database.
*   `VITE_API_BASE_URL`: The public URL of your backend. For local Docker deployment, this should be `http://localhost:5000/api`.
*   `VITE_GOOGLE_MAPS_API_KEY`: Your API key from the Google Cloud Platform for using Google Maps.
*   `STRIPE_API_KEY`: Your secret API key from Stripe.
*   `CORS_ORIGINS`: The URL of your frontend. For local Docker deployment, this should be `http://localhost:80`.

### 2. Build and Run the Application

With Docker running and your `.env` file configured, you can start the entire application with a single command from the project root:

```bash
docker-compose up --build
```

*   `--build` tells Docker Compose to build the images from the Dockerfiles the first time you run it.
*   The backend will be available at `http://localhost:5000`.
*   The frontend will be available at `http://localhost:80`.

### 3. Create an Admin User

To access the admin panel, you'll need to create an admin user. Open a new terminal and run the following command:

```bash
docker-compose exec backend flask create-admin <your-desired-password>
```

You can now log in with the username `admin` and the password you provided.

### 4. Stopping the Application

To stop the application, press `Ctrl + C` in the terminal where `docker-compose` is running. To stop and remove the containers, you can run:

```bash
docker-compose down
```
