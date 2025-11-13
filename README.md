# Final dregree project of Computer Science
Recommendation system for adding songs to playlists in Spotify.
### Dataset
- Data RecSys Challenge 2018. The goal is given a playlist recommend a new song
- Data used: from the million playlist dataset 1000 playlists where chosen randomly, keeping the ~30000 songs of all these playlists.
- From all these songs, features were obtained from the Spotify API such us liveness, energy or danceability. Also, the genres were obtained in order to make better predictions.
### Model development
- Objective: build a recurrent model taking advantage of the sequential component of playlists.
- First, tried with several libraries as Keras or Tensorflow but due to limited computation resources, switched to RecBole, a especialised library containing precomputed models for recommender systems.
- From this library, the model selected was GRU4Rec, a variation of the classic recurrent neural network GRU for recommender systems.
- In the end, 4 models can be selected:
    - Popularity: for all the playlists recommend the most popular songs.
    - Random: random recommendations.
    - Nearest neighbours: represent each playlist by a mean of the features of all the songs included in the playlist and recommend similar songs to this representation.
    - GRU4Rec: recurrent neural network
### Web application development
- Development of a web application in Django and uploaded to render in the link: https://spotiwhy.onrender.com/spotiwhy/
