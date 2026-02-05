🔗<div align="center">

# 🔗 Shortly
### Authenticated URL Shortener

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

**A full-stack URL shortening service with user authentication.** *Built to understand backend fundamentals, security tradeoffs, and data ownership.*

</div>

---

## 📖 About The Project

**Shortly** is not just a redirect service; it is a learning exercise in designing a small backend system end-to-end. Unlike simple anonymous shorteners, Shortly focuses on **data ownership**—ensuring users can track, manage, and delete the links they create.

**Key Design Decisions:**
* **Session-Based Auth:** Chosen over JWT to explore server-side session management and secure cookies.
* **Separation of Concerns:** Distinct separation between request handling (`app.py`) and database access (`db.py`).
* **Defensive Coding:** Ownership-based data access ensures users can only modify their own resources.

---

## ✨ Features

| Category | Capability |
| :--- | :--- |
| **Authentication** | User registration, login, and secure session management. |
| **Core Function** | URL shortening with collision handling & custom 404 redirects. |
| **Data Ownership** | Users can view history and delete their own URLs. |
| **Metadata** | Automatic extraction of page titles from target URLs (fault-tolerant). |
| **Security** | Password hashing (Werkzeug) & CORS with credential support. |

---

## 🧱 Tech Stack

### Backend
* **Language:** Python
* **Framework:** Flask
* **Database:** MySQL (using `mysql-connector-python`)
* **Auth:** Server-side Sessions (Secure Cookies)
* **Utilities:** `BeautifulSoup4` (Metadata), `Werkzeug` (Security)

### Frontend
* **Core:** HTML5, CSS3, Vanilla JavaScript
* **Network:** Fetch API (configured with `credentials: include`)

---

## 🏗️ Architecture

```mermaid
graph TD
    User[Frontend Client] -->|Fetch API + Credentials| API[Flask Backend]
    API -->|Connector| DB[(MySQL Database)]
    
    subgraph "Data Flow"
    API -- Hashed Passwords --> DB
    API -- Short Codes --> DB
    end

---

## 📡 API Reference

### Authentication

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/register` | Register a new user account. |
| `POST` | `/api/login` | Authenticate user and set session cookie. |
| `POST` | `/api/logout` | Invalidate session and log out. |

### URL Management

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/shorten` | Create a new short URL (Requires Auth). |
| `GET` | `/api/urls` | Retrieve the logged-in user's URL history. |
| `DELETE` | `/api/urls/<id>` | Delete a specific URL (Ownership verified). |

### Redirection

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/<short_code>` | Redirects to the original URL or shows custom 404. |

---

## 🗄️ Database Schema

### `users` table
* **id** (PK): Integer, Auto-increment
* **username**: Varchar (Unique)
* **password_hash**: Varchar (Stored securely)
* **created_at**: Timestamp

### `dmforlink` table
* **id** (PK): Integer, Auto-increment
* **original**: Text (Original URL)
* **short_code**: Varchar (Unique identifier)
* **link_name**: Varchar (Scraped page title)
* **user_id** (FK): Links to `users.id` (Cascading delete)
* **created_at**: Timestamp

---

## ⚙️ Local Setup

Follow these steps to get the project running on your machine.

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd url-shortener

### 2. Configure Environment
Create a `.env` file in the root directory:
```ini
DB_HOST=localhost
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=url_shortner
FLASK_SECRET_KEY=generate_a_strong_random_key_here

### 3. Initialize Database
Log into your MySQL instance and run the source SQL:
```sql
SOURCE database.sql;

### 4. Install Dependencies
```bash
pip install flask flask-cors mysql-connector-python python-dotenv requests beautifulsoup4

### 5. Run the Application
**Backend:**
```bash
python app.py
**Frontend:**
Open `index.html` using a generic local server (e.g., VS Code Live Server).

---

## 🚧 Limitations & Roadmap

This project focuses on correctness over scale. Current limitations include:

* [ ] **Rate Limiting:** Currently vulnerable to abuse.
* [ ] **Async Jobs:** Metadata fetching is synchronous (blocks request).
* [ ] **CSRF Protection:** Standard token protection is planned.
* [ ] **HTTPS:** Production deployment would enforce HTTPS.
* [ ] **Scalability:** Short code generation is probabilistic.

---

## 🎯 Learning Outcomes

This project was built to demonstrate proficiency in:
1.  **Request Lifecycle:** Managing HTTP verbs, headers, and status codes.
2.  **State Management:** Handling user sessions without relying on JWTs.
3.  **Relational Design:** writing efficient SQL schemas with Foreign Keys.
4.  **Security First:** Implementing salt/hash for passwords and ownership checks for data access.

