import os
import requests
import re
import random
import folium

from lib.Place import Place

HERE_APIKEY = os.environ.get('HERE_API_KEY')

geocode_endpoint = 'https://geocode.search.hereapi.com/v1/geocode?q={address}&apiKey={api_key}'
coordinates_regex = '^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$'

# https://www.developer.here.com/documentation/geocoding-search-api/dev_guide/topics-places/places-category-system-full.html
hospital_categories = [
  # { 'value': '800-8000-0000', 'label': 'Hospital or Health Care Facility' },
  # { 'value': '800-8000-0158', 'label': 'Medical Services-Clinics' },
  { 'value': '800-8000-0159', 'label': 'Hospital' }
]
places_categories = [
  { 'value': '400-4000',      'label': 'Airport' },
  { 'value': '500-5000',      'label': 'Hotel-Motel' },
  { 'value': '500-5100-0000', 'label': 'Lodging' },
  { 'value': '500-5100-0056', 'label': 'Campground' },
  { 'value': '500-5100-0059', 'label': 'Holiday Park' },
  { 'value': '550-5510',      'label': 'Outdoor-Recreation' },
  { 'value': '600-6400',      'label': 'Drugstore or Pharmacy' },
  { 'value': '800-8100-0165', 'label': 'Military Base' },
  { 'value': '800-8200',      'label': 'Education Facility' },
  { 'value': '800-8400',      'label': 'Event Spaces' },
  { 'value': '800-8500-0178', 'label': 'Parking Lot' }
]


def is_geocode (location):
  geocode = None
  if isinstance(location, str):
    l = location.split(',')
    if len(l) == 2:
        geocode = '{},{}'.format(l[0].strip(), l[1].strip())
  elif isinstance(location, list) and len(location) == 2:
    geocode = ','.join(str(l) for l in location)
      
  if geocode is not None and re.match(coordinates_regex, geocode):
    return [float(l) for l in geocode.split(',')]
  else:
    return False
    

def get_geocode (address):
  g = is_geocode(address)

  if not g:
    url = geocode_endpoint.format(address=address, api_key=HERE_APIKEY)
    response = requests.get(url)

    if response.ok:
      jsonResponse = response.json()
      position = jsonResponse['items'][0]['position']
      g = [position['lat'], position['lng']]
    else:
      print(response.text)
          
  return g 


def get_browse_url (location, categories, limit=100):
  categories = ','.join(c for c in categories)
  geocode = get_geocode(location)
  coordinates = ','.join(str(g) for g in geocode)
  # circle = coordinates + ';r=' + str(radius)

  browse_url = 'https://browse.search.hereapi.com/v1/browse?categories=%s&at=%s&apiKey=%s' % (
    categories,
    coordinates,
    HERE_APIKEY
  )

  if limit > 0:
    browse_url = '{}&limit={}'.format(browse_url, limit)
  
  return browse_url


def get_map_tile_url ():
  load_balance = random.randint(1, 4)  # between 1-4
  map_type = 'base'         # aerial, base, traffic
  tile_type = 'streettile'  # basetile, maptile, streettile, etc.
  map_version = 'newest'
  scheme = 'normal.day'
  zoom = 13
  column = 4400             # any number between 0 and (2**zoom - 1)
  row = 2686                # any number between 0 and(2**zoom - 1)
  size = 256                # image size (256 or 512)
  img_format = 'png8'

  # HERE MAP Tile API:
  # GET: https://{1-4}.{map_type}.maps.ls.hereapi.com/maptile/2.1/{tile_type}/{map_version}/{scheme}/{zoom}/{column}/{row}/{size}/{img_format}?apiKey={HERE_API_KEY}
  tiles_url = 'https://%s.%s.maps.ls.hereapi.com/maptile/2.1/%s/%s/%s/{z}/{x}/{y}/%s/%s?apiKey=%s' % (
      load_balance,
      map_type,
      tile_type,
      map_version,
      scheme,
      size,
      img_format,
      HERE_APIKEY
  )

  return tiles_url


def get_matrix_routing_url ():
  route_mode = 'shortest;car;traffic:disabled;'
  summary_attributes = 'routeId,distance'

  # HERE Matrix Routing API
  matrix_routing_url = 'https://matrix.route.ls.hereapi.com/routing/7.2/calculatematrix.json?mode=%s&summaryAttributes=%s&apiKey=%s' % (
    route_mode,
    summary_attributes,
    HERE_APIKEY
  )

  return matrix_routing_url


def add_markers (map, markers, fit_bounds=False):
  feature_group = folium.FeatureGroup('places')

  if len(markers) > 0:
    for m in markers:
      if 'color' in m and m['color'] is not None:
        icon = folium.Icon(color=m['color'], icon=m['icon'] if 'icon' in m else None)
      else:
        icon = None

      y = m['y'] if 'y' in m else m['lat']
      x = m['x'] if 'x' in m else m['lng']
      p = m['marker'] if 'marker' in m else m['title']

      feature_group.add_child(
          folium.Marker([y, x], icon=icon, popup=p)
      )
      map.add_child(feature_group)

    if fit_bounds:
      bounds = feature_group.get_bounds()
      map.fit_bounds(bounds, max_zoom=15)

  return map


def get_here_map (location, markers=[]):
  geocode = get_geocode(location)
  map = folium.Map(location=geocode,
                  zoom_start=13.5,
                  tiles=get_map_tile_url(),
                  attr='HERE Map')
  add_markers(map, markers)

  return map


def browse_places (location, categories=[], results_limit=100):
  places_list = []
  
  browse_url = get_browse_url(location, categories, limit=results_limit)
  response = requests.get(browse_url)

  if response.ok:
    json_response = response.json()
    places_list = json_response['items']
  else:
    print(response.text)

  return places_list


def get_places_nearby (location, categories=[], results_limit=100, max_distance_km=50):
  places_list = browse_places(location, categories=categories, results_limit=results_limit)
  
  filtered_places = []

  for p in places_list:
    if p['distance'] <= max_distance_km * 1000:
      filtered_places.append(Place(p))

  return filtered_places


def get_hospitals_nearby (location, results_limit=100, max_distance_km=50):
  h_cat = [h['value'] for h in hospital_categories]
  hospitals_list = browse_places(location, categories=h_cat, results_limit=results_limit)
  
  filtered_hospitals = []

  for h in hospitals_list:
    if h['distance'] <= max_distance_km * 1000:
      filtered_hospitals.append(Place(h, is_medical=True))

  return filtered_hospitals


def get_waypoint (position):
  location = is_geocode(position)

  if not location and 'lat' in position and 'lng' in position:
    location = [position['lat'], position['lng']]

  return '{},{}'.format(location[0], location[1])


def get_route_summaries (current_geocode, places, hospitals):
  # Request should not contain more than 15 start positions
  num_starts = 15

  postal_codes_set = set()
  postal_codes_geocodes = []
  places_waypoints = {}

  for i, p in enumerate(places):
    if p.postal_code:
      postal_codes_set.add('{}:{}'.format(p.postal_code, p.country))
    places_waypoints['destination{}'.format(i)] = p.geocode

  for p in postal_codes_set:
    geocode = get_geocode(p)
    postal_codes_geocodes.append({
      'postal_code': p.split(':')[0],
      'geocode': ','.join(str(g) for g in geocode)
    })

  current = {
    'geocode': ','.join(str(g) for g in current_geocode)
  }

  start_geocodes = [current] + postal_codes_geocodes + [h.to_dict() for h in hospitals]
  start_coords = [
    start_geocodes[i:i+num_starts] 
    for i in range(0, len(start_geocodes), num_starts)
  ]

  route_summaries = []
  matrix_routing_url = get_matrix_routing_url()

  for sc in start_coords:
    start_waypoints = {}
    for i, s in enumerate(sc):
      start_waypoints['start{}'.format(i)] = s['geocode']
    
    coords = {**start_waypoints, **places_waypoints}
    response = requests.post(matrix_routing_url, data = coords)

    if not response.ok:
      print(response.text)
    else:
      json_response = response.json()
      for entry in json_response['response']['matrixEntry']:
        start_geocode = start_waypoints['start{}'.format(entry['startIndex'])]
        dest_geocode = places_waypoints[
          'destination{}'.format(entry['destinationIndex'])
        ]

        for s in sc:
          if 'address' not in s and 'postal_code' in s and s['geocode'] == start_geocode:
            route_summaries.append({
              'start': s['postal_code'],
              'destination': dest_geocode,
              'distance': entry['summary']['distance'],
              'route_id': entry['summary']['routeId']
            })
            break
        
        route_summaries.append({
          'start': start_geocode,
          'destination': dest_geocode,
          'distance': entry['summary']['distance'],
          'route_id': entry['summary']['routeId']
        })

  return route_summaries
