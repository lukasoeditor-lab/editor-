import { Config } from "@remotion/cli/config";
import fs from "fs";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// Use the preinstalled Chromium when available (no network to download Remotion's own)
const localChrome =
  "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell";
if (fs.existsSync(localChrome)) {
  Config.setBrowserExecutable(localChrome);
}
