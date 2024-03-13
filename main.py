# Info: Country Comparer between BeatLeader and ScoreSaber
# Author: Spoekle
# Version 1.0.0

import requests
import math
import time
from tkinter import *
from tkinter import messagebox

def submit():
    # Get the user input from the form
    global nPlayers
    nPlayers = int(players_entry.get())
    nPages_per_batch = 10
    nPages_total = math.ceil(nPlayers / 50)

    print(nPages_total)
    steamArray = []
    blCountryArray = []
    ssUsernameArray = []
    ssCountryArray = []

    # Iterate through batches of 10 pages
    for batch_start in range(1, nPages_total + 1, nPages_per_batch):
        batch_end = min(batch_start + nPages_per_batch - 1, nPages_total)
        total_players_fetched = 0  # Track the total number of players fetched in this batch

        # Fetch data for the current batch
        for x in range(batch_start, batch_end + 1):
            # Stop fetching data if total_players_fetched exceeds nPlayers
            if total_players_fetched >= nPlayers:
                break

            retries = 3
            while retries > 0:
                try:
                    r = requests.get(f"https://api.beatleader.xyz/players?sortBy=pp&page={x}&count=50&mapsType=ranked&ppType=general&friends=false")
                    r.raise_for_status()  # Raise an exception for HTTP errors
                    data = r.json()
                    break  # Break out of the retry loop if request succeeds
                except requests.exceptions.RequestException as e:
                    print(f"Failed to fetch data for page {x}: {e}")
                    retries -= 1
                    if retries == 0:
                        print("Max retries exceeded. Moving to the next page.")
                        break
                    else:
                        print("Retrying after 5 seconds...")
                        time.sleep(5)
                    continue

            if 'data' in data:
                for player in data['data']:
                    # Stop fetching data if total_players_fetched exceeds nPlayers
                    if total_players_fetched >= nPlayers:
                        break

                    username = player['name']
                    blCountry = player['country']
                    steamId = player['id']

                    steamArray.append(steamId)
                    blCountryArray.append(blCountry)

                    total_players_fetched += 1
            else:
                print(f"Data not found in response for page {x}")

    print(f"Total players fetched: {nPlayers}! Moving On...")

    # ScoreSaber API Interaction
    for id in steamArray:
        r = requests.get(f"https://scoresaber.com/api/player/{id}/basic")
        if r.status_code == 200:
            data = r.json()
            username = data['name']
            ssCountry = data['country']
            ssCountryArray.append(ssCountry)
            ssUsernameArray.append(username)
        else:
            print(f"Failed to get ScoreSaber info for player {id}. Status code: {r.status_code}")
            # Append None to indicate missing data
            ssCountryArray.append(None)
            ssUsernameArray.append(None)

    # Filter out corresponding entries from blCountryArray for None entries in ssCountryArray
    filtered_blCountryArray = [blCountryArray[i] for i in range(len(ssCountryArray)) if ssCountryArray[i] is not None]

    # Filter out None entries from ssCountryArray and ssUsernameArray
    filtered_ssCountryArray = [country for country in ssCountryArray if country is not None]
    filtered_ssUsernameArray = [username for username in ssUsernameArray if username is not None]

    # Call the compare function
    compare(filtered_blCountryArray, filtered_ssCountryArray, filtered_ssUsernameArray)

def compare(blCountryArray, ssCountryArray, ssUsernameArray):
    # Ensure all arrays have the same length
    if len(blCountryArray) != len(ssCountryArray) or len(blCountryArray) != len(ssUsernameArray):
        print("Arrays are not of equal length")
        return

    # Count the number of mismatched entries
    mismatch_count = 0
    mismatched_data = []

    for blCountry, ssCountry, username in zip(blCountryArray, ssCountryArray, ssUsernameArray):
        if ssCountry is not None:  # Only compare if ScoreSaber data is available
            if blCountry != ssCountry:
                mismatch_count += 1
                mismatched_data.append((username, blCountry, ssCountry))

    # Calculate the percentage of players not using their ScoreSaber country for BeatLeader
    total_players = len(ssCountryArray)  # Use the length of filtered ssCountryArray
    if total_players != 0:
        percentage = (mismatch_count / total_players) * 100
    else:
        percentage = 0

    # Prepare the message
    message = ""
    if mismatched_data:
        message += "Mismatched countries:\n"
        for username, blCountry, ssCountry in mismatched_data:
            message += f"{username} ~ BeatLeader ~ {blCountry} ~ ScoreSaber ~ {ssCountry}\n"
    else:
        message = "All countries matched."

    # Create a new window for displaying the message with a scrollbar
    top = Toplevel()
    top.title("Comparison Results")

    # Create a Text widget to display the message
    text = Text(top, wrap='word', width=80, height=20)
    text.pack(side='left', fill='both', expand=True)

    # Create a Scrollbar widget and attach it to the Text widget
    scrollbar = Scrollbar(top, command=text.yview)
    scrollbar.pack(side='right', fill='y')
    text.config(yscrollcommand=scrollbar.set)

    # Insert the message into the Text widget
    text.insert('1.0', message)

    # Display the percentage of players not using their ScoreSaber country for BeatLeader
    text.insert('end', f"\n\nPercentage of {nPlayers} players not using their ScoreSaber country for BeatLeader: {percentage:.2f}%")

# Form creation
root = Tk()
root.title("Country Compare")
root.geometry('300x100')

# Create labels and entry fields for input
players_label = Label(root, text="Number of players:")
players_label.pack()
players_entry = Entry(root)
players_entry.pack()

# Create submit button
submit_button = Button(root, text="Submit", command=submit)
submit_button.pack()

# Print GUI
root.mainloop()