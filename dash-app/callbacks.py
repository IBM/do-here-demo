import dash

from dash.dependencies import Input, Output, State
from app import app
import re

from lib.here import get_geocode, get_here_map, get_places_nearby, get_hospitals_nearby, add_markers, get_route_summaries
from lib.do import find_possible_sites

def get_deployment_uid(query_param):
  deployment_uid = None

  if query_param and 'deployment' in query_param:
    m = re.match(r'deployment=[^&]*', query_param[1:], re.I)
    deployment_uid = m.group()[len('deployment='):]

  return deployment_uid


def reset_map(address):
  geocode = get_geocode(address)
  here_map = None

  if geocode:
    here_map = get_here_map(geocode)

  return here_map, geocode


def find_places(geocode, categories, max_distance, max_results):
  places = []
  hospitals = []

  if len(categories) > 0:
    places = get_places_nearby(
      geocode,
      categories=categories, 
      max_distance_km=max_distance,
      results_limit=max_results
    )

  if len(places) > 0:
    max_places_dist = max([p.distance for p in places]) / 1000
    hospitals = get_hospitals_nearby(
      geocode,
      max_distance_km=max_places_dist + 2
    )

  return places, hospitals


def show_places(here_map, places, current_geocode=None, address=None):
  markers = [p.marker() for p in places]
  if current_geocode is not None:
    markers.append({
      'lat': current_geocode[0],
      'lng': current_geocode[1],
      'marker': address or 'current location',
      'color': 'green'
    })
  add_markers(here_map, markers, fit_bounds=True)


def handle_optimize(current_geocode, places, hospitals, deployment_uid):
  route_summaries = get_route_summaries(current_geocode, places, hospitals)
  possible_sites, status = find_possible_sites(
    places + hospitals, 
    route_summaries, 
    number_sites=3, 
    deployment_uid=deployment_uid
  )
  return possible_sites, status


@app.callback(
  [
    Output('hereMap', 'srcDoc'),
    Output('currentGeocode', 'value'),
    Output('solutionStatus', 'children')
  ],
  [
    Input('optimizeButton', 'n_clicks'),
    Input('searchButton', 'n_clicks')
  ],
  [
    State('addressInput', 'value'),
    State('maxDistance', 'value'),
    State('maxResults', 'value'),
    State('selectCategories', 'value'),
    State('currentGeocode', 'value'),
    State('url', 'search')
  ]
)
def map_update(optimize_btn, search_btn, address, max_distance, max_results, categories, geocode, query_param):
  ctx = dash.callback_context

  if not ctx.triggered:
    button_id = None
  else:
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

  deployment_uid = get_deployment_uid(query_param)
  here_map, current_geocode = reset_map(address)
  places, hospitals = find_places(
    current_geocode, categories, float(max_distance), int(max_results)
  )

  if button_id == 'optimizeButton':
    possible_sites, status = handle_optimize(
      current_geocode, places, hospitals, deployment_uid
    )
    show_places(
      here_map, 
      possible_sites + hospitals, 
      current_geocode=current_geocode, 
      address=address
    )
  else:
    status = ''
    show_places(
      here_map, places + hospitals, 
      current_geocode=current_geocode, 
      address=address
    )
  
  map_html = here_map.get_root().render()

  return map_html, current_geocode, status


@app.callback(
  [
    Output('optimizeButton', 'disabled'),
    Output('searchButton', 'disabled')
  ],
  [
    Input('optimizeButton', 'n_clicks'),
    Input('searchButton', 'n_clicks'),
    Input('currentGeocode', 'value')
  ]
)
def disable_enable_buttons(optimize_btn, search_btn, geocode):
  ctx = dash.callback_context

  if not ctx.triggered:
    button_id = None
  else:
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

  if button_id in ['optimizeButton', 'searchButton']:
    if (optimize_btn is not None and optimize_btn > 0) or (search_btn is not None and search_btn > 0):
      return True, True
    else:
      return False, False
  else:
    return False, False
