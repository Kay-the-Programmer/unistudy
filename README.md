# ZStudy - Academic Resource Hub

ZStudy is a platform designed to help students access and share academic materials, engage in course-specific discussions, and stay updated with relevant university information.

## Features (Implemented & Planned)

*   **University & Course Browsing:** Explore universities, faculties, and their course offerings.
*   **Material Sharing:** Upload and download course materials like lecture notes, past papers, and assignments.
*   **Discussion Forums:** Engage in discussions related to specific courses or threads.
*   **User Accounts:** Sign up, log in, manage profiles.
*   **Notifications:** Get notified about new materials in relevant courses or replies to your discussions.
*   **Search:** Global search for materials by title or tags.
*   **Filtering:** Filter materials within a course by type, upload year, or uploader's university.
*   **Markdown Support:** Format discussion posts using Markdown.
*   **Moderation:** Staff tools for managing content (soft-delete, reporting).

## Setup Instructions

Follow these steps to set up the ZStudy project locally for development:

1.  **Clone Repository:**
    ```bash
    git clone <repository_url>
    cd zstudy-project # Or your project directory name
    ```

2.  **Create Virtual Environment:**
    It's highly recommended to use a virtual environment.
    ```bash
    python -m venv venv
    ```
    Activate the environment:
    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        venv\Scripts\activate
        ```

3.  **Install Dependencies:**
    Make sure your virtual environment is activated.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Open the `.env` file and fill in the required values. See the "Environment Variables" section below for details. At a minimum, ensure `DJANGO_SECRET_KEY` is set to a unique, random string for development.

5.  **Run Database Migrations:**
    This will create the necessary database tables.
    ```bash
    python manage.py migrate
    ```

6.  **Create a Superuser (Admin Account):**
    This account will have access to the Django admin interface.
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to set a username, email, and password.

7.  **Load Sample Data (Optional but Recommended for Dev):**
    This script populates the database with some initial universities, faculties, courses, and users.
    ```bash
    python manage.py load_sample_data
    ```

8.  **Run Development Server:**
    ```bash
    python manage.py runserver
    ```
    The application should now be running at `http://127.0.0.1:8000/`.

## Environment Variables (`.env` file)

The `.env` file is used to configure settings sensitive to the environment (development, production, etc.). It should not be committed to version control.

Here's an explanation of the variables found in `.env.example`:

*   `DJANGO_SECRET_KEY`: **Required.** A secret key for a particular Django installation. This is used to provide cryptographic signing, and should be set to a unique, unpredictable value. **Change this from the default for production!**
*   `DJANGO_DEBUG`: Set to `True` for development (enables debug information, auto-reloads server on code changes). Set to `False` for production.
*   `DJANGO_ALLOWED_HOSTS`: A comma-separated list of strings representing the host/domain names that this Django site can serve. For development, `localhost,127.0.0.1` is usually sufficient. For production, set this to your actual domain(s).
*   `DATABASE_URL`: Specifies the database connection.
    *   For local development with SQLite (default): `sqlite:///db.sqlite3`
    *   For PostgreSQL (example): `postgres://USER:PASSWORD@HOST:PORT/NAME`
*   `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL`: These are standard Django email settings. For development, `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` is set in `settings.py`, so emails are printed to the console. For production, you'll need to configure these for a real email provider.

## Running Tests

To run the automated tests for the project:
```bash
python manage.py test
```
To run tests for a specific app:
```bash
python manage.py test <app_name>
# e.g., python manage.py test materials
```

## Tech Stack

*   Python
*   Django
*   PostgreSQL (for production, SQLite for development)
*   Gunicorn (for production WSGI server)
*   Whitenoise (for serving static files in production)
*   HTML, CSS, Plain JavaScript

## Contributing

(Details on how to contribute will be added here if applicable.)

---

This `README.md` provides a good starting point. It can be expanded with more details about specific features, deployment to particular platforms, or contribution guidelines as the project evolves.
