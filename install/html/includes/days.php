<?php

function delete_directory($dirname) {
	error_log("deleting image directory: rm -rf ".$dirname."/");
	$result=system("sudo rm -rf ".$dirname);
        error_log($result);
	return true;
}

function ListDays(){

$days = array();

if (isset($_POST['delete_directory'])) {
	$dir = $_POST['delete_directory'];
  echo '<div class="alert alert-warning">Deleted directory '.$dir.'</div>';
  delete_directory('/home/pi/allsky/images/'.$dir);
}

if ($handle = opendir('/home/pi/allsky/images/')) {
    $blacklist = array('.', '..', 'somedir', 'somefile.php');
    while (false !== ($day = readdir($handle))) {
        if (!in_array($day, $blacklist)) {
            $days[] = $day;
        }
    }
    closedir($handle);
}

arsort($days);

?>
<style>
	table th {
		text-align:center;
		padding: 0 10px;
	}
	table tr td {
		padding: 0 10px;
	}
</style>
<div class="row">
  <div class="col-lg-12">
  <div class="panel panel-primary">
  <div class="panel-heading"><i class="fa fa-image fa-fw" style="margin-right: 10px"></i>Images</div>
  <div class="panel-body">
    <div class="row">
	<form action="?page=list_days" method="POST" onsubmit="return confirm('Are you sure you want to delete ALL images for that day?');">
	<table style='margin: 20px; text-align:center'>
		<thead>
			<tr>
				<th style="text-align:center">Day</th>
				<th style="text-align:center">Images</th>
				<th style="text-align:center">Timelapse</th>
				<th style="text-align:center">Keogram</th>
				<th style="text-align:center">Startrails</th>
			</tr>
		</thead>
		<tbody>
<?php
echo "<tr>
                                <td style='font-weight:bold'>All
                                </td>
                                <td></td>
				<td></td>
                                <td><a href='index.php?page=list_keograms&day=all' title='All Keograms'><i class='fa fa-barcode fa-lg fa-fw'></i></a>
                                </td>
                                <td><a href='index.php?page=list_startrails&day=all' title='All Startrails'><i class='fa fa-circle-notch fa-lg fa-fw'></i></a>
                                </td>
                                <td style='padding: 22px 0'></td>
                        </tr>";
foreach ($days as $day) {
	echo "<tr>
                                <td style='font-weight:bold'>$day
                                </td>
				<td><a href='index.php?page=list_images&day=$day' title='Images'><i class='fa fa-image fa-lg fa-fw'></i></a>
				</td>
				<td><a href='index.php?page=list_videos&day=$day' title='Timelapse'><i class='fa fa-film fa-lg fa-fw'></i></a>
                                </td>
                                <td><a href='index.php?page=list_keograms&day=$day' title='Keogram'><i class='fa fa-barcode fa-lg fa-fw'></i></a>
                                </td>
  				<td><a href='index.php?page=list_startrails&day=$day' title='Startrails'><i class='fa fa-circle-notch fa-lg fa-fw'></i></a>
                                </td>
				<td style='padding: 5px'>
					<button type='submit'
						class='btn btn-danger'
						data-toggle='confirmation'
						name='delete_directory'
						value='$day'
						style='width: 90px; text-align: center, color:white'>
					<i class='fa fa-trash text-danger' style='color:white'></i> Delete</button>
				</td>
			</tr>";
}
?>
		</tbody>
	</table>
	</form>
    </div><!-- /.row -->
	</div><!-- /.panel-body -->
  </div><!-- /.panel-primary -->
  </div><!-- /.col-lg-12 -->
  </div><!-- /.row -->
  <?php 
}

?>


