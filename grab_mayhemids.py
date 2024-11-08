import aiohttp
import aiofiles
import asyncio
import time
import os
from aiohttp import ClientResponseError, ClientPayloadError, ClientConnectorError
from xml.etree import ElementTree as ET

# Define the range for applicationUserId
START_ID = 9816000000
END_ID = 9816000000

# Maximum concurrent requests and retries
MAX_CONCURRENT_REQUESTS = 25000
MAX_RETRIES = 1000
TIMEOUT = 10  # Timeout in seconds for each request
GLOBAL_TIMEOUT = 30  # Global timeout for each task to ensure no task runs forever

# Semaphore to limit concurrent requests
semaphore = None
existing_files_dict = {}

def load_existing_files():
    """Load existing XML files into a dictionary for fast lookup."""
    global existing_files_dict
    # Store the file as a dictionary with applicationUserId as the key
    for fn in os.listdir("."):
        if fn.endswith(".xml"):
            try:
                # Extract applicationUserId from the filename and add to the dictionary
                app_user_id = fn.split("_")[1]  # Assumes filename format: applicationUserId_123_mayhemId_456.xml
                existing_files_dict[app_user_id] = fn
            except IndexError:
                continue  # Skip files that don't follow the expected naming pattern

async def fetch_user_data(session, applicationUserId, retries=MAX_RETRIES):
    # Check if the file already exists (skip if it does)
    if str(applicationUserId) in existing_files_dict:
        print(f"File for applicationUserId {applicationUserId} already exists, skipping...")
        return

    url = f"https://prod.simpsons-ea.com/mh/users?appLang=en&application=nucleus&applicationUserId={applicationUserId}"
    headers = {
        'Accept': 'application/xml'
    }

    async with semaphore:
        try:
            # Apply a global timeout for the entire task
            response = await asyncio.wait_for(session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=TIMEOUT)), timeout=GLOBAL_TIMEOUT)
            if response.status == 200:
                try:
                    content = await response.text()  # This is where ClientPayloadError might occur
                except ClientPayloadError:
                    print(f"ClientPayloadError for user ID {applicationUserId}, retrying ({MAX_RETRIES - retries + 1} retries left)...")
                    if retries > 0:
                        await asyncio.sleep(2 ** (MAX_RETRIES - retries))  # Exponential backoff
                        return await fetch_user_data(session, applicationUserId, retries - 1)
                    else:
                        print(f"Failed to fetch data for user ID {applicationUserId} after {MAX_RETRIES} retries.")
                        return

                # Parse the XML response to check for <Resources>
                root = ET.fromstring(content)
                if root.tag == 'Resources':
                    # Extract mayhemId from the URI
                    uri = root.find('URI').text
                    mayhem_id = uri.split('/')[-1]
                    
                    # Save the response to a file
                    filename = f"applicationUserId_{applicationUserId}_mayhemId_{mayhem_id}.xml"
                    async with aiofiles.open(filename, 'w') as file:
                        await file.write(content)
                    print(f"Saved: {filename}")
                    existing_files_dict[str(applicationUserId)] = filename  # Add to the dictionary
                else:
                    print(f"No valid <Resources> found for user ID {applicationUserId}")
            else:
                print(f"Error: Received status code {response.status} for user ID {applicationUserId}")
                if response.status in {502, 503, 504} and retries > 0:
                    # Retry on server errors
                    print(f"Retrying for user ID {applicationUserId} ({MAX_RETRIES - retries + 1} retries left)...")
                    await asyncio.sleep(2 ** (MAX_RETRIES - retries))  # Exponential backoff
                    return await fetch_user_data(session, applicationUserId, retries - 1)

        except ClientResponseError as e:
            print(f"Request error for user ID {applicationUserId}: {str(e)}")
            if retries > 0:
                print(f"Retrying for user ID {applicationUserId} ({MAX_RETRIES - retries + 1} retries left)...")
                await asyncio.sleep(2 ** (MAX_RETRIES - retries))  # Exponential backoff
                return await fetch_user_data(session, applicationUserId, retries - 1)

        except ClientConnectorError as e:
            print(f"ClientConnectorError for user ID {applicationUserId}: {str(e)}, retrying...")
            if retries > 0:
                await asyncio.sleep(2 ** (MAX_RETRIES - retries))  # Exponential backoff
                return await fetch_user_data(session, applicationUserId, retries - 1)
            else:
                print(f"Failed to fetch data for user ID {applicationUserId} after {MAX_RETRIES} retries.")
                return

        except asyncio.TimeoutError:
            print(f"Global Timeout for user ID {applicationUserId}, retrying...")
            if retries > 0:
                await asyncio.sleep(2 ** (MAX_RETRIES - retries))  # Exponential backoff
                return await fetch_user_data(session, applicationUserId, retries - 1)
            else:
                print(f"Failed to fetch data for user ID {applicationUserId} after {MAX_RETRIES} retries.")
                return

        await asyncio.sleep(1)  # Add delay to prevent rate-limiting

async def process_users(start_id, end_id):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for applicationUserId in range(start_id, end_id + 1):
            task = fetch_user_data(session, applicationUserId)
            tasks.append(task)

        await asyncio.gather(*tasks)

async def main():
    global semaphore
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    # Load the existing XML files once at the start
    load_existing_files()

    # Process users in batches
    batch_size = 1000  # Process 100 users per batch
    for start_id in range(START_ID, END_ID + 1, batch_size):
        end_id = min(start_id + batch_size - 1, END_ID)
        print(f"Processing users {start_id} to {end_id}")
        await process_users(start_id, end_id)
        print(f"Finished processing users {start_id} to {end_id}")

if __name__ == "__main__":
    start_time = time.time()
    
    # Run the main loop
    asyncio.run(main())
    
    print(f"Finished in {time.time() - start_time} seconds")
