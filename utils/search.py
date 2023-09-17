from utils.render import render_message
from utils.time import format_dates


def get_search_params(request):
    """
    Get the search parameters from the request object.

    @param request - The request object

    @return The search parameters, or an error message if the parameters are invalid
    """
    vfrom, to = format_dates(request.form["from"], request.form["to"])
    from_price = request.form["from-price"]
    to_price = request.form["to-price"]
    country = request.form["country"]
    guests = int(request.form["guests"]) if guests != "" else 0

    return vfrom, to, from_price, to_price, country, guests
