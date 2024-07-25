import requests
import os
import subprocess
import time
import signal
import sys
import json
import hashlib
from pathlib import Path

#--------------------------------------Path variables-------------------------------------
script_directory = Path(__file__).parent  # Get the directory of the current script
current_script_path = f'{script_directory}/current_script.py'  # Path to your current script
previous_script_path = f'{script_directory}/previous_script.py'  # Path to your previous script
TEMP_PATH = f'{script_directory}/temp_script.py'  # Temporary path for the update
CONFIG_PATH = f'{script_directory}/configuration.json'

#--------------------------------------Helper variables-----------------------------------------
connection_key = ""
depolyment_id = ""
fetched_depolyment_data={}


def update_status(param_deployment_id: str, param_status: str, param_log=""):
    url = "https://device.ap-in-1.anedya.io/v1/ota/updateStatus"

    payload = json.dumps({
        "reqId": "",
        "deploymentId": param_deployment_id,
        "status": param_status,
        "log": param_log
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Auth-mode': 'key',
        'Authorization': connection_key
    }

    response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
    errorcode = json.loads(response.text).get('errorcode')
    if errorcode == 0:
        # print("Status updated !!")
        return True
    else:
        print(response.text)
        return False


def submit_log(param_log:str)->bool:

    url = f"https://device.ap-in-1.anedya.io/v1/logs/submitLogs"
    payload = json.dumps({
    "reqId": "",
    "data": [
        {
        "timestamp": int(time.time()*1000),
        "log": param_log
        }
    ]
    })
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Auth-mode': 'key',
    'Authorization': connection_key
    }
    # print(payload)
    response = requests.request("POST", url, headers=headers, data=payload,timeout=10)
    # print(response.text)
    error_code=json.loads(response.text).get('errorcode')
    if error_code==0:
        print("[Logged]:"+param_log)
        # print()
        return True
    else:
        print(response.text)
        return False

def get_file(param_r_or_w:str,param_content=""):
    param_path=CONFIG_PATH
    if param_r_or_w=="r":
        with open(param_path, param_r_or_w,encoding='utf-8') as file:
            content = json.load(file)
            return content
    elif param_r_or_w=="w":
        with open(param_path, param_r_or_w,encoding='utf-8') as file:
            json.dump(param_content, file,indent=4)
            return True


def fetch_update():
    global depolyment_id, fetched_depolyment_data
    try:
        url = "https://device.ap-in-1.anedya.io/v1/ota/next"
        payload = json.dumps({"reqId": ""})
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Auth-mode': 'key',
            'Authorization': connection_key
        }
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response_message = response.json()
        fetched_depolyment_data=response_message.get('data', {})
        depolyment_id = response_message.get('data', {}).get("deploymentId")
        depolyment_version=response_message.get('data', {}).get("assetVersion")
        if depolyment_id:
            asset_url = response_message.get('data', {}).get("asseturl")
            update_status(param_deployment_id=depolyment_id, param_status="start", param_log="success")
            submit_log(f"Received new deployment request, [Version:{depolyment_version}]")
            check_sum = response_message.get('data', {}).get("assetChecksum")
            # print(check_sum)

            if not asset_url:
                print("No asset URL found in the update response.")
                return False
            else:
                asset_response = requests.get(asset_url, timeout=10)
                # print(asset_response.content.decode('utf-8'))
                if asset_response.status_code == 200:
                    update_status(param_deployment_id=depolyment_id, param_status="download", param_log="success")
                    submit_log("Downloading update...")
                    with open(TEMP_PATH, 'wb') as file:
                        file.write(asset_response.content)
                    if check_sum:
                        print("verifying checksum...")
                        file_hash_code=sha256_checksum(TEMP_PATH)
                        print(file_hash_code[:36])
                        if file_hash_code[:36] == check_sum:
                            print("Checksum verified.")
                            update_status(param_deployment_id=depolyment_id, param_status="extract", param_log="Checksum verified")
                            submit_log("Extracting update...")
                            return True
                        else:
                            print("Checksum verification failed.")
                            update_status(param_deployment_id=depolyment_id, param_status="failed", param_log="Checksum verification failed")
                            submit_log("Checksum verification failed.")
                            print("continuing the script run...")
                            return False
                    else:
                        return True
                else:
                    print(f'Failed to fetch update. Status code: {asset_response.status_code}')
                    return False
        else:
            print("No Update available.")
            return False
    except requests.exceptions.RequestException as e:
        print(f'Error fetching update: {e}')
        return False
    except json.JSONDecodeError as e:
        print(f'Error decoding JSON response: {e}')
        return False
    except Exception as e:
        print(f'Unexpected error: {e}')
        return False

#function to sha256 checksum
def sha256_checksum(filename):
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

def apply_update():
    try:
        if os.path.exists(TEMP_PATH):
            # Open the source file in read mode and the destination file in write mode
            with open(current_script_path, 'r',encoding='utf-8') as src, open(previous_script_path, 'w', encoding='utf-8') as dest:
                # Read the content of the source file
                content = src.read()
                # Write the content to the destination file
                dest.write(content)
            os.replace(TEMP_PATH, current_script_path)
            config_data=get_file(param_r_or_w="r")
            config_data["CONNECTION_KEY"]=connection_key
            if config_data['ACTIVE_DEPLOYMENT']!="":
                config_data["PREVIOUS_DEPLOYMENT"]=config_data['ACTIVE_DEPLOYMENT']
            config_data["ACTIVE_DEPLOYMENT"]=fetched_depolyment_data
            config_data['ACTIVE_VERSION']=fetched_depolyment_data['assetVersion']
            get_file(param_r_or_w="w",param_content=config_data)
            return True
        else:
            print('Update file does not exist.')
            return False
    except Exception as e:
        print(f'Error applying update: {e}')
        return False

def restart_script():
    try:
        # Check if the script runs successfully
        try:
            update_status(param_deployment_id=depolyment_id, param_status="installing", param_log="installing")
            submit_log("Deploying update...")
            config_data = get_file(param_r_or_w='r')
            config_data['LAST_DEPLOYMENT_STATUS']='success'
            config_data['LAST_CHANGED_LOG']=int(time.time()*1000)
            get_file(param_r_or_w='w',param_content=config_data)            

            subprocess.check_call([sys.executable, current_script_path])


        except subprocess.CalledProcessError as e:
            print(f'Script run failed with error code {e.returncode}')
            update_status(param_deployment_id=depolyment_id, param_status="failed", param_log=f'Script run failed with error code {e.returncode}')
            submit_log('Script run failed!! restarting previous script')
            
            #-------------------------update config file----------------------------------------------
            config_data = get_file(param_r_or_w='r')
            previous_deployment=config_data.get('PREVIOUS_DEPLOYMENT')
            if previous_deployment!="":
                config_data["ACTIVE_DEPLOYMENT"]=previous_deployment
                config_data["ACTIVE_VERSION"]=config_data.get('PREVIOUS_DEPLOYMENT').get('assetVersion')
            config_data['LAST_DEPLOYMENT_STATUS']='failed'
            config_data['LAST_CHANGED_LOG']=int(time.time()*1000)
            get_file(param_r_or_w='w',param_content=config_data)
            #------------------------------------------------------------------------------------------

            with open(previous_script_path, 'r',encoding='utf-8') as src, open(current_script_path, 'w', encoding='utf-8') as dest:
                # Read the content of the source file
                content = src.read()
                # Write the content to the destination file
                dest.write(content)
            subprocess.Popen([sys.executable, previous_script_path])
            # return False
   

        # Terminate the current script
        if os.name == 'posix':  # Check if the operating system is POSIX (e.g., Linux)
            os.kill(os.getpid(), signal.SIGTERM)
        elif os.name == 'nt':  # Check if the operating system is Windows
            os._exit(0)  # Exit the script on Windows
    except Exception as e:
        print(f'Error restarting script: {e}')

def check_for_updates(param_connection_key:str):
    global connection_key
    connection_key=param_connection_key
    if fetch_update():
        # print('Applying update...')
        if apply_update():
            # print('Update applied successfully. Restarting the script...')
            try:
                restart_script()
            except Exception as e:
                print(f'Error restarting script: {e}')
        else:
            print('No update needed.')
    else:
        print('continuing the script run...')