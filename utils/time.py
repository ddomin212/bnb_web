from datetime import datetime, timedelta


def format_dates(fromd, tod):
    today = datetime.today()
    formatted_today = today.strftime('%m-%d-%Y')
    future_date = today + timedelta(days=365*10)
    formatted_date = future_date.strftime('%m-%d-%Y')

    vfrom = datetime.strptime(fromd, '%Y-%m-%d').date(
    ) if fromd else formatted_today
    to = datetime.strptime(tod, '%Y-%m-%d').date(
    ) if tod else formatted_date

    return vfrom, to


def format_firebase_date(dt_with_ns):
    return datetime.date(datetime(dt_with_ns.year, dt_with_ns.month, dt_with_ns.day))
