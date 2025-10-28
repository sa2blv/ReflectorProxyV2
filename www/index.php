<?php

$redis = new Redis();
//Connecting to Redis
include 'config.php'

$redis = new Redis();
//Connecting to Redis
$redis->connect($redis_host , '6379');
$redis->auth($auh_key);



$JSON_RAW = $redis->get('PORTAL_PORXY_JSON_CURRENT');

$json = json_decode($JSON_RAW);
$json->proxyData->key = $redis->get('PORTAL_PORXY_JSON_CURRENT_KEY');
header("Access-Control-Allow-Origin: *");
header('Content-Type: application/json');
echo json_encode($json);

$redis->close();



?>
