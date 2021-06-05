import json
from flask import Flask, session, redirect, request, url_for, Response, Blueprint
from functools import wraps
from . import mysql
from werkzeug.wrappers import response

api = Blueprint("api", __name__, url_prefix="/api")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        is_safe = ["GET"]
        if request.method not in is_safe:
            if "user" not in session:
                return redirect(url_for("home"))
            return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # safe http verbs
        is_safe = ["GET"]
        # if the http request verbs is not save
        if request.method not in is_safe:
            db_connection = mysql.connect()
            cursor = db_connection.cursor()
            # fetch user from database
            cursor.execute("SELECT * FROM users WHERE id=%s", (session["user"]["id"]))
            user = cursor.fetchone()
            # If user is admin , return response
            if user["is_admin"] == 1:
                return f(*args, **kwargs)
            # If user is not admin, redirect to home
            return redirect(url_for("home"))
        # If the http verb is safe, return response
        return f(*args, **kwargs)

    return decorated


@api.route("/artists", methods=["GET", "POST"])
def artists():
    db_connection = mysql.connect()
    cursor = db_connection.cursor()

    if request.method == "GET":
        cursor.execute("SELECT * FROM artists")
        query_result = cursor.fetchall()
        return Response(
            json.dumps(query_result), status=200, mimetype="application/json"
        )

    if request.method == "POST":
        try:
            cursor.execute(
                "SELECT * FROM artists WHERE artist_name=%s",
                (request.json["artist_name"]),
            )
            if cursor.fetchone() == None:
                cursor.execute(
                    "INSERT INTO artists (artist_name ,artist_image ,  artist_profile , artist_works_url) VALUES (%s , %s , %s , %s) ",
                    (
                        request.json["artist_name"],
                        request.json["artist_image"],
                        request.json["artist_profile"],
                        request.json["artist_works_url"],
                    ),
                )
                db_connection.commit()
                return Response(status=200)

            msg = {"error": [f"field {request.json['artist_name']} already exists"]}
            print(msg)
            return Response(json.dumps(msg), status=400, mimetype="application/json")

        except KeyError as err:
            res = {"error": [f"This field {str(err)} is required"]}
            return Response(json.dumps(res), status=400, mimetype="application/json")
        except Exception as e:
            print(e)
            return Response(status=400)


@api.route("/artists/<int:id>", methods=["GET", "PUT", "DELETE"])
def edit_artist(id):
    db_connection = mysql.connect()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM artists WHERE id=%s", (id))
    query_result = cursor.fetchone()
    if query_result == None:
        return Response(status=404)

    if request.method == "GET":
        return query_result

    if request.method == "PUT":
        try:
            cursor.execute(
                "UPDATE artists SET artist_name =%s, artist_image=%s,  artist_profile =%s, artist_works_url=%s WHERE (id = %s)",
                (
                    request.json["artist_name"],
                    request.json["artist_image"],
                    request.json["artist_profile"],
                    request.json["artist_works_url"],
                    id,
                ),
            )
            db_connection.commit()
            return Response(status=200)
        except KeyError as err:
            res = {"error": [f"This field {str(err)}is required"]}
            return Response(json.dumps(res), status=400, mimetype="application/json")
        except:
            return Response(status=400)

    if request.method == "DELETE":
        cursor.execute("DELETE FROM artists WHERE id=%s", (id))
        db_connection.commit()
        return Response(status=200)


@api.route("/financial_report", methods=["GET", "POST"])
def financial_report():
    db_connection = mysql.connect()
    cursor = db_connection.cursor()

    if request.method == "GET":
        cursor.execute("SELECT * FROM financial_report")
        query_result = cursor.fetchall()
        return Response(
            json.dumps(query_result), status=200, mimetype="application/json"
        )

    if request.method == "POST":
        try:
            cursor.execute(
                "SELECT * FROM financial_report WHERE year=%s and month=%s",
                (request.json["year"], request.json["month"]),
            )
            if cursor.fetchone() == None:
                cursor.execute(
                    "INSERT INTO financial_report (year ,month , file_url) VALUES (%s , %s , %s) ",
                    (
                        request.json["year"],
                        request.json["month"],
                        request.json["file_url"],
                    ),
                )
                db_connection.commit()
                return Response(status=200)

            msg = {
                "error": [
                    f"field  with year {request.json['year']} and month {request.json['month']} already exists"
                ]
            }
            return Response(json.dumps(msg), status=400, mimetype="application/json")

        except KeyError as err:
            res = {"error": [f"This field {str(err)} is required"]}
            return Response(json.dumps(res), status=400, mimetype="application/json")
        except Exception as e:
            print(e)
            return Response(status=400)


@api.route("/financial_report/<int:id>", methods=["GET", "PUT", "DELETE"])
def edit_finicial_report(id):
    db_connection = mysql.connect()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM financial_report WHERE id=%s", (id))
    query_result = cursor.fetchone()
    if query_result == None:
        return Response(status=404)

    if request.method == "GET":
        return query_result

    if request.method == "PUT":
        try:
            cursor.execute(
                "UPDATE financial_report SET year=%s, month=%s,  file_url = %s WHERE (id = %s)",
                (
                    request.json["year"],
                    request.json["month"],
                    request.json["file_url"],
                    id,
                ),
            )
            db_connection.commit()
            return Response(status=200)
        except KeyError as err:
            res = {"error": [f"This field {str(err)}is required"]}
            return Response(json.dumps(res), status=400, mimetype="application/json")
        except:
            return Response(status=400)

    if request.method == "DELETE":
        cursor.execute("DELETE FROM financial_report WHERE id=%s", (id))
        db_connection.commit()
        return Response(status=200)


@api.route("/forum", methods=["GET", "POST"])
def forum():
    db_connection = mysql.connect()
    cursor = db_connection.cursor()

    if request.method == "GET":
        cursor.execute("SELECT * FROM forum")
        query_result = cursor.fetchall()
        return Response(
            json.dumps(query_result), status=200, mimetype="application/json"
        )

    if request.method == "POST":
        try:
            cursor.execute(
                "SELECT * FROM forum WHERE forum_name=%s ",
                (request.json["forum_name"]),
            )
            if cursor.fetchone() == None:
                cursor.execute(
                    "INSERT INTO forum (forum_name ,forum_cover_url , forum_report_cover_url , forum_report_file_url ) VALUES (%s , %s , %s, %s) ",
                    (
                        request.json["forum_name"],
                        request.json["forum_cover_url"],
                        request.json["forum_report_cover_url"],
                        request.json["forum_report_file_url"],
                    ),
                )
                db_connection.commit()
                return Response(status=200)

            msg = {"error": [f"field {request.json['forum_name']}  already exists"]}
            return Response(json.dumps(msg), status=400, mimetype="application/json")

        except KeyError as err:
            res = {"error": [f"This field {str(err)} is required"]}
            return Response(json.dumps(res), status=400, mimetype="application/json")
        except Exception as e:
            print(e)
            return Response(status=400)


@api.route("/forum/<int:id>", methods=["GET", "PUT", "DELETE"])
def edit_forum(id):
    db_connection = mysql.connect()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM forum WHERE id=%s", (id))
    query_result = cursor.fetchone()
    if query_result == None:
        return Response(status=404)

    if request.method == "GET":
        return query_result

    if request.method == "PUT":
        try:
            cursor.execute(
                "UPDATE forum SET forum_name = %s ,forum_cover_url =%s , forum_report_cover_url = %s , forum_report_file_url = %s WHERE (id = %s)",
                (
                    request.json["forum_name"],
                    request.json["forum_cover_url"],
                    request.json["forum_report_cover_url"],
                    request.json["forum_report_file_url"],
                    id,
                ),
            )
            db_connection.commit()
            return Response(status=200)
        except KeyError as err:
            res = {"error": [f"This field {str(err)}is required"]}
            return Response(json.dumps(res), status=400, mimetype="application/json")
        except:
            return Response(status=400)

    if request.method == "DELETE":
        cursor.execute("DELETE FROM forum WHERE id=%s", (id))
        db_connection.commit()
        return Response(status=200)


@api.route("/donors", methods=["GET", "POST"])
def donors():
    db_connection = mysql.connect()
    cursor = db_connection.cursor()

    if request.method == "GET":
        cursor.execute("SELECT * FROM donors")
        query_result = cursor.fetchall()
        return Response(
            json.dumps(query_result), status=200, mimetype="application/json"
        )

    if request.method == "POST":
        try:
            cursor.execute(
                "SELECT * FROM donors WHERE name=%s ",
                (request.json["name"]),
            )
            if cursor.fetchone() == None:
                cursor.execute(
                    "INSERT INTO donors (name ,profile , logo_url , website_url ) VALUES (%s , %s , %s, %s) ",
                    (
                        request.json["name"],
                        request.json["profile"],
                        request.json["logo_url"],
                        request.json["website_url"],
                    ),
                )
                db_connection.commit()
                return Response(status=200)

            msg = {"error": [f"field {request.json['name']}  already exists"]}
            return Response(json.dumps(msg), status=400, mimetype="application/json")

        except KeyError as err:
            res = {"error": [f"This field {str(err)} is required"]}
            return Response(json.dumps(res), status=400, mimetype="application/json")
        except Exception as e:
            print(e)
            return Response(status=400)


@api.route("/donors/<int:id>", methods=["GET", "PUT", "DELETE"])
def edit_donors(id):
    db_connection = mysql.connect()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM donors WHERE id=%s", (id))
    query_result = cursor.fetchone()
    if query_result == None:
        return Response(status=404)

    if request.method == "GET":
        return query_result

    if request.method == "PUT":
        try:
            cursor.execute(
                "UPDATE donors SET name = %s ,profile = %s , logo_url = %s, website_url = %s WHERE (id = %s)",
                (
                    request.json["name"],
                    request.json["profile"],
                    request.json["logo_url"],
                    request.json["website_url"],
                    id,
                ),
            )
            db_connection.commit()
            return Response(status=200)
        except KeyError as err:
            res = {"error": [f"This field {str(err)}is required"]}
            return Response(json.dumps(res), status=400, mimetype="application/json")
        except:
            return Response(status=400)

    if request.method == "DELETE":
        cursor.execute("DELETE FROM donors WHERE id=%s", (id))
        db_connection.commit()
        return Response(status=200)


@api.route("/team", methods=["GET", "POST"])
def team():
    db_connection = mysql.connect()
    cursor = db_connection.cursor()

    if request.method == "GET":
        cursor.execute("SELECT * FROM team")
        query_result = cursor.fetchall()
        return Response(
            json.dumps(query_result), status=200, mimetype="application/json"
        )

    if request.method == "POST":
        try:
            cursor.execute(
                "SELECT * FROM team WHERE name=%s ",
                (request.json["name"]),
            )
            if cursor.fetchone() == None:
                cursor.execute(
                    "INSERT INTO team (name ,profile , image_url ) VALUES (%s , %s , %s) ",
                    (
                        request.json["name"],
                        request.json["profile"],
                        request.json["image_url"],
                    ),
                )
                db_connection.commit()
                return Response(status=200)

            msg = {"error": [f"field {request.json['name']}  already exists"]}
            return Response(json.dumps(msg), status=400, mimetype="application/json")

        except KeyError as err:
            res = {"error": [f"This field {str(err)} is required"]}
            return Response(json.dumps(res), status=400, mimetype="application/json")
        except Exception as e:
            print(e)
            return Response(status=400)


@api.route("/team/<int:id>", methods=["GET", "PUT", "DELETE"])
def edit_team(id):
    db_connection = mysql.connect()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM team WHERE id=%s", (id))
    query_result = cursor.fetchone()
    if query_result == None:
        return Response(status=404)

    if request.method == "GET":
        return query_result

    if request.method == "PUT":
        try:
            cursor.execute(
                "UPDATE team SET name = %s ,profile = %s , image_url = %s WHERE (id = %s)",
                (
                    request.json["name"],
                    request.json["profile"],
                    request.json["image_url"],
                    id,
                ),
            )
            db_connection.commit()
            return Response(status=200)
        except KeyError as err:
            res = {"error": [f"This field {str(err)}is required"]}
            return Response(json.dumps(res), status=400, mimetype="application/json")
        except:
            return Response(status=400)

    if request.method == "DELETE":
        cursor.execute("DELETE FROM team WHERE id=%s", (id))
        db_connection.commit()
        return Response(status=200)


@api.route("/partners", methods=["GET", "POST"])
def partners():
    db_connection = mysql.connect()
    cursor = db_connection.cursor()

    if request.method == "GET":
        cursor.execute("SELECT * FROM partners")
        query_result = cursor.fetchall()
        return Response(
            json.dumps(query_result), status=200, mimetype="application/json"
        )

    if request.method == "POST":
        try:
            cursor.execute(
                "SELECT * FROM partners WHERE name=%s ",
                (request.json["name"]),
            )
            if cursor.fetchone() == None:
                cursor.execute(
                    "INSERT INTO partners (name ,profile , logo_url , website_url ) VALUES (%s , %s , %s, %s) ",
                    (
                        request.json["name"],
                        request.json["profile"],
                        request.json["logo_url"],
                        request.json["website_url"],
                    ),
                )
                db_connection.commit()
                return Response(status=200)

            msg = {"error": [f"field {request.json['name']}  already exists"]}
            return Response(json.dumps(msg), status=400, mimetype="application/json")

        except KeyError as err:
            res = {"error": [f"This field {str(err)} is required"]}
            return Response(json.dumps(res), status=400, mimetype="application/json")
        except Exception as e:
            print(e)
            return Response(status=400)


@api.route("/partners/<int:id>", methods=["GET", "PUT", "DELETE"])
def edit_partners(id):
    db_connection = mysql.connect()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM partners WHERE id=%s", (id))
    query_result = cursor.fetchone()
    if query_result == None:
        return Response(status=404)

    if request.method == "GET":
        return query_result

    if request.method == "PUT":
        try:
            cursor.execute(
                "UPDATE partners SET name = %s ,profile = %s , logo_url = %s, website_url = %s WHERE (id = %s)",
                (
                    request.json["name"],
                    request.json["profile"],
                    request.json["logo_url"],
                    request.json["website_url"],
                    id,
                ),
            )
            db_connection.commit()
            return Response(status=200)
        except KeyError as err:
            res = {"error": [f"This field {str(err)}is required"]}
            return Response(json.dumps(res), status=400, mimetype="application/json")
        except:
            return Response(status=400)

    if request.method == "DELETE":
        cursor.execute("DELETE FROM partners WHERE id=%s", (id))
        db_connection.commit()
        return Response(status=200)


@api.route("/forum-gallery", methods=["GET", "POST"])
def forumgallery():
    db_connection = mysql.connect()
    cursor = db_connection.cursor()

    if request.method == "GET":
        cursor.execute("SELECT * FROM forum_gallery")
        query_result = cursor.fetchall()
        return Response(
            json.dumps(query_result), status=200, mimetype="application/json"
        )

    if request.method == "POST":
        try:
            cursor.execute(
                "SELECT * FROM forum_gallery WHERE forum=%s ",
                (request.json["forum"]),
            )
            if cursor.fetchone() == None:
                cursor.execute(
                    "INSERT INTO forum_gallery (forum ,forum_gallery_cover , forum_gallery , full_video_cover_url, full_video_url, snippet_cover_url, snippet_url ) VALUES (%s , %s , %s, %s,%s , %s , %s) ",
                    (
                        request.json["forum"],
                        request.json["forum_gallery_cover"],
                        request.json["forum_gallery"],
                        request.json["full_video_cover_url"],
                        request.json["full_video_url"],
                        request.json["snippet_cover_url"],
                        request.json["snippet_url"],
                    ),
                )
                db_connection.commit()
                return Response(status=200)

            msg = {"error": [f"field {request.json['forum']}  already exists"]}
            return Response(json.dumps(msg), status=400, mimetype="application/json")

        except KeyError as err:
            res = {"error": [f"This field {str(err)} is required"]}
            return Response(json.dumps(res), status=400, mimetype="application/json")
        except Exception as e:
            print(e)
            return Response(status=400)


@api.route("/forum-gallery/<int:id>", methods=["GET", "PUT", "DELETE"])
def edit_forumgallery():
    db_connection = mysql.connect()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM forum_gallery WHERE id=%s", (id))
    query_result = cursor.fetchone()
    if query_result == None:
        return Response(status=404)

    if request.method == "GET":
        return query_result

    if request.method == "PUT":
        try:
            cursor.execute(
                "UPDATE forum_gallery SET forum = %s ,forum_gallery_cover = %s  , forum_gallery = %s , full_video_cover_url = %s , full_video_url = %s , snippet_cover_url = %s , snippet_url = %s  WHERE (id = %s)",
                (
                    request.json["forum"],
                    request.json["forum_gallery_cover"],
                    request.json["forum_gallery"],
                    request.json["full_video_cover_url"],
                    request.json["full_video_url"],
                    request.json["snippet_cover_url"],
                    request.json["snippet_url"],
                    id,
                ),
            )
            db_connection.commit()
            return Response(status=200)
        except KeyError as err:
            res = {"error": [f"This field {str(err)}is required"]}
            return Response(json.dumps(res), status=400, mimetype="application/json")
        except:
            return Response(status=400)

    if request.method == "DELETE":
        cursor.execute("DELETE FROM forum_gallery WHERE id=%s", (id))
        db_connection.commit()
        return Response(status=200)


@api.route("/info", methods=["GET", "POST"])
def info():
    db_connection = mysql.connect()
    cursor = db_connection.cursor()

    if request.method == "GET":
        cursor.execute("SELECT * FROM info")
        query_result = cursor.fetchall()
        return Response(
            json.dumps(query_result), status=200, mimetype="application/json"
        )

    if request.method == "POST":
        try:
            cursor.execute(
                "SELECT * FROM info WHERE header=%s ",
                (request.json["header"]),
            )
            if cursor.fetchone() == None:
                cursor.execute(
                    "INSERT INTO info (header, body ) VALUES (%s , %s) ",
                    (
                        request.json["header"],
                        request.json["body"],
                    ),
                )
                db_connection.commit()
                return Response(status=200)

            msg = {"error": [f"field {request.json['header']}  already exists"]}
            return Response(json.dumps(msg), status=400, mimetype="application/json")

        except KeyError as err:
            res = {"error": [f"This field {str(err)} is required"]}
            return Response(json.dumps(res), status=400, mimetype="application/json")
        except Exception as e:
            print(e)
            return Response(status=400)


@api.route("/info/<int:id>", methods=["GET", "PUT", "DELETE"])
def edit_info(id):
    db_connection = mysql.connect()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM info WHERE id=%s", (id))
    query_result = cursor.fetchone()
    if query_result == None:
        return Response(status=404)

    if request.method == "GET":
        return query_result

    if request.method == "PUT":
        try:
            cursor.execute(
                "UPDATE info SET header = %s ,body = %s  WHERE (id = %s)",
                (
                    request.json["header"],
                    request.json["body"],
                    id,
                ),
            )
            db_connection.commit()
            return Response(status=200)
        except KeyError as err:
            res = {"error": [f"This field {str(err)}is required"]}
            return Response(json.dumps(res), status=400, mimetype="application/json")
        except:
            return Response(status=400)

    if request.method == "DELETE":
        cursor.execute("DELETE FROM info WHERE id=%s", (id))
        db_connection.commit()
        return Response(status=200)


# ['DataError', 'DatabaseError', 'Error', 'IntegrityError', 'InterfaceError', 'InternalError', 'NotSupportedError',
# 'OperationalError', 'ProgrammingError', 'Warning', '__class__',
# '__delattr__', '__dict__', '__dir__', '__doc__', '__enter__', '__eq__', '__exit__', '__format__', '__ge__', '__getattribute__', '__gt__',
# '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__',
# '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_check_executed', '_clear_result', '_conv_row', '_do_execute_many', '_do_get_result', '_ensure_bytes',
# '_escape_args', '_executed', '_fields', '_get_db', '_last_executed', '_nextset', '_query', '_result', '_rows', 'arraysize', 'callproc', 'close', 'connection', 'description',
# 'dict_type', 'execute', 'executemany', 'fetchall', 'fetchmany', 'fetchone', 'lastrowid', 'max_stmt_length', 'mogrify', 'nextset', 'rowcount', 'rownumber',
# 'scroll', 'setinputsizes', 'setoutputsizes']

{
    "name": "Temi Davids",
    "profile": "Temi Davids is a woman intrested in empowering africa",
    "image_url": "https://fabwoman.ng/wp-content/uploads/2019/05/Temi-Otedola-net-worth.jpg",
}