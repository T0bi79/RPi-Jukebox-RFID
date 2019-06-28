<!--
Quota Set Form
-->
<!-- input-group -->
<?php
        include ("inc.quotaCfg.php");

        function getRemaingQuota(){
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
                return round((strtotime($quota_endval)-$unixtime)/60);
            }
        }

        function evalPostAction(){
            function postGetInt($key){
                if(!isset($_POST[$key])) return null;
                $s = trim($_POST[$key]);
                if($s == "") return null;
                return intval($s);
            }

            function postGetFloat($key){
                if(!isset($_POST[$key])) return null;
                $s = trim($_POST[$key]);
                if($s == "") return null;
                return floatval($s);
            }

            function postGetIntArray($key){
                if(!isset($_POST[$key])) return null;
                $s = trim($_POST[$key]);
                if($s == "") return [];
                $gp = explode(",", $s);
                $gi = [];
                    foreach ($gp as $g) {
                    if(!preg_match("/^[0-9]+$/", $g)) return null;
                    $gi[] = intval($g);
                }
                return $gi;
            }

            global $conf;

           # look for the presence of each valid config element
            $tupels = [ # post variable, config name, parse function
                ["quota_en","enabled",         'postGetInt'],
                ["quota_dm","default_minutes", 'postGetInt'],
                ["quota_mr","minutes_to_reset",'postGetInt'],
                ["quota_lg","led_gpios",       'postGetIntArray'],
                ["quota_mu","led_minutes",     'postGetInt'],
                ["quota_la","led_animation",   'postGetFloat']
            ];
            $formaterr = False;
            $updvar = null;
            foreach($tupels as $t) {
                $value = $t[2]($t[0]);
                if($value !== null){
                    if(!checkImmediateValue($t[1], $value)) $formaterr = True;
                    else if($value != readElem($t[1])){
                        writeElem($t[1], $value);
                        $updvar = $t[0];
                    }
                }
            }

            # notify quota script about relevant changes
            if($updvar){
                if($updvar == "quota_en" && postGetInt("quota_en")){
                    # quota system was enabled, call init routine
                    writeElem("last_quota_activation", time()); // ensure that there'll be default quota
                    exec("/usr/bin/sudo python ".$conf['scripts_abs']."/quota.py -i");
                }
                else if($updvar == "quota_en"){
                    # quota system was disabled, cancel all timers
                    exec("/usr/bin/sudo python ".$conf['scripts_abs']."/quota.py -c");
                }
                # on changes incompatible to active timers we cancel them
                if($updvar=="quota_mu" || $updvar=="quota_lg"){
                    exec("/usr/bin/sudo python ".$conf['scripts_abs']."/quota.py -c");
                }
                # notify quota script about changed GPIO configuration
                if($updvar=="quota_lg"){
                    exec("/usr/bin/sudo python ".$conf['scripts_abs']."/quota.py -g");
                }
            }

            return $formaterr;
        }

        function printEnableForm($lng, $cfg){
            print "        <div class='col-md-12 col-sm-12'>\n";
            print "            <form name='quota_en' method='post' action='".$_SERVER['PHP_SELF']."'>\n";
            $tgl = ($cfg['enabled'] ? 0 : 1);
            print "                <input type='hidden' id='quota_en' name='quota_en' value='".$tgl."'/>\n";
            $lbl = ($tgl ? $lng['globalQuotaEnable'] : $lng['globalQuotaDisable']);
            print "                <input type='submit' class='btn btn-default' name='submit' value='".$lbl."'/>\n";
            print "            </form>\n";
            print "        </div>\n";
        }

        function printGrantForm($lng, $remaining_minutes){
	        print "            <div class='row' style='margin-bottom:1em;'>\n";
            print "                <div class='col-xs-5'>\n";
            print "                    <div class='orange c100 p".round(min($remaining_minutes, 240)*100/240)."'>\n";
            print "                        <span>\n";
            if($remaining_minutes == 0) {
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
            print "                <div class='col-md-6'><br>\n";
            print "                    <form name='grantquota' method='get' action='".$_SERVER['PHP_SELF']."'>\n";
            print "                        <input type='hidden' id=\"grantquota\" name=\"grantquota\" value=\"0\">\n";
            print "                        <input type='submit' class='btn btn-default' name='submit' value='".$lng["globalQuotaUnlimited"]."'/>\n";
            print "                    </form>\n";
            print "                </div>\n";
	        print "            </div><!-- ./row -->\n";
            print "            <div class='row' style='margin-bottom:1em;'>\n";
            print "                <form name='grantquota' method='get' action='".$_SERVER['PHP_SELF']."'>\n";
            print "                    <div class='col-md-8'>\n";
            print "                        <input type='submit' class='btn btn-default' name='submit' value='".$lng['globalQuotaGrant']."'/>\n";
            print "                    </div>\n";
            print "                    <div class='col-md-4'>\n";
            print "                        <input value=\"".$remaining_minutes."\" id=\"grantquota\" name=\"grantquota\" class=\"form-control input-md\" type=\"number\" required=\"required\">\n";
            print "                    </div>\n";
            print "                </form>\n";
            print "            </div><!-- ./row -->\n";
        }

        function printEditForm($formhead, $in_val, $out_postvar, $txt_lbl, $txt_ph, $txt_hlp, $txt_btn, $isnum=True, $req = True){
            print "        <div class=\"col-md-4 col-sm-6\">\n";
            print "            <h4>".$formhead."</h4>\n";

            print "            <form name=\"".$out_postvar."\" method=\"post\" action=\"".$_SERVER['PHP_SELF']."\">\n";
            print "                <div class=\"form-group\">\n";
            print "                    <label class=\"col-md-6 control-label\" for=\"".$out_postvar."\">".$txt_lbl."</label>\n";
            print "                    <div class=\"input-group my-group\">\n";
            $tp = ($isnum ? "number" : "text");
            $rs = ($req ? " required=\"required\"" : "");
            print "                        <input value=\"".$in_val."\" id=\"".$out_postvar."\" name=\"".$out_postvar."\" placeholder=\"".$txt_ph."\" class=\"form-control input-md\" type=\"".$tp."\"".$rs.">\n";
            print "                        <span class=\"input-group-btn\">\n";
            print "                            <input type=\"submit\" class=\"btn btn-default\" name=\"submit\" value=\"".$txt_btn."\"/>\n";
            print "                        </span>\n";
            print "                    </div>\n";
            print "                </div>\n";
            print "                <span class=\"help-block\">".$txt_hlp."</span>\n";
            print "            </form>\n";

            print "        </div>\n";
        }


        function printSettings($lng, $cfg){
            function printSettingLine($txt_lbl, $in_val, $out_getvar){
                print "                <tr>\n";
                print "                    <td>".$txt_lbl."&nbsp;</td>\n";
                $tag1 = ($out_getvar ? "<a href=\"".$_SERVER['PHP_SELF']."?".$out_getvar."\" style=\"text-decoration:none;\">":"");
                $tag2 = ($out_getvar ? "</a>":"");
                print "                    <td>".$tag1."&#x270E;".$tag2.$in_val."</td>\n";
                print "                </tr>\n";
            }

            print "        <div class='col-md-4 col-sm-6'>";
            print "            <h4>".$lng['globalQuotaView']."</h4>";
            print "            <table>";

            $dsp = $cfg["default_minutes"]." minutes";
            printSettingLine($lng['globalQ_dm_lbl'],  $dsp, (isset($_GET["qedt_dm"])  ? "" : "qedt_dm"));

            $dsp = $cfg["minutes_to_reset"]." min";
            printSettingLine($lng['globalQ_mr_lbl'], $dsp, (isset($_GET["qedt_mr"]) ? "" : "qedt_mr"));

            $dsp = "No LEDs";
            $lar = $cfg["led_gpios"];
            if($lar !== null && ($n_leds = count($lar))>0){
                $dsp = $n_leds." LEDs: ";
                for($i=0; $i < $n_leds; $i++) {
                    $dsp.=$lar[$i];
                    if($i < ($n_leds-1)) $dsp.=",";
                }
            }

            printSettingLine($lng['globalQ_lg_lbl'],  $dsp, (isset($_GET["qedt_lg"])  ? "" : "qedt_lg"));

            if($lar !== null && count($lar) > 0){
                $dsp = $cfg["led_minutes"]." min";
                printSettingLine($lng['globalQ_mu_lbl'], $dsp, (isset($_GET["qedt_mu"]) ? "" : "qedt_mu"));

                $dsp = $cfg['led_animation']." sec";
                printSettingLine($lng['globalQ_la_lbl'],  $dsp, (isset($_GET["qedt_la"])  ? "" : "qedt_la"));
            }


            print "            </table>";
            print "        </div>";
        }

        function printEditArea($postprob, $lng, $cfg){
            if($postprob){
                print "        <div class=\"col-md-4 col-sm-6\">\n";
                print "            <h4>".$lng['globalQuotaNotify']."</h4>\n";
                print "            <p style=\"color:#ff0000\">".$lng['globalQuotaFrmErr']."</p>\n";
                print "        </div>\n";
            }
            else{
                $btn = $lng['globalSet'];
                $leddsp = "";
                if($cfg["led_gpios"] !== null && ($n_leds = count($cfg["led_gpios"]))>0){
                    for($i=0; $i < $n_leds; $i++) {
                        $leddsp.=$cfg["led_gpios"][$i];
                        if($i < ($n_leds-1)) $leddsp.=",";
                    }
                }
                if     (isset($_GET["qedt_dm"])) printEditForm($lng['globalQuotaEdit'], $cfg["default_minutes"],  "quota_dm", $lng["globalQ_dm_lbl"], $lng["globalQ_dm_ph"], $lng["globalQ_dm_hlp"], $btn);
                else if(isset($_GET["qedt_mr"])) printEditForm($lng['globalQuotaEdit'], $cfg["minutes_to_reset"], "quota_mr", $lng["globalQ_mr_lbl"], $lng["globalQ_mr_ph"], $lng["globalQ_mr_hlp"], $btn);
                else if(isset($_GET["qedt_lg"])) printEditForm($lng['globalQuotaEdit'], $leddsp,                  "quota_lg", $lng["globalQ_lg_lbl"], $lng["globalQ_lg_ph"], $lng["globalQ_lg_hlp"], $btn, False, False);
                else if(isset($_GET["qedt_mu"])) printEditForm($lng['globalQuotaEdit'], $cfg["led_minutes"],      "quota_mu", $lng["globalQ_mu_lbl"], $lng["globalQ_mu_ph"], $lng["globalQ_mu_hlp"], $btn);
                else if(isset($_GET["qedt_la"])) printEditForm($lng['globalQuotaEdit'], $cfg["led_animation"],    "quota_la", $lng["globalQ_la_lbl"], $lng["globalQ_la_ph"], $lng["globalQ_la_hlp"], $btn, False);
            }
        }

        $postprob = evalPostAction();
        $q_remaining_minutes = getRemaingQuota(); # Get remaining time quota in minutes
        $cfg = readCfg();

        # left column: on/off and (if on) quota granting
        print "        <div class='col-md-4 col-sm-6'>\n";
        print "            <div class='row' style='margin-bottom:1em;'>\n";
        printEnableForm($lang, $cfg);
        print "            </div><!-- ./row -->\n";
        if($cfg['enabled']){
            printGrantForm($lang, $q_remaining_minutes);
        }
        print "        </div>\n";
        if($cfg['enabled']){
            printSettings($lang, $cfg);
            printEditArea($postprob, $lang, $cfg);
        }

?>
        <!-- /input-group -->
