![Electron Notion](https://user-images.githubusercontent.com/64391274/235363274-375ce61c-721f-4543-a150-1b99525d54ac.png)


# Movie Matcher
Movie Matcher is a project that takes in a video clip and uses facial recognition technology to determine the movie it's from. The project uses Django as a backend and ElectronJS as a frontend. The facial recognition model is built using the dlib and OpenCV libraries.
## Team members
[John George Chelamattom](https://github.com/john-George510)  
[Adwaith H R](https://github.com/adwaithhr)
## Link to product walkthrough
[link to video]
## How it Works ?
The user uploads a video clip to the Movie Matcher website. The website then uses the facial recognition model to analyze the clip and compare it to a database of known movies. The website returns the name of the movie if it's a match, or informs the user that the clip couldn't be matched.
## Libraries used
Django - 4.2.1
ElectronJS - 15.0.0
dlib - 19.24.1
OpenCV - 4.5.4
## How to configure
Clone the repository: git clone https://github.com/john-George510/Movie-Matcher.git
Create and activate a virtual environment: python -m venv env and source env/bin/activate
Install the required packages: pip install -r requirements.txt
Install ElectronJS: npm install electron
## How to Run
Start the Django server: python manage.py runserver
Start the ElectronJS app: npm start
Upload a video clip to the website and wait for the movie to be matched.