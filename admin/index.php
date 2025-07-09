<?php
// admin/index.php

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Путь к файлу БД
$dbFile = __DIR__ . '/../database.bd';
if (!file_exists($dbFile)) {
    die('Не найдена база данных: ' . htmlspecialchars($dbFile));
}

$db = new PDO('sqlite:' . $dbFile);
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Определяем, с чем работаем
$section = $_GET['section'] ?? 'events';  // по умолчанию — события
$id      = isset($_GET['id']) ? (int)$_GET['id'] : null;

// --- Обработка POST для добавления ---
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if ($section === 'events') {
        // Добавляем событие
        $title   = $_POST['title'] ?? '';
        $desc    = $_POST['description'] ?? '';
        $date    = $_POST['date'] ?? '';
        $link    = $_POST['link'] ?? '';
        $article = $_POST['article'] ?? '';
        $imgName = '';
        if (!empty($_FILES['image']['name'])) {
            $ext     = pathinfo($_FILES['image']['name'], PATHINFO_EXTENSION);
            $imgName = uniqid('ev_') . '.' . strtolower($ext);
            move_uploaded_file($_FILES['image']['tmp_name'], __DIR__ . "/../static/img/events/$imgName");
        }
        $stmt = $db->prepare('INSERT INTO events(title,description,article,link,date,image) VALUES(?,?,?,?,?,?)');
        $stmt->execute([$title, $desc, $article, $link, $date, $imgName]);
    } else {
        // Добавляем преподавателя
        $name       = $_POST['name'] ?? '';
        $position   = $_POST['position'] ?? '';
        $experience = $_POST['experience'] ?? '';
        $link       = $_POST['link'] ?? '';
        $photoName  = '';
        if (!empty($_FILES['photo']['name'])) {
            $ext       = pathinfo($_FILES['photo']['name'], PATHINFO_EXTENSION);
            $photoName = uniqid('tch_') . '.' . strtolower($ext);
            move_uploaded_file($_FILES['photo']['tmp_name'], __DIR__ . "/../static/img/teachers/$photoName");
        }
        $stmt = $db->prepare('INSERT INTO teachers(name,position,experience,photo,link) VALUES(?,?,?,?,?)');
        $stmt->execute([$name, $position, $experience, $photoName, $link]);
    }
    header("Location: index.php?section=$section");
    exit;
}

// --- Обработка удаления ---
if ($id !== null && isset($_GET['action']) && $_GET['action']==='delete') {
    if ($section === 'events') {
        // удаляем картинку
        $old = $db->query("SELECT image FROM events WHERE id=$id")->fetchColumn();
        if ($old && file_exists(__DIR__ . "/../static/img/events/$old")) {
            unlink(__DIR__ . "/../static/img/events/$old");
        }
        $db->exec("DELETE FROM events WHERE id=$id");
    } else {
        $old = $db->query("SELECT photo FROM teachers WHERE id=$id")->fetchColumn();
        if ($old && file_exists(__DIR__ . "/../static/img/teachers/$old")) {
            unlink(__DIR__ . "/../static/img/teachers/$old");
        }
        $db->exec("DELETE FROM teachers WHERE id=$id");
    }
    header("Location: index.php?section=$section");
    exit;
}

// --- Получаем данные для вывода ---
if ($section === 'events') {
    $items = $db->query('SELECT id,title,date,image FROM events ORDER BY date DESC')
                ->fetchAll(PDO::FETCH_ASSOC);
} else {
    $items = $db->query('SELECT id,name,position,photo FROM teachers ORDER BY id')
                ->fetchAll(PDO::FETCH_ASSOC);
}

?>
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Админка — <?= $section === 'events' ? 'События' : 'Преподаватели' ?></title>
  <style>
    body { font-family: sans-serif; padding: 20px; }
    nav a { margin-right: 15px; }
    table { border-collapse: collapse; margin-top: 15px; }
    td, th { border: 1px solid #ccc; padding: 5px 10px; }
    img { max-height: 60px; }
    form { margin-top: 20px; background: #f9f9f9; padding: 10px; }
  </style>
</head>
<body>
  <h1>Админка</h1>
  <nav>
    <a href="?section=events"<?= $section==='events'?' style="font-weight:bold"':'' ?>>События</a>
    <a href="?section=teachers"<?= $section==='teachers'?' style="font-weight:bold"':'' ?>>Преподаватели</a>
  </nav>

  <?php if ($section === 'events'): ?>
    <h2>Список событий</h2>
    <table>
      <tr><th>ID</th><th>Дата</th><th>Заголовок</th><th>Картинка</th><th>Действия</th></tr>
      <?php foreach ($items as $e): ?>
      <tr>
        <td><?= $e['id'] ?></td>
        <td><?= $e['date'] ?></td>
        <td><?= htmlspecialchars($e['title']) ?></td>
        <td><?php if($e['image']): ?><img src="../static/img/events/<?= $e['image'] ?>"><?php endif; ?></td>
        <td>
          <a href="?section=events&id=<?= $e['id'] ?>&action=delete" onclick="return confirm('Удалить?')">Удалить</a>
        </td>
      </tr>
      <?php endforeach; ?>
    </table>

    <h3>Добавить новое событие</h3>
    <form method="post" enctype="multipart/form-data">
      <p>Дата: <input type="date" name="date" required></p>
      <p>Заголовок: <input type="text" name="title" required></p>
      <p>Описание:<br><textarea name="description"></textarea></p>
      <p>Статья (HTML):<br><textarea name="article"></textarea></p>
      <p>Ссылка:<br><input type="url" name="link"></p>
      <p>Картинка: <input type="file" name="image" accept="image/*"></p>
      <p><button type="submit">Создать событие</button></p>
    </form>

  <?php else: ?>
    <h2>Список преподавателей</h2>
    <table>
      <tr><th>ID</th><th>Имя</th><th>Должность</th><th>Фото</th><th>Действия</th></tr>
      <?php foreach ($items as $t): ?>
      <tr>
        <td><?= $t['id'] ?></td>
        <td><?= htmlspecialchars($t['name']) ?></td>
        <td><?= htmlspecialchars($t['position']) ?></td>
        <td><?php if($t['photo']): ?><img src="../static/img/teachers/<?= $t['photo'] ?>"><?php endif; ?></td>
        <td>
          <a href="?section=teachers&id=<?= $t['id'] ?>&action=delete" onclick="return confirm('Удалить?')">Удалить</a>
        </td>
      </tr>
      <?php endforeach; ?>
    </table>

    <h3>Добавить нового преподавателя</h3>
    <form method="post" enctype="multipart/form-data">
      <p>Имя: <input type="text" name="name" required></p>
      <p>Должность: <input type="text" name="position" required></p>
      <p>Опыт (лет): <input type="text" name="experience"></p>
      <p>Ссылка (профиль): <input type="url" name="link"></p>
      <p>Фото: <input type="file" name="photo" accept="image/*"></p>
      <p><button type="submit">Создать преподавателя</button></p>
    </form>
  <?php endif; ?>

</body>
</html>