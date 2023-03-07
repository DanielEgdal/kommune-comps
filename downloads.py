import requests
import os
import json
import zipfile
import io

script_dir = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(script_dir, 'kommuner.geojson')
comps = os.path.join(script_dir, 'WCA_export_Competitions.tsv')
res = os.path.join(script_dir, 'WCA_export_Results.tsv')

def download_file():
    if os.path.exists(filename):
        return True
    else:
        s = requests.get("https://github.com/Neogeografen/dagi/raw/master/geojson/kommuner.geojson")
        assert s.status_code == 200
        with open(filename,'w') as f:
            json.dump(json.loads(s.content),f)
        return True

def download_wca(): # This should really have some check so it doesn't start more than once in caes of a refresh happening.
    if os.path.exists(comps):
        return True
    else:
        print('starting big download')
        a = requests.get("https://www.worldcubeassociation.org/results/misc/WCA_export.tsv.zip")
        assert a.status_code == 200
        # with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        with zipfile.ZipFile(io.BytesIO(a.content), 'r') as zip_ref: 
            zip_ref.extract("WCA_export_Competitions.tsv",path=script_dir)
            zip_ref.extract("WCA_export_Results.tsv",path=script_dir)
        print('done big download')
        return True

# download_file()