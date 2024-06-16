# Populate database
# This file has to be placed within the
# catalog/management/commands directory in your project.
# If that directory doesn't exist, create it.
# The name of the script is the name of the custom command,
# that is, populate.py.
#
# execute python manage.py  populate
#
# use module Faker generator to generate data
# (https://zetcode.com/python/faker/)
import os
import pandas as pd

from django.core.management.base import BaseCommand
from app.models import Playlist, Song, PlaylistSong, SongFeatures, Genre, SongGenre


# The name of this class is not optional must be Command
# otherwise manage.py will not process it properly
class Command(BaseCommand):
    # helps and arguments shown when command python manage.py help populate
    # is executed.
    help = """populate spotiwhy database
           """
    # if you want to pass an argument to the function
    # uncomment this line
    # def add_arguments(self, parser):
    #    parser.add_argument('publicId',
    #        type=int,
    #        help='game the participants will join to')
    #    parser.add_argument('sleep',
    #        type=float,
    #        default=2.,
    #        help='wait this seconds until inserting next participant')

    def __init__(self, sneaky=True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print('Loading data')

        df_pl = pd.read_csv('C:\\Users\\alber\\Desktop\\tfg info\\SpotiWhy\\limpio\\data\\playlists.csv')
        df_songs = pd.read_csv('C:\\Users\\alber\\Desktop\\tfg info\\SpotiWhy\\limpio\\data\\songs.csv')
        df_ps = pd.read_csv('C:\\Users\\alber\\Desktop\\tfg info\\SpotiWhy\\limpio\\data\\playlistSong.csv', sep='\t')

        df_pl = df_pl[['id', 'name', 'num_tracks', 'description']]

        self.playlists = df_pl.to_dict('records')
        self.songs = df_songs.to_dict('records')
        self.playlistSongs = df_ps.to_dict('records')
        

    def cleanDataBase(self):
        # delete all models stored (clean table)
        # in database
        # order in which data is deleted is important
        # your code goes here...
        print("clean Database")
        Song.objects.all().delete()
        Playlist.objects.all().delete()
        Genre.objects.all().delete()

    # handle is another compulsory name, do not change it"
    # handle function will be executed by 'manage populate'
    def handle(self, *args, **kwargs):
        "this function will be executed by default"

        self.cleanDataBase()  # clean database
        self.song()  # create songs
        self.playlist()  # crea playlists
        self.playlistSong()
        self.features()  # create features
        self.genre()
        self.songGenre()


    def playlist(self):
        " Insert playlisst"
        # create user
        print("Playlists")
        # your code goes here
        for pl in self.playlists:
            if pd.isnull(pl["description"]):
                p = Playlist.objects.create(
                id=pl["id"],
                name=pl["name"],
                n_Songs=pl["num_tracks"],
            )
            else:
                p = Playlist.objects.create(
                    id=pl["id"],
                    name=pl["name"],
                    n_Songs=pl["num_tracks"],
                    description=pl["description"],
                )
            p.save()

    def song(self):
        "insert songs"
        print("Songs")
        # your code goes here
        for s in self.songs:
            s = Song.objects.create(
                external_id=s["id"],
                uri_spotify=s["uri"],
                name=s["name"],
                artist=" ".join(s["artists"]),
                album=s["album"]
            )
            s.save()
    
    def playlistSong(self):
        "insert playlistSong"
        print("PlaylistSong")
        # your code goes here
        for ps in self.playlistSongs:
            p = Playlist.objects.get(id=ps["playlist_id"])
            s = Song.objects.get(external_id=ps["song_id"])
            if PlaylistSong.objects.filter(playlist=p, song=s).exists():
                p.n_Songs -= 1
                p.save()
            else:
                ps = PlaylistSong.objects.create(
                    playlist=p,
                    song=s,
                    position=ps["position"]
                )
                ps.save()

    def features(self):
        "insert features"
        print("Features")
        # your code goes here
        for s in self.songs:
            song = Song.objects.get(external_id=s["id"])
            sf = SongFeatures.objects.create(
                song=song,
                danceability=s["danceability"],
                energy=s["energy"],
                # Hay 12 columnas key_i para i=0,1,2,...,11 en el dataset queremos guardar aquella que tiene el valor 1
                key=[k for k in s.keys() if 'key_' in k and s[k] == True][0][4:],
                liveness=s["liveness"],
                loudness=s["loudness"],
                # Hay 2 columnas mode_i para i=0,1 en el dataset queremos guardar aquella que tiene el valor 1
                mode=[m for m in s.keys() if 'mode_' in m and s[m] == True][0][5:],
                speechiness=s["speechiness"],
                acousticness=s["acousticness"],
                instrumentalness=s["instrumentalness"],
                valence=s["valence"],
                tempo=s["tempo"],
                # Hay 6 columnas mode_i para i=0,...,5 en el dataset queremos guardar aquella que tiene el valor 1
                time_signature=[m for m in s.keys() if 'time_signature_' in m and s[m] == True][0][15:],
            )
            sf.save()
    
    def genre(self):
        "insert genre"
        print("Genre")
        # your code goes here
        generos = [genre[6:] for genre in self.songs[0].keys() if genre.startswith("genre_")]
        for g in generos:
            genre = Genre.objects.create(
                name=g
            )
            genre.save()
    
    def songGenre(self):
        "insert songGenre"
        print("SongGenre")
        # your code goes here
        for s in self.songs:
            song = Song.objects.get(external_id=s["id"])
            generos = [genre.split('_')[1] for genre in s.keys() if genre.startswith("genre_") and s[genre] > 0]
            for g in generos:
                genre = Genre.objects.get(name=g)
                sg = SongGenre.objects.create(
                    song=song,
                    genre=genre
                )
                sg.save()