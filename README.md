## Provide tiktok URL to play audio on loop, audios are all shown at once on screen

Problem: Titkok sounds section does not allow audio to play on loop unless you press into the sound. So i can’t dance around to the best part of different songs seamlessly

---

Solution:  Build a browser application (in mobile format) for me where the ui takes in a tiktok URL and saves all audio into one screen together (scrollable)

---

Features in V1: 

-input tiktok URL

-audio can play on loop (gap: MP3 files carry a little bit of silence at the start and end. It’s fixable, either with a different audio format or a different way of playing it,)

-saved sounds appear in a list, tap one to loop it

---

Maybe features in V2:

-shuffle option

-able to name saved audio

-search bar to find audio

-able to remove audio

-interface design similar to tiktok sound section

-able to shift saved audios around (gap: scrolling and dragging like the same, solution is to make a separate edit mode for dragging)

-open browser on phone (while labtop runs the program)

-desktop shortcut

---

Maybe features in V3:

-standalone application on mobile (gap: 

1. Hosted online (costs a bit, TikTok may block cloud servers)
2. Native phone app (much bigger project)

-youtube url? to save ur fav parts thats not on tiktok

-able to save different versions of one sound (like sped up, slowed), on the ui you can click a dropdown on that sound (original speed), dropdown will display your different versions saved

---

Roadmap(v1):

M1: input to accept tiktok URL on ui

M2: yt dlp sees URL and converts to MP3 

M3: MP3 plays on loop (with no noticeable pause)

---

Roadmap(v2)
M4: upon adding audio asks for renaming

M5: saved audios can be renamed

M6: search bar to find audio

M7: saved audio can be removed

M8: interface similar to tiktok

M9: saved audios can be reordered

M10: program can run smoothly on phone

M11: desktop shortcut

M12: all audios is adjusted to balanced volume

Known Issues: 
-audios are not sorted by latest
-two audios can be played simultaneously 
-timestamp is not restarted for previous audio
-timestamp is not restarted when pausing current audio
-downloads can fail on some networks (HTTP 403). try a different network or wait.

Run without VS Code:

- Double-click `run_loop_player.bat` to start the app and open it in Chrome.
- Create a shortcut to `run_loop_player.bat` and pin that shortcut to the taskbar.
- Close the command window to stop the app.
