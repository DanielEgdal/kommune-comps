import polars as pl
import geopandas as gpd
from shapely import Point
import folium
from geopy.distance import distance
import os
from downloads import download_file,download_wca

def get_dk_comps():
    download_wca()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    comp_path = os.path.join(script_dir, 'WCA_export_Competitions.tsv')
    res_path = os.path.join(script_dir, 'WCA_export_Results.tsv')

    dk = (pl.read_csv(comp_path,sep='\t')).lazy().filter(pl.col('countryId')=='Denmark')
    res = pl.read_csv(res_path,sep='\t').lazy()

    dk_res = dk.join(res,left_on='id',right_on='competitionId').select(["id","personId","latitude","longitude"])
    shortRs = dk_res.groupby(['id','personId']).first().collect()

    df = shortRs.to_pandas()
    df['geometry'] = df.apply(lambda x: Point(x['longitude']/10e5,x['latitude']/10e5),axis=1)
    geopandas_df = gpd.GeoDataFrame(df, crs='EPSG:4326')
    # print(geopandas_df.memory_usage(index=True).sum())
    # print(geopandas_df.columns)
 
    return geopandas_df

def get_kommuner():
    download_file()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    kommuner_path = os.path.join(script_dir, 'kommuner.geojson')
    kommuner = gpd.read_file(kommuner_path)
    kommuner.crs ='EPSG:4326'
    kommuner = kommuner.dissolve(by='KOMNAVN').reset_index()

    return kommuner

def make_map(municipalties:gpd.GeoDataFrame,comps:gpd.GeoDataFrame):
    m = folium.Map(location=[56, 12], zoom_start=7)
    style_function = lambda feature: {'fillOpacity': 0.5,}
    for index, row in municipalties.iterrows():
        geojson = folium.GeoJson(data=row.geometry.__geo_interface__,
                                 style_function=style_function,
                                 tooltip=f"{row.KOMNAVN} Kommune")
        geojson.add_to(m)
    for index, row in comps.iterrows():
        lon, lat = row.geometry.centroid.coords[0]
        folium.Circle(location=[lat, lon],
                  radius=distance(kilometers=0.2).meters,
                  color='darkred',
                  fill_color='darkred',
                  opacity=1,
                  fill_opacity=0.8,
                  tooltip = f"{row.id}").add_to(m)
    return m

def get_person_kommuner(personid:str,all_comps:gpd.GeoDataFrame,kommuner:gpd.GeoDataFrame):
    person_comps = all_comps.loc[all_comps['personId']==personid]
    person_municipalities = gpd.sjoin(kommuner, person_comps, predicate='contains')
    person_municipalities = person_municipalities[['id','KOMNAVN','geometry']]
    person_municipalities.drop_duplicates(subset=['KOMNAVN'],inplace=True)
    m = make_map(person_municipalities,person_comps)
    return m

def get_dk_kommuner(all_comps:gpd.GeoDataFrame,kommuner:gpd.GeoDataFrame):
    uniqueComps = all_comps.drop_duplicates(subset=['id'])
    municipalities = gpd.sjoin(kommuner, uniqueComps, predicate='contains')
    municipalities = municipalities[['id','KOMNAVN','geometry']]
    municipalities.drop_duplicates(subset=['KOMNAVN'],inplace=True)
    m = make_map(municipalities,uniqueComps)
    return m

def show_dk_no_comps(kommuner:gpd.GeoDataFrame):
    return kommuner.drop_duplicates(subset=['geometry']).explore()


# print(get_dk_comps())