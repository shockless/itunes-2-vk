import argparse
import os
import random
import re

import requests

import xmltodict

import pandas as pd
from time import gmtime, strftime, sleep
import vk_api
from tqdm import tqdm

import renaming


def xml(path):
    xml_data = open(path, 'r', encoding="utf-8").read()
    xmlDict = xmltodict.parse(xml_data)['DJ_PLAYLISTS']['COLLECTION']['TRACK']
    df = pd.DataFrame(columns=['Name', 'Artist'])
    for i, track in tqdm(enumerate(xmlDict), total=len(xmlDict), desc="Converting to DF"):
        track['@Name'] = re.sub(r"[^ \-.,&\'()!\[\]\w+]", '', track['@Name'])
        track['@Artist'] = re.sub(r"[^ \-.,&\'()!\[\]\w+]", '', track['@Artist'])
        df.loc[i] = [track['@Name'], track['@Artist']]

    return df


def captcha_handler(captcha):
    key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
    return captcha.try_again(key)


def download(path, logs_path, playlist, vk, source=2):
    errors_path = 'errors'
    success_path = 'success'
    errors_count = 0
    success_count = 0
    if source == 0:
        with open(playlist, encoding='UTF-16') as f:
            df = pd.read_csv(f, sep="\t", header=0)
    elif source == 1:
        df = pd.read_csv(playlist, header=0)
    elif source == 2:
        df = xml(playlist)
    playlist_len = len(df)

    with open(os.path.join(logs_path, errors_path + '.txt'), "a", encoding="utf-8") as f_e:
        with open(os.path.join(logs_path, success_path + '.txt'), "a", encoding="utf-8") as f_s:
            print('\n', strftime("%Y-%m-%d %H:%M:%S", gmtime()), playlist, end='\n', file=f_s)
            print('\n', strftime("%Y-%m-%d %H:%M:%S", gmtime()), playlist, end='\n', file=f_e)
            for index, row in df.iterrows():
                if source == 0:
                    real_name = str(row['Артист'] + ' - ' + row['Название'])
                elif source == 1:
                    real_name = str(row['Artist name'].strip('\"') + ' - ' + row['Track name'])
                elif source == 2:
                    real_name = row['Name']
                    if row['Artist'] != '':
                        real_name = str(row['Artist']) + ' - ' + real_name

                write_name = bytes(real_name, 'utf-8').decode('utf-8', 'ignore')
                write_name = write_name.replace('/', " ").replace('?', " ").replace(':', " ")
                name = 'NONE'
                audio_path = os.path.join(path, write_name + '.mp3')
                if not os.path.exists(audio_path):
                    json = vk.method("audio.search", {"q": real_name, 'count': 5})
                    if json['count'] != 0:
                        audios = "_".join(str(json['items'][0][i]) for i in ("owner_id", "id"))
                        audio_with_url = vk.method("audio.getById", {'audios': audios})
                        url = audio_with_url[0]['url']
                        name = str(audio_with_url[0]['artist'] + ' - ' + audio_with_url[0]['title'])
                        name = bytes(name, 'utf-8').decode('utf-8', 'ignore').replace('/', " ").replace('?', " ")
                        if audio_with_url[0]['url'] != '':
                            f = open(audio_path, "wb")
                            print(str(index + 1) + '/' + str(playlist_len),
                                  name,
                                  'File:', write_name)
                            ufr = requests.get(url)
                            f.write(ufr.content)
                            f.close()
                            print(str(index + 1) + '/' + str(playlist_len),
                                  "Found:", name,
                                  "Real:", real_name,
                                  "File:", write_name,
                                  end='\n',
                                  file=f_s)
                            success_count+=1
                        else:
                            print(str(index + 1) + '/' + str(playlist_len),
                                  "!!! NOT FOUND:", name,
                                  "Real:", real_name,
                                  end='\n',
                                  file=f_e)
                            errors_count+=1
                    else:
                        print(str(index + 1) + '/' + str(playlist_len),
                              "Found:", name,
                              "Real:", real_name,
                              end='\n',
                              file=f_e)
                        errors_count+=1
                    sleep(random.uniform(1, 2.5))
                else:
                    print('EXISTS', str(index + 1) + '/' + str(playlist_len), write_name)
                    print(str(index + 1) + '/' + str(playlist_len),
                          "Found:", name,
                          "Real:", real_name,
                          "File:", write_name,
                          end='\n',
                          file=f_s)
                    success_count+=1
    print(f"DOWNLOADING IS DONE\nsuccess:{success_count} | errors:{errors_count}")
    renaming.rename_tags(path, f_s)
    print("DONE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert txt to MP3')
    parser.add_argument('--path', default='.\\iTunes2VK', type=str, help='Path to save files to')
    parser.add_argument('--token_path', default='', type=str, help='Path to save token to')
    parser.add_argument('--playlist', type=str, help='iTunes playlist txt path')
    parser.add_argument('--mode', type=str, help='it\\spot\\rb', default='it')
    arguments = parser.parse_args()
    modes = {'it': 0,
             'spot': 1,
             'rb': 2}
    if arguments.playlist:

        PLAYLIST = arguments.playlist
        ROOT_PATH = arguments.path
        mode = modes[arguments.mode]
        AUDIO_PATH = '\\audio'
        LOGS_PATH = '\\logs'

        AUDIO_PATH = ROOT_PATH + AUDIO_PATH
        LOGS_PATH = ROOT_PATH + LOGS_PATH

        if not os.path.exists(ROOT_PATH):
            os.mkdir(ROOT_PATH)

        if not os.path.exists(AUDIO_PATH):
            os.mkdir(AUDIO_PATH)

        if not os.path.exists(LOGS_PATH):
            os.mkdir(LOGS_PATH)

        PATH = os.path.join(AUDIO_PATH, os.path.splitext(os.path.split(PLAYLIST)[-1])[-2])

        if not os.path.exists(PATH):
            os.mkdir(PATH)
        token_path = arguments.token_path
        if token_path == '':
            token_path = os.path.join(ROOT_PATH, 'token')

        token = None

        if not os.path.exists(token_path):
            token = input('Paste your access_token, gained from  '
                          '\n https://oauth.vk.com/authorize?client_id=6121396&scope=1&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1: ')
            print("SAVING TOKEN TO", token_path)
            with open(token_path, 'w') as file:
                file.write(token)
        else:
            print("READING TOKEN FROM", token_path)
            with open(token_path, 'r') as file:
                token = file.read()
        if not token:
            raise Exception('No Token')
        session = requests.Session()
        session.headers['User-Agent'] = "VKAndroidApp/4.38-849 (Android 6.0; SDK 23; x86; Google Nexus 5X; ru)"

        vk = vk_api.VkApi(token=token,
                          session=session,
                          captcha_handler=captcha_handler)

        print("SAVING TO", PATH)
        download(PATH, LOGS_PATH, PLAYLIST, vk, source=mode)
