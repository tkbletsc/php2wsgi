<?php

$pythonScript = 'wsgi-host.py';

$DEBUG = false;  // Set this to true to enable debugging, or false to disable

// Define the wsgi environment variables based on PHP inputs
$environ = [
    'REQUEST_METHOD' => $_SERVER['REQUEST_METHOD'],
    'PATH_INFO' => $_SERVER['SCRIPT_URL'],
    'QUERY_STRING' => $_SERVER['QUERY_STRING'],
    'CONTENT_TYPE' => $_SERVER['CONTENT_TYPE'] ?? null,
    'CONTENT_LENGTH' => $_SERVER['CONTENT_LENGTH'],
    'SERVER_NAME' => $_SERVER['SERVER_NAME'],
    'SERVER_PORT' => $_SERVER['SERVER_PORT'],
    'SERVER_PROTOCOL' => $_SERVER['SERVER_PROTOCOL'],
    'HTTP_ACCEPT' => $_SERVER['HTTP_ACCEPT'],
    'HTTP_USER_AGENT' => $_SERVER['HTTP_USER_AGENT'],
    'wsgi.url_scheme' => $_SERVER['REQUEST_SCHEME'] # http, https, etc
];

if ($DEBUG) {
    print_r($_SERVER);
    print("<hr>");
}

$environ_json = json_encode($environ);

// Build the command to execute the Python script with the environment variables
$command = array("python3",$pythonScript,$environ_json);

// Open a process to execute the command
$descriptors = [
    0 => ['pipe', 'r'],
    1 => ['pipe', 'w'],
    2 => ['pipe', 'w'],
    3 => ['pipe', 'w'], # we use non-standard file descriptor 3 to get the status and headers back
];

$process = proc_open($command, $descriptors, $pipes);

if (is_resource($process)) {
    // performance danger: this loads entire POST into memory, then forwards -- bad for big posts like file uploads
    $phpInput = file_get_contents('php://input');
    fwrite($pipes[0], $phpInput);
    
    // Close the input pipe
    fclose($pipes[0]);

    // Read the output from the script
    $output = stream_get_contents($pipes[1]);
    fclose($pipes[1]);

    // Read errors, if any
    $errors = stream_get_contents($pipes[2]);
    fclose($pipes[2]);
    
    $result_json = stream_get_contents($pipes[3]); # we use non-standard file descriptor 3 to get the status and headers back
    fclose($pipes[3]);

    // Close the process
    proc_close($process);
    
    # we read the status and headers via a special file dsecriptor #3 which the wsgi host knows to write into
    # format is a json with the status code (e.g. 200), status message (e.g. "OK"), and dictionary of HTTP headers
    $result = json_decode($result_json);
    list($status_code,$status_msg,$headers) = $result;
    header("HTTP/1.1 $status_code $status_msg");
    foreach ($headers as $key => $value) {
        header("$key: $value");
    }
    
    // Print the results
    echo $output;
    if ($DEBUG && $errors) {
        echo("<hr><pre style='background-color: #FFCCCC;'>$errors</pre>");
    }
    if ($DEBUG && $result) {
        print("<hr><pre style='background-color: #CCCCFF;'>");
        print_r($result);
        print("</pre>");
    }
} else {
    header("HTTP/1.1 500 Python wrapper error");
    echo "Failed to open child python process.\n";
}

