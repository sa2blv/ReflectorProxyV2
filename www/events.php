<?php
header('Content-Type: text/event-stream');
header('Cache-Control: no-cache'); // recommended to prevent caching of event data.

include 'config.php'

$redis = new Redis();
//Connecting to Redis
$redis->connect($redis_host , '6379');
$redis->auth($auh_key);

$redis1 = new Redis();
$redis1->connect($redis_host , '6379');
$redis1->auth($auh_key);



/**
 * Constructs the SSE data format and flushes that data to the client.
 *
 * @param string $id Timestamp/id of this connection.
 * @param string $msg Line of text that should be transmitted.
 */



function sendMsg($id, $msg) {
  echo "id: $id\n";
  echo "data: $msg \n\n";
  echo "\n";
  ob_flush();
  flush();
}


$i = 1;



$redis->subscribe(['PORTAL_PORXY_JSON_CURRENT_KEY_LIVE'], function($instance, $channelName, $message) {

       global $redis1;
       global $redis;

         $JSON_RAW = $redis1->get('PORTAL_PORXY_JSON_CURRENT');
         $json = json_decode($JSON_RAW);
         $json->proxyData->key = $redis1->get('PORTAL_PORXY_JSON_CURRENT_KEY');
         $datan = json_encode($json);
         sendMsg($i++, $datan);

});

while(1) {
	
	sleep(1);
}


