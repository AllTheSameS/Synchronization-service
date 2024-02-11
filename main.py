"""
Модуль запуска программы.
"""
import datetime
import os
import logging
from config import SYNCH_INTERVAL, TOKEN, PATH_LOCAL_CATALOG, CATALOG_SERVICE
from synch_file_methods import SynchFileMethods
from time import sleep
from typing import Dict, Any


logging.basicConfig(
    filename='log.log',
    filemode='w',
    level=logging.INFO,
    encoding='utf-8',
    format='%(module)s %(asctime)s %(levelname)s: %(message)s'
)


def get_name_and_time_last_changes_file() -> Any:
    """
    Функция, возвращает время последнего изменения файла на удаленном сервере.
    Attributes:
        CATALOG_SERVICE = Название каталога на сервисе
        url = Адрес сайта с путем до папки на сервисе
        params = Параметры функции
        response = Ответ от сервера
        result = Время последнего изменения файла
    :return: Время последнего изменения файла.
    """

    params: Dict[str: str] = {
        'fields': '_embedded.items.name, _embedded.items.modified'
    }

    url: str = f'{my_class.path}?path={CATALOG_SERVICE}'
    try:
        response = my_class.get_info(url, params=params)
        result: Dict[str: datetime] = {
            file['name']: datetime.datetime.fromisoformat(file['modified']).timestamp()
            for file in response['_embedded']['items']
        }
        return result
    except TypeError:
        return


def monitoring_files() -> None:
    """
    Функция, проверяет локальную директорию на появление новых или измененных файлов
    и вызывает соответсвующий метод, и удаляет файлы на удаленном хранилище,
    которых нет в локальной директории.
    Attributes:
        dict_files_on_disk = Список файлов на сервисе
        path_dir = Путь до локальной директории
        path_file = Путь до файла в локальной директории
        time = Время последнего изменения файла в локальной директории
    """

    dict_files_on_disk: Dict[str: datetime] = get_name_and_time_last_changes_file()
    path_dir: str = os.path.join(os.path.abspath(os.sep), PATH_LOCAL_CATALOG)
    try:
        for file in os.listdir(path_dir):
            path_file: str = os.path.join(os.path.abspath(os.sep), PATH_LOCAL_CATALOG, file)
            time = os.stat(path_file).st_mtime
            if file not in dict_files_on_disk:
                my_class.load_file(file)

            elif time > dict_files_on_disk[file]:
                my_class.overwriting_file(file)

        for file in dict_files_on_disk:
            if file not in os.listdir(path_dir):
                my_class.delete_file(file)
    except TypeError:
        return
    except FileNotFoundError:
        os.mkdir(path_dir)
        logging.error(f'Создан каталог по указанному пути: {path_dir}')


if __name__ == "__main__":
    logging.info(f'Программа синхронизации файлов начинает работу с директорией:\n{PATH_LOCAL_CATALOG}.')

    my_class = SynchFileMethods(
        token=TOKEN,
        path='https://cloud-api.yandex.net/v1/disk/resources'
    )

    while True:
        monitoring_files()
        sleep(int(SYNCH_INTERVAL))
