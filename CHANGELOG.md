# Changelog

All notable changes to this project will be documented in this file.

## 2.0.0

- Fixed #1 Rename misspelled additonal_data to additional_data on create_obj_from_data
- Fixed #3 Inverse partial flag: bool = False because it was wrong on update_obj_from_data

Notes:

You will need to change calls to `create_obj_from_data` according to #1 (rename additonal_data to additional_data)

You will need to change calls to `update_obj_from_data` according to #3 (if you supplied `partial`, you will need to reverse it: `true` -> `false` and `false` -> `true`)

## 1.3.0

- Addition of pagination proxy and pagination=off functionality (Thanks to @vikbhas)

## 1.2.5

- Bumped dependencies

## 1.2.4

- Enabled newer versions for all dependencies

## 1.2.3

- Added option to specify lookup_column for get_object_or_404

## 1.2.2

- Added order_by method

## 1.1.0

- Added headers to testing

## 1.0.0

- Bumped dependencies
- Added const documentation
- Added installation instructions and examples to README
- Added sqlalchemy session for db connection

## 0.2.0

- Added testing client
