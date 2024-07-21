import json
import logging
import re
import shutil
import sys
from urllib import request
from urllib.error import HTTPError, URLError, ContentTooShortError
from socket import timeout
from pathlib import Path
from dotenv import dotenv_values


ENVFILE_REQUIRED_KEYS = ["URL", "API_PATH", "ARTIFACTS_PATH", "ARTIFACTS_FIELD", "ARTIFACT_REL_FILE_PATH_FIELD"]
OUTPUT_DIR = "output"


def check_envfile(envfile_contents):
    if len(envfile_contents) < 1:
        logging.error(
            "envfile not found. Please copy '.env.example', rename it '.env', and set the values within. "
            "Then, try again.")
        sys.exit(1)
    for x in ENVFILE_REQUIRED_KEYS:
        if x not in envfile_contents.keys():
            logging.error(
                f"Malformed envfile is missing required key {x}. Please make sure you have copied '.env.example.'"
                f"to '.env'.")
            sys.exit(1)


def json_to_dict(response) -> dict:
    return json.loads(response.read().decode('utf-8'))


def get_api_data(url: str) -> dict:
    try:
        logging.info("Fetching data from the API...")
        with request.urlopen(url, timeout=30) as response:
            return json_to_dict(response)
    except (HTTPError, URLError) as e:
        logging.exception(e)
        logging.error("Connection error. Could not download API data.")
        sys.exit(1)


def parse_artifact_paths(api_data, env_config) -> list[str]:
    artifact_paths = []
    try:
        artifacts = api_data[env_config["ARTIFACTS_FIELD"]]
        for x in artifacts:
            artifact_paths.append(x[env_config["ARTIFACT_REL_FILE_PATH_FIELD"]])
        return artifact_paths
    except KeyError:
        logging.error(api_data)
        logging.error(f"Provided API data does not contain required field '{env_config["ARTIFACTS_FIELD"]}'.")
        sys.exit(1)


def create_filenames(paths_list: list[str]):
    names = {}
    ver_str = ""
    for p in paths_list:
        # Strip the version string
        output_filename = re.sub(r'^[^/]+/([^-]+)-.*(\..*)$', r'\1\2', p)
        names.update({p: output_filename})
        # Check the version string
        new_ver_str = re.search(r'-(.*)(\..*)$', p).group(1)
        if ver_str == "":
            ver_str = new_ver_str
        elif new_ver_str != ver_str:
            logging.error(f"Inconsistent version string. First: {ver_str}, Other: {new_ver_str}")
    logging.info(f"Parsed version string: {ver_str}")
    return names


def download_artifact(remote_path, dest_name, env_config):
    url = f"{env_config["URL"]}{env_config["ARTIFACTS_PATH"]}/{remote_path}"
    output_path = f"{OUTPUT_DIR}/{dest_name}"
    logging.info(f"Downloading file: '{dest_name}' from {url}")
    try:
        with open(output_path, 'wb') as out_file:
            with request.urlopen(url, timeout=10) as response:
                shutil.copyfileobj(response, out_file)
    except PermissionError as e:
        logging.exception(e)
        logging.error(f"Cannot write to file {output_path}: Insufficient permissions")
        sys.exit(1)
    except timeout:
        logging.error(f"Connection timed out")
        sys.exit(1)
    except ContentTooShortError as e:
        logging.exception(e)
        logging.error("Download interrupted")
        sys.exit(1)
    except (HTTPError, URLError) as e:
        logging.exception(e)
        logging.error("Unable to download file. Please try again later.")
        sys.exit(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    # Envfile
    config = dotenv_values()
    check_envfile(config)

    # Output directory
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    data = get_api_data(config["URL"] + config["API_PATH"])
    paths = parse_artifact_paths(data, config)
    filenames = create_filenames(paths)
    for path, filename in filenames.items():
        download_artifact(path, filename, config)
    logging.info("Done!")
