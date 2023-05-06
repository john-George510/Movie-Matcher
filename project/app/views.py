from django.shortcuts import render
import face_recognition,os,cv2,time,requests
from PIL import Image
import numpy as np

api_key = "95fd2f005505fb691f27cb9d308ede9f"
base_url = "https://api.themoviedb.org/3"

# Create your views here.
def home(request):
    return render(request,'home.html')

def result(request):
    if request.method == 'POST':
        print(request.POST)
        video_file=str(request.FILES['file'])
        # actors=actor_detect(video_file)
        movie=movie_search(['Zendaya Coleman','Timothee chalamet'])
        details=movie_details(movie)
        return render(request,'result.html',{'movie':movie,'release_date':details['release_date'],'Overview':details['overview'],'Rating':details['vote_average'],'genres':details['genres'],'poster':details['poster_url']})

def actor_detect(video_file):
    start_time=time.time()
    actors_dir = 'Actors'
    actors=os.listdir(actors_dir)
    actor_encodings={}
    i=0
    type(actors)
    for actor in actors[3:43]:
        i+=1
        print(i,actor,'encoding',time.time()-start_time)
        actor_images = os.listdir(os.path.join(actors_dir, actor))
        actor_encoding = []
        print(actor_images)
        for image in actor_images:
            print(image)
            actor_image = face_recognition.load_image_file(os.path.join(actors_dir, actor, image))
            actor_encoding.append(face_recognition.face_encodings(actor_image)[0])
        actor_encodings[actor] = actor_encoding

    video_capture = cv2.VideoCapture(video_file)
    fps = round(video_capture.get(cv2.CAP_PROP_FPS))
    frame_interval = 10
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
            for actor in actor_encodings:
                actor_encoding=actor_encodings[actor]
                for image in actor_encoding:
                    results=face_recognition.compare_faces([image],unknown_encoding)
                    if results[0]:
                        actors_present.append(actor)
                        print(actor,"is present")
                        break
                else:
                    continue
                break
    print(actors_present)
    return actors_present
    if len(actors_present):
        print("actors present in clip are:",actors_present)

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
    
    # Define the search query parameters
    query_params = {
        "api_key": api_key,
        "query": str(movie),
        "language": "en-US",
        "page": 1
    }

    # Get movie title input from user
    response = requests.get('https://api.themoviedb.org/3' + search_endpoint, params=query_params)

    json_data = response.json()

    # Check if movie was found
    if json_data['total_results'] == 0:
        print('Movie not found.')
    else:
        # Get first movie details
        movie = json_data['results'][0]
        url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            genres = {}
            for genre in response.json()['genres']:
                genres[genre['id']] = genre['name']
        # Print movie details
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

