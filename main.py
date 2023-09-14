import PySimpleGUI as sg
import os
import subprocess
from lib.RepeatedTimer import RepeatedTimer
from colorama import Fore, Back, Style
from datetime import datetime
from lib.Settings import Settings

class MainWindow:
    # name = []

    def __init__(self):
        self.layout = []
        self.window = None
        self.rt = None
        self.activeServices = []
        self.inactiveServices = []
        self.nginxStatus = ""
        settingsClass = Settings()
        self.mapDict = settingsClass.get_setting('hosts_dict')
        self.hosts_file_location = settingsClass.get_setting('hosts_file_location')
        self.nginx_config_location = settingsClass.get_setting('nginx_config_location')


    def initializeWindow(self):

        self.updateNginxData()

        generateButtons = [
                    [sg.Text('Opcje')],
                ]
        keys = self.mapDict.keys()
        for key in keys:
            name = key.upper()
            generateButtons.append([
                        sg.Frame(name, [

                            [sg.Button('Włącz ' + name, key='enable' + name)],
                            [sg.HorizontalSeparator()],
                            [sg.Button('Wyłącz ' + name, key='disable' + name)],

                        ], expand_x=True)
                    ])
        self.layout = [
            [
                sg.Column([
                    [sg.Text('Status NGINX:', key="nginxPrefix"),
                     sg.Text(self.nginxStatus, key='nginxStatus', text_color='yellow')],
                    [sg.Text('Aktywne serwisy:', text_color='lawngreen')],
                    [sg.Listbox(self.activeServices,
                                expand_x=True,
                                expand_y=True,
                                auto_size_text=True,
                                key='activeServices'
                                )],
                    [sg.Button('Odśwież', key='refresh')],
                    [sg.Button('Włącz NGINX', key='startNGINX'),
                     sg.Button('Wyłącz NGINX', key='stopNGINX'),
                     sg.Button('Restart NGINX', key='restartNGINX')],

                    [sg.Text('Nieaktywne serwisy:', text_color='firebrick')],
                    [sg.Listbox(self.inactiveServices,
                                expand_x=True,
                                expand_y=True,
                                auto_size_text=True,
                                key='inactiveServices'
                                )],
                    [sg.Text('Output:')],
                    [sg.Multiline(expand_x=True, expand_y=True, key='output', disabled=True)],
                    [sg.Button('Wyjdź', key='exit')],
                ], expand_y=True, expand_x=True),
                sg.Column(generateButtons, expand_y=True, expand_x=True)
            ],

        ]



        sg.theme('BluePurple')
        self.window = sg.Window('NGINX menu', self.layout, size=(600, 600))
        self.rt = RepeatedTimer(20, self.updateNginxData, True)

    def updateNginxData(self, set=False):
        print("updateNginxData\n")
        entries = os.listdir(self.nginx_config_location)
        # print(entries)
        active = []
        inactive = []
        for entry in entries:
            if "_backup" not in entry:
                active.append(entry)
            else:
                inactive.append(entry)
        self.activeServices = active
        self.inactiveServices = inactive

        # nginx_status = subprocess.check_output(['/usr/bin/systemctl is-active nginx'], shell=True)
        # nginx_status = os.system('/usr/bin/systemctl is-active nginx')
        # self.nginxStatus = nginx_status.decode('ascii')
        process = subprocess.Popen(['/usr/bin/systemctl', 'is-active', 'nginx'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        self.nginxStatus = str(stdout.decode('ascii')).replace('\n', '')
        '''if self.nginxStatus == 'inactive':
            self.nginxStatus = "Nieaktywny"
        elif self.nginxStatus == 'active':
            self.nginxStatus = "Aktywny"'''

        if set:
            self.setActiveServices(self.activeServices)
            self.setInactiveServices(self.inactiveServices)
            self.setNginxStatus(self.nginxStatus)

    def events(self):
        while True:  # Event Loop
            event, values = self.window.read()
            print(event, values)
            if event == sg.WIN_CLOSED or event == 'exit':
                self.rt.stop()
                break
            if event == 'refresh':
                # Update the "output" text element to be the value of "input" element
                # self.window['-OUTPUT-'].update(values['-IN-'])
                self.updateNginxData(set=True)
            if event == 'startNGINX':
                subprocess.call('service nginx start', shell=True)
                self.updateNginxData(set=True)
            if event == 'stopNGINX':
                subprocess.call('service nginx stop', shell=True)
                self.updateNginxData(set=True)
            if event == 'restartNGINX':
                subprocess.call('service nginx restart', shell=True)
                self.updateNginxData(set=True)

            if event == "test":
                self.hostsFileChange('akad', True)
                # false to włącz, true to wyłącz

            if "enable" in event:
                self.hostsFileChange('all', True)
                event = event.lower()
                event = event.replace('enable', '')
                self.enable(event)
                self.hostsFileChange(event, False)
                self.updateNginxData(set=True)

            if "disable" in event:
                event = event.lower()
                event = event.replace('disable', '')
                self.disable(event)
                self.hostsFileChange(event, True)
                self.updateNginxData(set=True)



        self.window.close()

    def enable(self, key_word):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        entries = os.listdir(self.nginx_config_location)
        print(entries)
        changes = 0
        if len(entries) > 0:
            if key_word == "all":
                for entry in entries:

                    if "_backup" in entry:
                        # text = "Włączam " + Fore.GREEN + entry + Fore.RESET
                        text = "Włączam " + entry

                        print(text)
                        self.addToOutput(text)
                        os.rename(self.nginx_config_location + '/' + entry,
                                  self.nginx_config_location + '/' + entry.replace('_backup', ''))
                        changes = changes + 1
                    else:
                        # text = entry + " jest już " + Fore.GREEN + " włączone" + Fore.RESET
                        text = entry + " jest już włączone"
                        print(text)
                        self.addToOutput(text)
            else:

                for entry in entries:
                    if key_word in entry:
                        if "_backup" in entry:
                            # text = "Włączam " + Fore.GREEN + entry + Fore.RESET
                            text = "Włączam " + entry
                            print(text)
                            self.addToOutput(text)
                            os.rename(self.nginx_config_location + '/' + entry,
                                      self.nginx_config_location + '/' + entry.replace('_backup', ''))
                            changes = changes + 1
                        else:
                            # text = entry + " jest już " + Fore.GREEN + " włączone" + Fore.RESET
                            text = entry + " jest już włączone"
                            print(text)
                            self.addToOutput(text)
        if changes > 0:
            # os.system('service nginx restart')
            subprocess.call('service nginx restart', shell=True)

    def disable(self, key_word):
        entries = os.listdir(self.nginx_config_location)
        print(entries)
        changes = 0

        if len(entries) > 0:
            if key_word == "all":

                for entry in entries:
                    if "_backup" not in entry:
                        # text = "Wyłączam " + Fore.RED + entry + Fore.RESET
                        text = "Wyłączam " + entry
                        print(text)
                        self.addToOutput(text)
                        os.rename(self.nginx_config_location + '/' + entry, self.nginx_config_location + '/' + entry + '_backup')
                        changes = changes + 1
                    else:
                        # text = entry + " jest już " + Fore.RED + "wyłączone" + Fore.RESET
                        text = entry + " jest już wyłączone"
                        print(text)
                        self.addToOutput(text)

            else:
                for entry in entries:
                    if key_word in entry:
                        if "backup" not in entry:
                            # text = "Wyłączam " + Fore.RED + entry + Fore.RESET
                            text = "Wyłączam " + entry
                            print(text)
                            self.addToOutput(text)
                            os.rename(self.nginx_config_location + '/' + entry, self.nginx_config_location + '/' + entry + '_backup')
                            changes = changes + 1
                        else:
                            # text = entry + " jest już " + Fore.RED + "wyłączone" + Fore.RESET
                            text = entry + " jest już wyłączone"
                            print(text)
                            self.addToOutput(text)
        if changes > 0:
            # os.system('service nginx restart')
            subprocess.call('service nginx restart', shell=True)

    def setActiveServices(self, arr):
        print("update listy")
        self.window['activeServices'].update(arr)

    def setInactiveServices(self, arr):
        print("update listy nieaktywnych")
        self.window['inactiveServices'].update(arr)

    def setNginxStatus(self, string):
        print("update status nginx")
        print(string)
        if string == "active":
            string = 'Aktywny'
            self.window['nginxStatus'].update(string, text_color='lawngreen')
        else:
            self.window['nginxStatus'].update(string, text_color='red')

    def addToOutput(self, string, timestamp=True):
        if timestamp:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            tmstp = "[" + current_time + "] "
            self.window['output'].update(tmstp + string + "\n", append=True)
        else:
            self.window['output'].update(string + "\n", append=True)

    def hostsFileChange(self, string, modeDisable):
        #file = open(os.getcwd() + '/' + self.hostsFileLocation, "r")
        file = open(self.hosts_file_location, "r")
        replaced_content = ""
        # looping through the file
        mapDictString = self.mapDict[string]
        # print("wchodze!")

        for line in file:
            # stripping line break
            line = line.strip()

            # replacing the texts
            if isinstance(mapDictString, list):
                #jazda tak samo jak by było pojedyńcze, i sprawdzamy czy pojedyńcza linia "podzielona"
                temp_line = line
                temp_line = temp_line.split(' ')
                #sprawdzamy czy linie da sie podzielic
                if len(temp_line) >= 2:
                    name = temp_line[1]
                    if name in mapDictString:
                        #jezeli jest w arrayu sprawdzamy jaki mod jest wlaczony i co mamyz robić :)
                        if modeDisable:
                            # jeżeli mode jest disable, sprawdzanie czy jest wyłączone już
                            if "#" in line:
                                replaced_content = replaced_content + line + '\n'

                            else:
                                new_line = '#' + line
                                replaced_content = replaced_content + new_line + "\n"

                        else:

                            if "#" in line:
                                new_line = line.replace('#', '')
                                replaced_content = replaced_content + new_line + '\n'

                            else:
                                replaced_content = replaced_content + line + '\n'
                    else:
                        #jezeli nie ma w arrayu przeklejamy dalej
                        replaced_content = replaced_content + line+ '\n'
                else:
                    #jezeli sie nie da to jakiś śmieciowy opis
                    replaced_content = replaced_content + line+ '\n'




            elif isinstance(mapDictString, str):
                if string in line:
                    if modeDisable:
                        # jeżeli mode jest disable, sprawdzanie czy jest wyłączone już
                        if "#" in line:
                            replaced_content = replaced_content + line + '\n'

                        else:
                            new_line = '#' + line
                            replaced_content = replaced_content + new_line + "\n"

                    else:

                        if "#" in line:
                            new_line = line.replace('#', '')
                            replaced_content = replaced_content + new_line + '\n'

                        else:
                            replaced_content = replaced_content + line + '\n'

                else:
                    replaced_content = replaced_content + line + "\n"
        file.close()
        #print(replaced_content)
        # Open file in write mode
        write_file = open(self.hosts_file_location, "w")
        # overwriting the old file contents with the new/replaced content
        write_file.write(replaced_content)
        # close the file
        write_file.close()

    def checkOne(self, file, string, mode):
        replaced_content = ""
        for line in file:
            line = line.strip()
            print("lynijka")
            print(line)
            if string in line:
                if mode:
                    # jeżeli mode jest disable, sprawdzanie czy jest wyłączone już
                    if "#" in line:
                        return line + '\n'

                    else:
                        new_line = '#' + line
                        return new_line + "\n"

                else:

                    if "#" in line:
                        new_line = line.replace('#', '')
                        return new_line + '\n'

                    else:
                        return line + '\n'

            else:
                return line + "\n"
        return replaced_content



mainWindow = MainWindow()
mainWindow.initializeWindow()
mainWindow.events()
