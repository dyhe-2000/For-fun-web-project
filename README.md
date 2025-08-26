## 📂 Project Structure

```text
flask-auth-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates (Jinja2)
│   ├── base.html          # Base layout template
│   ├── home.html          # Home page (after login)
│   ├── login.html         # User login page
│   ├── register.html      # User registration page with password checklist
│   ├── users.html         # List of all registered users
│   └── admin.html         # Admin dashboard
└── static/                # Static assets
    ├── css/
    │   └── style.css      # Custom styles including animations
    ├── js/
    │   └── script.js      # Frontend scripts
    └── images/
        └── flower.png     # Animated image on home page
