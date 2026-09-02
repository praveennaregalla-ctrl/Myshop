# ClothBook Backend - Python Flask & MySQL

Flask REST API backend with SQLAlchemy ORM, JWT Authentication, and transactional services for ClothBook.

## Requirements
- Python 3.9+
- MySQL 8.0+

## Quick Start

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Database:
   Create a `.env` file or update `app/config.py` with your MySQL credentials:
   ```env
   MYSQL_USER=root
   MYSQL_PASSWORD=password
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_DB=clothbook_db
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret-key
   ```

4. Initialize MySQL Database:
   ```bash
   mysql -u root -p < schema.sql
   ```

5. Run Seed Data & Server:
   ```bash
   python run.py
   ```
   The API will be live at `http://localhost:5000`.
