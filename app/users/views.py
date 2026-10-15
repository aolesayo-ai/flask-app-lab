from flask import render_template, request, redirect, url_for
from . import user_bp

@user_bp.route("/hi/<string:name>")
def greetings(name):
    name = name.upper()
    age = request.args.get("age", None, int)
    # Зверніть увагу на шлях до шаблону
    return render_template("users/hi.html", name=name, age=age)

@user_bp.route("/admin")
def admin():
    # users.greetings - це формат "назва_блюпринта.назва_функції"
    to_url = url_for("users.greetings", name="administrator", age=45, _external=True)
    print(to_url)
    return redirect(to_url)