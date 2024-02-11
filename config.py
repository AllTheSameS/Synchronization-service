import configparser


config = configparser.ConfigParser()
config.read('config.ini')

try:
    PATH_LOCAL_CATALOG = config.get('Settings', 'path_local_catalog')
    CATALOG_SERVICE = config.get('Settings', 'catalog_service')
    TOKEN = config.get('Settings', 'token')
    SYNCH_INTERVAL = config.get('Settings', 'synch_interval')
    PATH_LOG_FILE = config.get('Settings', 'path_log_file')
except configparser.NoOptionError as exc:
    exc = exc.message.split()
    print(f'Нет опции: {exc[2]}')
    exit()
else:
    print('Переменные окружения успешно загружены.')
