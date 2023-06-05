""" This module contains functions for formatting dates and times. """
from datetime import datetime, timedelta


def format_dates(fromd, tod):
    """
    Formats dates for use in the app.

    @param fromd - The date from which to start the conversion.
    @param tod - The date to which to end the conversion.

    @return A tuple of datetime. date objects for the start and end dates of the conversion. If one of the dates is None the other will be
    """
    today = datetime.today()
    formatted_today = today.strftime("%m-%d-%Y")
    future_date = today + timedelta(days=365 * 10)
    formatted_date = future_date.strftime("%m-%d-%Y")

    vfrom = datetime.strptime(fromd, "%Y-%m-%d").date() if fromd else formatted_today
    to = datetime.strptime(tod, "%Y-%m-%d").date() if tod else formatted_date

    return vfrom, to


def format_firebase_date(dt_with_ns):
    """
    Formats a datetime. date with nanoseconds since January 1 1970 for use with Firebase.

    @param dt_with_ns - A datetime. date with nanoseconds since January 1 1970.

    @return A datetime. date with nanoseconds since January 1 1970.
    """
    return datetime.date(datetime(dt_with_ns.year, dt_with_ns.month, dt_with_ns.day))
