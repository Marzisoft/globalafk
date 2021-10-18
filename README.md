# globalafk
A simple python script that sends ugly notifications when something happens on a jschan imageboard that you moderate.

## Requirements
A *Global Staff* account is obviously required.

### Linux
You must have **notify-send** installed to receive notifications on linux. 
Run `notify-send test` to test it.

### Termux (Android)
You must have **Termux:API** installed to receive notifications on android. 
Run `termux-notification --title test` to test it.

## Getting Started
1) (Optional) Create and activate a virtual environment
2) Run `pip3 install -r requirements.txt` to install the dependencies
3) Make a copy of [*config_example.py*](./config/config_example.py) and rename it to *config.py* 
4) Run `python3 main.py`