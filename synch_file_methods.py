"""
Модуль реализации работы с удаленным хранилищем.
"""
import os
import requests
import json
import logging
from config import CATALOG_SERVICE, PATH_LOCAL_CATALOG
from typing import Dict, BinaryIO, Any


class SynchFileMethods:
    """
    Класс, реализует работу с удалённым хранилищем(получение информации, загрузка, перезапись, удаление).
    Attributes:
        headers = Словарь, для авторизации в request-запросах, содержащий токен
        path = Путь к существующей папке для хранения резервных копий в удалённом хранилище
    Methods:
        get_info = Метод получения информации о файле на удалённом хранилище
        load_file = Метод загрузки файла на удалённое хранилище
        overwriting_file = Метод перезаписи файла на удалённом хранилище
        delete_file = Метод удаления файла из удалённого хранилища
    """
    def __init__(self, token, path: str) -> None:
        self.headers: Dict[str: str] = {'Authorization': token}
        self.path: str = path

    def get_info(self, url: str, params: dict = None) -> Any:
        """
        Метод, который отправляет запрос серверу.
        Attributes:
            response = Ответ от сервера
            response_text = Обработанный ответ от сервера
        :param url: Адрес сайта.
        :param params: Параметры функции.
        :return: Ответ от сервера
        """
        try:
            response: requests.Response = requests.get(url, headers=self.headers, params=params)
            response_text: dict = json.loads(response.text)
            if response.status_code >= 400:
                logging.error(response_text['message'])
                return
            return response_text
        except requests.exceptions.ConnectionError:
            logging.error('Ошибка соединения.')

    def load_file(self, file_name: str) -> None:
        """
        Метод, который загружает файл на удаленное хранилище.
        Attributes:
            url = Адрес сайта
            params = Параметр фильтрации вывода('fields') метода get_info, выводит только указанный ключ
            response = Запрос на загрузку файла
            path_file = Путь до файла на локальном компьютере
            files = Параметры метода put. Словарь, 'file': открытый файл,
                    для загрузки, в режиме бинарного чтения
        :param file_name: Имя загружаемого файла.
        """
        try:
            url: str = f'{self.path}/upload?path={CATALOG_SERVICE}/{file_name}'
            params: Dict[str: str] = {
                'fields': 'href'
            }
            response: dict = self.get_info(url, params=params)
            path_file: str = os.path.join(os.path.abspath(os.sep), PATH_LOCAL_CATALOG, file_name)

            files: Dict[str: BinaryIO] = {
                'file': open(path_file, 'rb')
            }
            requests.put(response['href'], files=files)
            logging.info(f'Файл: {file_name} успешно загружен.')
        except PermissionError:
            logging.error(f'{file_name} -  не файл.')

    def overwriting_file(self, file_name: str) -> None:
        """
        Метод перезаписи файла на удаленном хранилище.
        Attributes:
            url = Адрес сайта
            params = Параметры фильтрации вывода('fields') метода get_info, выводит только указанный ключ
                     и режим перезаписи файла('overwrite')
            response = Запрос на сервер
            path_file = Путь до файла на локальном компьютере
            files = Параметры метода put. Словарь, 'file': открытый файл,
                    для перезаписи, в режиме бинарного чтения.
        :param file_name: Имя файла, который нужно перезаписать.
        """
        url: str = f'{self.path}/upload?path={CATALOG_SERVICE}/{file_name}'
        params: Dict[str: str] = {
            'fields': 'href',
            'overwrite': 'true'
        }
        response: dict = self.get_info(url, params=params)
        path_file: str = os.path.join(os.path.abspath(os.sep), PATH_LOCAL_CATALOG, file_name)

        files: Dict[str: BinaryIO] = {
            'file': open(path_file, 'rb')
        }

        requests.put(response['href'], files=files)
        logging.info(f'Файл: {file_name} успешно перезаписан.')

    def delete_file(self, file_name: str) -> None:
        """
        Метод удаления файла в удаленном хранилище.
        Attributes:
            url = Адрес сайта.
        :param file_name: Имя файла, который нужно удалить.
        """
        url: str = f'{self.path}?path={CATALOG_SERVICE}/{file_name}'
        requests.delete(url, headers=self.headers)
        logging.info(f'Файл: {file_name} успешно удален.')
