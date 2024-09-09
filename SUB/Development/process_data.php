<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Process Data</title>
</head>
<body>
    <h1>Data Processing</h1>

    <?php
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        // Retrieve the data from the form
        $python_output = $_POST["output"];

        // Display the received data
        echo "<p>Received data from Python script:</p>";
        echo "<pre>$python_output</pre>";
    } else {
        echo "<p>No data received.</p>";
    }
    ?>

</body>
</html>
