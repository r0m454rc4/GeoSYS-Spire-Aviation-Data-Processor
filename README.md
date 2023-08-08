# GeoSYS Spire Aviation Data Processor

## Description
GeoSYS Spire Aviation Data Processor is a set of scripts that fetch data from the Spire Aviation API, filters it using pandas, and converts it to JSON format. Additionally, it includes a utility script to delete old files to manage storage efficiently.

## Installation
To use GeoSYS Spire Aviation Data Processor, you need Python 3.6 or above.

1. Clone the repository: `git clone https://github.com/romasarca/GeoSYS-Spire-Aviation-Data-Processor.git`
2. Navigate to the project folder: `cd GeoSYS-Spire-Aviation-Data-Processor`
3. Install the required dependencies: `pip install -r requirements.txt`

## Configuration
Before running the "main.py" script, make sure to set up the API credentials in `env.yaml` file.

Additionally, you need to specify the directory to store the data from the API in the Python files. Open the following Python files and change the `DATA_STORAGE_DIRECTORY` variable to your desired folder path:

- main.py
- csvToJSON.py
- deleteOldFiles.py

For example:

```
main.py

# Change this to your desired data storage directory path
DATA_STORAGE_DIRECTORY = '/path/to/your/data/folder'
```
## Usage
### Fetch and Filter Data
To fetch data from the Spire Aviation API, filter it, and start generating parsed json and csv files, run the following command:

```python
python3 main.py
```