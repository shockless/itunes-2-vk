# iTunes via VK playlist downloader

## Run downloader
```bash
pip install -r requirements.txt
python itunes2vk.py  --playlist PATH\TO\Playlist.txt --mode it
```
- ```--mode it\spot\rb are respectively Itunes\Spotify (via external services)\RekordBox xml files```

### Optional arguments:
- ```--path PATH\TO\SAVE\ (default: .\iTunes2VK\)```

### Audiofiles save to PATH\TO\SAVE\audio\Playlist\
- 'PATH\TO\SAVE\' is your --path folder 
- 'Playlist' is your playlist's name
### Logs save to PATH\TO\SAVE\logs\
