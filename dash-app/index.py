import dash_html_components as html

from app import server
from app import app

from dotenv import load_dotenv
load_dotenv()

from config import enable_debug, use_sample_data, demo_title, demo_description

from layouts.info import info_panel
from layouts.header import page_header
from layouts.main import page_content

import callbacks
import os

port = int(os.getenv('PORT', 8050))

app.title = '{}  | {}'.format(demo_description, demo_title)

app.layout = html.Div(
  id='emergency-center-dashboard',
  className='sample-data' if use_sample_data else '',
  children=[
    page_header,
    info_panel,
    page_content
  ]
)

if __name__ == '__main__':
  app.run_server(host='0.0.0.0', port=port, debug=enable_debug)
