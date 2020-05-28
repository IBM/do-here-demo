import os

def env_to_bool(value):
  if value is None or value.lower() in ['false', '0']:
    return False
  else:
    return bool(value)

enable_debug = env_to_bool(os.getenv('ENABLE_DEBUG'))

demo_title = 'DO + HERE'
demo_subtitle = 'Demo'
demo_description = 'Finding locations to establish temporary emergency facilities'

