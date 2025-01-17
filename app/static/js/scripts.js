// static/js/scripts.js

// Connect to Socket.IO server
const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

// Get DOM elements
const videoFeed = document.getElementById('video-feed');
const captureCanvas = document.getElementById('capture-canvas');
const overlayCanvas = document.getElementById('overlay-canvas');
const tagButton = document.getElementById('tag-button');

// Overlay canvas context
const overlayContext = overlayCanvas.getContext('2d');

// Start logs
console.log("Attempting to access webcam...");

// Request webcam access
navigator.mediaDevices.getUserMedia({ video: true, audio: false })
  .then((stream) => {
    console.log("Webcam access granted.");
    videoFeed.srcObject = stream;
    videoFeed.play().catch(err => console.error("Error in video.play()", err));
  })
  .catch((err) => {
    console.error("Error accessing webcam: ", err);
    alert("Could not access webcam. Please check camera permissions and refresh.");
  });

// Function to capture frames, scale them down, and send to server
function sendFrame() {
  const context = captureCanvas.getContext('2d');
  // Scale down for performance
  captureCanvas.width = videoFeed.videoWidth / 4;
  captureCanvas.height = videoFeed.videoHeight / 4;

  context.drawImage(videoFeed, 0, 0, captureCanvas.width, captureCanvas.height);
  const dataURL = captureCanvas.toDataURL('image/jpeg');
  console.log("Sending frame to server...");
  socket.emit('frame', dataURL);
}

// Capture frames at intervals (Adjust as needed, e.g., 500 ms)
setInterval(sendFrame, 500);

// Receive annotated frame and draw on overlay canvas
socket.on('response_back', (data) => {
  console.log("Received annotated frame from server.");
  const img = new Image();
  img.onload = function() {
    overlayContext.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
    overlayContext.drawImage(img, 0, 0, overlayCanvas.width, overlayCanvas.height);
  };
  img.src = data.image_data;
});

// Handle tagging
tagButton.addEventListener('click', () => {
  const context = captureCanvas.getContext('2d');
  captureCanvas.width = videoFeed.videoWidth;
  captureCanvas.height = videoFeed.videoHeight;
  context.drawImage(videoFeed, 0, 0, captureCanvas.width, captureCanvas.height);

  const dataURL = captureCanvas.toDataURL('image/jpeg');
  const personName = prompt("Enter a name for this face:");

  if (personName) {
    socket.emit('tag', { 'name': personName, 'face_image': dataURL });
    socket.on('tag_response', (resp) => {
      alert(resp.message);
      socket.off('tag_response');
    });
  } else {
    alert("No name entered. Tagging canceled.");
  }
});
