https://api.spotify.com/v1/search?q=remaster%2520track%3ADoxy%2520artist%3AMiles%2520Davis&type=track


URL Encoding Legend:
%25	%
%20	space
%3A	:

This converts the example request to the meaning

remaster
track:Doxy
artist:Miles Davis

remaster is a free-text search term
track:Doxy filters for tracks named "Doxy"
artist:Miles Davis filters for the artist Miles Davis

Spotify uses field filters such as artist:, track:, album:, year:, genre:, etc. in the q parameter.