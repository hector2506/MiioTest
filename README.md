# MiioTest
A repository for the Backend Test of Miio.

## API documentation
The documentation of the API is on the following link: https://documenter.getpostman.com/view/9423859/TzCL8oiE

## Tutorial
### Installing Docker
This project uses Docker, you'll need to install Docker to properly run the API, in case you don't have Docker installed, you can download it in this website: https://docs.docker.com/get-docker/

### .env
Before executing the API, you'll need to set the .env file. Firstly, rename the ".env.sample" file to ".env". Then, insert values into the variables of the .env file. The variables are detailed bellow:
1. DEBUG: True or False;
2. SECRET_KEY: A Django secret key, which you can generate in this website: https://djecrety.ir/
3. DATABASE_NAME: The name of your postgres database.
4. DATABASE_USER: The username of your postgres database.
5. DATABASE_PASSWORD: The password of your postgres database.
6. DATABASE_HOST: The host of your postgres database.
    1. This should have the same name as the postgres service in the docker-compose file, if you don't want to change the service's name just give this variable the value of "db".
8. MONGO_DB_PORT: The url of your mongodb client.
    1. This should follow this format: "mongodb://service_name:port/". With "service_name" being the name of the mongodb service in the docker-compose file (just use "mongodb" if you don't want to rename the service) and "port" being the port which you choose.
10. EMAIL_HOST_USER= The email which will be responsible for sending emails to a user which subscribes itself to a plan with publish=true.
11. EMAIL_HOST_PASSWORD= The password of the email which will be responsible for sending emails to a user which subscribes itself to a plan with publish=true.

### Execute the API
Before executing the api, you'll need to start the docker program, and then use the following commands on the root directory of this project:
```
docker-compose build
```
This command will download the images and build the services required to run the API. After that you'll just need to use this command:
```
docker-compose up
```
And then the API will work properly.

### Testing
You can run the automated tests using the following command:
```
docker-compose run web python manage.py test
```
You can also use the Coverage.py tool for measuring the code coverage of the API, simply use:
```
docker-compose run web coverage run manage.py test
```
Then, use the following command:
```
docker-compose run web coverage html
```
This will create a new "htmlcov" directory at the base directory of the project, in this new directory there is a "index.html" file, which you can execute to see the current percentage of code coverage of the project.
