from django.db import models

class Song(models.Model):
    external_id = models.CharField(max_length=1000)  # ID externo como un String
    uri_spotify = models.CharField(max_length=1000)  # URI a la API de Spotify
    name = models.CharField(max_length=1000, blank=True)
    artist = models.CharField(max_length=1000, blank=True)
    album = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return self.name
    
    
class Genre(models.Model):
    name = models.CharField(max_length=1000)

    def __str__(self):
        return self.name
    
    
class SongGenre(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.song.name} - {self.genre.name}"
    

class SongFeatures(models.Model):
    song = models.OneToOneField(Song, on_delete=models.CASCADE)
    danceability = models.FloatField()
    energy = models.FloatField()
    key = models.IntegerField()
    liveness = models.FloatField()
    loudness = models.FloatField()
    mode = models.IntegerField()
    speechiness = models.FloatField()
    acousticness = models.FloatField()
    instrumentalness = models.FloatField()
    valence = models.FloatField()
    tempo = models.FloatField()
    time_signature = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.song.name} features"
     

class Playlist(models.Model):
    name = models.CharField(max_length=1000)
    n_Songs = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    
    # Relación ManyToMany con Song, a través de una tabla intermedia PlaylistSong
    songs = models.ManyToManyField(Song, through='PlaylistSong')

    def __str__(self):
        return self.name

class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    class Meta:
        unique_together = ('playlist', 'song', 'position')  # Cada canción solo puede estar una vez en una playlist

    def __str__(self):
        return f"{self.playlist.name} - {self.song.name}"
