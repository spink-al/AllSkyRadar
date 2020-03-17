<?php

include_once( 'includes/status_messages.php' );

function DisplayLocationConfig(){

  $location_options_str = file_get_contents(RASPI_LOCATION_OPTIONS, true);
  $location_options_array = json_decode($location_options_str, true);

  $text_options = array();
   foreach($location_options_array as $option)
   {
      if ( $option['type'] === 'text' && !in_array($option['name'], ["filename", "fontcolor"])){
	$text_options[] = $option['name'];
      }
   }

  $status = new StatusMessages();
  if (isset($_POST['save_location_options'])) {
    if (CSRFValidate()) {
	  if ($location_settings_file = fopen(RASPI_LOCATION_SETTINGS, 'w')) {
		$settings = array();
	    	foreach ($_POST as $key => $value){
			// We look into POST data to only select camera settings
			if (!in_array($key, ["csrf_token", "save_location_options", "reset_location_options"])){
				if (location_options_array[$key] == "checkbox"){
					$settings[$key] = $value;
				} else {
					$settings[$key] = $value;
				}
			}
	    	}
		fwrite($location_settings_file, json_encode($settings));
		fclose($location_settings_file);
	    	$status->addMessage('LOCATION configuration saved.');
	    	shell_exec('touch /tmp/location_restart');
	  } else {
	    $status->addMessage('Failed to save LOCATION configuration', 'danger');
	  }
    } else {
      error_log('CSRF violation');
    }
  }

  if (isset($_POST['reset_location_options'])) {
    if (CSRFValidate()) {
	  if ($location_settings_file = fopen(RASPI_LOCATION_SETTINGS, 'w')) {
		$settings = array();
	    foreach ($location_options_array as $option){
			$key = $option['name'];
			$value = $option['default'];
			$settings[$key] = $value;
	    }
	    fwrite($location_settings_file, json_encode($settings));
		fclose($location_settings_file);
	    $status->addMessage('LOCATION configuration reset to default');
	  } else {
	    $status->addMessage('Failed to reset LOCATION configuration', 'danger');
	  }
    } else {
      error_log('CSRF violation');
    }
  }

  $location_settings_str = file_get_contents(RASPI_LOCATION_SETTINGS, true);
  $location_settings_array = json_decode($location_settings_str, true);

  $text_options = array();
   foreach($location_options_array as $option)
   {
      if ( $option['type'] === 'text' && !in_array($option['name'], ["filename", "fontcolor"])){
	$text_options[] = $option['name'];
      }
   }

?>
  <div class="row">
    <div class="col-lg-12">
      <div class="panel panel-primary">
        <div class="panel-heading"><i class="fa fa-camera fa-fw"></i> Configure LOCATION Settings</div>
        <!-- /.panel-heading -->
        <div class="panel-body">
          <p><?php $status->showMessages(); ?></p>

          <form method="POST" class="form-inline" action="?page=location_conf" name="location_conf_form">
            <?php CSRFToken()?>

             <?php
			foreach($location_options_array as $option) {
				$label = $option['label'];
				$name = $option['name'];
				$value = $location_settings_array[$option['name']] != null ? $location_settings_array[$option['name']] : $option['default'];
				$description = $option['description'];
				$type = $option['type'];
				echo "<div class='form-group' style='margin: 3px 0'>";
				echo "<label style='width: 140px'>$label</label>";
				if ($type == "text" || $type == "number"){
					echo "<input class='form-control' type='$type' ".
					"style='text-align: right; width: 120px; margin-right: 20px' ".
					"name='$name' value='$value'>";
				} else if ($type == "select"){
					echo "<select class='form-control' name='$name' ".
						"style='width: 120px; margin-right: 20px'>";
					foreach($option['options'] as $opt){
						$val = $opt['value'];
						$lab = $opt['label'];
						if ($value == $val){
							echo "<option value='$val' selected>$lab</option>";
						} else {
							echo "<option value='$val'>$lab</option>";
						}
					}
					echo "</select>";
				} else if ($type == "checkbox"){
					echo "<div class='switch-field'>";
						echo "<input id='switch_no_".$name."' class='form-control' type='radio' ".
        	                                "style='width: 40px; box-shadow:none' ".
                	                        "name='$name' value='0' ".
                        	                ($value == 0 ? " checked " : "").
                                	        ">";
						echo "<label for='switch_no_".$name."'>No</label>";
						echo "<input id='switch_yes_".$name."' class='form-control' type='radio' ".
	                                        "style='width: 40px; box-shadow:none' ".
        	                                "name='$name' value='1' ".
                	                        ($value == 1 ? " checked " : "").
                        	                ">";
						echo "<label for='switch_yes_".$name."'>Yes</label>";
					echo "</div>";
				}
				echo "<span>$description</span>";
				echo "</div><div style='clear:both'></div>";
			 }?>

            <div style="margin-top: 20px">
		<input type="submit" class="btn btn-outline btn-primary" name="save_location_options" value="Save changes">
		<input type="submit" class="btn btn-warning" name="reset_location_options" value="Reset to default values">
	    </div>
          </form>
        </div><!-- ./ Panel body -->
        <!--<div class="panel-footer"><strong>Note,</strong> WEP access points appear as 'Open'. Allsky fw Portal does not currently support connecting to WEP.</div>-->
      </div><!-- /.panel-primary -->
    </div><!-- /.col-lg-12 -->
  </div><!-- /.row -->
<?php
}

?>
