# Banking App – Phase 4 Project

A full-stack **banking web application** built as a **Phase 4 group project**. The application is a **single-page React app** that communicates asynchronously with a **FastAPI backend** using JSON. It implements **JWT-based authentication**, protected routes, and relational database design.

---

## Project Requirements Alignment

This project is designed to fully meet the **Phase 4 Project Requirements**:

### Frontend (React SPA)

* Built with **React** as a **single-page application** (one HTML file)
* At least **8 client-side routes**
* At least **5 protected routes** requiring authentication
* State management using **Context API / Redux / Zustand**
* Password/PIN reset flow for users who forget credentials
* Styled with **TailwindCSS / Bootstrap** for a clean, professional UI

### Backend (FastAPI REST API)

* Built with **FastAPI**
* At least **8 REST endpoints**

  * Minimum **2 each** of: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`
* At least **5 protected endpoints** (JWT required)
* **JWT authentication** using access tokens
* Asynchronous client–server communication using **JSON**

### Database Requirements

* At least **4 database models**, each with **4+ columns** (excluding ID)
* At least **2 one-to-many relationships**
* At least **1 many-to-many relationship**

### Engineering & Workflow

* Dependency management with **Pipenv**
* Clear and consistent **Git commit history**
* Organized project structure
* Deployed backend and frontend accessible via remote URLs
* Includes a project **license**

---

## Tech Stack

### Frontend

* React
* React Router
* State Management (Context API / Redux / Zustand)
* TailwindCSS or Bootstrap

### Backend

* FastAPI
* Python
* SQLAlchemy
* JWT (python-jose)
* Passlib (bcrypt)

### Database

* PostgreSQL / SQLite (development)

---

## Getting Started (Backend)

### Clone the Repository

```bash
git clone <repository-url>
cd Banking-App
```

### Install Dependencies

```bash
pipenv install
pipenv shell
```

### Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key
```

⚠️ **Never commit `.env` files**

---

## Running the Backend

```bash
uvicorn app.main:app --reload
```

---

## Authentication Flow

1. User logs in with credentials / PIN
2. PIN is verified using **bcrypt hashing**
3. Server issues a **JWT access token**
4. Token is sent with requests via the `Authorization` header

```http
Authorization: Bearer <access_token>
```

5. Protected routes verify the token before granting access

---

## Project Structure

```text
Banking-App/
│
├── app/
│   ├── main.py
│   ├── security.py
│   ├── models.py
│   ├── routes/
│   └── database.py
│
├── frontend/
│   └── (React App)
│
├── Pipfile
├── Pipfile.lock
├── README.md
└── LICENSE
```

---

## Team Contributions

This is a **group project**. All team members contribute to a **single repository** and update the project tracker daily.

* Ashley Mararo
* Daniel Kamweru
* David Kuron
* Jabir Ali Noor
* Thomas Mbula
* Yvonne Kadenyi

---

## License

This project is licensed under the MIT License and is intended for educational purposes only.
