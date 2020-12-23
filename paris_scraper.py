
import json, time
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


columns = [
'More Info',
'Facility Name',
'Permit Number',
'Permit Status',
'Permit Type',
'City',
'County',
'Violation Date',
'Is Addressed',
'Category',
'Type',
'Parameter',
'Units',
'Statistical Base',
'Measurement Value',
'Benchmark/Limit',
'Violation Notes',
'Violation Override',
'Feature Name']

columns_to_keep = columns[2:]+['ViolationId', 'FacilityId', 'Facility Name']

phantom_path = r"C:\Users\Tacocat\OneDrive\Desktop\overabundant_lakes\addresses\church_data\phantomjs-2.1.1-windows\phantomjs-2.1.1-windows\bin\phantomjs"
phantom_path = r"/home/taco/phantomjs-2.1.1-linux-x86_64/bin/phantomjs"

#search_url = 'https://apps.ecology.wa.gov/paris/ComplianceAndViolations/ViolationsAndPermitTriggers.aspx?PermitNumber=&FacilityName=&City=&County=Snohomish&PermitType=0&Region=0&ViolationCategory=0&StartDate=03/04/2020&EndDate=11/08/2020'
#search_url = 'https://apps.ecology.wa.gov/paris/ComplianceAndViolations/ViolationsAndPermitTriggers.aspx?PermitNumber=&FacilityName=&City=&County=&PermitType=0&Region=0&ViolationCategory=0&StartDate=09/04/2020&EndDate=11/08/2020'

search_url_root = 'https://apps.ecology.wa.gov/paris/ComplianceAndViolations/ViolationsAndPermitTriggers.aspx?'
#search_params_str = 'PermitNumber=&FacilityName=&City=&County=Snohomish&PermitType=0&Region=0&ViolationCategory=0&StartDate=08/04/2020&EndDate=11/08/2020'
#search_params_template = 'PermitNumber=${PermitNumber}s&FacilityName=&City=&County=Snohomish&PermitType=0&Region=0&ViolationCategory=0&StartDate=08/04/2020&EndDate=11/08/2020'
#search_url = search_url_root + search_params_str

search_params = dict(
  PermitNumber='',
  FacilityName='',
  City='',
  County='King',
  PermitType=0,
  Region=0,
  ViolationCategory=0,
  StartDate='08/04/2020',
  EndDate='11/08/2020'
)
def get_search_url(params):
  param_parts = [k+'='+str(v) for k, v in params.items()]
  params_str = '&'.join(param_parts)
  return search_url_root + params_str

def get_link(elem):
  # extra hyperlink url
  return elem.find_elements_by_tag_name('a')[0].get_attribute('href').split('=')[-1]

def get_records(url, driver):
  print('URL to crawl:\n', url, '\n')
  driver.get(url)
  records = []
  pg = 1
  while True:
    print('on page', pg)
    rows = driver.find_elements_by_class_name('rgRow')
    alt_rows = driver.find_elements_by_class_name('rgAltRow')
    broken_lines = [r.find_elements_by_tag_name('td') for r in rows + alt_rows]
    recs = [dict(zip(columns, bl)) for bl in broken_lines]
    for r in recs:
      for c in columns: 
        if c=='More Info':
          r['ViolationId'] = get_link(r[c])
        elif c=='Facility Name':
          r['FacilityId'] = get_link(r[c])
          r['Facility Name'] = r[c].text
        else: r[c] = r[c].text
    print('records found:', len(recs))
    if len(recs)==0: break
    if records and recs and \
      records[-1]['ViolationId']==recs[-1]['ViolationId']:
      # we already did the last page
      break
    recs_to_keep = [{k:v for k, v in r.items() if k in columns_to_keep}
      for r in recs]
    records.extend(recs_to_keep)
    try: next_page_button = driver.find_elements_by_class_name('rgPageNext')[0]
    except: break
    next_page_button.click()
    time.sleep(2.0)
    pg += 1
  print('found', len(records), 'violations')
  return records

region_map = dict(central=5, eastern=6, efsec=6,
  hanford=12, headquarters=7, industrial=11,
  northwest=8, southwest=9, unknown=10)
search_params = dict(
  PermitNumber='',
  FacilityName='',
  City='',
  County='',
  PermitType=0,
  Region=region_map['northwest'],
  ViolationCategory=0,
  StartDate='9/01/2020',
  EndDate='11/08/2020'
)
regions_to_cover = ['southwest', 'northwest', 'central', 'eastern']

import datetime
import dateutil.relativedelta
date_format = lambda dd: str(dd.month)+'/'+str(dd.day)+'/'+str(dd.year)
def get_date_ranges():
  ranges = []
  delt = dateutil.relativedelta.relativedelta(months=1)
  d = datetime.datetime.now().date() #datetime.date(2020, 11, 13)
  d_prev = d - 3*delt
  for i in range(2):
    print(i)
    ranges.append(dict(StartDate=date_format(d_prev), EndDate=date_format(d)))
    d = d_prev
    d_prev = d_prev - 3*delt
  return ranges

def get_facility_lat_lon(facid):
  url = 'https://apps.ecology.wa.gov/paris/FacilitySummary.aspx?FacilityId='+facid
  txt = requests.get(url).text
  lat, lon = txt.split('loc:')[1].split('"')[0].split('+')
  return float(lat), float(lon)


date_ranges = get_date_ranges()

records = []
for reg in regions_to_cover:
  for rng in date_ranges:
    print('\n\n**', reg, rng)
    phantom_driver = webdriver.PhantomJS(executable_path=phantom_path)
    search_params['Region'] = region_map[reg]
    search_params['StartDate'] = rng['StartDate']
    search_params['EndDate'] = rng['EndDate']
    url = get_search_url(search_params)
    recs = get_records(url, phantom_driver)
    print('got recs')
    records.extend(recs)



phantom_driver = webdriver.PhantomJS(executable_path=phantom_path)
url = get_search_url(search_params)
records = get_records(url, phantom_driver)

facility_ids = set([r['FacilityId'] for r in records])
facid_latlon_map = {facid: get_facility_lat_lon(facid) for facid in facility_ids}
for r in records:
  lat, lon = facid_latlon_map[r['FacilityId']]
  r['lat']=lat
  r['lon']=lon

df = pd.DataFrame(records)
df.to_csv('paris.csv')
import json
blob = dict(violations = records)
open('paris.json', 'w').write(json.dumps(blob)

#gunicorn using_dash:app.server -b :8000

records = json.load(open('paris_violations.json'))

for r in records:
  for k, v in r.items():
    if isinstance(v, float) and np.isnan(v): r[k]=None

open('paris_violations.json', 'w').write(json.dumps({'violations':records}))
open('paris_violations_2.json', 'w').write(json.dumps({'violations':records[:2]}))
open('paris_violations_3.json', 'w').write(json.dumps({'violations':records[:3]}))
open('paris_violations_4.json', 'w').write(json.dumps({'violations':records[:4]}))
open('paris_violations_5.json', 'w').write(json.dumps({'violations':records[:5]}))
open('paris_violations_6.json', 'w').write(json.dumps({'violations':records[:6]}))
open('paris_violations_7.json', 'w').write(json.dumps({'violations':records[:7]}))
open('paris_violations_8.json', 'w').write(json.dumps({'violations':records[:8]}))
open('paris_violations_9.json', 'w').write(json.dumps({'violations':records[:9]}))
open('paris_violations_10.json', 'w').write(json.dumps({'violations':records[:10]}))
open('paris_violations_20.json', 'w').write(json.dumps({'violations':records[:20]}))
open('paris_violations_50.json', 'w').write(json.dumps({'violations':records[:50]}))
open('paris_violations_100.json', 'w').write(json.dumps({'violations':records[:100]}))




len(set([r['ViolationId'] for r in records]))


len(set([r['FacilityId'] for r in records]0mmb=mo