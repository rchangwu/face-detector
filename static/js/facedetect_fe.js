// from https://stackoverflow.com/questions/105034/create-guid-uuid-in-javascript
function guid() {
    function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
        .toString(16)
        .substring(1);
    }
    return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
}

let clientId = guid();
let video = document.getElementById('webcam-video');  

function startApplication() {
    // Globals
    let canvas = document.createElement('canvas');
    let context = canvas.getContext('2d');
    let infoCanvas = document.getElementById("info-canvas");
    let infoCanvasContext = infoCanvas.getContext("2d");
    let socket = io.connect('http://' + document.domain + ':' + location.port, {upgrade: false, transports: ['websocket']});
    let learnButton = document.getElementById("learn-button");
    var peeps = [];
    var marked_remove = [];
    var ul = document.getElementById("dynamic-list");
    var busy = false;
    var pendingImage = false;
    var reader  = new FileReader();
    
    learnButton.onclick = function() {
        pendingImage = true;
    };

    var index = 0;
    function sendWebcamImage() {
        let dataUrl = getDataUrlFromCanvas(video, canvas, context)
        socket.emit('webcam_image', 
            {
                clientId: clientId, 
                dataUrl: encodeURIComponent(dataUrl.slice(16)),
                index: index++
            });
    }


    function sendCustomImage() {
        var customimage = document.querySelector('input[type=file]').files[0];
        reader.readAsDataURL(customimage);
        reader.addEventListener("load", function () {
            var dataUrl = reader.result;
            socket.emit('custom_image', 
                {
                    clientId: clientId, 
                    dataUrl: encodeURIComponent(dataUrl.slice(16)),
                    index: 0
                });
            pendingImage = false;
        }, false);
        
    }


    function startWebcamFeed() {
        busy = true;
        sendWebcamImage();
    }

    // Open Socket connection
    
    socket.on('connect', function() {
        startWebcamFeed();        
    });


    socket.on('people', function(json) {
        console.log(json);
        infoCanvasContext.clearRect(0, 0, infoCanvas.width, infoCanvas.height);
        infoCanvasContext.beginPath();
        json.people.forEach(function (person) {
            infoCanvasContext.font="12px Verdana";
            infoCanvasContext.strokeStyle="#00FF00";
            infoCanvasContext.fillStyle="#00FF00";
            infoCanvasContext.rect(person.boundingBox.left,person.boundingBox.top, person.boundingBox.right - person.boundingBox.left, person.boundingBox.bottom - person.boundingBox.top);
            infoCanvasContext.fillText(person.name,person.boundingBox.left,person.boundingBox.top - 12);

            if (!peeps.includes(person.name)) {
                var li = document.createElement("li");
                var img = document.createElement('img');
                img.src = person.image;
                li.setAttribute('id', person.name);
                li.appendChild(document.createTextNode(person.name));
                li.appendChild(img);
                ul.appendChild(li);
                li.ondblclick = mark4Removal;
                peeps.push(person.name);
            }

            });
        infoCanvasContext.stroke();
        busy = false;

        marked_remove.forEach(function (subject) {
            removeSubject(subject);
        });
        marked_remove = [];

        if (pendingImage) {
            sendCustomImage();
        }

        busy = true;
        sendWebcamImage();
    });

    socket.on('custom_people', function(json) {
        console.log(json);
        json.people.forEach(function (person) {
            if (!peeps.includes(person.name)) {
                var li = document.createElement("li");
                var img = document.createElement('img');
                img.src = person.image;
                li.setAttribute('id', person.name);
                li.appendChild(document.createTextNode(person.name));
                li.appendChild(img);
                ul.appendChild(li);
                li.ondblclick = mark4Removal;
                peeps.push(person.name);
            }

            });
    });

    function mark4Removal(e) {
        e.target.parentNode.style.display = 'none';
        marked_remove.push(e.target.parentNode);
    }

    function removeSubject(item) {
        peeps = arrayRemove(peeps, item.id);
        socket.emit('delete_subject', {clientId: clientId, subject: item.id});
        item.parentNode.removeChild(item);
    }

    function removeItem(e) {

    }


    function arrayRemove(arr, value) {

        return arr.filter(function(ele){
            return ele != value;
        });

    }


    function getDataUrlFromCanvas(video, canvas, context) {

        //Make sure the canvas is set to the current video size
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);

        //Convert the canvas to blob and post the file
        return canvas.toDataURL('image/jpeg', 1);
    }

    function getDataUrlFromImg(customimage, canvas, context) {

        //Make sure the canvas is set to the current video size
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);

        //Convert the canvas to blob and post the file
        return canvas.toDataURL('image/jpeg', 1);
    }


}



window.onload = function () {
    //Get camera video
    navigator.mediaDevices.getUserMedia({video: {width: 640, height: 480}, audio: false})
        .then(stream => {
            video.srcObject = stream;
            video.onplay = startApplication                
        })
        .catch(err => {
            console.log('navigator.getUserMedia error: ', err)
        });    
};