from flask import Flask, redirect, render_template, request, url_for, make_response
import csv
import json


def get_user_by_name(name):
    with open("./data.csv", "r") as file:
        csv_reader = csv.reader(file)
        contents = list(csv_reader)

    user_row = None
    for row in contents:
        if row[0].lower() == name.lower():
            user_row = row

    return user_row


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
        "screentime": user[2],
        "gender": user[3],
        "favourite music": user[4],
        "favourite pet": user[5],
        "favourite food": user[6],
        "favourite holiday": user[8],
        "favourite season": user[7],
    }


def get_user_matches(uuid):
    with open("./graph.json", "r") as file:
        graph = json.load(file)

    links_with_user = [
        link
        for link in graph["links"]
        if link["source"] == uuid or link["target"] == uuid
    ]

    links_with_user.sort(key=lambda link: link["weight"], reverse=True)

    return links_with_user


def create_app():
    app = Flask(__name__)

    @app.get("/<name>")
    def home(name):
        user = get_user_by_name(name)
        # user_uuid = request.cookies.get("user")
        # user = get_user(user_uuid)

        if user is None:
            return redirect(url_for("login"))

        user_uuid = user[-1]

        current_user = user_to_dict(user, is_current_user=True)

        user_matches = get_user_matches(user_uuid)

        best_match = user_matches[0]
        if best_match["source"] == user_uuid:
            matched_user_uuid = best_match["target"]
        else:
            matched_user_uuid = best_match["source"]

        matched_user = user_to_dict(get_user(matched_user_uuid))

        displayed_fields = [
            "age",
            "gender",
            "favourite music",
            "favourite holiday",
            "favourite pet",
            "favourite season",
            "favourite food",
            "screentime",
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

    return app
