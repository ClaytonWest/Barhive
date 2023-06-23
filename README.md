# Project Name

BarHive - A social network application for bars and nightlife enthusiasts

## Project Description

BarHive is a social networking platform for bars and people who love nightlife. It allows users to create profiles, connect with other users, and share posts related to their favorite bars and events. The application provides features such as creating posts, commenting, and liking posts. Users can also follow other users and view their profiles. The application also supports business profiles, which allows bar owners to create profiles for their bars and showcase their business.

## Technologies Used

The application is built using the following technologies:

- Python
- Flask
- PostgreSQL
- AWS S3
- HTML/CSS/JavaScript

## Getting Started

To run the application, first, clone the repository:

```bash
git clone https://github.com/WormWaffles/Forum-Project
```

Then, navigate to the project directory:

```bash
cd barhive
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and fill in following contents:

```bash
DB_USER=
DB_PASS=
DB_HOST=
DB_PORT=
DB_NAME=
SECRET_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
BUCKET_NAME=
URL=
```

Next, create the database by running the following command in postgres:

```bash
CREATE DATABASE barhive;
```

You will then need to create the tables from the database_schema.sql file.

Finally, start the application:

```bash
flask run
```

The application will be accessible at `http://127.0.0.1:5000` in your web browser.

## Database Schema

The application uses a PostgreSQL database with the following schema:

- `user` - Stores user profile information, including their name, email, and profile picture path
- `post` - Stores user posts, including their title, content, and associated image path
- `user_likes` - Stores information about which users liked which posts
- `rating` - Stores ratings given to business profiles by users
- `follower` - Stores information about which users are following which other users
- `comment` - Stores user comments on posts, including their content and associated image path

## ERD Data Schema
[PNG](static/images/ERD_PNG.png)

## Future Work

Future development of this application could include the following features:

- Improved search functionality to help users find bars and events they are interested in
- Integration with third-party APIs to provide more information about bars and events
- Chat functionality to allow users to communicate with each other directly
- Integration with a payment system to allow users to purchase tickets or make reservations for events.
