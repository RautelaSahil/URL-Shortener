🔗 Shortly — Authenticated URL Shortener

A full-stack URL shortening service with user authentication, built to understand backend fundamentals, security tradeoffs, and data ownership rather than just URL redirection.

This project was developed as a learning exercise to design and implement a small backend system end-to-end, including authentication, persistence, and a simple frontend client.


---

✨ Features

User registration and login

Session-based authentication using secure cookies

URL shortening with collision handling

Per-user URL ownership and history

Redirect handling with custom 404 page

URL metadata extraction (page title)

Delete URLs owned by the user

Basic health check endpoint



---

🧱 Tech Stack

Backend

Python, Flask

MySQL

Session-based authentication

Password hashing using Werkzeug

CORS enabled for frontend integration


Frontend

HTML, CSS, Vanilla JavaScript

Fetch API with credentials

Minimal UI for auth, shortening, and history



---

🏗️ Architecture Overview

Frontend (HTML / JS)
        |
        |  (Fetch API with credentials)
        v
Flask Backend (REST APIs)
        |
        |  (MySQL Connector)
        v
MySQL Database

Key Design Decisions

Session-based auth was chosen over JWT for simplicity and to understand cookie-based authentication.

Separation of concerns between request handling (app.py) and database access (db.py).

Ownership-based data access: users can only view or delete URLs they created.

Metadata fetching (page title) is optional and fault-tolerant.



---

🔐 Authentication & Security Model

Passwords are stored as hashed values using generate_password_hash.

User sessions are stored server-side and tracked via secure cookies.

All protected routes validate session presence.

CORS is configured with supports_credentials=True for frontend integration.


> ⚠️ Note:
This project uses session cookies and is intended for local / learning use.
CSRF protection, HTTPS enforcement, and production-grade secret management are listed as future improvements.




---

📡 API Endpoints

Auth

Method	Endpoint	Description

POST	/api/register	Register a new user
POST	/api/login	Login user
POST	/api/logout	Logout user


URL Management

Method	Endpoint	Description

POST	/api/shorten	Create short URL
GET	/api/urls	Get user URL history
DELETE	/api/urls/<id>	Delete a user-owned URL


Redirect

| GET | /<short_code> | Redirect to original URL |


---

🗄️ Database Schema

users

id (PK)

username (unique)

password_hash

created_at


dmforlink

id (PK)

original (original URL)

short_code (unique)

link_name

user_id (FK → users.id)

created_at


Foreign key constraints ensure referential integrity and cascading deletes.


---

⚙️ Running Locally

1. Clone Repository

git clone <repo-url>
cd url-shortener

2. Setup Environment

Create a .env file:

DB_HOST=localhost
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=url_shortner
FLASK_SECRET_KEY=your_secret_key

3. Setup Database

SOURCE database.sql;

4. Install Dependencies

pip install flask flask-cors mysql-connector-python python-dotenv requests beautifulsoup4

5. Run Backend

python app.py

6. Run Frontend

Open index.html using a local server (e.g. Live Server).


---

⚠️ Known Limitations

No rate limiting (vulnerable to abuse)

No CSRF protection

No async background jobs for metadata fetching

No connection pooling

Not deployed (local environment only)

Short code generation is probabilistic (collision-checked but not deterministic)


These limitations are intentional learning boundaries and documented tradeoffs.


---

🚀 Future Improvements

JWT-based auth alternative

Rate limiting & abuse prevention

URL expiration support

Click analytics

Redis caching

Async metadata fetch

Dockerized deployment

HTTPS & CSRF protection



---

🎯 Learning Goals

This project focuses on:

Backend request lifecycle

Auth flows and session management

Database schema design

Ownership-based access control

Error handling and defensive coding

Full-stack integration



---

🧠 Final Note

This project prioritizes clarity and correctness over scale.
It is designed as a stepping stone toward building larger, production-grade backend systems.
