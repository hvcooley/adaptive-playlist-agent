from database import engine, Base

# Import all models so SQLAlchemy knows about them
from models import (
    Artist,
    ArtistTag,
    Song,
    UserPreference,
    Playlist,
    PlaylistSong
)

Base.metadata.create_all(engine)

print("Tables created!")