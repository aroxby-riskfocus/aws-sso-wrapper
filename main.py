#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess


def sso_login():
    subprocess.run(['aws', 'sso', 'login'], check=True)


def get_cached_path():
    CACHE_SUBDIR = '.aws/cli/cache'
    cache_path = Path.home() / CACHE_SUBDIR

    latest_cache = None
    latest_cache_time = 0
    for cache_file in cache_path.iterdir():
        stat = cache_file.stat()
        if not latest_cache or stat.st_ctime > latest_cache_time:
            latest_cache = cache_file
            latest_cache_time = stat.st_ctime

    if not latest_cache:
        raise RuntimeError('No cached login detected')

    return latest_cache


def get_cached_login():
    cached_path = get_cached_path()
    with cached_path.open() as fp:
        data = json.load(fp)
    return data['Credentials']


def create_exports(creds):
    mapping = {
        'AccessKeyId': 'AWS_ACCESS_KEY_ID',
        'SecretAccessKey': 'AWS_SECRET_ACCESS_KEY',
        'SessionToken': 'AWS_SESSION_TOKEN',
    }
    exports = []
    for cache_name, export_name in mapping.items():
        value = creds.get(cache_name)
        if value:
            exports.append(f'export {export_name}={value}')
    return exports


def create_credential_file_data(creds):
    mapping = {
        'AccessKeyId': 'aws_access_key_id',
        'SecretAccessKey': 'aws_secret_access_key',
        'SessionToken': 'aws_session_token',
    }
    lines = ['[default]', ]
    for cache_name, storage_name in mapping.items():
        value = creds.get(cache_name)
        if value:
            lines.append(f'{storage_name}={value}')
    return '\n'.join(lines) + '\n'


def write_credentials_file(file_data):
    FILE_SUBPATH = '.aws/credentials'
    file_path = Path.home() / FILE_SUBPATH
    with file_path.open('w') as fp:
        fp.write(file_data)


def main():
    sso_login()
    creds = get_cached_login()
    file_data = create_credential_file_data(creds)
    write_credentials_file(file_data)


if __name__ == '__main__':
    main()
