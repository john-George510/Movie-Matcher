import face_recognition,os,cv2,time
from PIL import Image
import numpy as np

start_time=time.time()
actors_dir = 'Actors'
actors=os.listdir(actors_dir)
actor_encodings={}
i=0
for actor in actors:
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

video_capture = cv2.VideoCapture("dune-final-trailer_h480p.mov")
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
        # for actor in actors:
        #     i+=1
        #     print(str(i)+' '+actor)
        #     actor_images=os.listdir('Actors/'+actor)
        #     for image in actor_images:
        #         actor_image=face_recognition.load_image_file('Actors/'+actor+'/'+image)
        #         actor_encoding = face_recognition.face_encodings(actor_image)[0]
        #         results = face_recognition.compare_faces([actor_encoding], unknown_encoding)
        #         # print(results,actor)
        #         if results[0]:
        #             actors_present.append(actor)
        #             print(actor,"is present")
        #             break
        #     else:
        #         continue  # only executed if the inner loop did NOT break
        #     break 
if len(actors_present):
    print("actors present in clip are:",actors_present)