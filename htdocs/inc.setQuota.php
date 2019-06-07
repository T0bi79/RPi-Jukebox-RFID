
<!--
Quota Set Form
-->
        <!-- input-group -->          
        <?php

        $MINUTES_PER_UNIT = 30; // as defined in quota.py

        function getQuotaFromPost(&$q_remaining_minutes){
			if(!isset($_POST['grantquota'])) return false;
			$gq = trim($_POST['grantquota']);
			if($gq == "" || !is_numeric($gq)) return false;
			$gqi = intval($gq);
			$q_remaining_minutes = $gqi * $MINUTES_PER_UNIT;
			return true;
        }


        function getQuotaFromAtq(&$q_remaining_minutes){
	        $quota_endval = exec("sudo atq -q q | awk '{print $5}'");
	        if ($quota_endval != "") {
	            $unixtime = time();
	            /*
	            * For the night owls: if the shutdown time is after midnight (and so on the next day), 
	            * $shutdowntime is something like 00:30:00 and time() is e.g. 23:45:00.
	            * strtotime($shutdowntime) returns the unix time for today and we get a negative 
	            * value in the calculation below.
	            * This is fixed by subtracting a day from the current time, as we only need the difference.
	            */
	            if ($unixtime > strtotime($quota_endval)) {
	                $unixtime = $unixtime - 86400;
	            }
	            $q_remaining_minutes   = round((strtotime($quota_endval)-$unixtime)/60);
	        }
        } 
        
        
        /*
        * Values for pulldown form
        */
        
        $quotapresets = [
		    1,
		    2,
		    3,
		    4,
		    5,
		    6,
		    7,
		    8,
		];
		        
        /*
        * Get remaining time quota.
        * We prefer to determine this by evaluating the POST data.
        * Reason: After new quota was granted via this web-frontend module, the ATQ table might not be ready yet
        * (since inc.header.php starts the quota update asynchronously to avoid blocking the webpage by the animation of possible configured LEDs)
        */
        $q_remaining_minutes   = 0;
		if(!getQuotaFromPost($q_remaining_minutes)){
			getQuotaFromAtq($q_remaining_minutes);
		}

        ?>
        <div class="col-md-4 col-sm-6">
            <div class="row" style="margin-bottom:1em;">
              <div class="col-xs-6">
              <h4><?php print $lang['globalQuotaEdit']; ?></h4>
                <form name='grantquota' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <div class="input-group my-group">
                    <select id="grantquota" name="grantquota" class="selectpicker form-control">
                        <option value='0'><?php print $lang['globalOff']; ?></option>
                    <?php
                    foreach($quotapresets as $i) {
                        print "
                        <option value='".$i."'";
                        print ">".($MINUTES_PER_UNIT * $i)." min</option>";
                    }
                    print "\n";
                    ?>
                    </select> 
                    <span class="input-group-btn">
                        <input type='submit' class="btn btn-default" name='submit' value='<?php print $lang['globalSet']; ?>'/>
                    </span>
                  </div>
                </form>
              </div>
              
              <div class="col-xs-6">
                  <div class="orange c100 p<?php print round(min($q_remaining_minutes, 240)*100/240); ?>">
                    <span><?php 
                        if($q_remaining_minutes == 0) {
                            print $lang['globalOff'];
                        } else {
                            print $q_remaining_minutes."min"; 
                        }
                    ?></span>
                    <div class="slice">
                        <div class="bar"></div>
                        <div class="fill"></div>
                    </div>
                  </div> 
              </div>
            </div><!-- ./row -->
        </div>
        <div class="col-md-4 col-sm-6">
              <h4><?php print $lang['globalQuotaSettings']; ?></h4>
              <p>To follow...</p>
        </div>
        <!-- /input-group -->
