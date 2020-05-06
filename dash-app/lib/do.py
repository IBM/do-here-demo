from time import sleep
import pandas as pd
import os

from lib.Place import Place
from config import use_sample_data
from data.sample import sample_possible_sites

DEPLOYMENT_UID = os.environ.get('WML_DEPLOYMENT_UID')
WML_API_KEY = os.environ.get('WML_API_KEY')
WML_INSTANCE_ID = os.environ.get('WML_INSTANCE_ID')
WML_URL = os.environ.get('WML_URL')

def get_deployment(deployment_uid):
  if deployment_uid is not None:
    guid = deployment_uid
  else:
    guid = DEPLOYMENT_UID
  return guid

def find_possible_sites(places_objs, routes_obj, number_sites=3, deployment_uid=None):
  if use_sample_data:
    sleep(3)
    return [Place(p) for p in sample_possible_sites]
  else:
    places_df = pd.DataFrame.from_records([p.to_dict() for p in places_objs])
    routes_df = pd.DataFrame.from_records(routes_obj)
    routes_df.drop_duplicates(subset=['geopoints'], keep='last', inplace=True)

    guid = get_deployment(deployment_uid)
    
    if guid == 'local' or guid is None:
      possible_sites, status = DOLocal().solve(places_df, routes_df, number_sites)
    else:
      possible_sites, status = DOWml(guid).solve(places_df, routes_df, number_sites)

    return [Place(p) for p in possible_sites], status
    

class DOLocal:
  def __init__(self):
    from lib.model import build_and_solve
    self.build_and_solve = build_and_solve

  def solve(self, places_df, routes_df, number_sites=3):
    print('Running local model')
    possible_sites = self.build_and_solve(places_df, routes_df, number_sites)
    return [p._asdict() for p in possible_sites], ''


class DOWml:
  def __init__(self, deployment_uid=None):
    from watson_machine_learning_client import WatsonMachineLearningAPIClient

    self.deployment_uid = deployment_uid

    wml_credentials = {
      'apikey': WML_API_KEY,
      'instance_id': WML_INSTANCE_ID,
      'url': WML_URL
    }
    self.wml_client = WatsonMachineLearningAPIClient(wml_credentials)

  def solve (self, places_df, routes_df, number_sites=3):
    solve_payload = {
      self.wml_client.deployments.DecisionOptimizationMetaNames.INPUT_DATA: [
        { 'id': 'places.csv', 'values' : places_df },
        { 'id': 'routes.csv', 'values' : routes_df }
      ],
      self.wml_client.deployments.DecisionOptimizationMetaNames.OUTPUT_DATA: [
        { 'id': '.*\.csv' }
      ]
    }

    print('Solving using WML deployment: {}'.format(self.deployment_uid))

    job_details = self.wml_client.deployments.create_job(self.deployment_uid, solve_payload)
    print('Created job')

    job_uid = self.wml_client.deployments.get_job_uid(job_details)
    print('Running job: {}'.format(job_uid))

    while job_details['entity']['decision_optimization']['status']['state'] not in ['completed', 'failed', 'canceled']:
      print(job_details['entity']['decision_optimization']['status']['state'] + '...')
      sleep(3)
      job_details = self.wml_client.deployments.get_job_details(job_uid)

    status = job_details['entity']['decision_optimization']['status']['state']

    if status in ['failed', 'canceled']:
      print(job_details['entity']['decision_optimization']['status'])
      possible_sites = []
      status = 'Model did not solve. There may not have been a possible solution. Adjust settings and try again.'
    else:
      solution_df = pd.DataFrame(
        job_details['entity']['decision_optimization']['output_data'][0]['values'],
        columns = job_details['entity']['decision_optimization']['output_data'][0]['fields']
      )
      status = ''
      
      possible_sites = solution_df.to_dict('records')

    return possible_sites, status

