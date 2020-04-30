import dash
import dash_html_components as html
import flask

from config import use_sample_data, demo_title, demo_description

from layouts.info import info_panel
from layouts.header import page_header
from layouts.main import page_content

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

app.config.suppress_callback_exceptions = True
app.title = '{} | {}'.format(demo_description, demo_title)

app.layout = html.Div(
  id='emergency-center-dashboard',
  className='sample-data' if use_sample_data else '',
  children=[
    page_header,
    info_panel,
    page_content
  ]
)

import callbacks
