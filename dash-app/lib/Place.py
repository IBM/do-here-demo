
class Place(object):
  def __init__(self, p, is_medical=False):
    self.id = p['id']
    self.title = p['title']
    self.address = p['address']['label'] if 'label' in p['address'] else p['address']
    self.postal_code = p['address']['postalCode'] if 'postalCode' in p['address'] else p['postal_code']
    self.distance = p['distance']
    self.primary_category = p['categories'][0]['id'] if 'categories' in p else p['primary_category']
    self.geocode = '{},{}'.format(p['position']['lat'], p['position']['lng']) if 'position' in p else p['geocode']
    self.country = p['address']['countryCode'] if 'countryCode' in p['address'] else p['country']
    self.is_medical = p['is_medical'] if 'is_medical' in p else is_medical
    if isinstance(self.is_medical, str):
      self.is_medical = self.is_medical.lower() in ['true', '1']

  def __str__(self):
    # return(f'{self.title} ({self.postal_code}): {self.distance}')
    return self.address

  def marker(self):
    location = self.geocode.split(',')
    return {
      'title': self.title,
      'lat': float(location[0]),
      'lng': float(location[1]),
      'marker': str(self),
      'color': 'red' if self.is_medical else None,
      'icon': 'plus-sign' if self.is_medical else None
    }
    
  def to_dict(self):
    location = self.geocode.split(',')
    return({
      'id': self.id,
      'title': self.title,
      'address': self.address,
      'postal_code': self.postal_code,
      'distance': self.distance,
      'primary_category': self.primary_category,
      'geocode': self.geocode,
      'country': self.country,
      'is_medical': self.is_medical
    })
