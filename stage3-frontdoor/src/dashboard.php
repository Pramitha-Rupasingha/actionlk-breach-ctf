<?php
session_start();

if (!isset($_SESSION["role"])) {
    header("Location: login.php");
    exit;
}

$flag = getenv("STAGE3_FLAG") ?: "ACTIONLK{flag_not_set}";
$isAdmin = $_SESSION["role"] === "admin";
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>ActionLK Employee Portal — Dashboard</title>
    <style>
        body { font-family: sans-serif; background:#0f1628; color:#e6e6e6; margin:0; padding:40px;}
        .box { background:#182236; padding:24px 32px; border-radius:10px; max-width:560px; }
        .flag { background:#0f1628; border:1px dashed #3b6bdb; padding:12px; border-radius:6px;
                font-family:monospace; margin-top:16px; }
        a { color:#8ab4ff; }
    </style>
</head>
<body>
    <div class="box">
        <h1>Welcome, <?= htmlspecialchars($_SESSION["user"]) ?></h1>
        <?php if ($isAdmin): ?>
            <p>Admin dashboard — fraud monitoring escalation log</p>
            <p>Internal note: the file server at <code>fileshare.actionlk.internal</code>
               is still reachable over plain FTP — flagged for a config review
               after this quarter's audit.</p>
            <div class="flag"><?= htmlspecialchars($flag) ?></div>
        <?php else: ?>
            <p>You are logged in as a standard employee. Nothing to see here.</p>
        <?php endif; ?>
        <p><a href="logout.php">Log out</a></p>
    </div>
</body>
</html>
