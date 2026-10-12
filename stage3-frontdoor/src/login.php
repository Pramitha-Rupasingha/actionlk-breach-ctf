<?php
session_start();
require __DIR__ . "/config.php";

$error = "";

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $username = $_POST["username"] ?? "";
    $password = $_POST["password"] ?? "";

    // ---------------------------------------------------------------
    // STAGE-03 "Front Door" — intentionally vulnerable to SQL injection.
    // User input is concatenated directly into the query instead of using
    // a parameterised/prepared statement. This is deliberate for the
    // ActionLK Breach CTF (IE3132 Assignment 01) and must NOT be "fixed"
    // in the running challenge container.
    // ---------------------------------------------------------------
    $query = "SELECT id, username, role FROM users "
           . "WHERE username = '$username' AND password = '$password'";
    $result = mysqli_query($conn, $query);

    if ($result && mysqli_num_rows($result) > 0) {
        $row = mysqli_fetch_assoc($result);
        $_SESSION["user"] = $row["username"];
        $_SESSION["role"] = $row["role"];
        header("Location: dashboard.php");
        exit;
    } else {
        $error = "Invalid username or password.";
    }
}
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>ActionLK Employee Portal — Login</title>
    <style>
        body { font-family: sans-serif; background:#0f1628; color:#e6e6e6;
               display:flex; align-items:center; justify-content:center; height:100vh; margin:0;}
        .card { background:#182236; padding:32px 40px; border-radius:10px; width:320px; }
        h1 { font-size:18px; margin-bottom:4px;}
        p.sub { color:#8a93a8; margin-top:0; font-size:13px;}
        input { width:100%; padding:10px; margin:8px 0; border-radius:6px; border:1px solid #2c3856;
                background:#0f1628; color:#e6e6e6; box-sizing:border-box;}
        button { width:100%; padding:10px; border:none; border-radius:6px; background:#3b6bdb;
                 color:white; font-weight:bold; cursor:pointer; margin-top:8px;}
        .error { color:#ff6b6b; font-size:13px; margin-top:10px;}
    </style>
</head>
<body>
    <div class="card">
        <h1>ActionLK Employee Portal</h1>
        <p class="sub">Internal use only — authorised personnel</p>
        <form method="post">
            <input type="text" name="username" placeholder="Username" autocomplete="off">
            <input type="password" name="password" placeholder="Password" autocomplete="off">
            <button type="submit">Sign in</button>
        </form>
        <?php if ($error): ?><div class="error"><?= htmlspecialchars($error) ?></div><?php endif; ?>
    </div>
</body>
</html>
