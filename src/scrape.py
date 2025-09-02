import requests
# import necessary modules from requests library
from requests.auth import HTTPBasicAuth
import pdfkit
# importing os module for environment variables
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv
# importng logging module for creating logs
import logging
import re

# loading variables from .env file
load_dotenv() 
logger = logging.getLogger(__name__)
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#pdfkit.configuration(wkhtmltopdf='C:/Users/KannanK/Downloads/wkhtmltox-0.12.6-1.mxe-cross-win64/wkhtmltox/bin/wkhtmltopdf.exe') 

# Replace with your own credentials and URL
CONFLUENCE_URL = os.getenv('CONFLUENCE_URL')
API_TOKEN = os.getenv('CONFLUENCE_API_TOKEN')
EMAIL = os.getenv('CONFLUENCE_EMAIL')
SPACE_KEY = os.getenv('CONFLUENCE_SPACE_KEY')
OUTPUT_FOLDER=f'Data/{SPACE_KEY}'
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# fetching  page ids for all the pages in the space 
def get_page_ids(space_key):
    try:
        url = f"{CONFLUENCE_URL}/rest/api/content?spaceKey={space_key}&expand=body.storage"
        response = requests.get(url, auth=HTTPBasicAuth(EMAIL, API_TOKEN), headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        return [(page['title'],page['id'] ) for page in data['results']]
    except Exception as e:
        logger.error(f'Found problem in fetching page ids: {e}')

# fetching  content of the page       
def get_page_html(page_id):
    try:
        logger.info('Fetching content of the page %s',page_id)
        url = f"{CONFLUENCE_URL}/rest/api/content/{page_id}?expand=body.storage"
        response = requests.get(url, auth=HTTPBasicAuth(EMAIL, API_TOKEN), headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        return data['body']['storage']['value']
    except Exception as e:
        logger.error(f"Failed to get page {page_id}: {e}")

 # converting html_content into pdfs   
def convert_html_to_pdf(html_content, output_filename):
    try:
        pdfkit.from_string(html_content, output_filename)
    except Exception as e:
        logger.error(f'Failed to convert {output_filename} file: {e}')

def main():
    page_ids = get_page_ids(SPACE_KEY)
    try:
        if not os.path.exists(OUTPUT_FOLDER): # checks and creates folder for the files
            os.makedirs(OUTPUT_FOLDER)
        logger.info('creating files')
        for title,page_id in page_ids:
            page_name=re.sub(r'[<>:"/\\|?*]', '', title)
            html_content = get_page_html(page_id)
            output_filename = os.path.join(OUTPUT_FOLDER, f"page_{page_name}.pdf")
            convert_html_to_pdf(html_content, output_filename)
            logger.info("file %s created",page_name)
        logger.info('successful')
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    main()

