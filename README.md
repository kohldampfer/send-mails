# send-mails

## Description
This small program reads a list of URLs, which will be parsed for new links. If there is a new link there, then `Receiver` gets an e-mail with the new link in it.

### listoflinks.txt

Exampe of a `listoflinks.txt` file
```
https://stackoverflow.com/questions/tagged/nmap
https://security.stackexchange.com/questions/tagged/nmap
https://superuser.com/questions/tagged/nmap

```

### emailsettings.ini

Exampe of a `emailsettings.ini` file

```
[EmailSettings]
Host = hostname
Port = 587
Sender = somemail@somehost.ext
Receiver = someothermail@somehost.ext
Password = password_of_sender_for_authentication
```