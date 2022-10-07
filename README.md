# Kilid Global Location Provider

This project has been designed to use as a starting point for developers and data scientists we'll collaborate to 
expand location data to several countries all around the world.

## Description

Here we are going to set up our environment using a PostgreSQL db and some Python codes, to crawl some location 
data from 3rd party applications, transform them to appropriate schemas, and finally put them on the right database 
tables and check if all things went well.

Since we are currently working with different developers each of which with different attitudes and coding styles, 
it's definitely important to follow some simple standards and structures, so all the codes and materials need to be 
reusable and readable by others. Therefore, we designed database tables and schemas, based on what would best satisfy 
production needs and asked you to follow the steps bellow to create these schemas and tables, and put your codes on the
appropriate files and functions.

## Getting Started

### Dependencies

Before you go further, make sure you have these dependencies installed and ready:
* One python IDE. We highly recommend you use the Pycharm as your main IDE for python, the community edition is 
available here [Pycharm Community](https://www.jetbrains.com/pycharm/download/#section=linux) for Windows, macOS, 
and Linux.
* One database IDE supporting PostgreSQL. We also highly recommend you use 
[DBeaver Community](https://dbeaver.io/download/) which is also available for Windows, macOS, and Linux.
* One PosrgreSQL node with PostGIS extension installed.
  * You can use these tutorials for installing Posrgres 
on [Windows](https://www.postgresqltutorial.com/postgresql-getting-started/install-postgresql/), 
[macOS](https://www.postgresqltutorial.com/postgresql-getting-started/install-postgresql-macos/), 
or [Linux](https://www.cherryservers.com/blog/how-to-install-and-setup-postgresql-server-on-ubuntu-20-04).
  * You can use this tutorial to install PostGIS on 
  [macOS and Windows](https://postgis.net/workshops/postgis-intro/installation.html)
  or this tutorial for [Ubuntu/Linux](https://www.vultr.com/docs/install-the-postgis-extension-for-postgresql-on-ubuntu-linux/).

### Installing

Open a command line, head to the repository directory, create a Python virtual environment, and use the command bellow 
to install the project requirements and make sure to add all the packages and libraries you used to the 
requirements file, so we can regenerate and run the codes.

```commandline
pip install -r requirements.txt
```

### Branching

We would have one branch for each country we are going to expand location data to, and we won't merge these branches 
into the `master` branch. So make sure you are on the correct branch.


### Database creation

Go through the steps bellow to create a postgresql database on you local machine and create appropriate schemas and 
tables required for this project.
1. Create a postgres database on you local pc/laptop/machine/whatever you are using, and name it anything you like, say `mydb`
2. From the previous 
[Dependencies](https://gitlab.com/kilid-com/data-factory/location-provider/-/blob/master/README.md#L20) part, 
you probably made a user/password for your postgres database, otherwise make one.
3. Put these credentials on the `config/db_configs.yaml` file. **CAUTION** you **MUST** never commit your credentials 
on this file.
4. Run the `db/create.py` file in using the command bellow or using your IDE interface to create the sample tables 
in your local DB. After running the code, you must have 4 tables named: `country`, `location`, `location_hierarchy` 
and `location_type`.
5. Connect to you local db using the database IDE (Dbeaver) to see the tables and data.

## Workflow
* Use the `src` directory if you want to add any additional file required for your codes and pipeline
* Use the `code` directory to put your codes on. The `location.py` file designed for the location data gathering codes 
and pipelines (as you know from the on-boarding sessions). And the `location_hierarchy.py` file has been designed for 
the location hierarchy codes. You can also add mode python files if it's needed.
* Upon finishing the tasks and pipelines, give us only a command to run your codes and insert the data as it's required.
* The codes **MUST** be reproducible. It's very important, every time we run it, it can be able to insert the data, 
or update previous one and make them correct if they are erroneous. So please test your pipelines a couple of times.


## License

This project is licensed under the MIT License - see the LICENSE.md file for details
