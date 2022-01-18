# globalafk
A python script that sends ugly notifications when something happens on a [*jschan*](https://gitgud.io/fatchan/jschan) imageboard that you moderate.
It has been developed around composition principles in order to help you to expand or change it to fit your needs and goals. Most of the components are easily swappable.

## Features
For now, this project has one (1) basic feature, send notifications. 
That said, you can configure it to send notifications when:
- New reports
- A new post includes some fine-grained pre-configured entry or some (clear or partially obfuscated) url that you have not whitelisted

All of these features can be turned off independently. 

## Requirements
You need to have **moderation privileges** in at least one board and an environment with **python3** and **the dependencies listed in [*requirements.txt*](./requirements.txt) file** in order to run this script. 

To send notifications on Linux you must have **notify-send** installed. 
Run `notify-send test` to test it.

To send notifications on Android (assuming you are using [*Termux*](https://termux.com/)) you must have **Termux:API** installed. 
Run `termux-notification --title test` to test it.

## Getting Started
1) (Optional) Create and activate a virtual environment
2) Run `pip3 install -r requirements.txt` to install the dependencies
3) Install (if is not already installed) *notify-send* or *termux-notification* accordingly to your needs
4) Make a copy of [*config_example.py*](./config/config_example.py) and rename it to *config.py*
5) Fill the account details and configure the script behavior in your new *config.py* file
6) Run `python3 main.py`

## Contribute
All contributions are welcomed. Feel free to open a issue or make a pull request. 
