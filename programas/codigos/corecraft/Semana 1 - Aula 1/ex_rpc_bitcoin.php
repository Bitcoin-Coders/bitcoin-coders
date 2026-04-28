<?php
$url  ="http://127.0.0.1:58443/";
$user ="teste";
$pass ="teste";

$payload =json_encode([
"jsonrpc" =>"1.0",
"id"      =>"corecraft",
"method"  =>"getblockchaininfo",
"params"  => []
]);

$ch =curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER,true);
curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
curl_setopt($ch, CURLOPT_USERPWD,"$user:$pass");
curl_setopt($ch, CURLOPT_POSTFIELDS,$payload);

$response =curl_exec($ch);
curl_close($ch);

$data =json_decode($response,true);
echo"<h1>Status do Node Bitcoin</h1>";
echo"<p>Chain: " .$data["result"]["chain"] ."</p>";
echo"<p>Altura: " .$data["result"]["blocks"] ."</p>";
