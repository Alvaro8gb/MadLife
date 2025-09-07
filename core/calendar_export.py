"""
Calendar export utilities for MadLife Event Search Application.

This module provides functionality to export events to various calendar formats
including Google Calendar, Outlook, Yahoo Calendar, and ICS files.
"""

import urllib.parse
import pandas as pd
from datetime import datetime


def create_calendar_export_links(event_data):
    """
    Create calendar export links for an event.
    
    Args:
        event_data (dict): Dictionary containing event information
        
    Returns:
        dict: Dictionary with calendar platform URLs
    """
    title = event_data.get('title', 'Evento Madrid')
    description = event_data.get('description_preview', '') + f"\n\nMás información: {event_data.get('url', '')}"
    location = f"{event_data.get('venue', '')}, {event_data.get('district', '')}, Madrid"
    
    event_date = event_data.get('date', '')
    event_time = event_data.get('time', '00:00')
    
    try:
        # Try to parse the full datetime
        if event_date:
            date_obj = pd.to_datetime(event_date)
            if event_time and event_time != '':
                # Combine date and time
                time_parts = event_time.split(':')
                if len(time_parts) >= 2:
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    start_datetime = date_obj.replace(hour=hour, minute=minute)
                else:
                    start_datetime = date_obj
            else:
                start_datetime = date_obj
        else:
            start_datetime = datetime.now()
            
        # End time (2 hours later by default)
        end_datetime = start_datetime + pd.Timedelta(hours=2)
        
        # Format for Google Calendar (YYYYMMDDTHHMMSSZ)
        start_str = start_datetime.strftime('%Y%m%dT%H%M%S')
        end_str = end_datetime.strftime('%Y%m%dT%H%M%S')
        
    except Exception:
        # Fallback to current time if parsing fails
        now = datetime.now()
        start_str = now.strftime('%Y%m%dT%H%M%S')
        end_str = (now + pd.Timedelta(hours=2)).strftime('%Y%m%dT%H%M%S')
    
    google_calendar_url = (
        f"https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={urllib.parse.quote(title)}"
        f"&dates={start_str}/{end_str}"
        f"&details={urllib.parse.quote(description)}"
        f"&location={urllib.parse.quote(location)}"
    )
    
    outlook_url = (
        f"https://outlook.live.com/calendar/0/deeplink/compose?subject={urllib.parse.quote(title)}"
        f"&startdt={start_str}&enddt={end_str}"
        f"&body={urllib.parse.quote(description)}"
        f"&location={urllib.parse.quote(location)}"
    )
    
    # Yahoo Calendar URL
    yahoo_url = (
        f"https://calendar.yahoo.com/?v=60&view=d&type=20"
        f"&title={urllib.parse.quote(title)}"
        f"&st={start_str}&dur=0200"
        f"&desc={urllib.parse.quote(description)}"
        f"&in_loc={urllib.parse.quote(location)}"
    )
    
    return {
        'google': google_calendar_url,
        'outlook': outlook_url,
        'yahoo': yahoo_url
    }


def generate_ics_content(event_data):
    """
    Generate ICS (iCalendar) file content for the event.
    
    Args:
        event_data (dict): Dictionary containing event information
        
    Returns:
        str: ICS file content as string
    """
    title = event_data.get('title', 'Evento Madrid')
    description = event_data.get('description_preview', '') + f"\\n\\nMás información: {event_data.get('url', '')}"
    location = f"{event_data.get('venue', '')}, {event_data.get('district', '')}, Madrid"
    
    # Parse date and time
    event_date = event_data.get('date', '')
    event_time = event_data.get('time', '00:00')
    
    try:
        if event_date:
            date_obj = pd.to_datetime(event_date)
            if event_time and event_time != '':
                time_parts = event_time.split(':')
                if len(time_parts) >= 2:
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    start_datetime = date_obj.replace(hour=hour, minute=minute)
                else:
                    start_datetime = date_obj
            else:
                start_datetime = date_obj
        else:
            start_datetime = datetime.now()
            
        end_datetime = start_datetime + pd.Timedelta(hours=2)
        
        # Format for ICS (YYYYMMDDTHHMMSS)
        start_str = start_datetime.strftime('%Y%m%dT%H%M%S')
        end_str = end_datetime.strftime('%Y%m%dT%H%M%S')
        created_str = datetime.now().strftime('%Y%m%dT%H%M%SZ')
        
    except Exception:
        now = datetime.now()
        start_str = now.strftime('%Y%m%dT%H%M%S')
        end_str = (now + pd.Timedelta(hours=2)).strftime('%Y%m%dT%H%M%S')
        created_str = now.strftime('%Y%m%dT%H%M%SZ')
    
    # Generate unique ID
    uid = f"madrid-event-{hash(title + start_str)}@madlife.com"
    
    desc = description.replace('\n', '\\n') 

    ics_content = f"""
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//MadLife//Madrid Events//ES
    BEGIN:VEVENT
    UID:{uid}
    DTSTAMP:{created_str}
    DTSTART:{start_str}
    DTEND:{end_str}
    SUMMARY:{title}
    DESCRIPTION:{desc}
    LOCATION:{location}
    STATUS:CONFIRMED
    SEQUENCE:0
    END:VEVENT
    END:VCALENDAR
    
    """
    
    return ics_content


def render_calendar_export_buttons(calendar_links):
    """
    Render HTML buttons for calendar export.
    
    Args:
        calendar_links (dict): Dictionary with calendar platform URLs
        
    Returns:
        str: HTML string with styled buttons
    """
    return f"""
    <div style="display: flex; flex-direction: column; gap: 8px;">
        <a href="{calendar_links['google']}" target="_blank" style="text-decoration: none;">
            <button style="width: 100%; padding: 8px; background-color: #4285f4; color: white; border: none; border-radius: 4px; cursor: pointer;">
                📅 Google Calendar
            </button>
        </a>
        <a href="{calendar_links['outlook']}" target="_blank" style="text-decoration: none;">
            <button style="width: 100%; padding: 8px; background-color: #0078d4; color: white; border: none; border-radius: 4px; cursor: pointer;">
                📅 Outlook Calendar
            </button>
        </a>
        <a href="{calendar_links['yahoo']}" target="_blank" style="text-decoration: none;">
            <button style="width: 100%; padding: 8px; background-color: #7b0099; color: white; border: none; border-radius: 4px; cursor: pointer;">
                📅 Yahoo Calendar
            </button>
        </a>
    </div>
    """


def render_quick_calendar_button(calendar_links):
    """
    Render a quick calendar export button for search results.
    
    Args:
        calendar_links (dict): Dictionary with calendar platform URLs
        
    Returns:
        str: HTML string with styled button
    """
    return f'<a href="{calendar_links["google"]}" target="_blank"><button style="width: 100%; padding: 4px; background-color: #4285f4; color: white; border: none; border-radius: 4px; font-size: 12px;">📅 + Calendario</button></a>'
