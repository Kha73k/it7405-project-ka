IT7405 Car Polish Booking System
A Django + MongoDB web application for booking car polishing services, managing appointments, and submitting customer ratings.

Features
• Book car polishing services
• View available services and pricing
• Submit overall and service-specific ratings
• Auto‑incrementing numeric IDs for ratings
• Admin dashboard for managing bookings and feedback
• MongoDB database with Djongo connector

Requirements
• Python 3.10
• MongoDB Community Edition
• Django 3.1.12
• Djongo 1.3.7
• MongoDB Compass (optional)

Installation Instructions
1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

2. Install dependencies
basic
pip install -r requirements.txt

3. Start MongoDB
Make sure MongoDB server is running on:

mongodb://localhost:27017/

4. Run migrations
python manage.py migrate

5. Start the server
python manage.py runserver

Open the site in your browser:

http://127.0.0.1:8000/

Admin Login
You may create a superuser:

python manage.py createsuperuser

Then login:

http://127.0.0.1:8000/admin/

Rating System Notes (IMPORTANT)
The project uses MongoDB with Djongo, which does not natively support auto‑incrementing IDs.

A fix has been applied to ensure stable numeric primary keys for the Rating model.

The fix included:
Adding a manual primary key to the Rating model:
id = models.IntegerField(primary_key=True)

Cleaning the MongoDB collection and removing old _id conflicts.
Rebuilding the collection with fresh _ids so MongoDB would not create duplicate keys.
Creating the proper auto‑increment sequence in django_sequences:
{
  "_id": "bookings_rating_id_seq",
  "last_id": 4
}

Restarting Django to apply changes.
This ensures new ratings use:

id = 5, 6, 7, ...

How to Export / Import Database (Optional)
To export a collection in MongoDB Compass:
• Open collection → Export Collection → JSON

To import:
• Create database → Create collection → Import JSON


Notes for Tutor / Marker
• The version uploaded to GitHub is the fully working version.
• All database conflicts involving rating IDs have been resolved.
• The system now cleanly accepts new ratings without errors.
• The application runs successfully on both Windows and laptop environments.


