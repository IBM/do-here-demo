from dotenv import load_dotenv
load_dotenv()

from app import app
from app import server

from config import enable_debug

import os

port = int(os.getenv('PORT', 8050))

if __name__ == '__main__':
  app.run_server(host='0.0.0.0', port=port, debug=enable_debug)
