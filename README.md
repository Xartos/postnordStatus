# Postnord shippment status fetcher

Simple script that fetches the current status of a Postnord package

## Usage

`postnordStatus.py <Tracking ID>`

### Parameters

Flag | description
-----|------------
-a / --all | Prints the whole json that gets returned from the API call
-v / --verbose | Print all debug messages
-s / --status | Prints the very short status string e.g. "EN_ROUTE", "INFORMED", "STOPPED"