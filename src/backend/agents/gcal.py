# from typing import Callable
# from pydantic import Field
from typing import Callable
from pydantic import Field
from langchain.tools.base import BaseTool

import datetime
import os.path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

class gcalendar:
  def __init__(self,SCOPES=["https://www.googleapis.com/auth/calendar.readonly"],  SERVICE_ACCOUNT_FILE='/tmp/credentials.json',CALENDAR_ID='ahmed.aviata@gmail.com'):
    self.SCOPES = SCOPES
    self.SERVICE_ACCOUNT_FILE = SERVICE_ACCOUNT_FILE
    self.CALENDAR_ID = CALENDAR_ID
  
  def get_events(self, MAX_RESULTS=10):
    creds = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
    try:
      service = build("calendar", "v3", credentials=creds)

      # Call the Calendar API
      now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
      print(f"Getting the upcoming {MAX_RESULTS} events")
      
      events_result = (
          service.events()
          .list(
              # calendarId="primary",
              calendarId=self.CALENDAR_ID,
              timeMin=now,
              maxResults=MAX_RESULTS,
              singleEvents=True,
              orderBy="startTime",
          )
          .execute()
      )
      events = events_result.get("items", [])

      if not events:
        return "No upcoming events found."

      # Prints the start and name of the next 10 events
      for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start, event["summary"])
      return events

    except HttpError as error:
      print(f"An error occurred: {error}")

class gcal(BaseTool):
    """Tool that reads calendar items"""
    name = "gcal"
    description = (
        "You can use this to read calendar items"
    )

    def _run(self, query: str) -> str:
        """Reads calendar items."""
        print("XXXXXX Entering the CALENDAR tool")
        c = gcalendar()
        response = c.get_events(5)
        # print(response)

        return response

    async def _arun(self, query: str) -> str:
        """Use the Cloudwatch tool asynchronously."""
        raise NotImplementedError("Cloudwatch tool does not support async")