import sys
import hashlib
import json
import requests
import time

apikey = ""

# Function that handles file upload to metadefender API
def uploadFile(file):

    # URL for file upload endpoint
    url = "https://api.metadefender.com/v4/file"

    # Read file for binary upload
    filedata = open(file, 'rb').read()

    # Try and send a HTTP post request
    try:
        req = requests.post(url, headers={
            "filename": file,
            "apikey": apikey,
            "content-type": "application/octet-stream"
        }, data=filedata)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    # If the response code is not 200 then print the error
    if req.status_code != 200:
        print(json.dumps(req.json(), indent=4, sort_keys=True))
        sys.exit()

    print("Upload successful")

    # Variable initializations
    uploadres = req.json()
    data_id = uploadres['data_id']
    filesha256 = uploadres['sha256']
    finished_upload = False
    pollurl = "https://api.metadefender.com/v4/file/{}".format(data_id)

    # Max retry count to prevent infinite loop
    total_retries = 10
    retry_count = 0

    # Polling loop, retries endpoint every 30 seconds with a maximum of 10 retries
    while not finished_upload and retry_count <= total_retries:
        # Try and send a HTTP get request
        try:
            pollreq = requests.get(pollurl, headers={
                "apikey": apikey
            })
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        
        # If the response code is 200 then grab the percent progress from the response
        if pollreq.status_code == 200:
            polljson = pollreq.json()
            percent = polljson['scan_results']['progress_percentage']
            # Check if the upload is complete
            if percent == 100:
                finished_upload = True
            # If not complete then sleep for 30 seconds
            else:
                print("File at {:.2%} retrying in 30 seconds ({}/{})".format((percent/100), retry_count, total_retries))
                time.sleep(30)
        # If the response code is not 200 then exit and print the error
        else:
            print("Polling error HTTP status", pollreq.status_code)
            print(json.dumps(pollreq.json(), indent=4, sort_keys=True))
            return

    # Print the final results after upload is complete
    print(json.dumps(polljson, indent=4, sort_keys=True))

# Function that handles hash lookup to metadefender API
# Return 0 : Hash not found, should continue to file upload
# Return 1 : Hash found
# Return -1 : Error has occured
def hashLookup(hash):

    # URL for hash lookup endpoint with specified hash
    hashlookupurl = "https://api.metadefender.com/v4/hash/{}".format(hash)

    # Try and send a get request 
    try:
        req = requests.get(hashlookupurl, headers={
            "apikey": apikey
        })
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    # If the status code is 404 and the error is 404003 then return 0
    if req.status_code == 404:
        errorjson = req.json()
        if(errorjson['error']['code'] == 404003):
            print(json.dumps(errorjson, indent=4, sort_keys=True))
            return 0

    elif req.status_code == 200:
        print(json.dumps(req.json(), indent=4, sort_keys=True))
        return 1

    return -1

# Main function
def main(argv):

    # Usage should have 1 extra command argument, the file
    if len(argv) != 1:
        raise SystemExit("usage: opswat.py <filename>")

    if not apikey:
        raise SystemExit("API Key has not been specified. Please edit line 7 with your key")

    # Get filename from command line argument
    filename = argv[0]

    # MD5 function
    hash_md5 = hashlib.md5()

    # Try and open the specified file
    try:
        # Open filename
        with open(filename, "rb") as f:
            # Read filename in chunks incase the filesize is extremely large
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        # Compute hash
        filehash = hash_md5.hexdigest()
    # IO Error
    except IOError as e:
        raise SystemExit(e)

    # Try and do a hash lookup to the metadefender API
    # If 0 is returned then continue to file upload
    if hashLookup(filehash) == 0:
        print("Hash not found, uploading file")
        uploadFile(filename)

    return

if __name__ == "__main__":
   main(sys.argv[1:])