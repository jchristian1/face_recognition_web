# run.py
from app import create_app

# Create the Flask app and SocketIO instance using the factory
app, socketio = create_app()

@socketio.on('frame')
def on_frame(data):
    # Import the handle_frame function locally to avoid circular imports
    from app.sockets import handle_frame
    annotated = handle_frame(data)
    if annotated:
        socketio.emit('response_back', {'image_data': annotated})

@socketio.on('tag')
def on_tag(data):
    from app.sockets import handle_tag
    result = handle_tag(data)
    socketio.emit('tag_response', result)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
