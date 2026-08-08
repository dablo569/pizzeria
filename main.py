import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, redirect, url_for, request, session
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash




BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    print(f"Увага: файл .env не знайдено: {ENV_PATH}")


SUPABASE_URL = os.getenv("LINK_DB")
SUPABASE_KEY = os.getenv("API_KEY")


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "bestpizza_local_secret_key"
)


if not SUPABASE_URL:
    raise RuntimeError("У файлі .env відсутня змінна LINK_DB")

if not SUPABASE_KEY:
    raise RuntimeError("У файлі .env відсутня змінна API_KEY")


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)




app = Flask(__name__)
app.secret_key = SECRET_KEY

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False


TABLE_NAME = "Table"




menu_tovariv = {
    "Основне меню": {
        "Піца": [
            {
                "name": "Пепероні",
                "photo": "/static/photos/PEP.png",
                "price": "73,90",
                "sklad": (
                    "Ковбаса пепероні, подвійна моцарела, "
                    "перетерті томати."
                )
            },
            {
                "name": "Маргарита",
                "photo": "/static/photos/MAR.png",
                "price": "69,90",
                "sklad": (
                    "Тісто, томатний соус з орегано, "
                    "сир моцарела."
                )
            },
            {
                "name": "Гавайська",
                "photo": "/static/photos/GAV.png",
                "price": "78,90",
                "sklad": (
                    "Запечена курка, кукурудза, ананас, "
                    "моцарела, томатний соус."
                )
            },
            {
                "name": "4 Сири",
                "photo": "/static/photos/4CH.png",
                "price": "70,90",
                "sklad": (
                    "Вершковий соус, моцарела, брі, "
                    "дор блю та вершковий сир."
                )
            }
        ],

        "Бургери": [
            {
                "name": "Чізбургер",
                "photo": "/static/photos/CHEESEBURGER.png",
                "price": "89,90",
                "sklad": (
                    "Булочка, яловича котлета, сир чедер, "
                    "салат, помідор та соус."
                )
            },
            {
                "name": "Бургер з куркою",
                "photo": "/static/photos/CHICKEN_BURGER.png",
                "price": "84,90",
                "sklad": (
                    "Булочка, куряче філе, салат, помідор, "
                    "сир та часниковий соус."
                )
            },
            {
                "name": "Бекон-бургер",
                "photo": "/static/photos/BACON_BURGER.png",
                "price": "99,90",
                "sklad": (
                    "Яловича котлета, бекон, сир чедер, "
                    "маринований огірок та соус барбекю."
                )
            },
            {
                "name": "BBQ-бургер",
                "photo": "/static/photos/BBQ_BURGER.png",
                "price": "94,90",
                "sklad": (
                    "Яловича котлета, цибуля, салат, сир, "
                    "соус барбекю та томати."
                )
            }
        ],

        "Гарячі закуски": [
            {
                "name": "Картопля фрі",
                "photo": "/static/photos/FRIES.png",
                "price": "39,90",
                "sklad": "Хрустка картопля фрі з сіллю."
            },
            {
                "name": "Крильця BBQ",
                "photo": "/static/photos/WINGS.png",
                "price": "79,90",
                "sklad": (
                    "Курячі крильця, спеції та "
                    "соус барбекю."
                )
            },
            {
                "name": "Курячі нагетси",
                "photo": "/static/photos/NUGGETS.png",
                "price": "59,90",
                "sklad": (
                    "Хрусткі шматочки курячого філе "
                    "та кетчуп."
                )
            },
            {
                "name": "Сирні палички",
                "photo": "/static/photos/CHEESE_STICKS.png",
                "price": "64,90",
                "sklad": (
                    "Панірувальні сирні палички "
                    "з часниковим соусом."
                )
            }
        ]
    },

    "Бар": {
        "Алкогольні напої": [
            {
                "name": "Пиво світле",
                "photo": "/static/photos/BEER_LIGHT.png",
                "price": "45,00",
                "sklad": "Світле пиво, 0,5 л."
            },
            {
                "name": "Пиво темне",
                "photo": "/static/photos/BEER_DARK.png",
                "price": "49,00",
                "sklad": "Темне пиво, 0,5 л."
            },
            {
                "name": "Вино червоне",
                "photo": "/static/photos/RED_WINE.png",
                "price": "95,00",
                "sklad": "Червоне напівсолодке вино, 0,2 л."
            },
            {
                "name": "Вино біле",
                "photo": "/static/photos/WHITE_WINE.png",
                "price": "95,00",
                "sklad": "Біле напівсолодке вино, 0,2 л."
            }
        ],

        "Безалкогольні напої": [
            {
                "name": "Кока-Кола",
                "photo": "/static/photos/COLA.png",
                "price": "29,90",
                "sklad": "Газований напій Coca-Cola, 0,5 л."
            },
            {
                "name": "Фанта",
                "photo": "/static/photos/FANTA.png",
                "price": "29,90",
                "sklad": "Газований апельсиновий напій, 0,5 л."
            },
            {
                "name": "Спрайт",
                "photo": "/static/photos/SPRITE.png",
                "price": "29,90",
                "sklad": "Газований лимонний напій, 0,5 л."
            },
            {
                "name": "Мінеральна вода",
                "photo": "/static/photos/WATER.png",
                "price": "24,90",
                "sklad": "Мінеральна вода без газу, 0,5 л."
            }
        ],

        "Лимонади": [
            {
                "name": "Лимонад класичний",
                "photo": "/static/photos/LEMONADE_CLASSIC.png",
                "price": "39,90",
                "sklad": "Лимон, вода, цукровий сироп та м'ята."
            },
            {
                "name": "Лимонад полуничний",
                "photo": "/static/photos/LEMONADE_STRAWBERRY.png",
                "price": "44,90",
                "sklad": "Полуниця, лимон, вода та м'ята."
            },
            {
                "name": "Лимонад кокос ананас",
                "photo": "/static/photos/LEMONADE_COCONUT.png",
                "price": "44,90",
                "sklad": "Апельсин, лимон, вода та сироп."
            },
            {
                "name": "Лимонад м'ятний",
                "photo": "/static/photos/LEMONADE_MINT.png",
                "price": "39,90",
                "sklad": "Лимон, м'ята, вода та цукровий сироп."
            }
        ],

        "Чай": [
            {
                "name": "Чай чорний",
                "photo": "/static/photos/TEA_BLACK.png",
                "price": "29,90",
                "sklad": "Чорний чай, 400 мл."
            },
            {
                "name": "Чай зелений",
                "photo": "/static/photos/TEA_GREEN.png",
                "price": "29,90",
                "sklad": "Зелений чай, 400 мл."
            },
            {
                "name": "Чай з лимоном",
                "photo": "/static/photos/TEA_LEMON.png",
                "price": "34,90",
                "sklad": "Чорний чай, лимон та мед."
            },
            {
                "name": "Чай ягідний",
                "photo": "/static/photos/TEA_BERRY.png",
                "price": "39,90",
                "sklad": "Ягідний чай з малиною та смородиною."
            }
        ],

        "Кава": [
            {
                "name": "Еспресо",
                "photo": "/static/photos/ESPRESSO.png",
                "price": "29,90",
                "sklad": "Міцна чорна кава, 60 мл."
            },
            {
                "name": "Американо",
                "photo": "/static/photos/AMERICANO.png",
                "price": "34,90",
                "sklad": "Еспресо з гарячою водою, 200 мл."
            },
            {
                "name": "Капучино",
                "photo": "/static/photos/CAPPUCCINO.png",
                "price": "44,90",
                "sklad": "Еспресо, молоко та молочна пінка."
            },
            {
                "name": "Лате",
                "photo": "/static/photos/LATTE.png",
                "price": "49,90",
                "sklad": "Еспресо, багато молока та молочна пінка."
            }
        ]
    }
}


def read_users():
    """
    Отримує користувачів без паролів.
    """
    response = (
        supabase
        .table(TABLE_NAME)
        .select("id, user, liveplace")
        .execute()
    )

    return response.data or []


def get_user(username):
    """
    Знаходить користувача за логіном.
    """
    if not username:
        return None

    response = (
        supabase
        .table(TABLE_NAME)
        .select("id, user, password, liveplace")
        .eq("user", username)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


def insert_data(username, password, liveplace):
    """
    Додає нового користувача.
    Пароль хешується, але його складність не перевіряється.
    """
    password_hash = generate_password_hash(password)

    return (
        supabase
        .table(TABLE_NAME)
        .insert({
            "user": username,
            "password": password_hash,
            "liveplace": liveplace
        })
        .execute()
    )

def save_order(user_id, username, city, address, payment, cart):
    total_price = sum(
        item["price"] * item["quantity"]
        for item in cart.values()
    )

    order_response = (
        supabase
        .table("orders")
        .insert({
            "user_id": user_id,
            "username": username,
            "city": city,
            "address": address,
            "payment": payment,
            "total_price": round(total_price, 2),
            "status": "new"
        })
        .execute()
    )

    if not order_response.data:
        raise RuntimeError("Не вдалося створити замовлення.")

    order_id = order_response.data[0]["id"]

    items = []

    for item in cart.values():
        items.append({
            "order_id": order_id,
            "product_name": item["name"],
            "price": item["price"],
            "quantity": item["quantity"]
        })

    if items:
        (
            supabase
            .table("order_items")
            .insert(items)
            .execute()
        )

    return order_id, total_price

def delete_data(user_id):
    """
    Видаляє користувача за id.
    """
    return (
        supabase
        .table(TABLE_NAME)
        .delete()
        .eq("id", user_id)
        .execute()
    )

def find_product(product_name):
    """
    Знаходить товар у всьому меню за назвою.
    """
    for menu_section in menu_tovariv.values():
        for category_products in menu_section.values():
            for product in category_products:
                if product["name"] == product_name:
                    return product

    return None


def price_to_number(price):
    """
    Перетворює ціну '73,90' на число 73.90.
    """
    return float(price.replace(",", "."))




@app.route("/")
def index():
    try:
        users = read_users()
    except Exception as error:
        print(f"Помилка отримання користувачів: {error}")
        users = []

    return render_template(
        "index.html",
        menu=menu_tovariv,
        users=users,
        current_user=session.get("user")
    )




@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register-order", methods=["POST"])
def register_order():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    liveplace = request.form.get("liveplace", "").strip()

    if not username or not password or not liveplace:
        return render_template(
            "register.html",
            error="Заповніть усі поля."
        )

    try:
        existing_user = get_user(username)

        if existing_user:
            return render_template(
                "register.html",
                error="Такий користувач уже існує."
            )

        insert_data(
            username=username,
            password=password,
            liveplace=liveplace
        )

        session.clear()
        session["user"] = username
        session["liveplace"] = liveplace
        session["cart"] = {}

        return redirect(url_for("account"))

    except Exception as error:
        print(f"Помилка реєстрації: {error}")

        return render_template(
            "register.html",
            error="Помилка під час реєстрації."
        )


# ==================================================
# Кошик
# ==================================================

@app.route("/cart/data")
def cart_data():
    cart = session.get("cart", {})

    items = []
    total = 0
    count = 0

    for item in cart.values():
        item_total = item["price"] * item["quantity"]

        items.append({
            "name": item["name"],
            "photo": item["photo"],
            "price": item["price"],
            "quantity": item["quantity"],
            "item_total": round(item_total, 2)
        })

        total += item_total
        count += item["quantity"]

    return jsonify({
        "items": items,
        "total": round(total, 2),
        "count": count
    })


@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Спочатку увійдіть в акаунт."
        }), 401

    data = request.get_json(silent=True) or {}
    product_name = data.get("name")

    product = find_product(product_name)

    if not product:
        return jsonify({
            "success": False,
            "message": "Товар не знайдено."
        }), 404

    cart = session.get("cart", {})

    if product_name in cart:
        cart[product_name]["quantity"] += 1
    else:
        cart[product_name] = {
            "name": product["name"],
            "photo": product["photo"],
            "price": price_to_number(product["price"]),
            "quantity": 1
        }

    session["cart"] = cart
    session.modified = True

    return jsonify({
        "success": True,
        "cart": cart
    })


@app.route("/cart/change", methods=["POST"])
def change_cart_quantity():
    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Потрібно увійти в акаунт."
        }), 401

    data = request.get_json(silent=True) or {}

    product_name = data.get("name")
    change = int(data.get("change", 0))

    cart = session.get("cart", {})

    if product_name not in cart:
        return jsonify({
            "success": False,
            "message": "Товар відсутній у кошику."
        }), 404

    cart[product_name]["quantity"] += change

    if cart[product_name]["quantity"] <= 0:
        del cart[product_name]

    session["cart"] = cart
    session.modified = True

    return jsonify({
        "success": True
    })


@app.route("/checkout", methods=["POST"])
def checkout():
    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Для замовлення потрібно увійти в акаунт."
        }), 401

    cart = session.get("cart", {})

    if not cart:
        return jsonify({
            "success": False,
            "message": "Кошик порожній."
        }), 400

    data = request.get_json(silent=True) or {}

    city = session.get("liveplace")
    address = data.get("address", "").strip()
    payment = data.get("payment", "")

    if not city:
        return jsonify({
            "success": False,
            "message": "У вашому акаунті не вказано місто."
        }), 400

    if not address:
        return jsonify({
            "success": False,
            "message": "Введіть адресу доставки."
        }), 400

    if payment not in ["card", "cash"]:
        return jsonify({
            "success": False,
            "message": "Оберіть спосіб оплати."
        }), 400

    try:
        user = get_user(session["user"])

        if not user:
            return jsonify({
                "success": False,
                "message": "Користувача не знайдено."
            }), 404

        order_id, total_price = save_order(
            user_id=user["id"],
            username=session["user"],
            city=city,
            address=address,
            payment=payment,
            cart=cart
        )

        session.pop("cart", None)
        session.modified = True

        return jsonify({
            "success": True,
            "message": "Дякуємо за замовлення!",
            "order_id": order_id,
            "total": round(total_price, 2)
        })

    except Exception as error:
        print(f"Помилка збереження замовлення: {error}")

        return jsonify({
            "success": False,
            "message": "Не вдалося зберегти замовлення."
        }), 500

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        return render_template(
            "login.html",
            error="Введіть логін і пароль."
        )

    try:
        user = get_user(username)

        if user and check_password_hash(user["password"], password):
            session.clear()

            session["user"] = user["user"]
            session["liveplace"] = user["liveplace"]

            return redirect(url_for("account"))

        return render_template(
            "login.html",
            error="Неправильний логін або пароль."
        )

    except Exception as error:
        print(f"Помилка входу: {error}")

        return render_template(
            "login.html",
            error="Помилка під час входу."
        )




@app.route("/account")
def account():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template(
        "profile.html",
        username=session.get("user"),
        liveplace=session.get("liveplace")
    )




@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))




@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    if "user" not in session:
        return redirect(url_for("login"))

    try:
        delete_data(item_id)
    except Exception as error:
        print(f"Помилка видалення: {error}")

    return redirect(url_for("index"))




if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )