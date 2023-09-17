from flask import session
from google.cloud.exceptions import GoogleCloudError

from utils.render import render_message
from utils.time import convert_date


def address_data(request):
    """
    Add an address to the database

    :param adress_line: The address line
    :param apt: The apartment number, defaults to None
    :param district: The district, defaults to None

    :return: A message
    """
    adress_line = request.form["address_line"].strip().split(",")
    apt = request.form["address_line2"].strip()
    district = None
    if len(adress_line) == 4:
        loc = adress_line[0]
        city = adress_line[1]
        district = adress_line[2]
        country = adress_line[3]
    elif len(adress_line) == 3:
        loc = adress_line[0]
        city = adress_line[1]
        country = adress_line[2]
    else:
        return render_message(
            400, "Please enter a full address (city, state, country...)"
        )
    data = {
        "loc": loc,
        "city": city,
        "district": district if district else "None",
        "country": country,
        "apt": apt if apt else "None",
        "user_uid": session["user"]["uid"],
    }
    return data


def tags_data(request):
    basics = request.form.getlist("basics")
    views = request.form.getlist("views")
    safety = request.form.getlist("safety")
    standout = request.form.getlist("standout")
    data = {
        "tags": {
            "basics": basics,
            "views": views,
            "safety": safety,
            "standout": standout,
        },
    }
    return data


def type_date_data(request):
    typ = request.form["type"].strip()
    vfrom = convert_date(request.form["from"])
    to = convert_date(request.form["to"])
    data = {
        "type": typ,
        "from": vfrom,
        "to": to,
    }
    return data


def basic_data(request):
    bedrooms = request.form["bedrooms"]
    guests = request.form["guests"]
    baths = request.form["baths"]
    beds = request.form["beds"]
    data = {
        "bedrooms": bedrooms,
        "baths": baths,
        "guests": guests,
        "beds": beds,
    }
    return data


def price_data(request):
    price = request.form["price"]
    month_disc = request.form["month-disc"]
    year_disc = request.form["year-disc"]
    data = {
        "price": price,
        "month_disc": month_disc,
        "year_disc": year_disc,
    }
    return data


def user_data(user):
    try:
        desc = user.custom_claims["description"]
        phone = user.custom_claims["phone"]
    except GoogleCloudError:
        desc = ""
        phone = ""

    data = {
        "displayName": user.display_name,
        "email": user.email,
        "description": desc,
        "uid": user.uid,
        "photoURL": user.photo_url,
        "phoneNumber": phone,
    }
    return data
