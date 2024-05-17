import click
import pandas as pd
from tqdm.auto import tqdm
from yandex_music import Client


def get_id(result, stype):
    if result[stype] is None:
        if stype in result['best']['result']:
            id_obj = result['best']['result'][stype]
        else:
            return None
    else:
        id_obj = result[stype]['results']

    if len(id_obj) > 0 and 'id' in id_obj[0]:
        return id_obj[0]['id']
    else:
        return None


type2dict = {'Album': 'albums',
             'Artist': 'artists',
             'Favorite': 'tracks',
             'Playlist': 'playlists'}


@click.command()
@click.option('--api_key', prompt='API Key',
              help='Yandex Music API Key')
@click.option('--library', prompt='CSV Path',
              help='Path to library csv')
def main(api_key, library):
    client = Client(api_key).init()
    library_df = pd.read_csv(library)

    user_playlists = client.users_playlists_list()
    playlists = {playlist.title: playlist.kind for playlist in user_playlists}

    for ind, row in tqdm(library_df.iterrows(), total=len(library_df)):
        name, artist, album, playlist, stype, _ = row
        if pd.isna(artist) and stype != 'Artist':
            continue
        elif stype == 'Artist':
            search_query = ' - '.join([name])
        else:
            search_query = ' - '.join([artist, name])

        result = client.search(search_query).to_dict()
        if result['best'] is None:
            print(search_query, 'not found')
            continue

        stype = type2dict[stype]
        if stype == 'playlists':
            result_id = get_id(result, 'tracks')
        else:
            result_id = get_id(result, stype)

        if result_id is None:
            print(search_query, 'not found')
            continue

        if stype == 'playlists':
            if playlist not in playlists:
                playlist_obj = client.users_playlists_create(playlist)
                playlists[playlist] = playlist_obj.kind
            album_id = client.tracks(result_id)[0]['albums'][0]['id']
            revision = client.users_playlists(playlists[playlist]).revision
            client.users_playlists_insert_track(kind=playlists[playlist],
                                                track_id=result_id,
                                                album_id=album_id,
                                                revision=revision)
        else:
            eval(f'client.users_likes_{stype}_add')(result_id)


if __name__ == '__main__':
    main()
