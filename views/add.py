""" This module contains all the routes related to adding a new post. """
from flask import Blueprint, redirect, render_template, request, session

from utils.add import (
    address_data,
    basic_data,
    price_data,
    tags_data,
    type_date_data,
)
from utils.auth import login_required
from utils.firebase import (
    add_to_firestore,
    firebase_get,
    update_firestore,
    upload_images,
)
from utils.render import render_message
from utils.time import convert_date

add = Blueprint("add", __name__)


def get_add_page(pid, template):
    """
    Get the specific add page for a post.

    @param pid - pid of the post to get the page for
    @param template - template to render

    @return the template to render
    """
    if pid:
        with firebase_get("posts", f"{pid}|{session['user']['uid']}") as doc:
            # If doc is not found return 404
            if not doc:
                return render_message(404, "Post not found")
            return render_template(template, doc=doc)
    return render_template(template)


@add.route("/edit/<int:pid>", methods=["GET"])
def edit(pid: int):
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
@add.route("/add-1/<int:pid>", methods=["GET", "POST"])
@login_required
def add_loc(pid: int):
    """
    Add or edit a location to the database. This is a form to allow users
    to enter an address in the format of a city state and country

    @param pid - Identifier of the person to add to the database

    @return redirect to the next step in the add process.
            If you are editing the post, redirect to the property page.
    """
    # This is the main entry point for the firestore.
    if request.method == "POST":
        data = address_data(request)
        # Add or edit a user s post.
        if pid:
            update_firestore(data, pid, "posts")
            return redirect("/edit/" + str(pid))
        add_to_firestore(data, "posts")
        return redirect("/add-2")
    else:
        # This is the main page for the user s post
        return get_add_page(pid, "add-1.html")


@add.route("/add-2", defaults={"pid": None}, methods=["GET", "POST"])
@add.route("/add-2/<int:pid>", methods=["GET", "POST"])
@login_required
def add_type(pid: int):
    """
    Add or edit a type of a post. This can be an apartment, house, exprience and so on. Also includes the dates of availability.

    @param pid - pid of the post to add type to

    @return redirect to the next step in the add process.
            If you are editing the post, redirect to the property page.
    """

    # POST request. form type from date to date
    if request.method == "POST":
        data = type_date_data(request)
        update_firestore(
            data, session["user"]["creation_id"] if not pid else pid, "posts"
        )
        # Redirect to edit page if pid is not set
        return redirect("/add-3") if not pid else redirect("/edit/" + str(pid))
    else:
        # This is the main page for the user s post
        return get_add_page(pid, "add-1-1.html")


@add.route("/add-3", defaults={"pid": None}, methods=["GET", "POST"])
@add.route("/add-3/<int:pid>", methods=["GET", "POST"])
@login_required
def add_space(pid: int):
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
        return redirect("/add-4") if not pid else redirect("/edit/" + str(pid))
    else:
        # This is the main page for the user s post
        return get_add_page(pid, "add-1-2.html")


@add.route("/add-4", defaults={"pid": None}, methods=["GET", "POST"])
@add.route("/add-4/<int:pid>", methods=["GET", "POST"])
@login_required
def add_tags(pid: int):
    """
    Add or edit the tags of the post. These tags are used to describe the amenities of the property.

    @param pid - id of the post to add tags to

    @return redirect to the next step in the add process.
            If you are editing the post, redirect to the property page.
    """
    # Add a new post to the firestore
    if request.method == "POST":
        data = tags_data(request)
        update_firestore(
            data, session["user"]["creation_id"] if not pid else pid, "posts"
        )
        # Redirect to edit page if pid is not set
        return redirect("/add-5") if not pid else redirect("/edit/" + str(pid))
    else:
        # This is the main page for the user s post
        return get_add_page(pid, "add-1-4.html")


@add.route("/add-5", defaults={"pid": None}, methods=["GET", "POST"])
@add.route("/add-5/<int:pid>", methods=["GET", "POST"])
@login_required
def add_desc(pid: int):
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
        return redirect("/add-6") if not pid else redirect("/edit/" + str(pid))
    else:
        return get_add_page(pid, "add-1-5.html")


@add.route("/add-6", defaults={"pid": None}, methods=["GET", "POST"])
@add.route("/add-6/<int:pid>", methods=["GET", "POST"])
@login_required
def add_image(pid: int):
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
        return redirect("/add-7") if not pid else redirect("/edit/" + str(pid))
    else:
        return get_add_page(pid, "add-1-6.html")


@add.route("/add-7", defaults={"pid": None}, methods=["GET", "POST"])
@add.route("/add-7/<int:pid>", methods=["GET", "POST"])
@login_required
def add_basics(pid: int):
    """
    Add or edit the basics of the post. These are the basic details of the property.
    Bathrooms, bedrooms, beds etc.

    @param pid - id of the post to add basics to

    @return redirect to the next step in the add process.
            If you are editing the post, redirect to the property page.
    """
    # Add a new post to the firestore
    if request.method == "POST":
        data = basic_data(request)
        update_firestore(
            data, session["user"]["creation_id"] if not pid else pid, "posts"
        )
        # Redirect to edit page if pid is not set
        return redirect("/add-8") if not pid else redirect("/edit/" + str(pid))
    else:
        return get_add_page(pid, "add-1-7.html")


@add.route("/add-8", defaults={"pid": None}, methods=["GET", "POST"])
@add.route("/add-8/<int:pid>", methods=["GET", "POST"])
@login_required
def add_prices(pid: int):
    """
    Add the price to a post. You can also add the monthly or yearly discount

    @param pid - pid of the post to add prices to

    @return redirect to the next step in the add process.
            If you are editing the post, redirect to the property page.
    """
    if request.method == "POST":
        data = price_data(request)
        update_firestore(
            data, session["user"]["creation_id"] if not pid else pid, "posts"
        )
        pid = session["user"]["creation_id"]
        session["user"][
            "creation_id"
        ] = ""  # this clears the session creation id so the next time you add a
        # post it will be a new post and wont overwrite the old one
        if pid:
            return redirect("/edit/" + str(pid))
        return redirect("/view/" + str(pid))
    else:
        return get_add_page(pid, "add-1-8.html")
