# 🛍️ IntelliWear Backend — AI-Powered E-Commerce Platform

This is the **Django backend** of **IntelliWear**, an AI-powered e-commerce platform designed to make online shopping smarter, faster, and more personalized.

---

## 📌 Project Overview

The backend provides APIs and business logic to support advanced features such as:
- NLP-based voice/text search
- Image-based product search
- Virtual assistant functionality
- Real-time analytics dashboard for admin
- JWT-based authentication system
- Admin-controlled product and user management

---

## ⚙️ Tech Stack

- **Framework:** Django Rest Framework (Python)
- **Database:** PostgreSQL
- **Authentication:** JWT (Simple JWT)
- **Media Management:** Cloudinary
- **API:** Django REST Framework (DRF)

---

## 🛠️ Getting Started

### 📦 Prerequisites

Make sure you have the following installed:
- Python 3.9+
- PostgreSQL
- Virtualenv (optional but recommended)

---

### 🔧 Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/your-username/intelliwear-backend.git
cd intelliwear-backend
```
2 **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
3. **Install dependencies**

```bash
pip install -r requirements.txt
```
4. **Configure environment variables**

Create a .env file in the root directory and set the following:
```bash

SECRET_KEY=your-secret-key
EMAIL_HOST=your-credential
EMAIL_PORT=your-credential
DELIVERY_PARTNER_EMAIL=your-credential
EMAIL_HOST_USER=your-credential
EMAIL_HOST_PASSWORD=your-credential
EMAIL_USE_TLS=your-credential
DB_NAME=your-credential
DB_USER=your-credential
DB_PASSWORD=your-credential
DB_HOST=your-credential
DB_PORT=your-credential
DB_SSLMODE=your-credential
DEBUG=your-credential
STRIPE_SECRET_KEY=your-credential
STRIPE_PUBLIC_KEY=your-credential
STRIPE_WEBHOOK_SECRET=your-credential
FRONTEND_URL=your-credential
CLOUDINARY_CLOUD_NAME=your-credential
CLOUDINARY_API_KEY=your-credential
CLOUDINARY_API_SECRET=your-credential
```
5. **Apply migrations**

```bash

python manage.py migrate
```
6. **Run the server**

```bash

python manage.py runserver
```
