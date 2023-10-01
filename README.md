## Regium Klavye: A CLI application and python library for Royal Kludge keyboards

![GitHub Repo stars](https://img.shields.io/github/stars/airblast-dev/Regium-Klavye?logo=github&label=stars&color=blue)
![Discord](https://img.shields.io/discord/1144927977558253568?logo=discord&label=Discord&color=rgb(114%20137%20217))
![Static Badge](https://img.shields.io/badge/code_format_-black-black?color=black&link=https%3A%2F%2Fgithub.com%2Fpsf%2Fblack)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![GitHub](https://img.shields.io/github/license/airblast-dev/Regium-Klavye)

<!--toc:start-->
- [Regium Klavye: A CLI application and python library for Royal Kludge keyboards](#regium-klavye-a-cli-application-and-python-library-for-royal-kludge-keyboards)
- [Examples:](#examples)
  - [Command Line example:](#command-line-example)
  - [Library Examples:](#library-examples)
- [Supported Devices](#supported-devices)
<!--toc:end-->

Regium klavye is a CLI application and python library that allows configuration for Royal Kludge keyboards. The application is mainly tested to run on Linux but should run on Windows and Mac OS. 

The goal is to provide an easy to use, simple, library and command-line interface for Royal Kludge keyboards. While it started as a way to control my RK68 keyboard lighting in Linux, I intend to add support for more devices down the line.

> This application does not have any affiliation with Royal Kludge. I am not reliable for any damage that the application may cause to your keyboard. In the case you do have problems, please create an issue so it can be fixed or removed all together depending on the severity.

## Examples:
### Command Line example:
```
python -m regium_klavye # Prints out help message.
python -m regium_klavye set-color red  # Sets the keyboard lighting to red.
python -m regium_klavye set-color 0 255 0  # Sets keyboard lighting to green.
```	

### Library Examples:
```python
>>> from regium_klavye import rkapi
>>> from regium_klavye import rkapi
>>> keyboards = rkapi.get_keyboards()
>>> keyboard = keyboards[0]  # Assuming we want to change the first keyboard.
>>> keyboard.apply_color((255, 0, 255))  # Sets the keyboards lighting to red.
```
>For each keyboard please read supported commands from the documentation, as every implemented keyboard might not have full functionality.

## Supported Devices

Below is currently supported CLI functionalities. For the library feel free to take a look at the documentation.

Keyboards | Color | Animation | Keymapping | CustomAnimation 
---|---|---|---|---
 Royal Kludge RK68 | :heavy_check_mark: | :white_check_mark:| :heavy_check_mark: | :white_check_mark: 
 
 