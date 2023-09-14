import json
import os


class Settings:
    __settings_file_name = './nginx-helper-settings.json'
    __settings = {
        'hosts_dict': {
            'short_name': 'domain.pl',
            'short_name2': [
                'domain2.pl',
                'www.domain2.pl'
            ]
        },
        'nginx_config_location': '/etc/nginx/conf.d',
        'hosts_file_location': '/etc/hosts'
    }

    def __init__(self):
        self.__load_settings()

    def __load_settings(self):
        if os.path.isfile(self.__settings_file_name):
            settings_file = open(self.__settings_file_name, 'r')
            settings = json.load(settings_file)
            # print(settings)

            for sett in self.__settings:
                # print("Settigns!")
                # print(sett)
                if sett not in settings:
                    settings[sett] = self.__settings[sett]
            self.__settings = settings
            self.__save_settings_to_file()


        else:
            settings_file = open(self.__settings_file_name, 'w')
            json.dump(self.__settings, settings_file)
            settings_file.close()
        # sprawdzenie czy istnieje plik z ustawieniami
        # jeżeli nie istnieje zainicjowanie z domyślnymi ustawieniami
        # jeżeli istnieje wczytanie
        pass

    def __save_settings_to_file(self):
        settings_file = open(self.__settings_file_name, 'w')
        json.dump(self.__settings, settings_file)
        settings_file.close()

    def save_settings(self):
        self.__save_settings_to_file()

    def get_setting(self, setting_name: str):
        return self.__settings[setting_name]
