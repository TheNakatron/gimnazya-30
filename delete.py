from models import Teacher, SessionLocal

db = SessionLocal()
bad_teachers = db.query(Teacher).filter(
    Teacher.photo == '2143339805_BQACAgIAAxkBAAMJaF7Hx4yP4ImRH7vMZ-rWbusUsHkAAmSAAAI_VfBK5WMOe5ug1W82BA.jpg'  # точно скопируй имя файла
).all()

for t in bad_teachers:
    db.delete(t)
db.commit()
db.close()