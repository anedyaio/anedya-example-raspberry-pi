import time
import json
import requests
from pathlib import Path

from updater import fetch_update
from updater import check_deploybility
from updater import apply_update


#-----------credentials-----------------------------
CONNECTION_KEY = ""

#----------settings---------------------------------
CHECK_FOR_OTA_UPDATE_SEC=5

#-----------Helpers variables-----------------------
runned_once = False

#--------------Path variables-----------------------
# Get the directory of the current script
script_directory = Path(__file__).parent
CONFIG_PATH = f'{script_directory}/configuration.json'

def main():
    global runned_once, CONNECTION_KEY
    update_interval=int(time.time())
    config_data = r_or_w_config_file(param_r_or_w='r')
    CONNECTION_KEY = config_data["CONNECTION_KEY"]

    while True:
        #----------------------------------------OTA section---------------------------------------------------------------
        if int(time.time()) - update_interval > CHECK_FOR_OTA_UPDATE_SEC:
            print("----------------------------------------------")
            print("checking for updates...")
            new_deployment = fetch_update()  #check for updates and return True if there is a new deployment
            if new_deployment: #if there is a new deployment
                print(f"new deployment: {new_deployment.get('assetName')}")
                print(f"new deployment assetID: {new_deployment.get('assetId')}")
                print(f"new deployment version: {new_deployment.get('assetVersion')}")
                print(f"new deployment deploymentId: {new_deployment.get('deploymentId')}")
                print(f"new deployment checksum: {new_deployment.get('checksum')}")
                print(f"new deployment assetMeta : {new_deployment.get('assetMeta')}")
                print(f"new deployment assetUrl : {new_deployment.get('assetUrl')}")

                print("checking deploybility of the received asset - check its version, checksum..")
                if check_deploybility(): #check deploybility of the received asset - check its version, checksum..
                    print("deploybility check passed!")

                    print("applying the update : if the version is not the same and checksum is correct, apply the update")
                    apply_update()  #apply the update : if the version is not the same and checksum is correct, apply the update

                else:
                    submit_log("deploybility check failed!..continuing the script run...")
            else:
                print('continuing the script run...')

            update_interval=int(time.time())
            print("----------------------------------------------")
        if not runned_once:
            config_data = r_or_w_config_file(param_r_or_w='r')
            try:
                deployed_id = config_data["ACTIVE_DEPLOYMENT"]["deploymentId"]
                deployed_version=config_data["ACTIVE_DEPLOYMENT"]["assetVersion"]
                if deployed_id!="":
                    update_status(param_deployment_id=deployed_id, param_status="success", param_log="success")
                    print("====================================================================================")
                    submit_log(f"version: {deployed_version} - deployed!!")
                    print("====================================================================================")
                    runned_once = True
            except KeyError:
                # print("No deploymentId found in the configuration file.")
                pass
        #--------------------------------------------------------------------------------------------------------------------



        print()
        config_data = r_or_w_config_file(param_r_or_w='r')
        asset_version = config_data["ACTIVE_VERSION"]
        print(f"[Version {asset_version}] Runnning...")
        print()
        time.sleep(2)



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
        'Authorization': CONNECTION_KEY
    }

    response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
    errorcode = json.loads(response.text).get('errorcode')
    if errorcode == 0:
        # print("Status updated !!")
        return True
    else:
        # print(response.text)
        return False
    
def submit_log(param_log: str) -> bool:
    url = "https://device.ap-in-1.anedya.io/v1/logs/submitLogs"
    payload = json.dumps({
        "reqId": "",
        "data": [
            {
                "timestamp": int(time.time() * 1000),
                "log": param_log
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Auth-mode': 'key',
        'Authorization': CONNECTION_KEY
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False

    try:
        response_data = response.json()
    except json.JSONDecodeError:
        print(f"Failed to decode JSON response: {response.text}")
        return False

    error_code = response_data.get('errorcode')
    if error_code == 0:
        print("[Logged]:"+param_log)
        return True
    else:
        print(f"Error in response: {response_data}")
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
    
if __name__ == "__main__":
    main()
