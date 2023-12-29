-----------------------------------
Getting everything up and running
-----------------------------------

0. Ensure you have Docker Compose v2.20.2+ installed, if you have Docker
   Desktop 4.22+ you're good to go. You can check with: docker compose version

1. Copy .env.example to .env

2. Add your email and Stripe credentials to your .env file.
  (use your instance/settings.py file from section 20's code as a reference)

3. Open a terminal configured to run Docker and then run:

docker compose down -v
docker compose build --no-cache
docker compose up
./run flask db reset --with-testdb
./run flask add all
./run quality
./run test


-----------------------------------
Troubleshooting
-----------------------------------

Q: You get a permission error when upping the project

A: Some unzipping tools remove executable file permission bits from files, so you
might need to run the command below to update a few shell script permissions:

chmod +x run bin/*

You'll want to run that if you get an error when upping everything that's
related to permissions or you notice those files are not executable. This will
depend on your terminal but usually executable files will be green in color.

Q: After upping, you get 'no service selected' or docker compose build is empty

A: Make sure you to copy the COMPOSE_PROFILES lines from the .env.example file
to your real .env file.


-----------------------------------
Reference Links
-----------------------------------

- TODO

-----------------------------------
Video Timestamps
-----------------------------------

- TODO
