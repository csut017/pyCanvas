# pyCanvas

This project contains a number of scripts to work with Canvas via Python.

## Prerequisites

The following components need to be installed:
* keyring
* requests
* pandas
* openpyxl

These can be installed via:
> python -m pip install requests keyring pandas openpyxl

## Retrieving Canvas identifiers

The required identifiers can be retrieved from the URLs in Canvas. Canvas normally uses a consistent structure for its URLs.

For example:
> https://canvas.auckland.ac.nz/courses/121853/assignments/461382

The course identifier immediately follow the keyword **courses**, and for this example will be `121853`. Likewise, we can see that the identifier of the assignment is `461382`.

## store_token

This script will store the token to access Canvas. It is required for all other scripts.

Usage:
> python store_token.py *token*

Where:
* *token*: the token to store

## download_marks

This script will download the marks for an assignment to an Excel spreadsheet.

Usage:
> python download_marks.py *course* *assignment* *file_path*

Where:
* *course*: the identifier of the course. This identifier can be retrieved from the Canvas URL.
* *assignment*: the identifier of the assignment. This identifier can be retrieved from the Canvas URL.
* *file_path*: the path to the file. This file will contain the marks after the download. **Note**: if the file already exists, it will be overwritten.

Options are:
* --rubrics: include rubrics in the download.
* --comments: include comments in the download. **Note**: these will be concatenated into a single cell.

## upload_marks

This script will download the marks for an assignment to an Excel spreadsheet.

Usage:
> python upload_marks.py *course* *assignment* *file_path*

Where:
* *course*: the identifier of the course. This identifier can be retrieved from the Canvas URL.
* *assignment*: the identifier of the assignment. This identifier can be retrieved from the Canvas URL.
* *file_path*: the path to the file. This file will contain the marks to download.


Options are:
* --rubrics: include rubrics in the upload. The names of the rubric items must be the column names. If the score matches a rating, then the rating label will be applied.
