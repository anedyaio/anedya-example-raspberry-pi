[<img src="https://img.shields.io/badge/Anedya-Documentation-blue?style=for-the-badge">](https://docs.anedya.io?utm_source=github&utm_medium=link&utm_campaign=github-examples&utm_content=pi)

# Update Firmware (OTA)

This Python script allows you to update the firmware via OTA. It fetches the firmware from Anedya and updates the firmware.

> [!WARNING]
> This code is for hobbyists and learning purposes. It is not recommended for production use!

## Steps for Deployment:
### Anedya Dashboard

1. Go to OTA Deployments -> Assets List and click on "Upload".
2. Upload your script.
3. Fill in the following details precisely:
    - **Asset Identifier**
    - **Asset Version**
    - **Checksum**: Use the following command to obtain the checksum. Open the command prompt, navigate to the file directory, and run:
      ```
      certutil -hashfile [file location] SHA256
      ```
4. Next, go to Deployments -> Create Deployment. Fill in the details:
    - **Deployment Name**
    - **Set Start Time**
    - **Select Asset Identifier**: Choose the identifier filled in the previous step.

All set on the dashboard side.

### Hardware Side:
1. Copy the example code.
2. Write down your code and credentials (e.g., connection key) in the `current_script.py` file.
3. Install the necessary dependencies and it's ready to go.
4. Run the `current_script.py`.

## For Testing

Sample assets are included in the folder. You can use the sample script to test the OTA through Anedya.

Checksums:
- **v0.2.py**: `a0aab80c2328a784bbd7c02f3267d415237af45b1b99f7e5fb29f42e51705b88`
- **v0.3.py**: `c31ec285d39b89e22f97ae8243af42a7e5d4c05456713249eba9d496a0e2ed65`

> [!TIP]
> For more details, visit Anedya [documentation](https://docs.anedya.io?utm_source=github&utm_medium=link&utm_campaign=github-examples&utm_content=pi).

> [!TIP]
> Looking for the Python SDK? Visit [PyPi](https://pypi.org/project/anedya-dev-sdk/) or the [Github Repository](https://github.com/anedyaio/anedya-dev-sdk-pyhton).

> [!TIP]
> For more information, visit [anedya.io](https://anedya.io/?utm_source=github&utm_medium=link&utm_campaign=github-examples&utm_content=pi).
