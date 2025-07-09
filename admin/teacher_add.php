<?php
$db = new PDO('sqlite:../database.bd');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

if (\$_SERVER['REQUEST_METHOD']==='POST') {
    \$name = \$_POST['name'] ?? '';
    \$pos  = \$_POST['position'] ?? '';
    \$exp  = \$_POST['experience'] ?? '';
    \$link = \$_POST['link'] ?? '';
    \$photoName = '';
    if (!empty(\$_FILES['photo']['name'])) {
        \$ext = pathinfo(\$_FILES['photo']['name'], PATHINFO_EXTENSION);
        \$photoName = uniqid('tch_').'.'.strtolower(\$ext);
        move_uploaded_file(\$_FILES['photo']['tmp_name'], "../static/img/teachers/\$photoName");
    }
    \$stmt = \$db->prepare('INSERT INTO teachers(name,position,experience,photo,link) VALUES(?,?,?,?,?)');
    \$stmt->execute([\$name,\$pos,\$exp,\$photoName,\$link]);
    header('Location: teachers.php'); exit;
}
?>
<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Добавить преподавателя</title></head>
<body>
  <h1>Добавить преподавателя</h1>
  <form method="post" enctype="multipart/form-data">
    <p>Имя: <input type="text" name="name" required></p>
    <p>Должность: <input type="text" name="position" required></p>
    <p>Опыт (лет): <input type="text" name="experience"></p>
    <p>Ссылка (профиль): <input type="url" name="link"></p>
    <p>Фото: <input type="file" name="photo" accept="image/*"></p>
    <p><button type="submit">Создать</button> <a href="teachers.php">Отмена</a></p>
  </form>
</body>
</html>
