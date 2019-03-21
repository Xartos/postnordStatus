#!/usr/bin/python3

import sys
import json
import requests
import argparse
import logging


def getStatus(url, headers, data, trackID, all = False, status = False):
  logging.debug("Fetching status from url '{}' with all: '{}' and status: '{}'".format(url, all, status))
  try:
    response = requests.post(url, data = data, headers = headers)
  except Exception as err:
    logging.error("Got error '{}' when fetching from '{}'".format(err, url))
    exit(1)

  responseJson = response.json()
  logging.debug("Got response '{}'".format(responseJson))

  ## Throw exception instead?
  if 'data' not in responseJson:
    logging.error("Got an error response, maybe the trackID dont exist?")
    if 'compositeFault' in responseJson:
      for err in responseJson['compositeFault']:
        logging.error("[{}] {}".format(err['faultCode'], err['explanationText']))
    else:
      logging.error(responseJson)
    return
  elif len(responseJson['data'][trackID]['checkpoints']) == 0:
    logging.error("No shippment for trackID")
    return

  if all:
    result = json.dumps(responseJson['data'], indent = 2)
    result = result.encode('utf-8').decode('unicode_escape')
  else:
    if status:
      result = responseJson['data'][trackID]['checkpoints'][-1]['status_desc']
    else:
      events = responseJson['data'][trackID]['checkpoints']
      locationName = ""
      for event in events:
          if 'city' in event and event['city'] != ".":
            locationName = event['city']
          elif 'country_code' in event:
            locationName = event['country_code']
      result = responseJson['data'][trackID]['checkpoints'][-1]['status_desc']
      if locationName != "":
          result += " (" + locationName + ")"
  return result

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Fetch status for a postnord package')
  parser.add_argument('TrackID', help='The tracking ID to fetch')
  parser.add_argument('-a', '--all', default=False, help='Return the whole json thats fetched', action='store_true')
  parser.add_argument('-v', '--verbose', default=False, help='Set logging to debug mode', action='store_true')
  parser.add_argument('-s', '--status', default=False, help='Show only a very short status string', action='store_true')
  parser.add_argument('-l', '--locale', default="sv", help='Set the locale string (Default: "sv")')
  args = parser.parse_args()

  if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Called with args: '{}'".format(args))
  else:
    logging.basicConfig(level=logging.ERROR)

  # curl -s 'https://wishpost.wish.com/api/tracking/search' -H 'Accept-Language: en-US,en;q=0.5' --compressed -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' --data 'ids%5B%5D=YT1906601224004271&api_name=tracking%2Fsearch&params_num=1' | jq -M '.["data"]["YT1906601224004271"]["checkpoints"][-1]["status_desc"]'
  url = "https://wishpost.wish.com/api/tracking/search"

  headers = {"Accept-Language": "en-US,en;q=0.5", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
  data = "ids%5B%5D={}&api_name=tracking%2Fsearch&params_num=1".format(args.TrackID)

  #response = getStatus(url, args.all, args.status)
  response = getStatus(url, headers, data, args.TrackID, args.all, args.status)

  if response:
    print(response)
  else:
    exit(1)
