# -*- coding: utf-8 -*-
"""
@file Decrypter for HeidSQL Config export files


"""

from __future__ import unicode_literals, print_function

import fileinput
import json

_SPLIT_STRING = "<|||>"
_DEFAULT_INPUT_ENCODING = "utf8"
_SERVER_CONFIG_PREFIX = "Servers"
_SERVER_CONFIG_DELIMITER = "\\"
_SERVER_CONFIG_SUB_DELIMITER ="|"
_SERVER_PASSWORD_KEY ="Password"

def parse_config_line(config_line):
	"""
	Returns a dictionary, mapping the line's key to a value tuple

	:param config_line: unicode
	:return: dict
	"""
	config_line = config_line.decode(_DEFAULT_INPUT_ENCODING)
	line_tuple = config_line.strip().split(_SPLIT_STRING)
	return {line_tuple[0] : line_tuple[1:]}


def parse_raw_config_file(file_iterator):
	"""
	Reads lines from an iterator and parses the content into a dictionary

	:param file_iterator: iterable
	:return: dict
	"""
	config_data = {}
	for line in file_iterator:
		line_data = parse_config_line(line)
		config_data.update(line_data)
	return config_data


def decode_password(raw_password):
	"""
	Decodes the obfuscated password

	The password is encoded in shifted ASCII-HEX, the last character is the shift value. So to decode the
	password we need to remove + safe the shift value from the end, then take every two characters, convert them
	from ASCII-HEX to int, subtract the shift value and then generate the appropriate ASCII Character.

	:param raw_password: unicode
	:return: unicode
	"""
	shift = int(raw_password[-1])
	hex_password = raw_password[:-1]
	plain_password = ""
	for i in range(0, len(hex_password),2):
		plain_password += chr(int(hex_password[i:i+2], 16) - shift)
	return plain_password


def extract_server_data(config_data):
	"""
	Extract server data from the parsed config lines

	This enables us to re-use the HeidiSQL server list.

	:param config_data: dict
	:return: dict
	"""
	host_data = {}
	for data_key, value_tuple in config_data.items():
		if data_key.startswith(_SERVER_CONFIG_PREFIX):
			try:
				_, entry_name, value_key = data_key.split(_SERVER_CONFIG_DELIMITER)
				value = value_tuple[1]
				if value_key == _SERVER_PASSWORD_KEY:
					value = decode_password(value)
				try:
					host_data[entry_name][value_key] = value
				except KeyError:
					host_data[entry_name] = {value_key: value}
			except ValueError:
				# Ignore this line, it most probably contains additional data we don't want
				pass
	return host_data


def main():
	file_iterator =  fileinput.input()
	config_data = parse_raw_config_file(file_iterator)
	host_data = extract_server_data(config_data)

	print(json.dumps(host_data))

	return 0


if __name__ == "__main__":
	main()