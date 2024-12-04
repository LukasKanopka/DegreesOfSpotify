import time
import datetime
import  requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv
import os
from dotenv import load_dotenv

# Import Tkinter
from tkinter import *

load_dotenv()

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(
    client_id = os.getenv("CLIENT_ID"),
    client_secret = os.getenv("CLIENT_SECRET")
)
sp = spotipy.Spotify(
    client_credentials_manager=client_credentials_manager,
    requests_timeout=10  # 10-second timeout for all requests
)

CSV_FILE = "adjacency_list.csv"


def safe_request(func, *args, **kwargs):
    """
    Executes a Spotify API request with retry logic, handling rate limits.

    Tracks request timing and logs when requests are delayed due to hitting the rate limit.
    Args:
        func: The Spotipy function to call.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.

    Returns:
        The result of the Spotipy API call.

    Raises:
        Exception: If all retries fail or rate-limiting persists.
    """
    max_retries = 3
    delay = 10  # Fixed delay in seconds between retries

    for attempt in range(max_retries):
        try:
            # Log the request time
            print(f"Sending request...", flush=True)
            time.sleep(0.333)  # Rate limit: 3 requests per second

            # Execute the function
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in request: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...", flush=True)
                time.sleep(delay)
            else:
                print("Maximum retries reached. Request failed.")
                raise


def read_adjacency_list():
    """
    Reads the adjacency list from the CSV file.

    Returns:
        dict: Adjacency list mapping artist URLs to related artist URLs.
    """
    if not os.path.exists(CSV_FILE):
        return {}

    adjacency_list = {}
    with open(CSV_FILE, mode="r") as file:
        reader = csv.reader(file)
        for row in reader:
            artist_url = row[0]
            related_urls = row[1:]
            adjacency_list[artist_url] = related_urls
    return adjacency_list

def write_adjacency_list(adjacency_list):
    """
    Writes the adjacency list to the CSV file.

    Args:
        adjacency_list (dict): Adjacency list mapping artist URLs to related artist URLs.
    """
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        for artist_url, related_urls in adjacency_list.items():
            writer.writerow([artist_url] + related_urls)

def get_artist_url(artist_name):
    """
    Gets the Spotify URL for an artist by name.

    Args:
        artist_name (str): The name of the artist.

    Returns:
        str: Spotify URL for the artist or None if not found.
    """
    result = safe_request(sp.search, q=artist_name, type="artist", limit=1)
    if not result["artists"]["items"]:
        print("No artist with this name exists...")
        return None
    return result["artists"]["items"][0]["external_urls"]["spotify"]

def get_artist_name(artist_url):
    """
    Retrieves the artist's name from their Spotify URL.

    Args:
        artist_url (str): Spotify URL of the artist.

    Returns:
        str: Name of the artist, or None if the artist is not found.
    """
    try:
        artist_id = artist_url.split("/")[-1]
        result = safe_request(sp.artist, artist_id)
        return result["name"] if result else None
    except Exception as e:
        print(f"Error fetching artist name: {e}")
        return None



def make_bidirectional_connections(adjacency_list, artist_url, related_urls):
    """
    Ensures that all connections in the adjacency list are bidirectional.

    Args:
        adjacency_list (dict): Current adjacency list.
        artist_url (str): URL of the artist whose connections are being updated.
        related_urls (list): List of related artist URLs to be added bidirectionally.

    Returns:
        dict: Updated adjacency list with bidirectional connections.
    """
    for related_url in related_urls:
        if related_url not in adjacency_list:
            adjacency_list[related_url] = []
        if artist_url not in adjacency_list[related_url]:
            print(f"Adding reverse connection: {related_url} -> {artist_url}", flush=True)
            adjacency_list[related_url].append(artist_url)
    return adjacency_list

def find_related_artists(artist_url):
    """
    Finds all artists that have a feature with the given artist.
    Ensures bidirectional connections are maintained.

    Args:
        artist_url (str): Spotify URL of the artist.

    Returns:
        list: Related artist URLs.
    """
    adjacency_list = read_adjacency_list()

    if artist_url in adjacency_list:
        return adjacency_list[artist_url]

    artist_id = artist_url.split("/")[-1]
    featured_urls = set()

    albums = safe_request(sp.artist_albums, artist_id, album_type="album,single", country="US")
    for album in albums["items"]:
        tracks = safe_request(sp.album_tracks, album["id"])
        for track in tracks["items"]:
            for artist in track["artists"]:
                if artist["id"] != artist_id:
                    featured_urls.add(artist["external_urls"]["spotify"])

    adjacency_list[artist_url] = list(featured_urls)

    # Make connections bidirectional
    adjacency_list = make_bidirectional_connections(adjacency_list, artist_url, list(featured_urls))

    write_adjacency_list(adjacency_list)

    return list(featured_urls)

def breadth_first(starting_url, ending_url):
    """
    Uses BFS to find the shortest path between two artists.

    Args:
        starting_url (str): Spotify URL of the starting artist.
        ending_url (str): Spotify URL of the ending artist.

    Returns:
        list: Path of artist URLs from start to end, or None if no connection.
    """
    url_counter = 0
    queue = [(starting_url, [starting_url])]
    visited = set()


    while queue:
        current_url, path = queue.pop(0)

        url_counter += 1

        print(current_url)

        if current_url == ending_url:
            return [len(path) - 1] + path

        if current_url not in visited:
            visited.add(current_url)
            neighbors = find_related_artists(current_url)

            # Check if ending_url is in neighbors
            if ending_url in neighbors:
                return [len(path)] + [str(url_counter)] + path + [ending_url]

            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))

    return None
def depth_first(starting_url, ending_url):
    """
    Uses DFS to find any path between two artists

    Args:
        starting_url (str): Spotify URL of the starting artist.
        ending_url (str): Spotify URL of the ending artist.

    Returns:
        list: Path of artist URLs from start to end, or None if no connection.
    """
    url_counter = 0
    def dfs_recursive(current_url, visited, path):
        """
        Inner recursive function for DFS

        Args:
            current_url (str): Spotify URL of the current artist being visited.
            visited (set): Set of visited artists URLs.
            path (list): Path of artist URLs currently being explored.

        Returns:
            list: Path of artist URLs from start to end, or None if no connection.
        """
        nonlocal url_counter
        url_counter += 1
        visited.add(current_url)
        path.append(current_url)
        # if current audience is target audience, return path.
        if current_url == ending_url:
            return path
        # get related artists
        neighbors = find_related_artists(current_url)
        for neighbor in neighbors:
            if neighbor not in visited:
                result = dfs_recursive(neighbor, visited, path)
                if result:
                    return result
        # if no path found from current artist
        path.pop()
        return None
    # initialize visited set and path list
    visited = set()
    path = []
    result = dfs_recursive(starting_url, visited, path)
    if result:
        return [len(result) - 1] + [str(url_counter)] + result
    else:
        return None
"""
Console Testing 
"""
def main():
    """
    Main function to run the BFS and DFS program.
    """

    # create root window
    root = Tk()

    # tkinter variables for Artist 1 and Artist 2
    artist1 = StringVar()
    artist1.set("BLANK")

    artist2 = StringVar()
    artist2.set("BLANK")

    # tkinter var for search type
    searchType = StringVar()
    searchType.set("BLANK")

    # root window title and dimension
    root.title("DegreesOfSpotify by Laurynas Kanopka, Alessandro De-La-O, & Jordan Price")
    # Set geometry(widthxheight)
    root.geometry('1000x300')

    # adding menu bar in root window
    # new item in menu bar labeled as 'New'
    # adding more items in the menu bar
    menu = Menu(root)
    item = Menu(menu)
    item.add_command(label='New')
    menu.add_cascade(label='File', menu=item)
    root.config(menu=menu)

    # adding a label to the root window for Artist 1
    lbl = Label(root, text="Artist 1")
    lbl.grid()

    # adding Entry Field for Artist 1
    txt = Entry(root, width=20)
    txt.grid(column=1, row=0)

    # adding a label to the root window for Artist 2
    lbl2 = Label(root, text="Artist 2")
    lbl2.grid(column=4, row=0)

    # adding Entry Field for Artist 2
    txt2 = Entry(root, width=20)
    txt2.grid(column=5, row=0)



    # adding a label to the root window for start of line of connections from Artist 1 to Artist 2
    lbl7 = Label(root, text="")
    lbl7.grid(column=0, row=5)

    lbl13 = Label(root, text="--> " + artist2.get())
    #lbl13.grid(column=0, row=6)

    # function to display user text when
    # button is clicked
    # global res
    # res = ""
    def clicked():

        res = txt.get()
        #global artist1
        artist1.set(res)
        root.update()
        lbl.configure(text="Artist 1: " + res)
        # lbl7.configure(text = "Similar Artists to " + res + ": ")
        lbl7.configure(text=res)

    def clicked2():

        res2 = txt2.get()
        #global artist2
        artist2.set(res2)
        root.update()
        lbl2.configure(text="Artist 2: " + res2)
        lbl13.configure(text="--> " + artist2.get())

    # button widget with red color text inside
    btn = Button(root, text="Confirm",
                 fg="red", command=clicked)
    # Set Button Grid for Artist 1
    btn.grid(column=2, row=0)

    # button widget with green color text inside
    btn2 = Button(root, text="Confirm",
                  fg="green", command=clicked2)
    # Set Button Grid for Artist 2
    btn2.grid(column=6, row=0)

    # adding a label to the root window for Select Search Algorithm
    lbl5 = Label(root, text="Select Search Algorithm")
    lbl5.grid(column=0, row=2)

    def clicked3():
        searchType.set("DFS")
        res3 = "You Selected: Depth First Search"
        lbl5.configure(text=res3)

    # button widget with orange color text inside
    btn3 = Button(root, text="DFS",
                  fg="orange", command=clicked3)
    # Set Button Grid for DFS
    btn3.grid(column=1, row=2)

    def clicked4():
        searchType.set("BFS")
        res4 = "You Selected: Breadth First Search"
        lbl5.configure(text=res4)

    # button widget with blue color text inside
    btn4 = Button(root, text="BFS",
                  fg="blue", command=clicked4)
    # Set Button Grid for BFS
    btn4.grid(column=2, row=2)

    # adding a label to the root window for the Degree of Separation
    lbl6 = Label(root, text="Find Degrees of Separation")
    lbl6.grid(column=0, row=3)

    # adding labels for the connections to show path between artists
    lbl8 = Label(root, text="")
    lbl8.grid(column=1, row=5)

    lbl9 = Label(root, text="")
    lbl9.grid(column=2, row=5)

    lbl10 = Label(root, text="")
    lbl10.grid(column=3, row=5)

    lbl11 = Label(root, text="")
    lbl11.grid(column=4, row=5)

    lbl12 = Label(root, text="")
    lbl12.grid(column=5, row=5)

    def clicked5():
        #res5 = "Finding Degrees of Separation!"
        #lbl6.configure(text=res5)

        # RUN THE SEARCH USING THE ARTIST VARS AND THE SEARCH TYPE VAR
        # THEN HAVE A DEG VAR
        # HAVE A WAY TO GET THE LIST OF CONNECTIONS

        artist_name_1 = artist1.get().strip()
        artist_name_2 = artist2.get().strip()

        start_url = get_artist_url(artist_name_1)
        end_url = get_artist_url(artist_name_2)

        if not start_url or not end_url:
            print("Could not find one or both artists. Exiting.")
            #artists = False
            return
        #else:
            #artists = True

        if searchType.get() == "BFS":
            print(f"\nFinding shortest path between {artist_name_1} and {artist_name_2} using BFS...")
            result = breadth_first(start_url, end_url)
        elif searchType.get() == "DFS":
            print(f"\nFinding a path between {artist_name_1} and {artist_name_2} using DFS...")
            result = depth_first(start_url, end_url)
        else:
            print("Not a valid choice. Exiting")
            return

        if result:
            degrees = result[0]
            number_artists_searched = result[1]
            path = result[2:]
            # Converts URLs to artist names for better readability
            path_names = [get_artist_name(url) for url in path]
            print(f"\nSearched {number_artists_searched} Artists")
            print(f"\nDegrees of separation: {degrees}")
            print(" -> ".join(path_names))
        else:
            print("No connection found between the artists.")
            degrees = 0

        # deg is the degree of separation
        deg = degrees
        lbl4 = Label(root, text=deg)
        lbl4.grid(column=1, row=4)

        lbl15 = Label(root, text=searchType.get())
        lbl15.grid(column=2, row=4)

        if deg == "0":
            lbl16 = Label(root, text="No connection found between the artists.")
            lbl16.grid(column=1, row=5)

        # adding a label to the root window for First Connection from Artist 1 to Artist 2
        if deg == "1":
            Cartist1 = "--> " + artist2.get()
            lbl8.configure(text=Cartist1)
            #lbl13.grid(column=1, row=5)
        else:
            #Cartist1 = "--> A"
            Cartist1 = "--> " + path_names[1]
            #lbl8 = Label(root, text=Cartist1)
            #lbl8.grid(column=1, row=5)
            lbl8.configure(text=Cartist1)

        # adding a label to the root window for Second Connection from Artist 1 to Artist 2
        if int(deg) < 2:
            Cartist2 = ""
            lbl9.configure(text=Cartist2)
        elif deg == "2":
            Cartist2 = "--> " + artist2.get()
            lbl13.grid(column=2, row=5)
        else:
            Cartist2 = "--> " + path_names[2]
            lbl9.configure(text=Cartist2)
        # lbl9.configure(text = "--> " + artist2)

        # adding a label to the root window for Third Connection from Artist 1 to Artist 2
        if int(deg) < 3:
            Cartist3 = ""
            lbl10.configure(text=Cartist3)
        elif deg == "3":
            Cartist3 = "--> " + artist2.get()
            lbl13.grid(column=3, row=5)
        else:
            Cartist3 = "--> " + path_names[3]
            lbl10.configure(text=Cartist3)

        # adding a label to the root window for Fourth Connection from Artist 1 to Artist 2
        if int(deg) < 4:
            Cartist4 = ""
            lbl11.configure(text=Cartist4)
        elif deg == "4":
            Cartist4 = "--> " + artist2.get()
            lbl13.grid(column=4, row=5)
        else:
            Cartist4 = "--> " + path_names[4]
            lbl11.configure(text=Cartist4)

        # adding a label to the root window for Fifth Connection from Artist 1 to Artist 2
        if int(deg) < 5:
            Cartist5 = ""
            lbl12.configure(text=Cartist5)
        elif deg == "5":
            Cartist5 = "--> " + artist2.get()
            lbl13.grid(column=5, row=5)
        else:
            Cartist5 = "--> " + path_names[5]
            lbl12.configure(text=Cartist5)

    # button widget with blue color text inside
    btn4 = Button(root, text="Search",
                  fg="black", command=clicked5)
    # Set Button Grid for Search
    btn4.grid(column=1, row=3)

    # adding a label to the root window for the Degree of Separation
    lbl3 = Label(root, text="Degree of Separation: ")
    lbl3.grid(column=0, row=4)

    # artist2 = "Artist 2"

    #root.update()

    #lbl14 = Label(root, text=artist2.get())
    #lbl14.grid(column=0, row=7)



    # Execute Tkinter
    root.mainloop()

"""
    artist_name_1 = input("Enter the first artist name: ").strip()
    artist_name_2 = input("Enter the second artist name: ").strip()

    start_url = get_artist_url(artist_name_1)
    end_url = get_artist_url(artist_name_2)

    if not start_url or not end_url:
        print("Could not find one or both artists. Exiting.")
        return

    print("\nChoose a search method:")
    print("1. Breadth-First Search (BFS)")
    print("2. Depth-First Search (DFS)")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        print(f"\nFinding shortest path between {artist_name_1} and {artist_name_2} using BFS...")
        result = breadth_first(start_url, end_url)
    elif choice == "2":
        print(f"\nFinding a path between {artist_name_1} and {artist_name_2} using DFS...")
        result = depth_first(start_url, end_url)
    else:
        print("Not a valid choice. Exiting")
        return

    if result:
        degrees = result[0]
        number_artists_searched = result[1]
        path = result[2:]
        #Converts URLs to artist names for better readability
        path_names = [get_artist_name(url) for url in path]
        print(f"\nSearched {number_artists_searched} Artists")
        print(f"\nDegrees of separation: {degrees}")
        print(" -> ".join(path_names))
    else:
        print("No connection found between the artists.")

"""


if __name__ == "__main__":
    main()
