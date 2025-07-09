<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

$db = new PDO('sqlite:../database.bd');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

if (isset($_GET['delete'])) {
    $id = (int)$_GET['delete'];

    // Сначала удаляем файл картинки
    $stmt0 = $db->prepare('SELECT image FROM events WHERE id = ?');
    $stmt0->execute([$id]);
    $old = $stmt0->fetchColumn();

    if ($old && file_exists("../static/img/events/$old")) {
        unlink("../static/img/events/$old");
    }

    // Удаляем запись
    $stmt = $db->prepare('DELETE FROM events WHERE id = ?');
    $stmt->execute([$id]);

    header('Location: events.php');
    exit;
}

// Получаем все события
$events = $db
    ->query('SELECT id, title, date, image FROM events ORDER BY date DESC')
    ->fetchAll(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>События</title>
</head>
<body>
  <h1>Список событий</h1>
  <p><a href="event_add.php">Добавить событие</a></p>
  <table border="1" cellpadding="5">
    <tr>
      <th>ID</th>
      <th>Дата</th>
      <th>Заголовок</th>
      <th>Картинка</th>
      <th>Действия</th>
    </tr>
    <?php foreach ($events as $e): ?>
    <tr>
      <td><?= $e['id'] ?></td>
      <td><?= $e['date'] ?></td>
      <td><?= htmlspecialchars($e['title']) ?></td>
      <td>
        <?php if ($e['image']): ?>
          <img src="../static/img/events/<?= htmlspecialchars($e['image']) ?>" width="80">
        <?php endif; ?>
      </td>
      <td>
        <a href="?delete=<?= $e['id'] ?>" onclick="return confirm('Удалить?')">Удалить</a>
      </td>
    </tr>
    <?php endforeach; ?>
  </table>
  <p><a href="index.php">← Назад</a></p>
</body>
</html>
