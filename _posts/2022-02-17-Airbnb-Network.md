---
layout: page
title: "Airbnb Vermieter und deren Netzwerke"
excerpt: "Arbeitest du in der Welt der IT Security oder bist du einfach sonst IT Security affin und ab und zu in Airbnb Wohnungen? Dann überprüfe doch, dass nächste mal, den Router auf die grundlegenden Sicherheitsvorkehrungen und sollten diese nicht genügend sein, behebe sie und/oder informiere den Airbnb Host."
---

# Long Story Short
Arbeitest du in der Welt der IT Security oder bist du einfach sonst IT Security affin und ab und zu in Airbnb Wohnungen? Dann überprüfe doch, dass nächste mal, den Router auf die grundlegenden Sicherheitsvorkehrungen und sollten diese nicht genügend sein, behebe sie und/oder informiere den Airbnb Host. 

Alles folgende ist die "Long Story"...

# Wochenendausflug ins Tessin
Kürzlich war ich für ein Wochenende im Tessin, genauer in Ascona und habe dort ein Airbnb gemietet. Zum See trennte die Wohnung nur eine schöne, mit Restaurants gespickten Promenade. Auch an der Einrichtung des Airbnb gab es nichts zu bemängeln. Ascona und allgemein das Tessin, kann ich jedem empfehlen. Versuch auch einfach mal los zu laufen und schauen wo es dich hinführt, denn es gibt so schöne Plätze, die findest du nicht mit Google Maps. 
![Sicht über den Lago Maggiore (Von einem Platz, denn du nicht auf Google Maps findest.)]({{ '/assets/images/blog/2022-02-17/img01.jpg' | relative_url }})

# Das fehlende Passwort (Fancy Beschreibung: The vulnerability)
Eigentlich wollte ich das ganze Wochenende mein Notebook höchstens für einen Film am Abend hervor holen. Doch dann, als ich mich mit dem WLAN verbinden wollte und auf der Rückseite des Routers (eigentlich WLAN-Router) den Aufdruck: Default Access: http://tplinkmodem.net. sah, waren meine guten Vorsätze schon wieder weg...

![Rückseite des WLAN-Routers]({{ '/assets/images/blog/2022-02-17/img02.jpg' | relative_url }})

Ich konnte es dann natürlich nicht sein lassen, mal zu schauen was ich denn auf dieser URL tun kann. Erwartet habe ich eine standard Maske, mit einer Benutzername und Passwort Abfrage. In dem Fall hätte ich es dann auch sein lassen (Da ich ja eigentlich mal entspannend wollte). Tatsächlich war es dann auch eine standard Maske, jedoch fragte mich diese nach einem neuen Passwort, sowie dessen Bestätigung.

![Default Access]({{ '/assets/images/blog/2022-02-17/img03.png' | relative_url }})

# Das Problem
Vielleicht fragst du dich jetzt: Warum ist das ein Problem? Gute Frage, ich versuche dir das im folgenden zu erklären: 

## Router Webinterface
Auf was ich mich durch die Adresse "http://tplinkmodem.net" verbunden habe, ist das sogenannte Webinterface des Routers. Alle WLAN-Router (oder einfach nur Router, Access Point etc.) bieten ein Webinterface um diesen zu konfigurieren. Im folgenden einige Beispiele, was alles konfiguriert werden kann:
- Setzen des WLAN Namens sowie des Passworts
- Einrichten eines VPN (Virtual Private Network)
- Bevorzugen von Geräten
- Aussperren von Geräten (block und allowlisting)
- Aktivieren des Stromsparmodus
- Einrichten eines Gäste WLANs
- etc. 

Wenn der Zugang zum Webinterface des Routers, ohne Passwort (oder in meinem Fall hat wohl einfach noch nie jemand ein Passwort hinterlegt) möglich ist, steht jedem der sich mit diesem WLAN verbindet, die Einstellungen des Routers offen. Da der Router praktisch immer, die erste IP Adresse des Adressbereichs hat, findet man auch ohne Tools wie nmap, das Webinterface relativ schnell. Bei dir Zuhause hat der Router ziemlich sicher die Adresse 192.168.1.1. 
Wie oben kurz aufgezählt kann man bei heutigen Routern diverses einstellen, was zu ernsthaften Problemen führen kann. Im Folgenden nur ein paar Ideen was mit ein wenig krimineller Energie angestellt werden kann:
- Den Router verkonfigurieren, so dass er nicht mehr funktioniert. 
- Eigene Geräte bevorzugen.
- Eine MAC Address allowlist anlegen, so dass sich nur noch die eigenen Geräte verbinden können.
- Ein VPN einrichten, so dass man später seinen Datenverkehr über den Internetanschluss der Airbnb Wohnung umleiten kann. 
- Den gesamten Datenverkehr über einen Zwischenpunkt leiten, so dass dieser ausgelesen werden kann (Man-in-the-middle).
- etc.

Vor allem Punkt 4 und 5, kann je nachdem für den Airbnb Host zu juristischen Problemen führen. Denn ich könnte nun über das VPN, welches ich eingerichtet hätte, einen Angriff gegen jemanden starten. Für denjenigen, den ich angreife, sieht es dann so aus, als ob der Airbnb Host den Angriff fährt. (Sehr vereinfacht ausgedrückt)

# Die Behebung
Nun, was macht man in einer solchen Situation? Man will ja auch keinesfalls zu weit gehen und selber Probleme bekommen.

Ich habe mich dafür entschieden, dem Quick Setup Guide zu folgen und somit ein Passwort für das Webinterface des Routers zu setzen. Nebenbei habe ich auch gleich noch die Firmware aktualisiert. 

Weitere Einstellungen, welche ich bei meiner eigenen Airbnb Wohnung tätigen würde, wenn ich denn eine hätte, habe ich nicht vorgenommen. 

# Die Meldung
Zum Schluss habe ich eine Nachricht an den Host geschrieben, in welcher ich ihn informiert habe was das Problem war und warum das ein Problem ist, sowie das ich es behoben habe. Ebenfalls habe ich ihm beschrieben, wie er das Passwort erneut ändern kann, damit auch ich keinen Zugriff mehr auf den Router habe. 

Diese Meldung habe ich in möglichst einfachen Worten verfasst, so dass auch jemand der (offensichtlich (sorry...)) keine Ahnung von IT hat, versteht was ich gemacht habe. 

Abgeschlossen habe ich mit meiner E-Mail Adresse und dem Hinweis, dass er mich bei weiteren Fragen kontaktieren darf. Ich denke die Angabe einer Kontaktadresse ist wichtig um vertrauenswürdig zu erscheinen. In meinem Fall hatte er diese natürlich schon von der Buchung...

Der Host hat sich sehr schnell gemeldet, mit einem Dankeschön und dem Hinweis, dass er das Passwort bei Gelegenheit ändern wird.

# Fazit
Mit diesem kurzen Blogeintrag möchte ich dich als Leser dazu motivieren bei deinem nächsten Aufenthalt in einer Airbnb Wohnung (oder auch sonst wo) das Netzwerk und vor allem den Router auf die einfachsten Sicherheitsvorkehrungen zu prüfen und diese, wenn nicht vorhanden, zu melden und/oder gleich zu implementieren.

Das ganze (abgesehen von diesem Blogeintrag) hat mich ca. 30min gekostet und ein weiteres unsicheres Netzwerk ist nun etwas sicherer geworden. Im Endeffekt ist jedes Netzwerk, dass die grundlegenden Sicherheitsvorkehrungen erfüllt, ein Netzwerk weniger von welchem Angriffe auf Firmen, Privatpersonen, Journalisten etc. gestartet werden können. 

Was hättest du in meiner Situation gemacht? Was hast du sonst für Ideen (rein hypothetisch versteht sich) was man mit ein wenig krimineller Energie hätte anstellen können?