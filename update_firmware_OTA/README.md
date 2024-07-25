[<img src="https://img.shields.io/badge/Anedya-Documentation-blue?style=for-the-badge">](https://docs.anedya.io?utm_source=github&utm_medium=link&utm_campaign=github-examples&utm_content=pi)

# Update-Firmware (OTA)

This Python script allows you to update the firmware via OTA. It fetches the firmware from the anedya and updates the device firmware.

> [!WARNING]
> This code is for hobbyists for learning purposes. Not recommended for production use!!

## Set-Up Project in Anedya Dashboard

- Use following command to obtain the checksum 
    ```
    certutil -hashfile [file location] SHA256
    ```

# For testing
 
There are included sample assets folder. You can use that sample script to test the OTA through anedya.

checksum 
    - ** v0.2.py**: a0aab80c2328a784bbd7c02f3267d415237af45b1b99f7e5fb29f42e51705b88
    - ** v0.3.py**: c31ec285d39b89e22f97ae8243af42a7e5d4c05456713249eba9d496a0e2ed65

 > [!TIP]
 > For more details, Visit anedya [documentation](https://docs.anedya.io?utm_source=github&utm_medium=link&utm_campaign=github-examples&utm_content=pi)



### Code Set-Up

1. Replace `<PHYSICAL-DEVICE-UUID>` with your 128-bit UUID of the physical device.
2. Replace `<CONNECTION-KEY>` with your connection key, which you can obtain from the node description.


> [!TIP]
> Looking for Python SDK? Visit [PyPi](https://pypi.org/project/anedya-dev-sdk/) or [Github Repository](https://github.com/anedyaio/anedya-dev-sdk-pyhton)

>[!TIP]
> For more information, visit [anedya.io](https://anedya.io/?utm_source=github&utm_medium=link&utm_campaign=github-examples&utm_content=pi)
