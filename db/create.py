import os
import sys

PROJECT_PATH = str(
    str(os.path.realpath(__file__).replace('\\', '/')).split('location-provider/')[0]) + 'location-provider/'
if PROJECT_PATH not in sys.path:
    sys.path.append(PROJECT_PATH)

from utils import make_db_connection_psycopg2
DBNAME = "mydb"


def postgis_extension(dbname: str = DBNAME):
    query = "create extension if not exists postgis"
    conn, cursor = make_db_connection_psycopg2(dbname, autocommit=False)
    cursor.execute(query)
    conn.commit()


def schema(dbname: str = DBNAME):
    query = "create schema if not exists location"
    conn, cursor = make_db_connection_psycopg2(dbname, autocommit=False)
    cursor.execute(query)
    conn.commit()


def drop_tables(dbname: str = DBNAME):
    query = "drop table if exists location.location_hierarchy; " \
            "drop table if exists location.location; " \
            "drop table if exists location.location_type; " \
            "drop table if exists location.country;"
    conn, cursor = make_db_connection_psycopg2(dbname, autocommit=False)
    cursor.execute(query)
    conn.commit()


def country_table(dbname: str = DBNAME):
    query = "CREATE TABLE location.country (" \
            "id bigserial NOT NULL, " \
            "name_lat varchar(1000) NULL, " \
            "name_local varchar(1000) NULL, " \
            "search_box_types varchar(1000) NULL, " \
            "search_type_hierarchy varchar(1000) NULL, " \
            "srid int4 NULL, " \
            "CONSTRAINT country_pk PRIMARY KEY (id));"
    conn, cursor = make_db_connection_psycopg2(dbname, autocommit=False)
    cursor.execute(query)
    conn.commit()


def location_type_table(dbname: str = DBNAME):
    query = "CREATE TABLE location.location_type (" \
            "id bigserial NOT NULL, " \
            "type varchar(256) NULL, " \
            "country_id int8 NOT NULL, " \
            "listing_searchable bool NULL, " \
            "admin_level int4 NULL, " \
            "market_level int4 NULL, " \
            "CONSTRAINT location_type_pk PRIMARY KEY (id));" \
            "ALTER TABLE location.location_type ADD CONSTRAINT location_type_fk FOREIGN KEY (country_id) REFERENCES " \
            "location.country(id) ON DELETE CASCADE ON UPDATE CASCADE;"
    conn, cursor = make_db_connection_psycopg2(dbname, autocommit=False)
    cursor.execute(query)
    conn.commit()


def location_table(dbname: str = DBNAME):
    query = "CREATE TABLE location.location (" \
            "id int8 NOT NULL, " \
            "country_id int8 NOT NULL, " \
            "location_type_id int8 NOT NULL, " \
            "name_lat varchar(1000) NULL, " \
            "name_local varchar(1000) NULL, " \
            "surface_geom geometry(multipolygon) NULL, " \
            "point_geom geometry(multipoint) NULL, " \
            "local_id varchar(1000) NULL, " \
            "osm_id varchar(256) NULL, " \
            "additional_info json NULL, " \
            "CONSTRAINT location_pk PRIMARY KEY (id));" \
            "drop sequence if exists location.id_seq_location cascade;" \
            "CREATE SEQUENCE location.id_seq_location;" \
            "ALTER TABLE location.location ALTER id SET DEFAULT NEXTVAL('location.id_seq_location');" \
            "CREATE INDEX location_country_id_idx ON location.location USING btree (country_id);" \
            "CREATE INDEX location_location_type_id_idx ON location.location USING btree (location_type_id);" \
            "ALTER TABLE location.location ADD CONSTRAINT location_fk FOREIGN KEY (location_type_id) " \
            "REFERENCES location.location_type(id) ON DELETE CASCADE ON UPDATE CASCADE;" \
            "ALTER TABLE location.location ADD CONSTRAINT location_fk2 FOREIGN KEY (country_id) " \
            "REFERENCES location.country(id) ON DELETE CASCADE ON UPDATE CASCADE;"
    conn, cursor = make_db_connection_psycopg2(dbname, autocommit=False)
    cursor.execute(query)
    conn.commit()


def location_hierarchy_table(dbname: str = DBNAME):
    query = "CREATE TABLE location.location_hierarchy (" \
            "target_location_id int8 NOT NULL, parent_location_id int8 NULL);" \
            "ALTER TABLE location.location_hierarchy ADD CONSTRAINT location_hierarchy_fk FOREIGN KEY " \
            "(target_location_id) REFERENCES location.location(id); " \
            "ALTER TABLE location.location_hierarchy ADD CONSTRAINT location_hierarchy_fk2 FOREIGN KEY " \
            "(parent_location_id) REFERENCES location.location(id);"
    conn, cursor = make_db_connection_psycopg2(dbname, autocommit=False)
    cursor.execute(query)
    conn.commit()


def insert_static_data(dbname: str = DBNAME):
    conn, cursor = make_db_connection_psycopg2(dbname, autocommit=True)
    cursor.execute(open(PROJECT_PATH + "db/country.sql", "r", encoding="utf-8").read())
    cursor.execute(open(PROJECT_PATH + "db/location_type.sql", "r", encoding="utf-8").read())
    cursor.execute(open(PROJECT_PATH + "db/location.sql", "r", encoding="utf-8").read())
    cursor.execute(open(PROJECT_PATH + "db/location_hierarchy.sql", "r", encoding="utf-8").read())


if __name__ == '__main__':
    postgis_extension()
    print("Postgis extension created")
    schema()
    print("Location schema created")
    drop_tables()
    country_table()
    location_type_table()
    location_table()
    location_hierarchy_table()
    print("All tables created")

    insert_static_data()
    print("Static data inserted")

