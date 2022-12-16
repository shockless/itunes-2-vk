import argparse
import os
import pandas as pd
import random
import requests
import time
from time import gmtime, strftime
import vk_api


def TwoFactor():
    print('2Factor:')
    code = input()
    return code, True


def download(path, logs_path, playlist, vk):
    errors_path = 'errors'
    success_path = 'success'

    with open(playlist, encoding='UTF-16') as f:
        df = pd.read_csv(f, sep="\t", header=0)

    playlist_len = len(df)
    with open(os.path.join(logs_path, errors_path + '.txt'), "a", encoding="utf-8") as f_e:
        with open(os.path.join(logs_path, success_path + '.txt'), "a", encoding="utf-8") as f_s:
            print('\n', strftime("%Y-%m-%d %H:%M:%S", gmtime()), playlist, end='\n', file=f_s)
            print('\n', strftime("%Y-%m-%d %H:%M:%S", gmtime()), playlist, end='\n', file=f_e)
            for index, row in df.iterrows():
                real_name = str(row['Артист'] + ' - ' + row['Название'])
                write_name = bytes(real_name, 'utf-8').decode('utf-8', 'ignore')
                write_name = write_name.replace('/', " ")
                write_name = write_name.replace('?', " ")
                name = 'NONE'
                audio_path = os.path.join(path, write_name + '.mp3')
                if not os.path.exists(audio_path):
                    json = vk.method("audio.search", {"q": real_name, 'count': 1})
                    if json['count'] != 0:
                        audio_with_url = vk.method("audio.getById",
                                                   {"audios": "_".join(
                                                       str(json['items'][0][i]) for i in ("owner_id", "id"))})
                        url = audio_with_url[0]['url']
                        name = str(audio_with_url[0]['artist'] + ' - ' + audio_with_url[0]['title'])
                        name = bytes(name, 'utf-8').decode('utf-8', 'ignore')
                        name = name.replace('/', " ")
                        name = name.replace('?', " ")
                        if audio_with_url[0]['url'] != '':
                            f = open(audio_path, "wb")
                            print(str(index + 1) + '/' + str(playlist_len), name, 'File:', write_name)
                            ufr = requests.get(url)
                            f.write(ufr.content)
                            f.close()
                            print(str(index + 1) + '/' + str(playlist_len), "Found:", name, "Real:", real_name, "File:",
                                  write_name, end='\n',
                                  file=f_s)
                        else:
                            print(str(index + 1) + '/' + str(playlist_len), "Found:", name, "Real:", real_name,
                                  end='\n',
                                  file=f_e)

                    else:
                        print(str(index + 1) + '/' + str(playlist_len), "Found:", name, "Real:", real_name, end='\n',
                              file=f_e)
                    time.sleep(random.uniform(0.5, 2.5))
                else:
                    print('EXISTS', str(index + 1) + '/' + str(playlist_len), write_name)
                    print(str(index + 1) + '/' + str(playlist_len), "Found:", name, "Real:", real_name, "File:",
                          write_name,
                          end='\n', file=f_s)
    print("DONE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert txt to MP3')
    parser.add_argument('--path', default='.\\iTunes2VK', type=str, help='Path to save files to')
    parser.add_argument('--login', type=str, help='VK login')
    parser.add_argument('--password', type=str, help='VK password')
    parser.add_argument('--playlist', type=str, help='iTunes playlist txt path')
    arguments = parser.parse_args()

    if arguments.login and arguments.password and arguments.playlist:

        PLAYLIST = arguments.playlist
        ROOT_PATH = arguments.path

        AUDIO_PATH = '\\audio'
        LOGS_PATH = '\\logs'

        AUDIO_PATH = os.path.join(ROOT_PATH, AUDIO_PATH)
        LOGS_PATH = os.path.join(ROOT_PATH, LOGS_PATH)

        if not os.path.exists(ROOT_PATH):
            os.mkdir(ROOT_PATH)

        if not os.path.exists(AUDIO_PATH):
            os.mkdir(AUDIO_PATH)

        if not os.path.exists(LOGS_PATH):
            os.mkdir(LOGS_PATH)

        PATH = os.path.join(AUDIO_PATH, os.path.splitext(os.path.split(PLAYLIST)[-1])[-2])

        if not os.path.exists(PATH):
            os.mkdir(PATH)

        LOGIN = arguments.login
        PASS = arguments.password
        VK = vk_api.VkApi(login=LOGIN, password=PASS, app_id=6121396, auth_handler=TwoFactor)
        VK.auth(token_only=True)
        print("SAVING TO", PATH)
        download(PATH, LOGS_PATH, PLAYLIST, VK)
