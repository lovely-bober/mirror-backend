import requests


class SpotifyService:
    def __init__(self):
        self.mopidy_url = "http://localhost:6680/mopidy/rpc"
        self.command_list = {
            "play": self.play,
            "stop": self.stop,
            "next": self.next,
            "previous": self.previous,
            "set_volume": self.set_volume,
            "increase_volume": self.increase_volume,
            "decrease_volume": self.decrease_volume
        }
        #set first playlist to tracks
        try:
            response = requests.post(self.mopidy_url, json={"jsonrpc": "2.0", "id": 1, "method": "core.playlists.as_list"})
            response.raise_for_status()
            playlists = response.json().get("result", [])
            if playlists:
                first_playlist_uri = playlists[0]["uri"]
                resp = requests.post(self.mopidy_url, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.add", "params": [first_playlist_uri]})
                print(f"Loaded first playlist: {first_playlist_uri}")
        except requests.RequestException as e:
            print(f"Error initializing SpotifyService: {e}")
            return
        print("Initialized SpotifyService")
        

    def play(self):
        """Starts playback of the current track."""
        try:
            response = requests.post(self.mopidy_url, json={"method": "core.playback.play"})
            response.raise_for_status()
            print("Playback started.")
        except requests.RequestException as e:
            print(f"Error starting playback: {e}")
        
        

    def stop(self):
        """Stops playback of the current track."""
        try:
            response = requests.post(self.mopidy_url, json={"jsonrpc": "2.0", "id": 1,"method": "core.playback.stop"})
            response.raise_for_status()
            print("Playback stopped.")
        except requests.RequestException as e:
            print(f"Error stopping playback: {e}")
    

    def next(self):
        """Skips to the next track."""
        try:
            response = requests.post(self.mopidy_url, json={"jsonrpc": "2.0", "id": 1,"method": "core.playback.next"})
            response.raise_for_status()
            print("Skipped to next track.")
        except requests.RequestException as e:
            print(f"Error skipping to next track: {e}")
    def previous(self):
        """Goes back to the previous track."""
        try:
            response = requests.post(self.mopidy_url, json={"jsonrpc": "2.0", "id": 1,"method": "core.playback.previous"})
            response.raise_for_status()
            print("Went back to previous track.")
        except requests.RequestException as e:
            print(f"Error going back to previous track: {e}")
    
    def set_volume(self, volume: int):
        """Sets the volume to a specified level (0-100)."""
        try:
            if 0 <= volume <= 100:
                response = requests.post(self.mopidy_url, json={"jsonrpc": "2.0", "id": 1,"method": "core.playback.set_volume", "params": [volume]})
                response.raise_for_status()
                print(f"Volume set to {volume}.")
            else:
                print("Volume must be between 0 and 100.")
        except requests.RequestException as e:
            print(f"Error setting volume: {e}")
    
    def increase_volume(self,amount: int):
        """Increases the volume by a specified amount."""
        try:
            response = requests.post(self.mopidy_url, json={"jsonrpc": "2.0", "id": 1,"method": "core.playback.get_volume"})
            response.raise_for_status()
            current_volume = response.json().get("result", 0)
            new_volume = min(current_volume + amount, 100)
            self.set_volume(new_volume)
        except requests.RequestException as e:
            print(f"Error increasing volume: {e}")
        
    def decrease_volume(self, amount: int):
        """Decreases the volume by a specified amount."""
        try:
            response = requests.post(self.mopidy_url, json={"jsonrpc": "2.0", "id": 1,"method": "core.playback.get_volume"})
            response.raise_for_status()
            current_volume = response.json().get("result", 0)
            new_volume = max(current_volume - amount, 0)
            self.set_volume(new_volume)
        except requests.RequestException as e:
            print(f"Error decreasing volume: {e}")
        
    