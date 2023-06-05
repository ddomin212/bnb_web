""" This module contains all the routes related to adding a new post. """
from flask import Blueprint, render_template, redirect, request, session, jsonify
from utils.firebase import add_to_firestore, update_firestore, upload_images
from config import fetch_db
from utils.auth import login_required

add = Blueprint("add", __name__)


@add.route("/edit/<pid>", methods=["GET"])
def edit(pid):
    """
    View to edit a record. This is a special page for users
    who want to edit an existing record and presents them
    with various options to edit the record

    @param pid - ID of the record to edit. It's the same as the pid
    in the database but we don't know if it is a new record

    @return The template that renders the edit. html template and returns
    """
    return render_template("edit.html", pid=pid)


@add.route("/add-1", defaults={"pid": None}, methods=["GET", "POST"])
@add.route("/add-1/<pid>", methods=["GET", "POST"])
@login_required
def add_loc(pid):
    """
    Add or edit a location to the database. This is a form to allow users
    to enter an address in the format of a city state and country

    @param pid - Identifier of the person to add to the database

    @return redirect to the next step in the add process.
            If you are editing the post, redirect to the property page.
    """
    # This is the main entry point for the firestore.
    if request.method == "POST":
        adress_line = request.form["address_line"].strip().split(",")
        apt = request.form["address_line2"].strip()
        district = None
        # This function is used to display the address
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
            return render_template(
                "message.html",
                error_message="Please enter a full address (city, state, country...)",
                status_code=400,
            )
        data = {
            "loc": loc,
            "city": city,
            "district": district if district else "None",
            "country": country,
            "apt": apt if apt else "None",
            "user_uid": session["user"]["uid"],
        }
        # Add or edit a user s post.
        if pid:
            update_firestore(data, pid, "posts")
            return redirect("/edit/" + pid)
        else:
            add_to_firestore(data, "posts")
            return redirect("/add-2")
    else:
        # This is the main page for the user s post
        if pid:
            ref = (
                fetch_db()
                .collection("posts")
                .document(pid + "|" + str(session["user"]["uid"]))
            )
            doc = ref.get().to_dict()
            # If doc is not found return 404
            if not doc:
                return render_template(
                    "message.html", error_message="Post not found", status_code=404
                )
            return render_template("add-1.html", doc=doc)
        else:
            return render_template("add-1.html")


@add.route("/add-2", defaults={"pid": None}, methods=["GET", "POST"])
@add.route("/add-2/<pid>", methods=["GET", "POST"])
@login_required
def add_type(pid):
    """
    Add or edit a type of a post. This can be an apartment, house, exprience and so on.

    @param pid - pid of the post to add type to

    @return redirect to the next step in the add process.
            If you are editing the post, redirect to the property page.
    """
    from utils.firebase import convert_date

    # POST POST request. form type from date to date
    if request.method == "POST":
        typ = request.form["type"].strip()
        vfrom = convert_date(request.form["from"])
        to = convert_date(request.form["to"])
        data = {
            "type": typ,
            "from": vfrom,
            "to": to,
        }
        update_firestore(
            data, session["user"]["creation_id"] if not pid else pid, "posts"
        )
        # Redirect to edit page if pid is not set
        if pid:
            return redirect("/edit/" + pid)
        return redirect("/add-3")
    else:
        # This is the main page for the user s post
        if pid:
            ref = (
                fetch_db()
                .collection("posts")
                .document(pid + "|" + str(session["user"]["uid"]))
            )
            doc = ref.get().to_dict()
            # If doc is not found return 404
            if not doc:
                return render_template(
                    "message.html", error_message="Post not found", status_code=404
                )
            return render_template("add-1-1.html", doc=doc)
        else:
            return render_template("add-1-1.html")


@add.route("/add-3", defaults={"pid": None}, methods=["GET", "POST"])
@add.route("/add-3/<pid>", methods=["GET", "POST"])
@login_required
def add_space(pid):
    """
    Add or edit the provided space of the property.
    This can be a the whole apartement, a room or a bed.

    @param pid - pid of the post to add provided space to

    @return redirect to the next step in the add process.
            If you are editing the post, redirect to the property page.
    """
    # Add a new post to the firestore
    if request.method == "POST":
        space = request.form["space"].strip()
        data = {
            "space": space,
        }
        update_firestore(
            data, session["user"]["creation_id"] if not pid else pid, "posts"
        )
        # Redirect to edit page if pid is not set
        if pid:
            return redirect("/edit/" + pid)
        return redirect("/add-4")
    else:
        # This is the main page for the user s post
        if pid:
            ref = (
                fetch_db()
                .collection("posts")
                .document(pid + "|" + str(session["user"]["uid"]))
            )
            doc = ref.get().to_dict()
            # If doc is not found return 404
            if not doc:
                return render_template(
                    "message.html", error_message="Post not found", status_code=404
                )
            return render_template("add-1-2.html", doc=doc)
        else:
            return render_template("add-1-2.html")


@add.route("/add-4", defaults={"pid": None}, methods=["GET", "POST"])
@add.route("/add-4/<pid>", methods=["GET", "POST"])
@login_required
def add_tags(pid):
    """
    Add or edit the tags of the post. These tags are used to describe the amenities of the property.

    @param pid - id of the post to add tags to

    @return redirect to the next step in the add process.
            If you are editing the post, redirect to the property page.
    """
    # Add a new post to the firestore
    if request.method == "POST":
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
        update_firestore(
            data, session["user"]["creation_id"] if not pid else pid, "posts"
        )
        # Redirect to edit page if pid is not set
        if pid:
            return redirect("/edit/" + pid)
        return redirect("/add-5")
    else:
        # This is the main page for the user s post
        if pid:
            ref = (
                fetch_db()
                .collection("posts")
                .document(pid + "|" + str(session["user"]["uid"]))
            )
            doc = ref.get().to_dict()
            # If doc is not found return 404
            if not doc:
                return render_template(
                    "message.html", error_message="Post not found", status_code=404
                )
            return render_template("add-1-4.html", doc=doc)
        else:
            return render_template("add-1-4.html")


@add.route("/add-5", defaults={"pid": None}, methods=["GET", "POST"])
@add.route("/add-5/<pid>", methods=["GET", "POST"])
@login_required
def add_desc(pid):
    """
    Add or edit a post description.

    @param pid - id of the post to add description to

    @return redirect to the next step in the add process.
            If you are editing the post, redirect to the property page.
    """
    if request.method == "POST":
        value = request.form["desc"]
        data = {
            "description": value,
        }
        update_firestore(
            data, session["user"]["creation_id"] if not pid else pid, "posts"
        )
        # Redirect to edit page if pid is not set
        if pid:
            return redirect("/edit/" + pid)
        return redirect("/add-6")
    else:
        # This is the main page for the user s post.
        if pid:
            ref = (
                fetch_db()
                .collection("posts")
                .document(pid + "|" + str(session["user"]["uid"]))
            )
            doc = ref.get().to_dict()
            # If doc is not found return 404
            if not doc:
                return render_template(
                    "message.html", error_message="Post not found", status_code=404
                )
            return render_template("add-1-5.html", doc=doc)
        else:
            return render_template("add-1-5.html")


@add.route("/add-6", defaults={"pid": None}, methods=["GET", "POST"])
@add.route("/add-6/<pid>", methods=["GET", "POST"])
@login_required
def add_image(pid):
    """
    Add or edit the images of a post.

    @param pid - pid of the post to add images to

    @return redirect to the next step in the add process.
            If you are editing the post, redirect to the property page.
    """
    if request.method == "POST":
        img_urls = upload_images(request)
        data = {
            "images": img_urls,
        }
        update_firestore(
            data,
            session["user"]["creation_id"] if not pid else pid,
            "posts",
            images=True,
        )
        # Redirect to edit page if pid is not set
        if pid:
            return redirect("/edit/" + pid)
        return redirect("/add-7")
    else:
        # This is the main page for the user s post
        if pid:
            ref = (
                fetch_db()
                .collection("posts")
                .document(pid + "|" + str(session["user"]["uid"]))
            )
            doc = ref.get().to_dict()
            # If doc is not found return 404
            if not doc:
                return render_template(
                    "message.html", error_message="Post not found", status_code=404
                )
            return render_template("add-1-6.html", doc=doc)
        else:
            return render_template("add-1-6.html")


@add.route("/add-7", defaults={"pid": None}, methods=["GET", "POST"])
@add.route("/add-7/<pid>", methods=["GET", "POST"])
@login_required
def add_basics(pid):
    """
    Add or edit the basics of the post. These are the basic details of the property.
    Bathrooms, bedrooms, beds etc.

    @param pid - id of the post to add basics to

    @return redirect to the next step in the add process.
            If you are editing the post, redirect to the property page.
    """
    # Add a new post to the firestore
    if request.method == "POST":
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
        update_firestore(
            data, session["user"]["creation_id"] if not pid else pid, "posts"
        )
        # Redirect to edit page if pid is not set
        if pid:
            return redirect("/edit/" + pid)
        return redirect("/add-8")
    else:
        # This is the main page for the user s post
        if pid:
            ref = (
                fetch_db()
                .collection("posts")
                .document(pid + "|" + str(session["user"]["uid"]))
            )
            doc = ref.get().to_dict()
            # If doc is not found return 404
            if not doc:
                return render_template(
                    "message.html", error_message="Post not found", status_code=404
                )
            return render_template("add-1-7.html", doc=doc)
        else:
            return render_template("add-1-7.html")


@add.route("/add-8", defaults={"pid": None}, methods=["GET", "POST"])
@add.route("/add-8/<pid>", methods=["GET", "POST"])
@login_required
def add_prices(pid):
    """
    Add the price to a post. You can also add the monthly or yearly discount

    @param pid - pid of the post to add prices to

    @return redirect to the next step in the add process.
            If you are editing the post, redirect to the property page.
    """
    if request.method == "POST":
        price = request.form["price"]
        month_disc = request.form["month-disc"]
        year_disc = request.form["year-disc"]
        data = {
            "price": price,
            "month_disc": month_disc,
            "year_disc": year_disc,
        }
        update_firestore(
            data, session["user"]["creation_id"] if not pid else pid, "posts"
        )
        pid = session["user"]["creation_id"]
        session["user"]["creation_id"] = ""
        # Redirect to edit page if pid is set.
        if pid:
            return redirect("/edit/" + str(pid))
        return redirect("/view/" + str(pid))
    else:
        # This function is used to get the post s document
        if pid:
            ref = (
                fetch_db()
                .collection("posts")
                .document(pid + "|" + str(session["user"]["uid"]))
            )
            doc = ref.get().to_dict()
            # If doc is not found return 404
            if not doc:
                return render_template(
                    "message.html", error_message="Post not found", status_code=404
                )
            return render_template("add-1-8.html", doc=doc)
        else:
            return render_template("add-1-8.html")
