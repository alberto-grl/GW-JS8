# GW-JS8
This bot is a gateway between the JS8 terminal JS8CALL and Telegram.
It employs the Telegram library Telethon and the JS8CALL library JS8net 

https://github.com/LonamiWebs/Telethon

https://github.com/jfrancis42/js8net

Create a Telegram group, add the ultrajs8 bot and the traffic received by JS8CALL
should appear to anyone in the group. Please find elsewhere the documents showing how to authenticate,
obtain API id, hash, group id. These values should be written in a file named TelegramAPI.json, there is a template
that can be renamed and filled with your own values.
Also, JS8Call should be configured to expose its API.

These commands sent to the group trigger actions:

/hb                send heartbeat

/offset n          Changes offset

/qsnr              asks for SNR

/qinfo             asks info

/TX text           sends string

/semail addr text  sends email to addr containing text, like /semail POTUS@WHITEHOUSE.GOV LONG TIME NO SEE 73

/srxfilt call      sets a filter to the message sent to the group by the bot


It's trivial to add more.

Not sure if this is totally legal for use on the air. I'm testing it with two PCs connected back to back.
Ask for legal advice, you have been warned.





