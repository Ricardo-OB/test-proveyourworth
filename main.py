import logging as log
import requests
from utils import create_logs, get_params_session, get_payload, upoload_data


if __name__ == '__main__':

    MAIN_URL = "http://www.proveyourworth.net/level3/"
    name = 'Ricardo Ortega B'

    create_logs(file_name='logs')

    persisten_session = requests.Session()

    data = get_params_session(url=MAIN_URL, session=persisten_session, username=name)
    url_payload, img = get_payload(url=MAIN_URL, session=persisten_session, data=data)
    upoload_data(url=url_payload, session=persisten_session, data=data, image=img)
    

    

