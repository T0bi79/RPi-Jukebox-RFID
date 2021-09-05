<!--
Quota Set Form
-->
<!-- input-group -->
<?php
        include ("inc.quotaIf.php");

        function printGrantForm($lng, $remaining_minutes, $set_enabled){
	        print "            <div class='row' style='margin-bottom:1em;'>\n";
            print "                <div class='col-xs-5'>\n";
            print "                    <div class='orange c100 p".round(min($remaining_minutes, 240)*100/240)."'>\n";
            print "                        <span>\n";
            if($remaining_minutes <= 0) {
                print $lng['globalOff'];
            } else {
                print $remaining_minutes.'min';
            }
            print "                        </span>\n";
            print "                        <div class='slice'>\n";
            print "                            <div class='bar'></div>\n";
            print "                            <div class='fill'></div>\n";
            print "                        </div>\n";
            print "                    </div>\n";
            print "                </div>\n";
            if($set_enabled){
                print "                <div class='col-md-6'><br>\n";
                print "                    <form name='grantquota' method='post' action='".$_SERVER['PHP_SELF']."'>\n";
                print "                        <input type='hidden' id=\"grantquota1\" name=\"grantquota\" value=\"0\">\n";
                print "                        <input type='submit' class='btn btn-default' name='submit' value='".$lng["globalQuotaUnlimited"]."'/>\n";
                print "                    </form>\n";
                print "                </div>\n";
            }
	        print "            </div><!-- ./row -->\n";
            if($set_enabled){
                print "            <div class='row' style='margin-bottom:1em;'>\n";
                print "                <form name='grantquota' method='post' action='".$_SERVER['PHP_SELF']."'>\n";
                print "                    <div class='col-md-8'>\n";
                print "                        <input type='submit' class='btn btn-default' name='submit' value='".$lng['globalQuotaGrant']."'/>\n";
                print "                    </div>\n";
                print "                    <div class='col-md-4'>\n";
                print "                        <input value=\"".($remaining_minutes>0?$remaining_minutes:"")."\" id=\"grantquota2\" name=\"grantquota\" class=\"form-control input-md\" type=\"number\" required=\"required\">\n";
                print "                    </div>\n";
                print "                </form>\n";
                print "            </div><!-- ./row -->\n";
            }
        }

        $q_remaining_minutes = getRemaingQuota(); # Get remaining time quota in minutes
        
        if($q_remaining_minutes === NULL){
	        print "        <div class=\"col-md-12 col-xs-12\">\n";
	        print "            <h4>Quota service is not installed (or not responding).</h4>\n";
	        print "            <p>Read RPi-Jukebox-RFID\components\quota\README.md about how to set it up.</p>\n";
	        print "        </div>\n";
        }
        else{
	        print "        <div class='col-md-4 col-sm-6'>\n";
            printGrantForm($lang, $q_remaining_minutes, isSetIfEnabled());
	        print "        </div>\n";
        }
        
?>
        <!-- /input-group -->
