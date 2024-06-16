from django.shortcuts import render
from .models import Playlist, Song, PlaylistSong, SongFeatures, SongGenre
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yaml
import pandas as pd
import random

# Create your views here.
def home(request):
    if request.GET.get('search') is not None:
        search = request.GET.get('search')
        playlists = Playlist.objects.filter(name__icontains=search)
    else:
        playlists = Playlist.objects.all()
    return render(request, 'home.html', {'playlists': playlists})


def PlaylistDetailView(request, pk):
    # Obtenemos la playlist
    playlist = Playlist.objects.get(pk=pk)

    # Obtenemos las canciones de la playlist
    songs = PlaylistSong.objects.filter(playlist=playlist).order_by('position')
    songs = [song.song for song in songs]

    # Obtenemos las features de las canciones de la playlist ordenadas por la posición en la playlist
    response = []
    claves = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'valence', 'tempo']
    # Creamos el diccionario de features de la playlist
    features = []
    genre_frec = dict()
    for song in songs:
        sf = SongFeatures.objects.get(song=song)
        sg = SongGenre.objects.filter(song=song)
        for g in sg:
            if g.genre.name in genre_frec:
                genre_frec[g.genre.name] += 1
            else:
                genre_frec[g.genre.name] = 1
        response.append(sf)
        features.append([sf.danceability, sf.energy, sf.key, sf.loudness, sf.mode, sf.speechiness, sf.acousticness, sf.instrumentalness, sf.valence, sf.tempo])
    
    last_song = songs[-1]

    # Obtenemos los 5 géneros más frecuentes (solo el nombre)
    genres = list(genre_frec.keys())
    genres = sorted(genres, key=lambda x: genre_frec[x], reverse=True)[:5]

    # Sumamos las features de las canciones de la playlist
    features = pd.DataFrame(features)
    features = features.sum()
    # Dividimos entre el número de canciones para obtener la media
    features = features / len(songs)
    features_dict = {}
    f = dict()
    for i in range(len(features)):
        if claves[i] == 'danceability':
            f[claves[i]] = '<b>Danceability</b> indica qué tan adecuada es la playlist para bailar.<br>'
            if features[i] < 0.25:
                f[claves[i]] += 'Parece que esta playlist no es para bailar.'
            elif features[i] < 0.5:
                f[claves[i]] += 'Parece que se puede bailar un poco con esta playlist.'
            elif features[i] < 0.75:
                f[claves[i]] += 'Parece que es una buena playlist para bailar.'
            else:
                f[claves[i]] += 'Parece que es la playlist perfecta para bailar.'
        if claves[i] == 'acousticness':
            f[claves[i]] = '<b>Acousticness</b> indica cuán acústica es la playlist.<br>'
            if features[i] < 0.25:
                f[claves[i]] += 'Parece que la playlist no es casi acústica.'
            elif features[i] < 0.5:
                f[claves[i]] += 'Parece que la playlist es un poco acústica.'
            elif features[i] < 0.75:
                f[claves[i]] += 'Parece que la playlist es bastante acústica.'
            else:
                f[claves[i]] += 'Parece que la playlist es muy acústica.'
        if claves[i] == 'energy':
            f[claves[i]] = '<b>Energy</b> indica cuán intensa y enérgica es la playlist.<br>'
            if features[i] < 0.25:
                f[claves[i]] += 'Parece que la playlist es muy tranquila.'
            elif features[i] < 0.5:
                f[claves[i]] += 'Parece que la playlist es tranquila.'
            elif features[i] < 0.75:
                f[claves[i]] += 'Parece que la playlist es enérgica.'
            else:
                f[claves[i]] += 'Parece que la playlist es muy enérgica.'
        if claves[i] == 'tempo':
            f[claves[i]] = '<b>Tempo</b> indica el ritmo medio de la playlist.<br>'
            if features[i] < 0.25:
                f[claves[i]] += 'Parece que la playlist es muy lenta.'
            elif features[i] < 0.5:
                f[claves[i]] += 'Parece que la playlist es lenta.'
            elif features[i] < 0.75:
                f[claves[i]] += 'Parece que la playlist es rápida.'
            else:
                f[claves[i]] += 'Parece que la playlist es muy rápida.'
        if claves[i] == 'valence':
            f[claves[i]] = '<b>Valence</b> indica qué cuán positiva es la playlist.<br>'
            if features[i] < 0.25:
                f[claves[i]] += 'Parece que la playlist es muy negativa.'
            elif features[i] < 0.5:
                f[claves[i]] += 'Parece que la playlist es negativa.'
            elif features[i] < 0.75:
                f[claves[i]] += 'Parece que la playlist es positiva.'
            else:
                f[claves[i]] += 'Parece que la playlist es muy positiva.'
        if claves[i] == 'instrumentalness':
            f[claves[i]] = '<b>Instrumentalness</b> indica cuán instrumental es la playlist.<br>'
            if features[i] < 0.25:
                f[claves[i]] += 'Parece que la playlist es muy poco instrumental.'
            elif features[i] < 0.5:
                f[claves[i]] += 'Parece que la playlist es un poco instrumental.'
            elif features[i] < 0.75:
                f[claves[i]] += 'Parece que la playlist es bastante instrumental.'
            else:
                f[claves[i]] += 'Parece que la playlist es muy instrumental.'
        features_dict[claves[i]] = features[i]

    return render(request, 'playlist.html',
                  {'playlist': playlist, 'audio_features': response, 'last_song': last_song, 'mean_feat': features_dict, 'genres': genres, 'explanation': f})


def recommend(request, pk):
    # Obtenemos la playlist de la que queremos recomendar
    playlist = Playlist.objects.get(pk=pk)    

    if request.POST.get('model') is not None:
        model = request.POST.get('model')
    
    if model == 'knn':
        # Obtenemos las 25 canciones recomendadas
        preds = pd.read_csv('app/static/models/predictions_knn.tsv', sep='\t', header=None)
        preds = preds[preds[0] == pk][1].to_list()[:25]
        # Obtenemos las canciones de la base de datos que coinciden con las recomendadas
        recs = Song.objects.filter(external_id__in=preds)

    elif model == 'gru4rec':
         # Obtenemos las 25 canciones recomendadas
        preds = pd.read_csv('app/static/models/predictions_gru.tsv', sep='\t', header=None)
        preds = preds[preds[0] == pk][1].to_list()[:25]
        # Obtenemos las canciones de la base de datos que coinciden con las recomendadas
        recs = Song.objects.filter(external_id__in=preds)

    elif model == 'Pop':
        # Obtenemos las 25 canciones recomendadas
        preds = pd.read_csv('app/static/models/predictions_pop.tsv', sep='\t', header=None)
        preds = preds[preds[0] == pk][1].to_list()[:25]
        # Obtenemos las canciones de la base de datos que coinciden con las recomendadas
        recs = Song.objects.filter(external_id__in=preds)
    
    else:
        # Obtenemos las 25 canciones recomendadas
        total_songs = Song.objects.all().count()
        random_ids = random.sample(range(1, total_songs+1), 25)
        recs = Song.objects.filter(id__in=random_ids)

    # Obtenemos las canciones de la playlist
    songs = PlaylistSong.objects.filter(playlist=playlist).order_by('position')
    songs = [song.song for song in songs]

    genre_frec = dict()
    for song in songs:
        sg = SongGenre.objects.filter(song=song)
        for g in sg:
            if g.genre.name in genre_frec:
                genre_frec[g.genre.name] += 1
            else:
                genre_frec[g.genre.name] = 1

    # Obtenemos los 5 géneros más frecuentes (solo el nombre)
    genres = list(genre_frec.keys())
    genres = sorted(genres, key=lambda x: genre_frec[x], reverse=True)
    
    # Obtenemos las audio features de las recomendaciones
    recs_info = []
    for rec in recs:
        sf = SongFeatures.objects.get(song=rec)
        temp = {}
        temp['id'] = sf.song.external_id
        valores = dict()
        valores['danceability'] = sf.danceability
        valores['energy'] = sf.energy
        valores['acousticness'] = sf.acousticness
        valores['instrumentalness'] = sf.instrumentalness
        valores['tempo'] = sf.tempo
        valores['valence'] = sf.valence
        temp['valores'] = valores
        # Obtener géneros
        genres_rec = SongGenre.objects.filter(song=rec)
        # Obtenemos la lista con los nombres de los géneros
        genres_rec = [g.genre.name for g in genres_rec]
        # Obtenemos los 5 primeros géneros que coinciden con la playlist
        genres_rec = [g for g in genres if g in genres_rec]
        temp['genres'] = genres_rec[:5]
        recs_info.append(temp)

    # Obtenemos las features de las canciones de la playlist ordenadas por la posición en la playlist
    response = []
    claves = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'valence', 'tempo']
    # Creamos el diccionario de features de la playlist
    features = []
    for song in songs:
        sf = SongFeatures.objects.get(song=song)
        response.append(sf)
        features.append([sf.danceability, sf.energy, sf.key, sf.loudness, sf.mode, sf.speechiness, sf.acousticness, sf.instrumentalness, sf.valence, sf.tempo])

    # Sumamos las features de las canciones de la playlist
    features = pd.DataFrame(features)
    features = features.sum()
    # Dividimos entre el número de canciones para obtener la media
    features = features / len(songs)
    features_dict = {}
    for i in range(len(features)):
        features_dict[claves[i]] = features[i]

    return render(request, 'recommend.html', {'mean_feat': features_dict, 'recs': recs_info, 'playlist': playlist})
