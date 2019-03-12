#!/usr/bin/python3

import sys
import json
import requests
import argparse
import logging


def getStatus(url, all = False, status = False):
  logging.debug("Fetching status from url '{}' with all: '{}' and status: '{}'".format(url, all, status))
  try:
    response = requests.get(url)
  except Exception as err:
    logging.error("Got error '{}' when fetching from '{}'".format(err, url))
    exit(1)

  responseJson = response.json()
  logging.debug("Got response '{}'".format(responseJson))

  ## Throw exception instead?
  if 'TrackingInformationResponse' not in responseJson:
    logging.error("Got an error response, maybe the trackID dont exist?")
    if 'compositeFault' in responseJson:
      for err in responseJson['compositeFault']:
        logging.error("[{}] {}".format(err['faultCode'], err['explanationText']))
    else:
      logging.error(responseJson)
    return
  elif len(responseJson['TrackingInformationResponse']['shipments']) == 0:
    logging.error("No shippment for trackID")
    return

  if all:
    result = json.dumps(responseJson['TrackingInformationResponse'], indent = 2)
    result = result.encode('utf-8').decode('unicode_escape')
  else:
    if status:
      result = responseJson['TrackingInformationResponse']['shipments'][0]['status']
    else:
      events = responseJson['TrackingInformationResponse']['shipments'][0]['items'][0]['events']
      locationName = ""
      for event in events:
          if 'locationType' in event['location']:
            locationName = event['location']['displayName']
      result = responseJson['TrackingInformationResponse']['shipments'][0]['statusText']['header']
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

  url = "https://ds.postnord.com/v2/trackandtrace/findByIdentifier.json?id={}&locale={}".format(args.TrackID, args.locale)

  response = getStatus(url, args.all, args.status)

  if response:
    print(response)
  else:
    exit(1)
