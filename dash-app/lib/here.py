import os
import requests
import re
import random
import folium

from config import use_sample_data
from data.sample import sample_geocode, sample_places, sample_route_summaries
from lib.Place import Place

HERE_APIKEY = os.environ.get('HERE_API_KEY')

geocode_endpoint = 'https://geocode.search.hereapi.com/v1/geocode?q={address}&apiKey={api_key}'
coordinates_regex = '^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$'

places_categories = [
  { 'value': '200-2200',      'label': 'Theatre, Music and Culture' },
  { 'value': '300-3200',      'label': 'Religious Place' },
  { 'value': '400-4000',      'label': 'Airport' },
  { 'value': '500-5000',      'label': 'Hotel-Motel' },
  { 'value': '500-5100-0000', 'label': 'Lodging' },
  { 'value': '500-5100-0055', 'label': 'Hostel' },
  { 'value': '500-5100-0056', 'label': 'Campground' },
  { 'value': '500-5100-0059', 'label': 'Holiday Park' },
  { 'value': '550-5510',      'label': 'Outdoor-Recreation' },
  { 'value': '600-6400',      'label': 'Drugstore or Pharmacy' }
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
  if use_sample_data:
    return sample_geocode
  else:
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

  browse_url = 'https://browse.search.hereapi.com/v1/browse?limit=%s&categories=%s&at=%s&apiKey=%s' % (
    limit,
    categories,
    coordinates,
    HERE_APIKEY
  )

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
      icon = folium.Icon(color=m['color']) if 'color' in m else None
      y = m['y'] if 'y' in m else m['lat']
      x = m['x'] if 'x' in m else m['lng']

      feature_group.add_child(
          folium.Marker([y, x], icon=icon, popup=m['title'] if 'title' in m else None)
      )
      map.add_child(feature_group)

    if fit_bounds:
      bounds = feature_group.get_bounds()
      map.fit_bounds(bounds, max_zoom=15)

  return map


def get_here_map (location, markers=[]):
  geocode = get_geocode(location)
  if use_sample_data:
    map = folium.Map(location=geocode, zoom_start=13.5)
  else:
    map = folium.Map(location=geocode,
                    zoom_start=13.5,
                    tiles=get_map_tile_url(),
                    attr='HERE Map')

  add_markers(map, markers)

  return map


def get_places_nearby (location, categories=[], max_distance_km=15, results_limit=100):
  if use_sample_data:
    places_list = sample_places
  else:
    browse_url = get_browse_url(location, categories, limit=results_limit)

    response = requests.get(browse_url)

    if response.ok:
      json_response = response.json()
      places_list = json_response['items']
    else:
      print(response.text)
  
  filtered_places = []

  for p in places_list:
    if p['distance'] <= max_distance_km * 1000:
      filtered_places.append(Place(p))

  return filtered_places


def get_waypoint (position):
  location = is_geocode(position)

  if not location and 'lat' in position and 'lng' in position:
    location = [position['lat'], position['lng']]

  return '{},{}'.format(location[0], location[1])


def get_route_summaries (places):
  if use_sample_data:
    route_summaries = sample_route_summaries
  else:
    # Request should not contain more than 15 starts
    nb_starts = 10

    waypoints = [p.geocode for p in places]

    dest_waypoints = {}
    for i, w in enumerate(waypoints):
      dest_waypoints['destination{}'.format(i)] = w
    
    start_coords = [waypoints[i:i+nb_starts] for i in range(0, len(waypoints), nb_starts)]

    route_summaries = []
    matrix_routing_url = get_matrix_routing_url()

    for sc in start_coords:
      start_waypoints = {}
      for i, s in enumerate(sc):
        start_waypoints['start{}'.format(i)] = s
      
      coords = {**start_waypoints, **dest_waypoints}
      response = requests.post(matrix_routing_url, data = coords)

      if not response.ok:
        print(response.text)
      else:
        json_response = response.json()

        for entry in json_response['response']['matrixEntry']:
          geopoints = start_waypoints['start{}'.format(entry['startIndex'])] + '_' + dest_waypoints['destination{}'.format(entry['destinationIndex'])]
          route_summaries.append({
            'geopoints': geopoints,
            'distance': entry['summary']['distance'],
            'route_id': entry['summary']['routeId']
          })

  return route_summaries


