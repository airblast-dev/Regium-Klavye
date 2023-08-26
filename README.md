## Regium Klavye: A CLI application and python library for Royal Kludge keyboards
___
![GitHub Repo stars](https://img.shields.io/github/stars/airblast-dev/Regium-Klavye?logo=github&label=stars&color=blue)
![Discord](https://img.shields.io/discord/1144927977558253568?logo=discord&label=Discord&color=rgb(114%20137%20217))
![Static Badge](https://img.shields.io/badge/code_format_-black-black?color=black&link=https%3A%2F%2Fgithub.com%2Fpsf%2Fblack)
![GitHub](https://img.shields.io/github/license/airblast-dev/Regium-Klavye)

Regium klavye is a CLI application and python library that allows configuration for Royal Kludge keyboards. The application is mainly tested to run on Linux but should run on Windows and Mac OS. 

The goal is to provide an easy to use, simple, library and command-line interface for Royal Kludge keyboards. While it started as a way to control my RK68 keyboard lighting in Linux, I intend to add support for more devices down the line.

> This application does not have any connection to Royal Kludge. I am not reliable for any damage that the application may cause to your keyboard. In the case you do have problems, please create an issue so it can be fixed or removed all together depending on the severity.

### Docs:
TODO

### Examples:
```python
python -m regium_klavye # Prints out help message.
python -m regium_klavye set-color red  # Sets the keyboard lighting to red.
python -m regium_klavye set-color 0 255 0  # Sets keyboard lighting to green.
```	