# BACKEND Repository for all BMS apps

### Overview

This project is a **production-grade Django REST API** repository which will be used to work on any backend projects within the BMS team

## Installation and Setup

### 1️ Clone the Repository

```bash
    git clone https://github.com/<your-org>/<your-repo>.git
    cd skbackend
```

### 2 Create a **Virtual Environment** and give it any name
```bash
python -m venv venv_name # Replace venv_name with your virtual env name
```

### 3 Activating installed virtual environment
```bash
source venv_name/bin/activate # venv_name should be replaced with your virtual environment name
```

### 3 Installing required packages
```bash
pip install -r requirements.txt
```

### 4 Create an .env file and paste Django key and any other keys shared from chat
```bash
# ensure you are in the project folder's root
touch .env
```

### 5 Apply migrations (For local development use the sqlite db)

```bash
python manage.py makemigrations #Please ensure you are in the project root
python manage.py migrate
```

### 6 Run development server
```bash
python manage.py runserver

```

## Swagger documentation endpoint

```bash
http://127.0.0.1:8080/api/docs/#/

```
