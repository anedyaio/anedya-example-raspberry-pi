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
fetched_deployment_data={}

#--------------------------------------Helper Functions-----------------------------------------
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

def r_or_w_config_file(param_r_or_w:str,param_content=""):
    param_path=CONFIG_PATH
    if param_r_or_w=="r":
        with open(param_path, param_r_or_w,encoding='utf-8') as file:
            content = json.load(file)
            return content
    elif param_r_or_w=="w":
        with open(param_path, param_r_or_w,encoding='utf-8') as file:
            json.dump(param_content, file,indent=4)
            return True
def sha256_checksum(filename):
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
#----------------------------------------------------------------------------------------------
def fetch_update():
    global depolyment_id, fetched_deployment_data, connection_key
    config_data=r_or_w_config_file(param_r_or_w="r")
    if config_data["CONNECTION_KEY"]:
        connection_key=config_data["CONNECTION_KEY"]
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
            fetched_deployment_data=response_message.get('data', {})
            if fetched_deployment_data is None:
                print('No new deployment request')
                return ""
            depolyment_id = fetched_deployment_data.get("deploymentId")
            if depolyment_id:
                return fetched_deployment_data
            else:
                print('No new deployment request')
                return ""

        except requests.exceptions.RequestException as e:
            print(f'Error fetching update: {e}')
            return False
        except json.JSONDecodeError as e:
            print(f'Error decoding JSON response: {e}')
            return False
        except Exception as e:
            print(f'Unexpected error: {e}')
            return False
    else:
        print('No connection key found!!')
    
def check_deploybility():
        new_asset_version=fetched_deployment_data.get("assetVersion")
        config_data=r_or_w_config_file("r")
        active_version=config_data.get("ACTIVE_VERSION")
        update_status(param_deployment_id=depolyment_id, param_status="start", param_log="Received new deployment request")
        submit_log(f"Received new deployment request, [Version:{new_asset_version}]")
        if active_version=="":
            active_version='0'
        if str(new_asset_version)>str(active_version):
            asset_url = fetched_deployment_data.get("asseturl")
            # print(asset_url)

            check_sum = fetched_deployment_data.get('data', {}).get("assetChecksum")
            # print(check_sum)

            if not asset_url:
                update_status(param_deployment_id=depolyment_id, param_status="failure", param_log="No asset URL found in the update response.")
                submit_log("No asset URL found in the update response.")
                return False
            else:
                i=0
                while i<5:
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
                                update_status(param_deployment_id=depolyment_id, param_status="failure", param_log="Checksum verification failed")
                                submit_log("Checksum verification failed. redownloading...")
                                i+=1
                        else:
                            return True
                    else:
                        print(f'Failed to fetch update. Status code: {asset_response.status_code}')
                        return False
                if i==5:
                    update_status(param_deployment_id=depolyment_id, param_status="failure", param_log="Failed to fetch update")
                    submit_log("Failed download update!")
                    return False
        else:
            update_status(param_deployment_id=depolyment_id, param_status="failure", param_log="check the asset version!")
            submit_log("CAUTION: check the asset version!")
            config_data = r_or_w_config_file(param_r_or_w='r')
            config_data['LAST_DEPLOYMENT_STATUS']=f'failed [version: {new_asset_version}]'
            config_data['LAST_CHANGED_LOG']=int(time.time()*1000)
            r_or_w_config_file(param_r_or_w='w',param_content=config_data)
            return False

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
            config_data=r_or_w_config_file(param_r_or_w="r")
            config_data["CONNECTION_KEY"]=connection_key
            if config_data['ACTIVE_DEPLOYMENT']!="":
                config_data["PREVIOUS_DEPLOYMENT"]=config_data['ACTIVE_DEPLOYMENT']
            config_data["ACTIVE_DEPLOYMENT"]=fetched_deployment_data
            config_data['ACTIVE_VERSION']=str(fetched_deployment_data['assetVersion'])
            r_or_w_config_file(param_r_or_w="w",param_content=config_data)
            
            try:
                # Check if the script runs successfully
                try:
                    update_status(param_deployment_id=depolyment_id, param_status="installing", param_log="installing")
                    submit_log("Deploying update...")
                    config_data = r_or_w_config_file(param_r_or_w='r')
                    config_data['LAST_DEPLOYMENT_STATUS']='success'
                    config_data['LAST_CHANGED_LOG']=int(time.time()*1000)
                    r_or_w_config_file(param_r_or_w='w',param_content=config_data)            

                    subprocess.check_call([sys.executable, current_script_path])


                except subprocess.CalledProcessError as e:
                    print(f'Script run failed with error code {e.returncode}')
                    update_status(param_deployment_id=depolyment_id, param_status="failure", param_log=f'Script run failed with error code {e.returncode}')
                    submit_log('Script run failed!! restarting previous script')
                    
                    #-------------------------update config file----------------------------------------------
                    config_data = r_or_w_config_file(param_r_or_w='r')
                    previous_deployment=config_data.get('PREVIOUS_DEPLOYMENT')
                    if previous_deployment!="":
                        config_data["ACTIVE_DEPLOYMENT"]=previous_deployment
                        config_data["ACTIVE_VERSION"]=str(config_data.get('PREVIOUS_DEPLOYMENT').get('assetVersion'))
                    config_data['LAST_DEPLOYMENT_STATUS']='failed'
                    config_data['LAST_CHANGED_LOG']=int(time.time()*1000)
                    r_or_w_config_file(param_r_or_w='w',param_content=config_data)
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
            
        else:
            print('Update file does not exist.')
            return False
    except Exception as e:
        print(f'Error applying update: {e}')
        return False
   