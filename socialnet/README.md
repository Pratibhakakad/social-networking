# Social Networking API

This is a Django-based social networking API that allows users to sign up, log in, search for other users, send/accept/reject friend requests, and list friends. The application is containerized using Docker and uses MySQL as the database.

## Features

- User Signup
- User Login
- Search Users by Email or Name
- Send/Accept/Reject Friend Requests
- List Friends
- List Pending Friend Requests
- Rate Limiting for Sending Friend Requests

## Requirements

- Docker
- Docker Compose

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Pratibhakakad/social-networking
cd socialnet

## Set Up Environment Variables
## Create a .env file in the root of your project and add the following environment variables:

DEBUG=1
SECRET_KEY=your_secret_key
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
DATABASE_URL=mysql://social_network_user:password@db:3306/social_network_db

## pip install -r requirements.txt
##  Build and Run Docker Containers
To run the project using Docker, build and start the containers:
docker-compose up --build

## Apply Migrations
Run the following commands to apply database migrations:
docker-compose exec web python manage.py migrate

##Create a Superuser
To create a superuser for accessing the Django admin panel:
docker-compose exec web python manage.py createsuperuser

##The application will be accessible at http://localhost:8000.
## Postman Collection
Import the social_networking_api.postman_collection.json file into Postman and use it to interact with the API.

To stop the containers, use docker-compose down.
To rebuild the containers after making changes, use docker-compose up --build.