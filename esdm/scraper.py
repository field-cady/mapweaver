import requests, json
from bs4 import BeautifulSoup
from datetime import datetime

url = 'https://www.esdm.co/esdm-therapists'


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
phantom_path = r"C:\Users\Tacocat\OneDrive\Desktop\overabundant_lakes\addresses\church_data\phantomjs-2.1.1-windows\phantomjs-2.1.1-windows\bin\phantomjs"
phantom_driver = webdriver.PhantomJS(executable_path=phantom_path)
phantom_driver.get(url)
d = phantom_driver
e=d.find_elements_by_tag_name('iframe')[1]
d.switch_to_frame(e)



api_key = 'a30dc3d5926f1a2809bceb69f99aef71'

def get_lat_lon(q):
  geocode_url = ('http://api.positionstack.com/v1/forward?access_key='
    +api_key+'&output=json&query='+q)
  r = requests.get(geocode_url)
  d = r.json()['data']
  return d[0]['latitude'], d[0]['longitude']

import pandas as pd
df = pd.read_csv('copied_therapists.tsv', sep='\t', names=['first_name', 'last_name',
  'degree', 'email', 'city', 'state', 'country'])
df['location'] = df.city.fillna('') + ', ' + df.state.fillna('') + ', ' + df.country.fillna('')

bad_location = 'Sarcamento / Toronto, California / Ontario, United States / Canada'
replacements = [
  dict(city='Sacramento', state='California', country='United States',
    location='Sacramento, California, United States'),
  dict(city='Toronto', state='Ontario', country='Canada',
    location='Toronto, Ontario, Canada')
]

records = df.to_dict(orient='records')
records_w_bad_loc = [r for r in records if r['location'] == bad_location]
bad_rec = records_w_bad_loc[0]
replacement_records = [bad_rec.copy() for rep in replacements]
for rec, rep in zip(replacement_records, replacements):
  rec.update(rep)

records.extend(replacement_records)

location_latlon_map = {}
bad_locations = []
for l in set([r['location'] for r in records]):
  if l in location_latlon_map: continue
  try:
    latlon = get_lat_lon(l)
    location_latlon_map[l]=latlon
  except: bad_locations.append(l)

remaining_bad_locations = []
for l in bad_locations:
  if l in location_latlon_map: continue
  try:
    latlon = get_lat_lon(l)
    location_latlon_map[l]=latlon
  except: remaining_bad_locations.append(l)

corrections = {
'Brisbae, Queensland, Australia': (-27.469309, 153.026164),
'Leuven, , Belgium': (40.755884, -73.978504),
'Périguex, France, France': (45.186376, 0.723957),
'Kfar Saba, , Israel': (32.175, 34.90694),
', Maine, United States': (45.243327, -69.171071)
}
location_latlon_map.update(corrections)
open('location_latlon_map.json', 'w').write(json.dumps(location_latlon_map))

records_w_good_locations = [r for r in records if r['location'] in location_latlon_map]

records_by_location = {}
for r in records_w_good_locations:
  loc = r['location']
  records_by_location[loc] = records_by_location.setdefault(loc, []) + [r]

def records_to_html(recs):
  #recs=[v for v in records_by_location.values() if len(v)>1][1]
  loc = recs[0]['location']
  html_start = f'''<h3><b>{loc}</b><h3>
  <table border="1">
  <tr>
      <th>Name</th>
      <th>Degree</th>
      <th>Email</th>
    </tr>'''
  html_parts = [html_start]
  for r in recs:
    html_parts.append(f"""\n
    <tr>
      <th>{r['first_name']+' '+r['last_name']}</th>
      <th>{r['degree']}</th>
      <th>{r['email']}</th>
      </tr>
    """)
  html_out = ''.join(html_parts)
  return html_out
  #open('foo.html', 'w').write(html_out)

blobs = [
  dict(location=loc,
    lat=location_latlon_map[loc][0],
    lon=location_latlon_map[loc][1],
    n_therapists=len(records),
    html=records_to_html(records))
  for loc, records in records_by_location.items()
  ]
open('esdm_data.json', 'w').write(json.dumps({'marker_blobs':blobs}))




bad_location = 'Sarcamento / Toronto, California / Ontario, United States / Canada'
replacements = [
  dict(city='Sacramento', state='California', country='United States',
    location='Sacramento, California, United States'),
  dict(city='Toronto', state='Ontario', country='Canada',
    location='Toronto, Ontario, Canada')
]

records = df.to_dict(orient='records')
records_w_bad_loc = [r for r in records if r['location'] == bad_location]
bad_rec = records_w_bad_loc[0]
replacement_records = [bad_rec.copy() for rep in replacements]
for rec, rep in zip(replacement_records, replacements):
  rec.update(rep)

records.extend(replacement_records)










  records = []
  pg = 1
  while True:
    print('on page', pg)
    rows = driver.find_elements_by_class_name('rgRow')



def parse_table_from_page(txt):
    # Return list of table entries on the page
    soup = BeautifulSoup(txt)
    tabulka = soup.find("table", {"class" : "tablesaw-stack"})
    rows = []
    fields = ['name', 'acres', 'elevation', 'county', 'location']
    for row in tabulka.findAll('tr'):
        col = row.findAll('td')
        parts = [c for c in col]
        r = dict(zip(fields, parts))
        rows.append(r)
    return rows

def html_to_record(r):
    # Turn HTML object for table row into a dict
    name = next(r['name'].children).string
    url = 'https://wdfw.wa.gov' + r['name'].findNext('a').get('href')
    elevation = next(r['elevation'].children).string.split()[0]
    county = next(r['county'].children).string.strip()
    acres = next(r['acres'].children).string.strip().split()[0]
    latlon = [x.string for x in r['location'].findAll('span')]
    return dict(name=name, url=url, elevation=float(elevation), county=county, lat=float(latlon[0]), lon=float(latlon[1]), acres=acres)

starting_url_base = 'https://wdfw.wa.gov/fishing/locations/high-lakes/getting-started?name=&county=All&order=title&sort=asc&page='

overabundant_url_base = 'https://wdfw.wa.gov/fishing/locations/high-lakes/overabundant?name=&county=All&order=title&sort=asc&page='

all_url_base = 'https://wdfw.wa.gov/fishing/locations/high-lakes?name=&county=All&order=title&sort=asc&page='

def get_lakes_from_all_pages(url_base):
    # Scrape all pages
    i = 0
    all_records = []
    while True:
        url = url_base + str(i)
        r = requests.get(url)
        txt = r.text
        try: rows = parse_table_from_page(txt)
        except: break
        records = [html_to_record(rw) for rw in rows if rw]
        if len(records)==0: break
        all_records.extend(records)
        i += 1
    return all_records

def get_data():
    all_lakes = get_lakes_from_all_pages(all_url_base)
    all_lakes = [lk for lk in all_lakes if lk['elevation']>2500.0]
    overabundant_lakes = get_lakes_from_all_pages(overabundant_url_base)
    starting_lakes = get_lakes_from_all_pages(starting_url_base)
    overabundant_urls = set(lk['url'] for lk in overabundant_lakes)
    starting_urls = set(lk['url'] for lk in starting_lakes)
    for lk in all_lakes:
        lk['starting'] = lk['url'] in starting_urls
        lk['overabundant'] = lk['url'] in overabundant_urls
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return dict(
        lakes=all_lakes,
        overabundant_lakes=[lk for lk in all_lakes if lk['overabundant']],
        starting_lakes=[lk for lk in all_lakes if lk['starting']],
        normal_lakes=[lk for lk in all_lakes if not lk['overabundant'] and not lk['overabundant']],
        timestamp=timestamp
    )



def lake2marker_html(lk):
  link = '<a target=\"_blank\" href=\"'+lk['url']+'\">WDFW Page</a>'
  elevation = '<p>Elevation: '+str(round(lk['elevation']))+'ft' + '</p>'
  county = '<p>County: '+lk['county']+'</p>'
  size = '<p>Size: '+str(lk['acres'])+' Acres</p>'
  return elevation + county + size + link

def get_kml(lakes):
  kml = simplekml.Kml()
  kml.parsetext(parse=False)
  for lk in lakes:
    desc = lake2marker_html(lk)
    coords = [(lk['lon'],lk['lat'])]
    pnt = kml.newpoint(name=lk['name'].replace('&', ' and '), coords=coords, description=desc)
  return kml

'''

starting_kml = get_kml(starting_lakes)
starting_kml.save("starting_lakes.kml")

overabundant_kml = get_kml(overabundant_lakes)
overabundant_kml.save("overabundant_lakes.kml")

all_kml = get_kml(all_lakes)#[130:131])
all_kml.save("all_lakes.kml")







'''

if __name__ == '__main__':
    data = get_data()
	# Store JSON
    output = json.dumps(dict(lakes=data['lakes'], timestamp=data['timestamp']))#data)
    open('data.json', 'w').write(output)
    open('data/starting_lakes.json', 'w').write(json.dumps(
        dict(lakes=data['starting_lakes'], timestamp=data['timestamp'])
    ))
    open('data/overabundant_lakes.json', 'w').write(json.dumps(
        dict(lakes=data['overabundant_lakes'], timestamp=data['timestamp'])
    ))
    open('data/normal_lakes.json', 'w').write(json.dumps(
        dict(lakes=data['normal_lakes'], timestamp=data['timestamp'])
    ))
	# Store KML
	starting_kml = get_kml(data['starting_lakes'])
	starting_kml.save("data/starting_lakes.kml")
	overabundant_kml = get_kml(data['overabundant_lakes'])
	overabundant_kml.save("data/overabundant_lakes.kml")
	all_kml = get_kml(data['lakes'])
	all_kml.save("data/all_lakes.kml")

