<?php
#$filename = 'button.txt';
#var_dump($argv);
#@ $fp = fopen("../messages/".$filename, 'w');
@ $fp = fopen("/tmp/AllSkyRadar/highlight", 'w');
if (!$fp)
{
    echo '<p><strong>Cannot generate message file</strong></p></body></html>';
    exit;
}
else
{
/*
foreach ($argv as $arg) {
    $e=explode("=",$arg);
    if(count($e)==2)
        $_GET[$e[0]]=$e[1];
    else   
        $_GET[$e[0]]=0;
echo $e

}
*/
//$filenamecs = 'current_speed'; @ $fpcs = fopen("../messages/".$filenamecs,"r"); if ($fpcs){  $line = fgets($fpcs) ;fclose($fpcs);}
$a = $_POST['name'];
#$a = "asasas";
#$outputstring1  = 'X:';
#$outputstring2  = $a ;
#$outputstring3  = $outputstring1.$outputstring2.PHP_EOL;
$outputstring3  = $a.PHP_EOL;

fwrite($fp, $outputstring3);

fclose($fp);
echo "Message inserted";
}
?>

