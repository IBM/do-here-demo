
import dash_core_components as dcc
import dash_html_components as html
import dash_table

from lib.here import places_categories

sorted_categories = sorted(places_categories, key=lambda c: c['label'])


########
# MAP
########
layout_map = html.Div(
  className='max-tile hereMapTile',
  children=[
    dcc.Loading(
      id='loading-map',
      children=[
        html.Iframe(id='hereMap')
      ],
      type='circle'
    )
  ]
)

########
# CONTROLS
########
layout_controls = html.Div(
  className='max-tile controlsTile',
  children=[
    html.Div(
      className='max-field',
      children=[
        html.Label(
          htmlFor='addessInput',
          children=['Address']
        ),
        dcc.Input(
          id='addressInput',
          type='text',
          placeholder='Enter an address',
          value='New York, NY',
        ),
        html.Div(id='currentGeocode')
      ]
    ),
    html.Div(
      className='max-field',
      children=[
        html.Label(
          htmlFor='selectCategories',
          children=['Categories']
        ),
        dcc.Dropdown(
          id='selectCategories',
          options=sorted_categories,
          value=[],
          multi=True
        )
      ]
    ),
    html.Div(
      className='max-field',
      children=[
        html.Label(
          htmlFor='maxDistance',
          children=['Search radius (km)']
        ),
        dcc.Slider(
          id='maxDistance',
          min=0,
          max=50,
          step=5,
          value=25,
          marks={ 0: '0', 10: '10', 20: '20', 30: '30', 40: '40', 50: '50' }
        )
      ]
    ),
    html.Div(
      className='max-field',
      children=[
        html.Label(
          htmlFor='maxResults',
          children=['Max search results']
        ),
        dcc.Slider(
          id='maxResults',
          min=0,
          max=100,
          step=5,
          value=40,
          marks={ 0: '0', 20: '20', 40: '40', 60: '60', 80: '80', 100: '100' }
        )
      ]
    ),
    html.Button(
      id='optimizeButton',
      className='max-btn-secondary',
      children=['Run model']
    ),
    html.Button(
      id='searchButton',
      className='max-btn-primary',
      children=['Search places']
    ),
    html.Div(id='selectedCategories'),
    dcc.Location(id='url', refresh=False),
    html.Div(
      id='solutionStatus',
      className='solutionStatus'
    )
  ]
)

########
# MAIN CONTENT
########
page_content = html.Div(
  id='max-main-content',
  className='max-main-content',
  children=[
    html.Div(
      className='mapRow',
      children=[
        html.Div(
          className='max-main-left',
          children=[
            layout_map
          ]
        ),
        html.Div(
          className='max-main-right',
          children=[
            layout_controls
          ]
        )
      ]
    )
  ]
)
