from django.shortcuts import render
import face_recognition,os,cv2,time,requests,tempfile
from PIL import Image
import numpy as np
from .models import Actor

api_key = "95fd2f005505fb691f27cb9d308ede9f"
base_url = "https://api.themoviedb.org/3"

# Create your views here.
def home(request):
    return render(request,'home.html')

def result(request):
    if request.method == 'POST':
        print(request.POST)
        with tempfile.NamedTemporaryFile(suffix='.mp4') as temp_video:
            for chunk in request.FILES['file'].chunks():
                temp_video.write(chunk)
            actors=actor_detect(temp_video.name)
        movie=movie_search(actors)
        details=movie_details(movie)
        return render(request,'result.html',{'movie':movie,'release_date':details['release_date'],'Overview':details['overview'],'Rating':details['vote_average'],'genres':details['genres'],'poster':details['poster_url']})

def actor_detect(video_file):
    video_capture = cv2.VideoCapture(video_file)
    fps = round(video_capture.get(cv2.CAP_PROP_FPS))
    frame_interval = 5
    frame_count = 0
    print('videocaptured')
    actors_present=[]
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        frame_count += 1
        if frame_count % (frame_interval*fps) != 0:
            continue
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(frame_rgb)
        print("face_locations",face_locations,"\t\tclip time",frame_count/fps)
        for face_location in face_locations:
            top, right, bottom, left = face_location
            face_image = Image.fromarray(frame_rgb[top:bottom, left:right])
            face_array = np.array(face_image)
            face_encodings = face_recognition.face_encodings(face_array)
            if len(face_encodings) > 0:
                unknown_encoding = face_encodings[0]
            else:
                print("No faces detected in the image.")
                continue
            i=0
            for image in Actor.objects.all():
                encoding=image.encoding
                results=face_recognition.compare_faces([encoding],unknown_encoding,tolerance=0.55)
                distance=face_recognition.face_distance([encoding],unknown_encoding)
                if results[0]:
                    print(results)
                    actors_present.append(image.name)
                    print(image.name,"is present with a confidence of",1-distance)
                    break
    print(actors_present)
    return actors_present

def movie_search(actors):
    
    movie_credits = {}

    for actor in actors:
        search_endpoint = "/search/person"
        query_params = {
            "api_key": api_key,
            "query": actor,
            "language": "en-US",
            "page": 1
        }
        response = requests.get(base_url + search_endpoint, params=query_params)
        results = response.json()["results"]
        person_id = results[0]["id"]
        credit_endpoint = f"/person/{person_id}/movie_credits"
        credit_params = {
            "api_key": api_key,
            "language": "en-US"
        }
        credit_response = requests.get(base_url + credit_endpoint, params=credit_params)
        movie_credits[actor] = set([movie["title"] for movie in credit_response.json()["cast"]])
    common_movies = set.intersection(*movie_credits.values())
    movies=[]
    for movie in common_movies:
        movies.append(movie)
    print(movies)
    return movies[0]

def movie_details(movie):
    search_endpoint = "/search/movie"
    query_params = {
        "api_key": api_key,
        "query": str(movie),
        "language": "en-US",
        "page": 1
    }
    response = requests.get('https://api.themoviedb.org/3' + search_endpoint, params=query_params)

    json_data = response.json()
    if json_data['total_results'] == 0:
        print('Movie not found.')
    else:
        movie = json_data['results'][0]
        url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            genres = {}
            for genre in response.json()['genres']:
                genres[genre['id']] = genre['name']
        print('Title:', movie['title'])
        print('Release date:', movie['release_date'])
        print('Overview:', movie['overview'])
        print('Rating:', movie['vote_average'])
        print('Genres:', ', '.join([genres[genre_id] for genre_id in movie['genre_ids']]))
        print('Poster URL:', movie['poster_path'])
        base_url = 'https://image.tmdb.org/t/p/'
        poster_size = 'w500'
        movie['genres']=', '.join([genres[genre_id] for genre_id in movie['genre_ids']])
        poster_url= f"{base_url}{poster_size}{movie['poster_path']}"
        movie['poster_url']=poster_url
    return movie


# # code to add new actors to database

# actor_names=[]
# actors=Actor.objects.all()
# for actor in actors:
#      if actor.name not in actor_names:
#              actor_names.append(actor.name)

# actors_dir = 'Actors'
# actors=os.listdir(actors_dir)
# for actor in actors:
#     actor_images = os.listdir(os.path.join(actors_dir, actor))
#     if actor not in actor_names:
#         for image in actor_images:
#             actor_names.append(actor)
#             print(actor,image,"is encoding")
#             actor_image = face_recognition.load_image_file(os.path.join(actors_dir, actor, image))
#             try:
#                 encoding = face_recognition.face_encodings(actor_image)[0]
#             except IndexError:
#                 print("No face found in the image")
#             new_actor = Actor.objects.create(name=actor, encoding=encoding)
#             new_actor.save()        
#     else:
#         print("in else")
        
