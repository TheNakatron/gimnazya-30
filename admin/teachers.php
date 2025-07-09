<?php
$db = new PDO('sqlite:../database.bd');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

if (isset(\$_GET['delete'])) {
    \$id = (int)\$_GET['delete'];
    \$old = \$db->query("SELECT photo FROM teachers WHERE id=\$id")->fetchColumn();
    if (\$old && file_exists("../static/img/teachers/\$old")) unlink("../static/img/teachers/\$old");
    \$db->exec("DELETE FROM teachers WHERE id=\$id");
    header('Location: teachers.php'); exit;
}

\$teachers = \$db->query('SELECT id,name,position,photo FROM teachers ORDER BY id')->fetchAll(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Преподаватели</title></head>
<body>
  <h1>Список преподавателей</h1>
  <a href="teacher_add.php">Добавить преподавателя</a>
  <table border="1" cellpadding="5">
    <tr><th>ID</th><th>Имя</th><th>Должность</th><th>Фото</th><th>Действия</th></tr>
    <?php foreach(\$teachers as \$t): ?>
    <tr>
      <td><?= \$t['id'] ?></td>
      <td><?= htmlspecialchars(\$t['name']) ?></td>
      <td><?= htmlspecialchars(\$t['position']) ?></td>
      <td><?php if(\$t['photo']): ?><img src="../static/img/teachers/<?= htmlspecialchars(\$t['photo']) ?>" width="80"><?php endif; ?></td>
      <td><a href="?delete=<?= \$t['id'] ?>" onclick="return confirm('Удалить?')">Удалить</a></td>
    </tr>
    <?php endforeach; ?>
  </table>
  <p><a href="index.php">← Назад</a></p>
</body>
</html>
