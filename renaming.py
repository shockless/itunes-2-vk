import argparse
import os

import eyed3
from tqdm import tqdm


def rename_tags(directory, errors_path='./errors.txt', encoding='utf-8', formats=['mp3']):
    eyed3.log.setLevel("ERROR")
    formats = set(formats)
    errors_count = 0
    success_count = 0
    dirlist = os.listdir(directory)
    print("TAGGING IN PROCESS")
    for index, filename in tqdm(enumerate(dirlist), total=len(dirlist)):
        f = os.path.join(directory, filename)
        if os.path.isfile(f) and os.path.splitext(f)[-1][1:] in formats:
            name = filename[:-4].split(' - ')
            audiofile = eyed3.load(f)
            if not audiofile.tag:
                audiofile.initTag(encoding=encoding)
                audiofile.tag.save()
                print(audiofile.tag.artist)
            try:
                if audiofile.tag.artist is None and len(name) >= 2:
                    audiofile.tag.artist = name[-2]
                    audiofile.tag.title = name[-1]
                    audiofile.tag.save()
                    success_count+=1
            except:
                with open(errors_path, "a", encoding="utf-8") as f_e:
                    print(str(index + 1),
                          "ERROR TAGGING"
                          "File:", f,
                          end='\n',
                          file=f_e)
                    errors_count += 1
    print(f"TAGGING IS DONE\nsuccess:{success_count} | errors:{errors_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MP3 tagging from filename')
    parser.add_argument('--path', type=str)
    arguments = parser.parse_args()
    rename_tags(arguments.path)
