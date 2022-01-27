def get_spotify_trackname(link, spotify_instance):
    track_info = spotify_instance.track(link)
    return track_info["album"]["artists"][0]["name"] + " " + track_info["album"]["name"]
