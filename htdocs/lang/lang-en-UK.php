<?php
$lang = array();

$lang['globalEdit'] = "Edit";
$lang['globalResume'] = "Resume";
$lang['globalPassword'] = "Password";
$lang['globalOff'] = "OFF";
$lang['globalOn'] = "ON";
$lang['globalSingle'] = "Single";
$lang['globalTrack'] = "Track";
$lang['globalList'] = "List";
$lang['globalPlaylist'] = "Playlist";
$lang['globalCardId'] = "Card ID";
$lang['globalRFIDCard'] = "RFID Card";
$lang['globalRFIDCards'] = "RFID Cards";
$lang['globalCardIdPlaceholder'] = "e.g. '1234567890'";
$lang['globalCardIdHelp'] = "The ID is usually printed on the card or fob. A list of used IDs can be found on the home page.";
$lang['globalRegisterCard'] = "Register new card ID";
$lang['globalRegisterCardShort'] = "Card ID";
$lang['globalLastUsedCard'] = "Last used Chip ID";
$lang['globalClose'] = "Close";
$lang['globalPlay'] = "Play";
$lang['globalVolume'] = "Volume";
$lang['globalVolumeSettings'] = "Volume Settings";
$lang['globalWifi'] = "WiFi";
$lang['globalWifiSettings'] = "WiFi Settings";
$lang['globalWifiNetwork'] = "WiFi Settings";
$lang['globalSSID'] = "SSID";
$lang['globalSet'] = "Set";
$lang['globalSettings'] = "Settings";
$lang['globalFolder'] = "Folder";
$lang['globalFolderName'] = "Folder name";
$lang['globalFilename'] = "File name";
$lang['globalStream'] = "Stream";
$lang['globalSubmit'] = "Submit";
$lang['globalUpload'] = "Upload";
$lang['globalUpdate'] = "Update";
$lang['globalCancel'] = "Cancel";
$lang['globalDelete'] = "Delete";
$lang['globalCreate'] = "Create";
$lang['globalMove'] = "Move";
$lang['globalJumpTo'] = "Jump to";
$lang['globalAutoShutdown'] = "Auto Shutdown";
$lang['globalIdleShutdown'] = "Idle Shutdown";
$lang['globalAutoStopPlayout'] = "Stop Playout Timer";
$lang['globalStopTimer'] = "Stop Playout Timer";
$lang['globalSleepTimer'] = "Shutdown Timer";
$lang['globalExternalInterfaces'] = "External Devices & Interfaces";
$lang['globalIdleTime'] = "Idle Time";
$lang['globalNotIdle'] = "Not Idle";
$lang['globalGpioButtons'] = "GPIO Buttons";
$lang['globalRfidReader'] = "RFID Reader";
$lang['globalEnabled'] = "Enabled";
$lang['globalDisabled'] = "Disabled";
$lang['globalSwitchOn'] = "Switch ON";
$lang['globalSwitchOff'] = "Switch OFF";
$lang['globalSystem'] = "System";
$lang['globalVersion'] = "Version";
$lang['globalDescription'] = "Description";
$lang['globalRelease'] = "Release";
$lang['globalStorage'] = "Storage";
$lang['globalShuffle'] = "Shuffle";
$lang['globalReplay'] = "Replay";
$lang['globalRepeat'] = "Repeat";
$lang['globalLoop'] = "Loop";
$lang['globalLang'] = "Language";
$lang['globalLanguageSettings'] = "Language Settings";
$lang['globalQuota'] = "Time quota";
$lang['globalQuotaEnable'] = "Enable time quota control";
$lang['globalQuotaDisable'] = "Disable time quota control";
$lang['globalQuotaGrant'] = "Grant time quota (in minutes):";
$lang['globalQuotaUnlimited'] = "Decontrol quota";
$lang['globalQuotaView'] = "Current settings";
$lang['globalQuotaEdit'] = "Edit setting";
$lang['globalQuotaNotify'] = "Notification";
$lang['globalQuotaFrmErr'] = "The value you just entered was invalid. Please respect the legal range for this parameter";
$lang['globalQ_mu_lbl'] = "Length indicated by 1 LED";
$lang['globalQ_mu_hlp'] = "Each time after this amount of minutes, 1 LED will switch off (if LEDs are used). Enter a number &gt; 0 (e.g. 30 for 30 minutes)";
$lang['globalQ_mu_ph'] = "e.g. &quot;30&quot;";
$lang['globalQ_dm_lbl'] = "Default grant:";
$lang['globalQ_dm_hlp'] = "Number of minutes that will be granted after booting the phoniebox. Enter a number &gt; 0 (e.g. 120 for 2 hours as default grant)";
$lang['globalQ_dm_ph'] = "e.g. &quot;120&quot;";
$lang['globalQ_mr_lbl'] = "New quota after:";
$lang['globalQ_mr_hlp'] = "Time span (in minutes) after which a new default time quota will be granted on boot-up. Counts from the time where the previous quota was granted. Enter a number &gt; 0 (e.g. 480 for 6 hours until the next grant)";
$lang['globalQ_mr_ph'] = "e.g. &quot;480&quot;";
$lang['globalQ_lg_lbl'] = "LED GPIO list:";
$lang['globalQ_lg_hlp'] = "Comma-separated list of GPIO numbers for a mounted LED row (in order of illumination). Leave empty to disable LED feature. Only use numbers between 2 and 31.";
$lang['globalQ_lg_ph'] = "e.g. &quot;7,8,12,13,19&quot;";
$lang['globalQ_la_lbl'] = "LED animation time:";
$lang['globalQ_la_hlp'] = "Time interval (in seconds) used for animated LED ignition. Example: If you specify \"0.3\", the 2nd LED will illuminate 300 ms after the first and the 3rd LED will do so 300 ms after the 2nd. Enter a number between 0.0 (no animation) and 10.0 (10 seconds).";
$lang['globalQ_la_ph'] = "e.g. &quot;0.3&quot;";

// Edition (classic, +spotify)
$lang['globalEdition'] = "Edition";
$lang['classic'] = "Classic edition (barebones)";
$lang['plusSpotify'] = "Plus edition (feat. Spotify integration)";

$lang['navEditionClassic'] = "Classic";
$lang['navEditionPlusSpotify'] = "+Spotify";

$lang['navBrand'] = "Phoniebox";
$lang['navHome'] = "Home";
$lang['navSettings'] = "Settings";
$lang['navInfo'] = "Info";
$lang['navShutdown'] = "Shutdown";
$lang['navReboot'] = "Reboot";

$lang['indexAvailAudio'] = "Available audio";
$lang['indexContainsFiles'] = "Contains the following file(s):";
$lang['indexShowFiles'] = "Show files";
$lang['indexManageFilesChips'] = "Manage Files and Chips";

$lang['Spotify'] = "Spotify";

/*
* Register & Edit Cards
*/
$lang['cardRegisterTitle'] = "Add new card";
$lang['cardEditTitle'] = "Edit or add card";
$lang['cardRegisterMessageDefault'] = "The 'Latest Card ID' value in the form is updated on the fly as you swipe a RFID card.<br/>(Requires Javascript in the browser to be enabled.)";
$lang['cardEditMessageDefault'] = "The card IDs used in this system are listed on the <a href='index.php' class='mainMenu'><i class='mdi mdi-home'></i> home page</a>.";
$lang['cardRegisterMessageSwipeNew'] = "Swipe another card, if you want to register more cards.";
$lang['cardEditMessageInputNew'] = "Type another card ID pick one from the list on the <a href='index.php' class='mainMenu'><i class='mdi mdi-home'></i> home page</a>.";
$lang['cardRegisterErrorTooMuch'] = "<p>This is too much! Please select only one audiofolder. Make up your mind.</p>";
$lang['cardRegisterErrorStreamAndAudio'] = "<p>This is too much! Either a stream or an audio folder. Make up your mind.</p>";
$lang['cardRegisterErrorStreamOrAudio'] = "<p>This is not enough! Add an URL including stream type or select an audio folder. Or 'Cancel' to go back to the home page.</p>";
$lang['cardRegisterErrorExistingAndNew'] = "<p>This is too much! Either choose an existing folder or create a new one.</p>";
$lang['cardRegisterErrorExistingFolder'] = "<p>A folder named with the same name already exists! Chose a different one.</p>";
$lang['cardRegisterErrorSuggestFolder'] = "A folder name for the stream needs to be created. Below in the form I made a suggestion.";
$lang['cardRegisterStream2Card'] = "Stream is linked to Card ID.";
$lang['cardRegisterFolder2Card'] = "Audio folder is now linked to Card.";
$lang['cardRegisterDownloadingYT'] = "<p>YouTube audio is downloading. This may take a couple of minutes. You may check the logfile \"youtube-dl.log\" in the shared folder.</p>";
$lang['cardRegisterSwipeUpdates'] = "This will automatically update as you swipe a RFID card.";
$lang['cardRegisterManualLinks'] = "<p>You can also connect cards to folders manually. The manual explains how to <a href='https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#connecting-to-the-phoniebox-to-add-files' target='–blank'>connect to the phoniebox</a> and <a href='https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#registering-cards-manually-through-samba-without-the-web-app' target='_blank'>register cards</a>.</p>";

/*
* Card edit form
*/
$lang['cardFormFolderLegend'] = "Audio Folder";
$lang['cardFormFolderLabel'] = "a) Link card to audio folder";
$lang['cardFormFolderSelectDefault'] = "None (pulldown to select a folder)";
$lang['cardFormStreamLabel'] = "b) ... or connect with Stream URL";
$lang['cardFormStreamPlaceholderClassic'] = "Livestream: http(...).mp3 / .m3u / .ogg / ...";
$lang['cardFormStreamPlaceholderPlusSpotify'] = "spotify:(user:username:)album/track/playlist:### / Livestream: http(...).mp3 / .m3u / .ogg / ...";
$lang['cardFormStreamHelp'] = "Add the URL for spotify, podcast, web radio, stream or other online media";
$lang['cardFormStreamTypeSelectDefault'] = "Select type";
$lang['cardFormStreamTypeHelp'] = "Select the type you are adding";
$lang['cardFormStreamFolderPlaceholder'] = "e.g. 'Album/Playlist/Station Name'";
$lang['cardFormStreamFolderHelp'] = "Name for the audio folder that will contain the stream URL.";
$lang['cardFormYTLegend'] = "YouTube";
$lang['cardFormYTLabel'] = "c) ... or download YouTube audio";
$lang['cardFormYTPlaceholder'] = "e.g. https://www.youtube.com/watch?v=7GI0VdPehQI";
$lang['cardFormYTSelectDefault'] = "Pull down to select a folder or create a new one below";
$lang['cardFormYTFolderPlaceholder'] = "e.g. 'New Folder'";
$lang['cardFormYTFolderHelp'] = "Name for the audio folder that will contain the YouTube audio.";
$lang['cardFormYTHelp'] = "Add the full YouTube-URL like in the example";
$lang['cardFormRemoveCard'] = "Remove Card ID";

/*
* Track edit form
*/
$lang['trackEditTitle'] = "Track management";
$lang['trackEditInformation'] = "Track information";
$lang['trackEditMove'] = "Move track";
$lang['trackEditMoveSelectLabel'] = "Select new folder";
$lang['trackEditMoveSelectDefault'] = "Do not move file";
$lang['trackEditDelete'] = "Delete track";
$lang['trackEditDeleteLabel'] = "Sure you want to delete???";
$lang['trackEditDeleteHelp'] = "There is no 'undo' for deleted files. They are gone! Are you sure?";
$lang['trackEditDeleteNo'] = "Do NOT delete this track";
$lang['trackEditDeleteYes'] = "Yes, DELETE this track";


/*
* Settings
*/
$lang['settingsVolChangePercent'] = "Vol. Change %";
$lang['settingsMaxVol'] = "Maximum Volume";
$lang['settingsWifiRestart'] = "The changes applied to your WiFi connection require a restart to take effect.";
$lang['settingsWifiSsidPlaceholder'] = "e.g.: PhonieHomie";
$lang['settingsWifiSsidHelp'] = "The name under which your WiFi shows up as 'available network'";
$lang['settingsSecondSwipe'] = "Second Swipe";
$lang['settingsSecondSwipeInfo'] = "When you swipe the same RFID a second time, what happens? Start the playlist again? Toggle pause/play?";
$lang['settingsSecondSwipeRestart'] = "Re-start playlist";
$lang['settingsSecondSwipeSkipnext'] = "Skip to next track";
$lang['settingsSecondSwipePause'] = "Toggle pause / play";
$lang['settingsSecondSwipeNoAudioPlay'] = "Ignore audio playout triggers, only system commands";
$lang['settingsWebInterface'] = "Web Interface";
$lang['settingsCoverInfo'] = "Do you want to show covers beside the albums and playlists on the main page?";
$lang['settingsShowCoverON'] = "Show cover";
$lang['settingsShowCoverOFF'] = "Don't show cover";
$lang['settingsMessageLangfileNewItems'] = "There are new language items in the original <em>lang-en-UK.php</em> file. Your language file has been updated and now contains these (in English). You might want to update your language file and commit your changes to the Phoniebox code :)";

/*
* System info
*/
$lang['infoOsDistrib'] = "OS Distribution";
$lang['infoOsCodename'] = "Codename";
$lang['infoStorageUsed'] = "Storage usage";
$lang['infoMopidyStatus'] = "Mopidy Server Status";
$lang['infoMPDStatus'] = "MPD Server Status";

/*
* Folder Management and File Upload
*/
$lang['manageFilesFoldersTitle'] = "Folders &amp; Files";
$lang['manageFilesFoldersUploadFilesLabel'] = "Select files from your drive";
$lang['manageFilesFoldersUploadLegend'] = "Upload files";
$lang['manageFilesFoldersUploadLabel'] = "Select and/or create new folder";
$lang['manageFilesFoldersUploadFolderHelp'] = "If you select AND name a new folder, the new folder will be created inside the selected folder.";
$lang['manageFilesFoldersNewFolderTitle'] = "Create new folder";
$lang['manageFilesFoldersNewFolderPositionLegend'] = "Folder position";
$lang['manageFilesFoldersNewFolderPositionDefault'] = "The new folder will be on the root level or inside (choose below)";
$lang['manageFilesFoldersErrorNewFolderName'] = "<p>No valid folder name given.</p>";
$lang['manageFilesFoldersErrorNewFolder'] = "<p>No folder selected nor a valid new folder specified.</p>";
$lang['manageFilesFoldersErrorNoNewFolder'] = "<p>No folder selected nor a valid new folder specified.</p>";
$lang['manageFilesFoldersErrorNewFolderExists'] = "<p>A folder by that name already exists. Be original, type a new name.</p>";
$lang['manageFilesFoldersErrorNewFolderNotParent'] = "<p>The parent folder does not exist.</p>";
$lang['manageFilesFoldersSuccessNewFolder'] = "New folder created: ";
$lang['manageFilesFoldersSelectDefault'] = "Pull down to select a folder and/or create a new child folder below";

$lang['manageFilesFoldersRenewDB'] = "Renew database";
$lang['manageFilesFoldersLocalScan'] = "Scan Music Library";
$lang['manageFilesFoldersRenewDBinfo'] = "Please scan your music library after you have uploaded new files or moved folders. The scan is not necessary to hear music, but it is necessary to see track information in the Web UI. Only new or moved files will be scanned. While the scan is running, mopidy will be stopped. After scan is complete, mopidy starts automatically. You can see the server status in the Info section.";


?>

