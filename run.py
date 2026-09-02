import os
from app import create_app
from app.extensions import db
from app.utils.seed_data import seed_database

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create tables automatically if using SQLite or fresh MySQL
        db.create_all()
        seed_database()

    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
