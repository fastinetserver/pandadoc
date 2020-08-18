import os
import string
import random
import requests

from .pandadocument import PandaDocumentAbstract
from .pandafolder import PandaFolder
from .pandatemplate import PandaTemplateAbstract

DEFAULT_PANDADOC_API_KEY = os.environ.get('DEFAULT_PANDADOC_API_KEY', 'put-your-key-here')
DEFAULT_PANDADOC_BASE_API_URL = os.environ.get('DEFAULT_PANDADOC_BASE_API_URL', 'https://api.pandadoc.com/public/v1/')
DEFAULT_PANDADOC_BASE_APP_URL = os.environ.get('DEFAULT_PANDADOC_BASE_APP_URL', 'https://app.pandadoc.com/')
DEFAULT_PANDADOC_DOWNLOAD_FOLDER = os.environ.get('DEFAULT_PANDADOC_DOWNLOAD_FOLDER', './pandadoc_docs')
DEFAULT_RANDOM_FILENAME_LENGTH = int(os.environ.get('DEFAULT_RANDOM_FILENAME_LENGTH', '20'))



class PandaDoc:
    def __init__(self):
        self.__api_key = DEFAULT_PANDADOC_API_KEY
        self.__base_api_url = DEFAULT_PANDADOC_BASE_API_URL
        self.__base_app_url = DEFAULT_PANDADOC_BASE_APP_URL
        self.__download_folder = DEFAULT_PANDADOC_DOWNLOAD_FOLDER
        self.__random_filename_length = DEFAULT_RANDOM_FILENAME_LENGTH

    @property
    def documents(self):
        class __PandaDocument(PandaDocumentAbstract):
            _pandadoc = self
        return __PandaDocument

    @property
    def templates(self):
        class __PandaTemplate(PandaTemplateAbstract):
            _pandadoc = self
        return __PandaTemplate

    @property
    def tempate_folders(self):
        class __PandaTemplatesFolder(PandaFolder):
            _pandadoc = self

            @classmethod
            def get_folder_type(cls):
                return 'templates'
        return __PandaTemplatesFolder

    @property
    def document_folders(self):
        class __PandaDocumentsFolder(PandaFolder):
            _pandadoc = self

            @classmethod
            def get_folder_type(cls):
                return 'documents'
        return __PandaDocumentsFolder

    @property
    def random_filename_length(self):
        return self.__random_filename_length

    @random_filename_length.setter
    def random_filename_length(self, value):
        self.__random_filename_length = value

    @property
    def headers(self):
        return {
            'Authorization': 'API-Key {api_key}'.format(api_key=self.__api_key),
            # 'Authorization': 'Bearer 755eafd4eb987e3aa2d8cc9f3f0b9b2220dc6959',
            'Content-Type': 'application/json',
        }

    @property
    def api_key(self):
        return self.__api_key

    @api_key.setter
    def api_key(self, value):
        self.__api_key = value

    @property
    def base_api_url(self):
        return self.__base_api_url

    @base_api_url.setter
    def base_api_url(self, value):
        self.__base_api_url = value

    def get_api_url(self, uri):
        return '{base_url}{uri}'.format(base_url=self.base_api_url, uri=uri)

    @property
    def base_app_url(self):
        return self.__base_app_url

    @base_app_url.setter
    def base_app_url(self, value):
        self.__base_app_url = value

    def get_app_url(self, uri):
        return '{base_url}{uri}'.format(base_url=self.base_app_url, uri=uri)

    @property
    def download_folder(self):
        return self.__download_folder

    @download_folder.setter
    def download_folder(self, value):
        self.__download_folder = value

    def random_filepath(self, download_folder: str = None, ext: str = '.pdf'):
        letters = string.digits + string.ascii_letters
        if download_folder is None:
            download_folder = self.__download_folder
        while True:
            filename = ''.join(random.choice(letters) for i in range(self.random_filename_length))
            filename_with_ext = '{filename}{ext}'.format(
                filename=filename,
                ext=ext,
            )
            filepath = os.path.join(download_folder, filename_with_ext)
            if not os.path.isfile(filepath):
                break
        return filepath

    @staticmethod
    def debug_response(response, debug=False):
        if debug:
            print(response.status_code)
            print(response.text)

    def post(self, uri, data=None, debug=False):
        url = self.get_api_url(uri)
        if data is None:
            data = {}
        response = requests.post(url, json=data, headers=self.headers)
        self.__class__.debug_response(response, debug)
        return response

    def put(self, uri, data=None, debug=False):
        url = self.get_api_url(uri)
        if data is None:
            data = {}
        response = requests.put(url, json=data, headers=self.headers)
        self.__class__.debug_response(response, debug)
        return response

    def get(self, uri, data=None, debug=False, **kwargs):
        url = self.get_api_url(uri)
        if data is None:
            data = {}
        response = requests.get(url, params=data, headers=self.headers, **kwargs)
        self.__class__.debug_response(response, debug)
        return response

    def delete(self, uri, data=None, debug=False):
        url = self.get_api_url(uri)
        if data is None:
            data = {}
        response = requests.delete(url, data=data, headers=self.headers)
        self.__class__.debug_response(response, debug)
        return response

    def download(self, uri, filename=None, download_folder=None) -> str:
        response = self.get(uri)
        if download_folder is None:
            download_folder = self.download_folder
        if filename is None:
            filepath = self.random_filepath(download_folder)
        else:
            filepath = os.path.join(download_folder, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return filepath

    def download_large(self, uri, filename=None, download_folder=None) -> str:
        if download_folder is None:
            download_folder = self.download_folder
        if filename is None:
            filepath = self.random_filepath(download_folder)
        else:
            filepath = os.path.join(download_folder, filename)
        with self.get(uri, debug=False, stream=True) as response:
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        return filepath