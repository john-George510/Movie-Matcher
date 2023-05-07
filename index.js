const {app, BrowserWindow} =require('electron')

let mainWindow

function createWindow () {
  var subpy = require('child_process').spawn('python', ['project\\manage.py', 'runserver']);
    var rq = require('request-promise');
    var mainAddr = 'http://localhost:8000/';
    var openWindow = function() {
        mainWindow = new BrowserWindow({ width: 800, height: 600 , fullscreen: true})
        mainWindow.loadURL('http://localhost:8000');

        mainWindow.on('closed', function() {
            mainWindow = null;
            subpy.kill('SIGINT');
        })
    }

    var startUp = function() {
        rq(mainAddr)
            .then(function(htmlString) {
                openWindow();
            })
            .catch(function(err) {
                startUp();
            });
    };
    startUp();
}
app.on('ready', createWindow)
