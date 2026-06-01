from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Numeric
)
from sqlalchemy.sql import func

from database import Base

class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True)

    name = Column(String(255), nullable=False)

    description = Column(Text)

    country = Column(String(100))

    popularity = Column(Integer)

class ArtistTag(Base):
    __tablename__ = "artist_tags"

    artist_id = Column(
        Integer,
        ForeignKey("artists.id"),
        primary_key=True
    )

    tag = Column(
        String(100),
        primary_key=True
    )

class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)

    artist_id = Column(
        Integer,
        ForeignKey("artists.id"),
        nullable=False
    )

    title = Column(String(255), nullable=False)

    spotify_id = Column(
        String(100),
        unique=True
    )


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id = Column(
        String(255),
        primary_key=True
    )

    artist_id = Column(
        Integer,
        ForeignKey("artists.id"),
        primary_key=True
    )

    score = Column(
        Numeric(5, 2)
    )

class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True)

    query = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )


class PlaylistSong(Base):
    __tablename__ = "playlist_songs"

    playlist_id = Column(
        Integer,
        ForeignKey("playlists.id"),
        primary_key=True
    )

    song_id = Column(
        Integer,
        ForeignKey("songs.id"),
        primary_key=True
    )

    rank = Column(Integer)