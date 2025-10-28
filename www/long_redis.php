<?php
header("Access-Control-Allow-Origin: *");
header('Content-Type: application/json');
$redis = new Redis();
include 'config.php'

$redis = new Redis();
//Connecting to Redis
$redis->connect($redis_host , '6379');
$redis->auth($auh_key);

$redis1 = new Redis();

//Connecting to Redis
$redis1->connect($redis_host , '6379');
$redis1->auth($auh_key);




$JSON_RAW = $redis->get('PORTAL_PORXY_JSON_CURRENT');


// set php runtime to unlimited
set_time_limit(5000);

$key = isset($_GET['key']) ? (int)$_GET['key'] : null;


if($key == null )
{
  $JSON_RAW = $redis->get('PORTAL_PORXY_JSON_CURRENT');
  $json = json_decode($JSON_RAW);
  $json->proxyData->key = $redis->get('PORTAL_PORXY_JSON_CURRENT_KEY');
   echo json_encode($json,JSON_PRETTY_PRINT);
    exit(0);
}


// main loop



$redis->subscribe(['PORTAL_PORXY_JSON_CURRENT_KEY_LIVE'], function($instance, $channelName, $message) {

       global $redis1;
       global $redis;

       if($key == null || ( floatval($key) < floatval($message)))
       {
         $JSON_RAW = $redis1->get('PORTAL_PORXY_JSON_CURRENT');
         $json = json_decode($JSON_RAW);
         $json->proxyData->key = $redis1->get('PORTAL_PORXY_JSON_CURRENT_KEY');
         echo json_encode($json,JSON_PRETTY_PRINT);
         $redis1->close();
         exit(0);
       }

});






