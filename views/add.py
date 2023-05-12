from flask import Blueprint, render_template, redirect, request, session, jsonify
from utils.firebase import add_to_firestore, update_firestore, upload_images
from config import fetch_db
from utils.auth import login_required

add = Blueprint("add", __name__)


@add.route("/edit/<pid>", methods=["GET"])
def edit(pid):
    return render_template("edit.html", pid=pid)


@add.route("/add-1", defaults={"pid": None}, methods=["GET", "POST"])
@add.route("/add-1/<pid>", methods=["GET", "POST"])
@login_required
def add_loc(pid):
    if request.method == "POST":
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
        if pid:
            update_firestore(data, pid, "posts")
            return redirect("/edit/" + pid)
        else:
            add_to_firestore(data, "posts")
            return redirect("/add-2")
    else:
        if pid:
            ref = (
                fetch_db()
                .collection("posts")
                .document(pid + "|" + str(session["user"]["uid"]))
            )
            doc = ref.get().to_dict()
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
    from utils.firebase import convert_date

    if request.method == "POST":
        type = request.form["type"].strip()
        vfrom = convert_date(request.form["from"])
        to = convert_date(request.form["to"])
        data = {
            "type": type,
            "from": vfrom,
            "to": to,
        }
        update_firestore(
            data, session["user"]["creation_id"] if not pid else pid, "posts"
        )
        if pid:
            return redirect("/edit/" + pid)
        return redirect("/add-3")
    else:
        if pid:
            ref = (
                fetch_db()
                .collection("posts")
                .document(pid + "|" + str(session["user"]["uid"]))
            )
            doc = ref.get().to_dict()
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
    if request.method == "POST":
        space = request.form["space"].strip()
        data = {
            "space": space,
        }
        update_firestore(
            data, session["user"]["creation_id"] if not pid else pid, "posts"
        )
        if pid:
            return redirect("/edit/" + pid)
        return redirect("/add-4")
    else:
        if pid:
            ref = (
                fetch_db()
                .collection("posts")
                .document(pid + "|" + str(session["user"]["uid"]))
            )
            doc = ref.get().to_dict()
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
        if pid:
            return redirect("/edit/" + pid)
        return redirect("/add-5")
    else:
        if pid:
            ref = (
                fetch_db()
                .collection("posts")
                .document(pid + "|" + str(session["user"]["uid"]))
            )
            doc = ref.get().to_dict()
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
    if request.method == "POST":
        value = request.form["desc"]
        data = {
            "description": value,
        }
        update_firestore(
            data, session["user"]["creation_id"] if not pid else pid, "posts"
        )
        if pid:
            return redirect("/edit/" + pid)
        return redirect("/add-6")
    else:
        if pid:
            ref = (
                fetch_db()
                .collection("posts")
                .document(pid + "|" + str(session["user"]["uid"]))
            )
            doc = ref.get().to_dict()
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
        if pid:
            return redirect("/edit/" + pid)
        return redirect("/add-7")
    else:
        if pid:
            ref = (
                fetch_db()
                .collection("posts")
                .document(pid + "|" + str(session["user"]["uid"]))
            )
            doc = ref.get().to_dict()
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
        if pid:
            return redirect("/edit/" + pid)
        return redirect("/add-8")
    else:
        if pid:
            ref = (
                fetch_db()
                .collection("posts")
                .document(pid + "|" + str(session["user"]["uid"]))
            )
            doc = ref.get().to_dict()
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
        if pid:
            return redirect("/edit/" + str(pid))
        return redirect("/view/" + str(pid))
    else:
        if pid:
            ref = (
                fetch_db()
                .collection("posts")
                .document(pid + "|" + str(session["user"]["uid"]))
            )
            doc = ref.get().to_dict()
            if not doc:
                return render_template(
                    "message.html", error_message="Post not found", status_code=404
                )
            return render_template("add-1-8.html", doc=doc)
        else:
            return render_template("add-1-8.html")
