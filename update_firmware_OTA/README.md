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
2. Fill the`project name`, `connection key` and `asset version` in `configuration.json`
3. Write down your code in the `current_script.py` file.
4. Install the necessary dependencies and it's ready to go.
5. Run the `current_script.py`.

## For Testing

Sample assets are included in the folder. You can use the sample script to test the OTA through Anedya.

Checksums:
- **asset_for_test_with_checksum.py**: `0f9888d0fe732a7d6537666e2e844d0baeec906671c73e9b53f6663c784c4c9f`

> [!TIP]
> For more details, visit Anedya [documentation](https://docs.anedya.io?utm_source=github&utm_medium=link&utm_campaign=github-examples&utm_content=pi).

> [!TIP]
> Looking for the Python SDK? Visit [PyPi](https://pypi.org/project/anedya-dev-sdk/) or the [Github Repository](https://github.com/anedyaio/anedya-dev-sdk-pyhton).

> [!TIP]
> For more information, visit [anedya.io](https://anedya.io/?utm_source=github&utm_medium=link&utm_campaign=github-examples&utm_content=pi).
