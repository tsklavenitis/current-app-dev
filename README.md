
# ORM Project Deployment Guide

This document provides step-by-step instructions for setting up, building, and deploying the ORM Project to Heroku. It also includes critical steps for backing up the database before deployment to ensure no data is lost.

## Prerequisites

- **Git**: Make sure you have Git installed on your machine.
- **Heroku CLI**: Install the Heroku CLI from [Heroku's official website](https://devcenter.heroku.com/articles/heroku-cli).
- **Python**: Ensure Python is installed and the necessary virtual environment tools are available.

## Step 1: Clone the Repository from GitHub

To get started, clone the project repository from GitHub:

```bash
git clone https://github.com/your-username/ormproject.git
cd ormproject
```

Replace `your-username` with your actual GitHub username.

## Step 2: Set Up the Virtual Environment

Create and activate a virtual environment for the project:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

## Step 3: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Step 4: Set Up the Django Project

Make sure all migrations are applied:

```bash
python manage.py migrate
```

Collect static files:

```bash
python manage.py collectstatic
```

## Step 5: Prepare for Deployment to Heroku

### Add the Heroku Remote

Ensure the Heroku remote is added to your Git repository:

```bash
heroku git:remote -a avaxermapp
```

### Backup the Online Database

Before deploying any changes, back up the current database from Heroku:

```bash
heroku ps:copy ./db.sqlite3 -a avaxermapp
```

This command downloads the `db.sqlite3` file from the Heroku app to your local machine. Verify that the backup is correct before proceeding.

### Deploy to Heroku

1. **Commit Changes**:

    Ensure all changes are committed:

    ```bash
    git add .
    git commit -m "Prepare for redeployment"
    ```

2. **Push to Heroku**:

    Deploy your changes to Heroku:

    ```bash
    git push heroku master
    ```

    Or, if you’re using the `main` branch:

    ```bash
    git push heroku main
    ```

3. **Run Migrations**:

    If your deployment includes database schema changes, apply the migrations on Heroku:

    ```bash
    heroku run python manage.py migrate -a avaxermapp
    ```

## Step 6: Verify the Deployment

Open your deployed application to verify everything is working correctly:

```bash
heroku open -a avaxermapp
```

Ensure the application is running as expected and that the data is intact.

## Troubleshooting

- **Heroku Git Remote Not Set**: If you encounter issues with the Heroku remote, ensure it’s added correctly using `heroku git:remote -a avaxermapp`.
- **Database Issues**: Always back up your database before deploying to avoid data loss.

## Conclusion

By following these steps, you should be able to successfully set up, deploy, and manage the ORM Project on Heroku. Remember to always back up the database before deploying to ensure your data is safe.
