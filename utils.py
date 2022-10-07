import psycopg2
from sqlalchemy import create_engine
import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
import os
import yaml

ROOT_DIR = str(str(os.path.realpath(__file__).replace('\\', '/')).split('location-provider/')[0]) + 'location-provider/'
conf_dir = ROOT_DIR + 'config/db_configs.yaml'
conn_dict = yaml.load(open(conf_dir), Loader=yaml.SafeLoader)


def make_db_connection_psycopg2(database: str, autocommit: bool = False):

    assert database in list(conn_dict.keys()), "server couldn't be recognized in the config file"

    host = conn_dict[database]['host']
    user = conn_dict[database]['user']
    password = conn_dict[database]['password']
    dbname = conn_dict[database]['dbname']

    conn = psycopg2.connect(user=user, password=password, host=host, dbname=dbname)
    cursor = conn.cursor()

    if autocommit:
        conn.autocommit = True

    return conn, cursor


def make_db_connection_alchemy(database: str, autocommit: bool = False):
    assert database in list(conn_dict.keys()), "provided server couldn't be recognized in the config file"

    host = conn_dict[database]['host']
    user = conn_dict[database]['user']
    password = conn_dict[database]['password']
    dbname = conn_dict[database]['dbname']

    engine = create_engine('postgresql+psycopg2://' + user + ':' + password + '@' + host + ':5432/' + dbname)

    metadata2 = sq.MetaData(engine)
    Base = declarative_base(metadata=metadata2)

    session_maker = sq.orm.sessionmaker(bind=engine, autocommit=autocommit)
    session = session_maker()

    return session, Base


def make_db_connection_engine(database: str):
    assert database in list(conn_dict.keys()), "provided server couldn't be recognized in the config file"

    host = conn_dict[database]['host']
    user = conn_dict[database]['user']
    password = conn_dict[database]['password']
    dbname = conn_dict[database]['dbname']

    engine = create_engine('postgresql+psycopg2://' + user + ':' + password + '@' + host + ':5432/' + dbname)

    return engine
