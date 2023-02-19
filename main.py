import datetime
import os

import functions_framework
from google.cloud import bigquery

from . import airthings, ecobee

CO2_THRESHOLD = 800
VOC_THRESHOLD = 250
PM25_THRESHOLD = 10


@functions_framework.cloud_event
def request_aq_data(_):
    client_id = os.environ['AIRTHINGS_CLIENT_ID']
    client_secret = os.environ['AIRTHINGS_CLIENT_SECRET']
    device_id = os.environ['DEVICE_ID']
    bq_table = os.environ['BIGQUERY_TABLE']
    ecobee_api_key = os.environ['ECOBEE_API_KEY']
    ecobee_refresh_token = os.environ['ECOBEE_REFRESH_TOKEN']

    ac = airthings.AirthingsClient(client_id, client_secret)

    readings = ac.get_latest_readings(device_id)['data']

    print(str(readings))

    client = bigquery.Client()

    bq_row = {'device_id': device_id, **readings}
    bq_row['time'] = datetime.datetime.fromtimestamp(
        bq_row['time'], tz=datetime.timezone.utc).isoformat()

    errors = client.insert_rows_json(bq_table, [bq_row])
    if errors:
        print('encountered errors: ' + str(errors))

    if readings['co2'] >= CO2_THRESHOLD or readings[
            'voc'] >= VOC_THRESHOLD or readings['pm25'] >= PM25_THRESHOLD:
        print('Current readings above threshold: ' + str(readings))
        ec = ecobee.EcobeeClient(ecobee_api_key, ecobee_refresh_token)
        if ec.is_fan_on():
            print('Fan already on hold')
        else:
            result = ec.set_fan_hold()
            if result:
                print('Turning on fan')
            else:
                print('WARNING: failed to turn on fan')
