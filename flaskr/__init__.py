from flask import Flask, redirect, render_template, request, url_for, make_response
import csv
import json
from pprint import pprint


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


def get_explain_users():
    with open("./explainer_data.csv", "r") as file:
        csv_reader = csv.reader(file)
        contents = list(csv_reader)

    contents = contents[1:]

    return [{"name": row[0], "age": row[1], "gender": row[2]} for row in contents]


def create_app():
    app = Flask(__name__)

    @app.get("/")
    @app.get("/matcher")
    def login():
        return redirect(url_for("home", name="daan"))

    @app.get("/matcher/<name>")
    def home(name):
        # user_uuid = request.cookies.get("user")
        # user = get_user(user_uuid)

        user = get_user_by_name(name)

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

    @app.get("/matcher/<name>/graph")
    def graph(name):
        user = get_user_by_name(name)

        if user is None:
            return redirect(url_for("login"))

        user_uuid = user[-1]
        user_matches = get_user_matches(user_uuid)

        best_matches = user_matches[:5]

        nodes = {}
        for match in best_matches:
            node_uuids = [match["source"], match["target"]]

            for node_uuid in node_uuids:
                if node_uuid not in nodes:
                    node = get_user(node_uuid)
                    nodes[node_uuid] = user_to_dict(
                        node, is_current_user=user_uuid == node_uuid
                    )
                    nodes[node_uuid]["id"] = node_uuid

        network = {"nodes": [n for n in nodes.values()], "links": best_matches}

        return render_template(
            "graph_page.html",
            user=user_to_dict(user, is_current_user=True),
            network=json.dumps(network),
        )

    @app.get("/my-friends")
    def my_friends():
        return render_template("my-friends.html")

    @app.get("/explain")
    def explain():
        data = get_explain_users()

        return render_template("explain.html", users=data)

    return app
