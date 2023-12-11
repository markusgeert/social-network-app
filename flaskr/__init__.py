from flask import Flask, redirect, render_template, request, url_for, make_response
import csv


def get_user(uuid):
    with open("./data.csv", "r") as file:
        csv_reader = csv.reader(file)
        contents = list(csv_reader)

    user_row = None
    for row in contents:
        if row[-1] == uuid:
            user_row = row

    return user_row


def user_to_dict(user, is_current_user=False):
    return {
        "firstname": user[0],
        "avatar_url": url_for("static", filename=f"profiles/{user[0].lower()}.png"),
        "is_current_user": is_current_user,
        "age": user[1],
        "gender": user[3],
        "favourite music": user[4],
        "favourite holiday": user[8],
        "favourite season": user[7],
        "favourite food": user[6],
    }


def create_app():
    app = Flask(__name__)

    @app.get("/")
    def home():
        user_uuid = request.cookies.get("user")

        user = get_user(user_uuid)
        if user is None:
            return redirect(url_for("login"))

        current_user = user_to_dict(user, is_current_user=True)
        matched_user = user_to_dict(get_user("3B27A88B-7A99-4E62-A6FA-0B7CCE00D5A8"))

        displayed_fields = [
            "age",
            "gender",
            "favourite music",
            "favourite holiday",
            "favourite season",
            "favourite food",
        ]

        resp = make_response(
            render_template(
                "matching_page.html",
                current_user=current_user,
                matched_user=matched_user,
                fields=displayed_fields,
            )
        )

        return resp

    @app.get("/login")
    def login():
        res = redirect(url_for("home"))

        res.set_cookie("user", "AAB5934A-1235-4969-A717-69026733E8A5")

        return res

    return app
