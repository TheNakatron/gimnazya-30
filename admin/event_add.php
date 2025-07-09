<?php
$db = new PDO('sqlite:../database.bd');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

if (\$_SERVER['REQUEST_METHOD']==='POST') {
    \$title = \$_POST['title'] ?? '';
    \$desc  = \$_POST['description'] ?? '';
    \$date  = \$_POST['date'] ?? '';
    \$link  = \$_POST['link'] ?? '';
    \$article = \$_POST['article'] ?? '';
    \$imgName = '';
    if (!empty(\$_FILES['image']['name'])) {
        \$ext = pathinfo(\$_FILES['image']['name'], PATHINFO_EXTENSION);
        \$imgName = uniqid('ev_').'.'.strtolower(\$ext);
        move_uploaded_file(\$_FILES['image']['tmp_name'], "../static/img/events/\$imgName");
    }
    \$stmt = \$db->prepare('INSERT INTO events(title,description,article,link,date,image) VALUES(?,?,?,?,?,?)');
    \$stmt->execute([\$title,\$desc,\$article,\$link,\$date,\$imgName]);
    header('Location: events.php'); exit;
}
?>
<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Добавить событие</title></head>
<body>
  <h1>Добавить событие</h1>
  <form method="post" enctype="multipart/form-data">
    <p>Дата: <input type="date" name="date" required></p>
    <p>Заголовок: <input type="text" name="title" required></p>
    <p>Описание:<br><textarea name="description" rows="3"></textarea></p>
    <p>Статья (HTML):<br><textarea name="article" rows="5"></textarea></p>
    <p>Ссылка:<br><input type="url" name="link"></p>
    <p>Картинка: <input type="file" name="image" accept="image/*"></p>
    <p><button type="submit">Создать</button> <a href="events.php">Отмена</a></p>
  </form>
</body>
</html>
