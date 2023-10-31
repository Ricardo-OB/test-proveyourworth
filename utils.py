from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import logging as log
import os
import shutil
import json


def create_logs(file_name:str='file_logs'):
    root_path = os.path.dirname(os.path.realpath(__file__))
    METADATA_PATH = root_path + "/metadata"

    # Create folder to store logs and headers
    if not os.path.exists(METADATA_PATH):
        os.makedirs(METADATA_PATH)
    else:
        # Delete all files if folder exists
        for filename in os.listdir(METADATA_PATH):
            file_path = os.path.join(METADATA_PATH, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    # Basic config of log
    log.basicConfig(level=log.INFO,
                    encoding='utf-8',
                    format='%(asctime)s: %(levelname)s [%(filename)s:%(lineno)s] %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p',
                    handlers=[log.FileHandler(METADATA_PATH+f'/{file_name}.log'), log.StreamHandler()]
                    )


def save_headers(headers, name:str="json_file"):
    # Function to save headers and inspect them
    folder_path = "./metadata/"
    try:
        log.info(f"Saving headers ({name})...")
        json_headers = json.dumps(dict(headers))
        with open(folder_path+name+".json", "w") as file:
            file.write(json_headers)
        log.info(f"Headers ({name}) saved successfully")
    except Exception as e:
        log.info(f"Error saving headers ({name}). " + e)


def get_params_session(url:str, session, username:str='Ricardo OB'):
    try:  
        log.info("Getting the data...")
        # Get request to obtain html content
        url_start = url + 'start'
        request_start = session.get(url_start, verify=False)
        if request_start.status_code == 200:
            save_headers(request_start.headers, name="headers_1")
            html_content = BeautifulSoup(request_start.text, features="html.parser")
            # Get input with hash value
            hash_value = html_content.find('input', {'name':'statefulhash'}).get('value')
            # Return dict with username and hash value
            data = {
                'statefulhash': hash_value,
                'username': username
            }
            log.info("Data was obtained successfully.")
            return data
    except Exception as e:
        log.info("Error getting session parameters/data. " + e)


def get_payload(url:str, session, data:dict):
    try:
        log.info("Downloading payload...")
        # Post request with the data obtained (hash and username)
        request = session.post(f'{url}/activate', params=data)
        if request.status_code == 200:
            save_headers(request.headers, name="headers_2")
            # Get request to obtain the payload
            url_payload = request.headers['X-Payload-URL']
            request_payload = session.get(url_payload, stream=True)
            if request_payload.status_code == 200:
                save_headers(request_payload.headers, name="headers_3")
                # Get image and preprocess image
                image = request_payload.raw
                image = Image.open(image)
                log.info("Payload downloaded successfully.")
    except Exception as e:
        log.info("Error to get payload URL and Image. " + e)

    return url_payload, image


def edit_image(data:dict, img:Image):
    try:
        log.info("Editing image...")
        # Define font, information to put, edit image and save iamge
        print(type(img))
        image_to_edit = ImageDraw.Draw(img)
        arial_font = ImageFont.truetype("arial.ttf", 18)
        info = ["Ricardo Ortega Bolaños", data['statefulhash'], "Web Developer", "ricardo.bo@outlook.com", "https://github.com/ricardo-ob"]
        y_pos = 25
        for text in info:
            image_to_edit.text((25,y_pos), text, fill=(255, 44, 37), font=arial_font)
            y_pos += 17
        img.save("edited_image.png", "PNG")
        log.info("Image edited successfully.")
    except Exception as e:
        log.info("Error editing image. " + e)


def upoload_data(url:str, session, data:dict, image:Image):
    try:
        log.info("Uploading data and files...")
        edit_image(data=data, img=image)
        # Get request to obtain the destination url
        request_payload = session.get(url, verify=False)
        if request_payload.status_code == 200:
            # Destination URL and cookies
            url_reaper = request_payload.headers['X-Post-Back-To']
            cookies = {'X-Oh-Look': str(request_payload.headers['Set-Cookie']).strip('; path=/')}

            # Information and files to send
            data = {
                "name" : "Ricardo Ortega Bolaños",
                "email" : "ricardo.bo@outlook.com",
                "aboutme" : "I am Ricardo Ortega Bolaños, a biomedical engineer and web developer with a deep commitment to the development of innovative solutions on both the Backend and Frontend sides, with a specialized focus on Python using tools such as FastAPI and with bases in Django and Flask. Among my soft skills are: self-learning, responsibility, creativity, time management and teamwork. Among some languages and tools that I use are Python (with frameworks), HTML, JS, CSS, MySQL, PostgreSQL, Git, Java, C# and I have strong foundations in Data Science."
            }
            files = {
                "image": open("edited_image.png", "rb"),
                "code": open("utils.py", "rb"),
                "resume": open("cv-ricardo-ortega.pdf", "rb")     
            }

            # Test post request
            # test_post_url = "https://httpbin.org/post"
            # request_reaper = session.post(test_post_url, data=data, files=files, cookies=cookies)

            # Post request to upload files, data and cookies
            request_reaper = session.post(url_reaper, data=data, files=files, cookies=cookies)
            map(lambda x: x.close(), files)

            if request_reaper.status_code == 200:
                save_headers(request_reaper.headers, name="headers_4")
                with open("output.txt", "w") as file:
                    file.write(request_reaper.text)

            log.info("Upload of data and files successfully.")
        
    except Exception as e:
        log.info("Error in upload data and files process. " + e)



"""
# main.py file that runs all functions #
# The file is not attached but you can find it at https://github.com/ricardo-ob/test-proveyourworth

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

"""