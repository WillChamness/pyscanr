# PyScanr

A simple tool to ping sweep small-sized subnets.

# Usage

```
usage: pyscanr [-h] [-s SOURCE] [-v] [-a] [-A] [-u] subnet

Pings a range of IP addresses

positional arguments:
  subnet                a.b.c.d/xy

options:
  -h, --help            Show this help message and exit.
  -s SOURCE, --source SOURCE
                        The source address to ping from. If not specified, a best effort will be made to decide the source address.
  -v, --verbose         Show information in real time.
  -a, --all-hosts       Print all hosts, including unreachable ones.
  -A, --asynchronous    Run asynchronously instead of multithreaded.
  -u, --user            Run in user mode. Generally significantly faster, but may spike CPU usage. This option supercedes the -A, --asyncrhonous option. Not recommended for medium- to large-sized networks.
```

# Installation
## pipx (recommended)
To install with [pipx](https://github.com/pypa/pipx), simply run the following command:

```
pipx install git+https://github.com/WillChamness/pyscanr
```

To run with root in Linux conviniently, run the following command:
```
cd /usr/bin
sudo ln -s /home/myusername/.local/pipx/venvs/pyscanr/bin/pyscanr pyscanr
```
To update for root, your user will have to run `pipx upgrade pyscanr`

## Windows
* Download the `pyscanr.exe` file from the Releases page
* Create the `%USERPROFILE%\.local` and `%USERPROFILE%\.local\bin` folders
* Move `pyscanr.exe` to `%USERPROFILE%\.local\bin`
* Add `%USERPROFILE%\.local\bin` to your user's PATH
    1. Open File Explorer
    2. Right click `This PC`
    3. Click `Properties`
    4. Click `Advanced system settings`
    5. Go to the `Advanced` tab
    6. Click `Environment Variables`
    7. Double click `PATH` for your user (NOT the system)
    8. Click `New` and add `%USERPROFILE%\.local\bin`
* Open a new CMD instance
* Run `pyscanr -h` to verify installation
 
## Linux
* Download the `pyscanr.linux` file from the Releases page
* If you want to add this program to your user only:
    1. Run `mkdir -p ~/.local/bin`
    2. Assuming the executable is in your Downloads folder, run `mv ~/Downloads/pyscanr.linux ~/.local/bin/pyscanr`
    3. Run `chmod u+x ~/.local/bin/pyscanr`
    4. Add `$HOME/.local/bin` to your $PATH
        * Exact steps may vary. If using Bash:
        * Add `export PATH=$HOME/.local/bin/:$PATH` to your `.bashrc` file
    5. To run with root, you may have to run `sudo $(which pyscanr)`
* If you want to install globally:
    * Assuming the executable is in your Downloads folder, run `sudo mv ~/Downloads/pyscanr.linux /usr/bin/pyscanr`
* Open a new terminal instance
* Run `pyscanr -h` to verify installation


## Run Directly With Python
This option is generally not recommended, but it is available if you have Python installed and need to run the CLI app only a handful of times.

### Downloading With `git`
Run the following commands:
```
git clone https://github.com/WillChamness/pyscanr
cd pyscanr
python -m venv env
source env/scripts/activate || env\Scripts\activate
pip install -r requirements.txt
```

If using PowerShell:
```
git clone https://github.com/WillChamness/pyscanr
cd pyscanr
pythen -m venv env env\Scripts\activate.ps1
pip install -r requirements.txt
```

Verify installation with `python -m pyscanr -h`

### Downloading from github.com
* Click `Code` and `Download ZIP`
* Extract and navigate to your terminal to the root of the project
* Run the following commands:
```
python -m venv env
source env/scripts/activate || env\Scripts\activate
pip install -r requirements.txt
```
* If using PowerShell:
```
python -m venv env
env\Scripts\activate.ps1
pip install -r requirements.txt
```

Verify installation with `python -m pyscanr -h`
