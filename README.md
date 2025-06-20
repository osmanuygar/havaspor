# Havaspor

Havaspor is a Simple Python-based project that fetches live sports programs and weather information. It provides functionalities such as filtering sports programs, listing unique channels, and sending weather or program details via email.

I make our day better by delivering morning sports broadcasts and informing about the weather via email  :D:D:D

## Features

- Fetch live sports programs from `sporekrani.com`.
- Display current weather information for specified cities.
- Filter sports programs by keyword or channel.
- List unique broadcasting channels.
- Send program or weather details via email in HTML format.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/osmanuygar/havaspor.git
   cd havaspor
   ```
   
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    
    ```

## Usage
Run the script with the following options:
Fetch Weather Information


Display weather and sport programs for a city: 

    ```bash
    python havaspor.py --havadurum Istanbul
    Send weather information via email:
    
    
    python havaspor.py --havadurum-email Istanbul example@example.com
    Fetch Sports Programs
    Search programs by keyword:
    
    
    python havaspor.py --search "Spor"
    Filter programs by channel:
    
    
    python havaspor.py --kanal "UYGAR Spor"
    List unique broadcasting channels:
    
    
    python havaspor.py --list-channels
    
    Send filtered programs via email:
    python havaspor.py --email example@example.com
    ```
