<?php
header("Access-Control-Allow-Origin: *");
header('Content-Type: application/json');
$redis = new Redis();
include 'config.php'

$redis = new Redis();
//Connecting to Redis
$redis->connect($redis_host , '6379');
$redis->auth($auh_key);


/*
$JSON_RAW = $redis->get('PORTAL_PORXY_JSON_CURRENT');

$json = json_decode($JSON_RAW);
$json->proxyData->key = $redis->get('PORTAL_PORXY_JSON_CURRENT_KEY');
*/
// set php runtime to unlimited
set_time_limit(5);
$key = $_GET['key'];
if (!$key)
{
        $JSON_RAW = $redis->get('PORTAL_PORXY_JSON_CURRENT');
        $json = json_decode($JSON_RAW);
        $json->proxyData->key = $redis->get('PORTAL_PORXY_JSON_CURRENT_KEY');
         echo json_encode($json,JSON_PRETTY_PRINT);
        // leave this loop step
exit(0);       
}



// main loop
$i =0;
while (true) 
{

    // if ajax request has send a timestamp, then $last_ajax_call = timestamp, else $last_ajax_call = null
    $key = isset($_GET['key']) ? (int)$_GET['key'] : null;
    $get_current_key = $redis->get('PORTAL_PORXY_JSON_CURRENT_KEY');

    // if no timestamp delivered via ajax or data.txt has been changed SINCE last ajax timestamp
    if ($key == null || ( floatval($key) < floatval($get_current_key)) || floatval($get_current_key) < 10 ) {
        $JSON_RAW = $redis->get('PORTAL_PORXY_JSON_CURRENT');
        $json = json_decode($JSON_RAW);
        $json->proxyData->key = $redis->get('PORTAL_PORXY_JSON_CURRENT_KEY');
         echo json_encode($json,JSON_PRETTY_PRINT);
        // leave this loop step
        break;
    } else {
        // wait for 0.2 sec (not very sexy as this blocks the PHP/Apache process, but that's how it goes)
//        sleep( 0.5 );
        usleep(30000);
        continue;
    }
if($i == 1000)
{
echo "fail";
}
$i++;

}
