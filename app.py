# backend/app.py
from flask import Flask, jsonify, request, send_from_directory, render_template
from models import Teacher, SessionLocal, Event, EventImage
app = Flask(__name__)

MAX_CAROUSEL = 15

@app.route("/")
def home():
    db = SessionLocal()
    teachers = db.query(Teacher).all()
    events = db.query(Event).order_by(Event.date.desc()).limit(MAX_CAROUSEL).all()
    db.close()
    return render_template("index.html", teachers=teachers, events=events)

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route("/teachers")
def teachers():
    db = SessionLocal()
    teachers = db.query(Teacher).order_by(Teacher.name).all()
    db.close()
    return render_template("teachers.html", teachers=teachers)

@app.route("/contacts")
@app.route("/contacts.html")
def contacts():
    return render_template("contacts.html")

@app.route("/debug")
def debug():
    db = SessionLocal()
    teachers = db.query(Teacher).all()
    db.close()
    return "<br>".join([f"{t.name} → {t.photo}" for t in teachers])

@app.route("/events")
def events():
    db = SessionLocal()
    all_events = db.query(Event).order_by(Event.date.desc()).all()
    db.close()
    return render_template("events.html", events=all_events)

@app.route("/event/<int:event_id>")
def event_detail(event_id):
    db = SessionLocal()
    event = db.query(Event).filter_by(id=event_id).first()
    images = db.query(EventImage).filter_by(event_id=event_id).all()
    db.close()

    # Приклеим список картинок в сам объект, чтобы Jinja мог их пройти
    event.images = images
    return render_template("event_detail.html", event=event)

@app.route("/about")                # URL “/about”
@app.route("/about.html")           # или “/about.html” — если хочешь именно с расширением
def about():
    return render_template("about.html")

# Запуск сервера
if __name__ == "__main__":
    # слушаем на 0.0.0.0 — все сетевые интерфейсы
    app.run(host="0.0.0.0", port=5000, debug=True)