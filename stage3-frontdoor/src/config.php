<?php
$DB_HOST = "127.0.0.1";
$DB_USER = "portal_app";
$DB_PASS = getenv("DB_APP_PASSWORD") ?: "P0rtal_App_2026";
$DB_NAME = "actionlk_portal";

$conn = mysqli_connect($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME);
if (!$conn) {
    http_response_code(500);
    die("Database connection failed.");
}
