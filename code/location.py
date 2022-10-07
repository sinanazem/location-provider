import geopandas
import pandas as pd
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from utils import make_db_connection_psycopg2, make_db_connection_engine
from geoalchemy2 import Geometry
from loguru import logger


DBNAME = "mydb"


class FeatureExtraction:

    def __init__(self, dbname, country_name):
        self.dbname = dbname
        self.country_name = country_name

        self.country_id = self.get_country_id(self.country_name)

    def get_country_id(self, country_name: str) -> int:
        country_name = str(country_name).lower()
        query = ''' SELECT id FROM location.country where LOWER(name_lat)='{}' '''.format(country_name)
        conn, cursor = make_db_connection_psycopg2(self.dbname, autocommit=False)
        cursor.execute(query)
        data = cursor.fetchone()

        return data[0]

    def get_location_type_id(self, location_type: str) -> int:
        query = ''' SELECT type,id FROM location.location_type where country_id={} '''.format(self.country_id)
        conn, cursor = make_db_connection_psycopg2(self.dbname, autocommit=False)
        cursor.execute(query)
        data = cursor.fetchall()

        return dict(data).get(location_type)

    def extract_multipolygon(self, geojson_path: str, location_type: str):
        # Read geojson file
        df = geopandas.read_file(geojson_path)
        logger.info(f'Reading data from "{geojson_path}"')

        # Add columns to GeoPandas dataframe
        df['country_id'] = self.country_id
        df['location_type_id'] = self.get_location_type_id(location_type=location_type)

        # Cleaning

        df['name_lat'] = df['name'].apply(lambda x: x.replace('-', '').replace(r"—", " ").strip().lower())
        df['surface_geom'] = df["geometry"].apply(lambda x: MultiPolygon([x]) if isinstance(x, Polygon) else x)
        df.rename({'local_name': 'name_local'}, axis=1, inplace=True)

        # Selected features
        selected_columns = ['country_id', 'location_type_id', 'name_lat',
                            'name_local', 'surface_geom', 'osm_id']
        df = df.loc[:, selected_columns]
        logger.info(f'Features are selected!')

        # Create final GeoPandas dataframe
        geo_df = geopandas.GeoDataFrame(df, crs='EPSG:4326', geometry='surface_geom')

        logger.info(f'{location_type} GeoDataFrame was created successfully!')
        logger.info(f'Shape of GeoDataFrame is: {geo_df.shape}')
        logger.info(f'Columns of GeoDataFrame: {geo_df.columns.to_list()}')

        return geo_df

    @staticmethod
    def test_name_lat(gdf):

        assert gdf['name_lat'].isna().sum() == 0, " 'name_lat' feature has missing value!"
        logger.info(' "name_lat" test passed!')

    @staticmethod
    def test_name_local(gdf):

        assert gdf['name_local'].isna().sum() == 0, " 'name_local' feature has missing value!"
        logger.info(' "name_local" test passed!')

    def test_country_id(self, gdf):

        for value in gdf['country_id']:

            assert value == self.country_id, " 'country_id' is wrong!"
        logger.info(' "country_id" test passed!')

    def test_location_type_id(self, gdf, location_type):
        for value in gdf['location_type_id']:
            assert value == self.get_location_type_id(location_type), " 'location_type_id' is wrong!"
        logger.info(f' "location_type_id" for {location_type} test passed!')

    @staticmethod
    def test_surface_geom(gdf):
        for value in gdf['surface_geom']:
            assert isinstance(value, MultiPolygon), 'Wrong! Polygon found!'
        logger.info(' "surface_geom" test passed!')

    def get_integrated_multipolygon(self, country_path=None, province_path=None,
                                    quarter_path=None, neighbourhood_path=None):
        country = self.extract_multipolygon(country_path, 'country')
        province = self.extract_multipolygon(province_path, 'province')
        division = None
        subdivision = None
        metropolitan = None
        quarter = self.extract_multipolygon(quarter_path, 'quarter')
        neighbourhood = self.extract_multipolygon(neighbourhood_path, 'neighbourhood')

        # integrated GeoDataFrames
        dataframes_list = [country, province, quarter, neighbourhood]
        integrated_gdf = geopandas.GeoDataFrame(pd.concat(dataframes_list, ignore_index=True),
                                                crs='EPSG:4326', geometry='surface_geom')
        # test GeoDataFrame
        self.test_name_lat(integrated_gdf)
        self.test_name_local(integrated_gdf)
        self.test_country_id(integrated_gdf)
        self.test_location_type_id(country, 'country')
        self.test_location_type_id(province, 'province')
        self.test_location_type_id(quarter, 'quarter')
        self.test_location_type_id(neighbourhood, 'neighbourhood')
        self.test_surface_geom(integrated_gdf)

        return integrated_gdf

    def create_temp_table(self):
        query = '''
                CREATE TABLE location.temp (
                id SERIAL,
                country_id int8 NOT NULL,
                location_type_id int8 NOT NULL,
                name_lat varchar(1000) NULL,
                name_local varchar(1000) NULL,
                surface_geom geometry(multipolygon,4326) NULL,
                point_geom geometry(multipoint,4326) NULL,
                local_id varchar(1000) NULL,
                osm_id varchar(256) NULL,
                additional_info json NULL);
                '''
        conn, cursor = make_db_connection_psycopg2(self.dbname, autocommit=False)
        cursor.execute(query)
        conn.commit()

    def insert_data(self, geopandas_dataframe, table_name, schema_name):
        # Following query will select and union all parts of a location and insert them into location table
        logger.info('Inserting to database...')
        engine = make_db_connection_engine(self.dbname)
        geopandas_dataframe.to_postgis(table_name, engine, schema=schema_name, if_exists="append",
                                       dtype={"surface_geom": Geometry("MULTIPOLYGON", srid=4326)})

        logger.info('Done!')

    def drop_temp_table(self):
        query = """ DROP TABLE IF EXISTS "location".temp; """

        conn, cursor = make_db_connection_psycopg2(self.dbname, autocommit=False)
        cursor.execute(query)
        conn.commit()


if __name__ == "__main__":
    canada = FeatureExtraction(DBNAME, 'canada')
    country_path = '../src/canada/country.geojson'
    province_path = '../src/canada/4.geojson'
    quarter_path = '../src/canada/9.geojson'
    neighbourhood_path = '../src/canada/10.geojson'

    integrated_gdf = canada.get_integrated_multipolygon(country_path=country_path,
                                                        province_path=province_path,
                                                        quarter_path=quarter_path,
                                                        neighbourhood_path=neighbourhood_path)
    canada.drop_temp_table()
    canada.create_temp_table()
    canada.insert_data(integrated_gdf, 'temp', 'location')
