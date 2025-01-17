# High Level Archicteture

                            +----------------------+
                            |     Web Browser      |
                            | (Video Stream / UI)  |
                            +----------+-----------+
                                       |
                                       | WebSocket (SocketIO)
                                       v
                          +-------------------------------------+
                          | Flask App (app.py)                  |
                          |  - Real-Time Face Recognition       |
                          |  - YOLOv8 + DeepFace                |
                          |  - SocketIO Event Handlers          |
                          |  - Embedding CRUD Operations (DB)   |
                          +----------------+--------------------+
                                       |
                                       | SQLAlchemy (ORM)
                                       v
                            +-----------------------+
                            |  PostgreSQL Database  |
                            +-----------------------+


## Browser Client

- Captures webcam video, sends frames (via SocketIO) to the server, receives annotated frames, and handles user interactions (tagging, etc.).

## Flask Server

- YOLOv8 for face detection.
- DeepFace for generating embeddings (Facenet or ArcFace).
- SQLAlchemy to store and manage face embeddings and metadata in the PostgreSQL database.
- Flask-SocketIO for real-time, bidirectional communication with the browser.

## PostgreSQL Database

- Stores embeddings, labels, images, and any additional metadata (e.g., date added, user ID).
- Provides ACID compliance, robust indexing, and concurrency control for production readiness.