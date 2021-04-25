# Opswat-File-Scanner

Python script that calls opswat's metadefender API endpoints to perform a hash lookup and file upload to scan a file for viruses

## Check Python Version

This script is intended to use with Python 3.8.x which should come preinstalled with Ubuntu 18.04+

Check your python version using

```
python3 ––version
```

or

```
python ––version
```

## Installation

Install python3 using

```bash
sudo apt install python3.8
```

## Usage

### Specify API Key

Before running the script, your own apikey must be provided. Please open `opswat.py` with a text editor of your choice and edit `line 7` with your metadefender API key
```python
apikey = ""
```

### Commands

```bash
python3 opswat.py <filename>
```

or

```bash
python opswat.py <filename>
```

`<filename>` should be inside the same directory as `opswat.py`

## Example

```bash
python3 opswat.py sampletext.txt
```