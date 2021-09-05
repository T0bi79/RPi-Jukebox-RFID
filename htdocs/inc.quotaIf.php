<?php

// Send a request (cmd) to the service and receive the resulting string (reply)
// returns True on success and False on failure.
function quota_if_cmd($cmd, &$reply){
	$result = False;
	$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
	if ($socket !== false) {
		$result = socket_connect($socket, gethostbyname('localhost'), 54711);
		if ($result !== false) {
			socket_write($socket, $cmd, strlen($cmd));
			$reply = socket_read($socket, 1024);
			$result = True;
		}
		// else echo "socket_connect() fehlgeschlagen.\nGrund: ($result) " . socket_strerror(socket_last_error($socket)) . "\n";
		socket_close($socket);
	}
	// else echo "socket_create() fehlgeschlagen: Grund: " . socket_strerror(socket_last_error()) . "\n";
	return $result;
}

// Requests and returns the currently remaining quota in minutes
// returns NULL if failed.
function getRemaingQuota(){
	$quota = NULL;
	$reply = NULL;
	if(quota_if_cmd("getquota", $reply) && is_numeric($reply)){
    	$quota = intval($reply);
	}
    return $quota;
}

// Retrieves the flag if granting quota from web interface is accepted
// returns NULL if failed.
function isSetIfEnabled(){
	$webok = NULL;
	$reply = NULL;
	if(quota_if_cmd("getwebok", $reply) && is_numeric($reply)){
    	$webok = (intval($reply)>0 ? True : False);
	}
    return $webok;
}
