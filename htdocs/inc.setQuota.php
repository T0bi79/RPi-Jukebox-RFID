
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

        function evalPostAction(){
            global $conf;

           # look for the presence of each valid config element
            $tupels = [ # post variable, config name, parse function
                ["quota_mu","minutes_per_unit",'postGetInt'],
                ["quota_du","default_units",   'postGetInt'],
                ["quota_mr","minutes_to_reset",'postGetInt'],
                ["quota_lg","led_gpios",       'postGetIntArray'],
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
                # on changes incompatible to active timers we cancel them
                if($updvar=="quota_mu" || $updvar=="quota_lg"){
                    $cmd = "/usr/bin/sudo python ".$conf['scripts_abs']."/quota.py -c";
                    print "cmd: ".$cmd."<br>\n";
                    exec($cmd);
                }
                # notify quota script about changed GPIO configuration
                if($updvar=="quota_lg"){
                    $cmd = "/usr/bin/sudo python ".$conf['scripts_abs']."/quota.py -g";
                    print "cmd: ".$cmd."<br>\n";
                    exec($cmd);
                }
            }

            return $formaterr;
        }

        $postprob = evalPostAction();

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
            9,
            10,
        ];

        /*
        * Get remaining time quota in minutes
        */
        $q_remaining_minutes = getRemaingQuota();

        ?>
        <div class="col-md-4 col-sm-6">
            <div class="row" style="margin-bottom:1em;">
              <div class="col-xs-6">
              <h4><?php print $lang['globalQuotaGrant']; ?></h4>
                <form name='grantquota' method='get' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <div class="input-group my-group">
                    <select id="grantquota" name="grantquota" class="selectpicker form-control">
                        <option value='0'><?php print $lang['globalOff']; ?></option>
<?php
        $mpu = readElem("minutes_per_unit");
        if($mpu === null) $mpu = 0;
        foreach($quotapresets as $i) {
            print "                        <option value='".$i."'>".$i." units (".($mpu * $i)." min)</option>\n";
        }?>
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
            <h4><?php print $lang['globalQuotaView']; ?></h4>
            <table>
<?php
    $cfg = readCfg();

    function printSettingLine($txt_lbl, $in_val, $out_getvar){
        print "                <tr>\n";
        print "                    <td>".$txt_lbl."&nbsp;</td>\n";
        $tag1 = ($out_getvar ? "<a href=\"".$_SERVER['PHP_SELF']."?".$out_getvar."\" style=\"text-decoration:none;\">":"");
        $tag2 = ($out_getvar ? "</a>":"");
        print "                    <td>".$tag1."&#x270E;".$tag2.$in_val."</td>\n";
        print "                </tr>\n";
    }

    $dsp = $cfg["default_units"]." units (".( $cfg["minutes_per_unit"]*$cfg["default_units"])." min)";
    printSettingLine($lang['globalQ_du_lbl'],  $dsp, (isset($_GET["qedt_du"])  ? "" : "qedt_du"));

    $dsp = $cfg["minutes_per_unit"]." min";
    printSettingLine($lang['globalQ_mu_lbl'], $dsp, (isset($_GET["qedt_mu"]) ? "" : "qedt_mu"));

    $dsp = $cfg["minutes_to_reset"]." min";
    printSettingLine($lang['globalQ_mr_lbl'], $dsp, (isset($_GET["qedt_mr"]) ? "" : "qedt_mr"));


    $dsp = "No LEDs";
    $lar = $cfg["led_gpios"];
    if($lar !== null && ($n_leds = count($lar))>0){
        $dsp = $n_leds." LEDs: ";
        for($i=0; $i < $n_leds; $i++) {
            $dsp.=$lar[$i];
            if($i < ($n_leds-1)) $dsp.=",";
        }
    }

    printSettingLine($lang['globalQ_lg_lbl'],  $dsp, (isset($_GET["qedt_lg"])  ? "" : "qedt_lg"));

    $dsp = $cfg['led_animation']." sec";
    printSettingLine($lang['globalQ_la_lbl'],  $dsp, (isset($_GET["qedt_la"])  ? "" : "qedt_la"));

?>
            </table>
        </div>



<?php
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

    function printResetForm($formhead, $txt_lbl, $txt_hlp, $txt_btn){
        print "        <div class=\"col-md-4 col-sm-6\">\n";
        print "            <h4>".$formhead."</h4>\n";

        print "            <form name=\"quota_reinit\" method=\"post\" action=\"".$_SERVER['PHP_SELF']."\">\n";
        #print "                <div class=\"form-group\">\n";
        print "                    <label class=\"col-md-8 control-label\" for=\"quota_reinit\">".$txt_lbl."</label>\n";
#        print "                    <span class=\"input-group-btn\">\n";
        print "                        <input type=\"submit\" class=\"btn btn-default\" id=\"quota_reinit\" name=\"quota_reinit\" value=\""."Btn"."\"/>\n";
#        print "                    </span>\n";
        #print "                </div>\n";
        #print "                <span class=\"help-block\">".$txt_hlp."</span>\n";
        print "            </form>\n";

        print "        </div>\n";
    }
    if($postprob){
        print "        <div class=\"col-md-4 col-sm-6\">\n";
        print "            <h4>".$lang['globalQuotaNotify']."</h4>\n";
        print "            <p style=\"color:#ff0000\">".$lang['globalQuotaFrmErr']."</p>\n";
        print "        </div>\n";
    }
    else{
        $btn = $lang['globalSet'];
        $leddsp = "";
        if($cfg["led_gpios"] !== null && ($n_leds = count($cfg["led_gpios"]))>0){
            for($i=0; $i < $n_leds; $i++) {
                $leddsp.=$cfg["led_gpios"][$i];
                if($i < ($n_leds-1)) $leddsp.=",";
            }
        }
        if     (isset($_GET["qedt_mu"])) printEditForm($lang['globalQuotaEdit'], $cfg["minutes_per_unit"], "quota_mu", $lang["globalQ_mu_lbl"], $lang["globalQ_mu_ph"], $lang["globalQ_mu_hlp"], $btn);
        else if(isset($_GET["qedt_du"])) printEditForm($lang['globalQuotaEdit'], $cfg["default_units"],    "quota_du", $lang["globalQ_du_lbl"], $lang["globalQ_du_ph"], $lang["globalQ_du_hlp"], $btn);
        else if(isset($_GET["qedt_mr"])) printEditForm($lang['globalQuotaEdit'], $cfg["minutes_to_reset"], "quota_mr", $lang["globalQ_mr_lbl"], $lang["globalQ_mr_ph"], $lang["globalQ_mr_hlp"], $btn);
        else if(isset($_GET["qedt_lg"])) printEditForm($lang['globalQuotaEdit'], $leddsp,                  "quota_lg", $lang["globalQ_lg_lbl"], $lang["globalQ_lg_ph"], $lang["globalQ_lg_hlp"], $btn, False, False);
        else if(isset($_GET["qedt_la"])) printEditForm($lang['globalQuotaEdit'], $cfg["led_animation"],    "quota_la", $lang["globalQ_la_lbl"], $lang["globalQ_la_ph"], $lang["globalQ_la_hlp"], $btn, False);
    }

?>

        <!-- /input-group -->
