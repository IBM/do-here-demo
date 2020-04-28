
class Place(object):
  def __init__(self, p):
    self.id = p['id']
    self.title = p['title']
    self.address = p['address']['label'] if 'label' in p['address'] else p['address']
    self.postal_code = p['address']['postalCode'] if 'postalCode' in p['address'] else p['postal_code']
    self.distance = p['distance']
    self.primary_category = p['categories'][0]['id'] if 'categories' in p else p['primary_category']
    self.geocode = '{},{}'.format(p['position']['lat'], p['position']['lng']) if 'position' in p else p['geocode']

  def __str__(self):
    return(f'{self.title} ({self.postal_code}): {self.distance}')

  def marker(self):
    location = self.geocode.split(',')
    return {
      'title': self.title,
      'lat': float(location[0]),
      'lng': float(location[1])
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
      'geocode': self.geocode
    })
