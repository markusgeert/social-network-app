from flask import Flask, redirect, render_template, url_for, make_response, request, g
import csv
import json
import random


DEFAULT_FIELDS = [
    "age",
    "gender",
    "favourite music",
    "favourite holiday",
    "favourite pet",
    "favourite season",
    "favourite food",
    "screentime",
]


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


def get_random_user():
    with open("./data.csv", "r") as file:
        csv_reader = csv.reader(file)
        contents = list(csv_reader)[1:]

    return random.choice(contents)


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


def get_user_edges(uuid):
    with open("./graph.json", "r") as file:
        graph = json.load(file)

    links_with_user = [
        link
        for link in graph["links"]
        if link["source"] == uuid or link["target"] == uuid
    ]

    links_with_user.sort(key=lambda link: link["weight"], reverse=True)

    return links_with_user


def nodes_from_edges(edges, current_user_uuid=None):
    nodes = {}
    for match in edges:
        node_uuids = [match["source"], match["target"]]

        for node_uuid in node_uuids:
            if node_uuid not in nodes:
                print(current_user_uuid, node_uuid)

                node = get_user(node_uuid)
                nodes[node_uuid] = user_to_dict(
                    node, is_current_user=node_uuid == current_user_uuid
                )
                nodes[node_uuid]["id"] = node_uuid
                nodes[node_uuid]["match_score"] = match["weight"]

    return nodes


def get_explain_users():
    with open("./explainer_data.csv", "r") as file:
        csv_reader = csv.reader(file)
        contents = list(csv_reader)

    contents = contents[1:]

    return [{"name": row[0], "age": row[1], "gender": row[2]} for row in contents]


def create_app():
    app = Flask(__name__)

    app.jinja_env.globals.update(round=round)

    @app.get("/")
    def home():
        user_uuid = request.cookies.get("user_uuid")

        if user_uuid is None:
            user = get_random_user()
            user_uuid = user[-1]
        else:
            user = get_user(user_uuid)

        current_user = user_to_dict(user, is_current_user=True)
        user_edges = get_user_edges(user_uuid)

        users = nodes_from_edges(user_edges, user_uuid)
        del users[user_uuid]

        resp = make_response(
            render_template(
                "users/main.html",
                current_user=current_user,
                users=users.values(),
                fields=DEFAULT_FIELDS,
            )
        )

        resp.set_cookie("user_uuid", user_uuid)

        return resp

    @app.post("/refresh")
    def refresh():
        user = get_random_user()
        user_uuid = user[-1]

        current_user = user_to_dict(user, is_current_user=True)
        user_edges = get_user_edges(user_uuid)

        users = nodes_from_edges(user_edges, user_uuid)
        del users[user_uuid]

        resp = make_response(
            render_template(
                "users/main.html",
                current_user=current_user,
                users=users.values(),
                fields=DEFAULT_FIELDS,
            )
        )

        resp.set_cookie("user_uuid", user_uuid)

        return resp

    @app.get("/compare/<name>")
    def specific_match(name):
        user_uuid = request.cookies.get("user_uuid")

        if user_uuid is None:
            user = get_random_user()
            user_uuid = user[-1]
        else:
            user = get_user(user_uuid)

        current_user = user_to_dict(user, is_current_user=True)
        matched_user = user_to_dict(get_user_by_name(name))

        resp = make_response(
            render_template(
                "users/compare.html",
                current_user=current_user,
                matched_user=matched_user,
                fields=DEFAULT_FIELDS,
            )
        )

        resp.set_cookie("user_uuid", user_uuid)

        return resp

    @app.get("/graph")
    def graph():
        user_uuid = request.cookies.get("user_uuid")

        if user_uuid is None:
            user = get_random_user()
            user_uuid = user[-1]
        else:
            user = get_user(user_uuid)

        user_matches = get_user_edges(user_uuid)

        nodes = nodes_from_edges(user_matches, user_uuid)
        network = {"nodes": [n for n in nodes.values()], "links": user_matches}

        resp = make_response(
            render_template(
                "graph/main.html",
                current_user=user_to_dict(user, is_current_user=True),
                network=json.dumps(network),
            )
        )

        resp.set_cookie("user_uuid", user_uuid)

        return resp

    return app
