---
layout: page
title: "Ein unauffällig auffälliger E-Paper-Raumluft-Monitor (Teil 1: Warum?)"
excerpt: "Warum ich für meine WG einen E-Paper-Raumluft-Monitor gebaut habe und wie das erste MVP funktioniert: Monitor Einheit mit E-Paper Display, Sensor und LED Panel -> Speicher und Weiterleitung an FastAPI Backend mit SQLite -> Darstellung auf interaktiven Dashboard."
---

> TL;DR – In der kalten Jahreszeit bleiben die Fenster oft geschlossen. Die Luft wird «dick»: Die Luftfeuchtigkeit steigt häufig über 60 %, was dem Wohlbefinden schaden und zu Schimmel führen kann. Gleichzeitig erhöht sich der CO₂‑Gehalt in der Luft, was sich negativ auf die Konzentration auswirkt. Darum habe ich einen Raumluft‑Monitor entwickelt, der so lange unauffällig bleibt, wie alles im grünen Bereich ist. Wird ein definierter Schwellenwert überschritten, wird er bewusst auffällig. Für meinen Bedarf an Statistiken visualisiere ich die Messwerte zusätzlich in einem übersichtlichen Dashboard.

## Das Warum
In der Zeit, in der die Fenster häufig geschlossen bleiben, wird die Luft schnell «dick». Die Luftfeuchtigkeit sowie der CO₂‑Gehalt steigen. CO₂ wird in «parts per million» (ppm) gemessen. Bei erhöhten Werten können folgende Probleme auftreten:

| CO₂-Gehalt                           | Bedeutung / mögliche Folgen                                                                                                         |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| ca. 400–450 ppm (typische Aussenluft) | Ausgangsbasis für frische Luft.                                                                                                    |
| bis ~1 000 ppm                       | Wird häufig als Obergrenze für gute Lüftung herangezogen. Werte über ~1 000 ppm deuten auf ungenügende Belüftung hin. |
| etwa 1 000–1 500 ppm                 | Konzentration steigt – Leistungsabfall, Konzentrationsprobleme und Müdigkeit werden wahrscheinlicher.                              |
| > 1 500 ppm oder mehr                | Sehr schlecht belüfteter Raum. Gesundheits- und Komfortprobleme treten vermehrt auf.                                               |
| Extreme Werte (z. B. > 5 000 ppm)    | Massive Symptome möglich – z. B. Atemnot oder Bewusstlosigkeit. In normalen Innenräumen sehr selten.                              |

**Quelle:** ASHRAE (2022). *ASHRAE Position Document on Indoor Carbon Dioxide*.  
https://www.svlw.ch/images/aktuell/2022/pd_indoorcarbondioxide_2022.pdf

Analog ist auch eine zu hohe oder zu tiefe Luftfeuchtigkeit nicht gesund. Ist sie zu tief, führt dies zu trockenen Schleimhäuten, gereizter Haut und erhöhter Infektionsanfälligkeit. Ist sie zu hoch, fördert das Schimmelbildung, Staubmilben und andere Bioorganismen, welche Atemwegserkrankungen, Allergien und Asthma begünstigen.
| Relative Luftfeuchtigkeit (RH) | Bedeutung / mögliche Folgen                                                                                                                                      |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| < 30 %                         | Sehr trocken: Schleimhäute gereizt, trockene Haut, Augen, allenfalls Nasenbluten, erhöhte Anfälligkeit für Atemwegsinfekte.                         |
| ~30–40 %                       | In vielen Quellen als untere Grenze für «gesund» angegeben.                                                                       |
| ~40–60 %                       | Häufig empfohlener Idealbereich für Innenräume bezüglich Gesundheit und Komfort.                                                 |
| > 60 % (bis 75 %)              | Risiko: verstärktes Schimmel- und Milbenwachstum, feuchte Räume, unangenehmes Raumklima.                                         |
| Sehr hoch (> 75 %)             | Hohe Feuchte + schlechte Belüftung = erhebliche Gesundheits- und Gebäuderisiken (Schimmel, Atemwegserkrankungen).               |

**Quelle:** 
Wang, W., Zhang, X., & Li, W. (2023). *Effects of indoor humidity on human health and comfort: A systematic review*. Building and Environment. 
https://www.sciencedirect.com/science/article/pii/S2352710223002188

Das zeigt, dass regelmässiges Lüften sehr wichtig ist. Der E‑Paper‑Raumluft‑Monitor hilft mir und meinen Mitbewohnenden, diese Werte im Griff zu behalten und so ein möglichst gutes Raumklima zu erreichen.

## Hardware im Überblick
Folgende Hardware habe ich verbaut – alles Komponenten, die ich bereits zu Hause hatte:

- Gerät: [M5Paper (ESP32 + 4,7" E‑Ink)](https://shop.m5stack.com/products/m5paper-esp32-development-kit-v1-1-960x540-4-7-eink-display-235-ppi?srsltid=AfmBOorSjXp6nymG2FA8GZ-k-BkO0u5ethURiVewOK5y07dIVydX46p8) – Werbegeschenk
- Sensor: [Sensirion SCD40 (CO₂ + Temperatur + Luftfeuchte)](https://shop.m5stack.com/products/co2-unit-with-temperature-and-humidity-sensor-scd40?srsltid=AfmBOorJuihThk46TBkpfEQu-Z4fheeFVYPYYES8r0D1RB8bDaSUIzbE) – vor ein paar Jahren gekauft, aber nie eingesetzt
- Status‑Indikator: [HEX RGB LED Board (SK6812)](https://shop.m5stack.com/products/hex-rgb-led-board-sk6812?srsltid=AfmBOop_IkssjPazb1FBL3kP_HIDJwAshBsXQMBzYHk91z8PbRrrYoKY) – lag ebenfalls seit Längerem ungenutzt herum
- Backend / Dashboard: [Raspberry Pi 4](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) – bereits im Heimnetzwerk im Einsatz
- Stromversorgung (mittlerweile nur noch USV): [Chimpy PowerBank](https://heychimpy.com/de/) – wie das mit Powerbanks so ist: Man vergisst sie zurückzubringen und irgendwann gehören sie einem halt
- «Gehäuse»: Karton – aus dem Altpapier gerettet

## E‑Paper‑Raumluft‑Monitor
Das Ziel des E‑Paper‑Raumluft‑Monitors ist, dass er so lange unauffällig bleibt, wie sich die Luftqualität im grünen Bereich befindet – aber sichtbar wird, sobald definierte Schwellenwerte überschritten werden. Dies wird durch das LED‑Board erreicht, das bei kritischen Werten zu blinken beginnt. Ausserdem zeigt das E‑Paper‑Display jederzeit die aktuelle Luftqualität sowie eine kurze Empfehlung, was zu tun ist.

![M5Paper E‑Paper‑Gerät]({{ '/assets/images/blog/2025-11-16/E-Paper-Raumluft-Monitor-MVP.jpg' | relative_url }})

## Dashboard
Das Dashboard soll uns helfen, den Verlauf der Luftqualität zu verstehen und uns motivieren, sie zu verbessern. Dazu zeige ich interaktive Grafiken und einige einfach zu interpretierende Kennzahlen. Das Dashboard soll ein Motivator sein, die Luftqualität langfristig im Blick zu behalten. Im Folgenden ein kleiner Einblick in das Dashboard.

![Dashboard All-in one Graph]({{ '/assets/images/blog/2025-11-16/dashboard_1.png' | relative_url }})
![Dashboard tägliche Lüftungsanzahl und Minuten über Warnschwelle (Feuchte & CO2)]({{ '/assets/images/blog/2025-11-16/dashboard_2.png' | relative_url }})
![Dashboard Minuten über kritischer Schwelle (Feuchte & CO2) und Minuten unter Warnschwelle (Feuchte & CO2)]({{ '/assets/images/blog/2025-11-16/dashboard_3.png' | relative_url }})


## Telegram Bot
Das aktive Anschauen der Statistiken auf dem Dashboard ist eine bewusste Entscheidung, die man im Alltag leicht vergisst. Darum habe ich einen Telegram‑Bot erstellt, der jeden Morgen um 7 Uhr einen Bericht über den letzten Tag in unseren WG‑Chat schickt. Das soll zusätzlich helfen, das Bewusstsein zu stärken und die Luftqualität im Alltag zu verbessern.

![Nachricht des Telegram Bots]({{ '/assets/images/blog/2025-11-16/telegram_bot_message.png' | relative_url }})

## Was kommt in Teil 2
Im zweiten Teil dieser Blog‑Serie möchte ich mehr auf den Code und die Implementation eingehen und zeigen, welche Herausforderungen es zu lösen gab. Ausserdem wird dann auch das GitHub‑Repository öffentlich sein, sodass interessierte Leser:innen den Code im Detail studieren, Verbesserungen vorschlagen oder sich ihren eigenen E‑Paper‑Raumluft‑Monitor bauen können.

## Zum Schluss
### Github
Das GitHub‑Repository ist aktuell noch nicht öffentlich. Spätestens mit Teil 2 der Blog‑Serie werde ich es freischalten.

### Willst du mithelfen?
Wenn du das Projekt spannend findest und mithelfen möchtest, hast du zum Beispiel folgende Möglichkeiten:

- Trage zum Code im GitHub‑Repository bei (sobald es veröffentlicht ist).
- Hast du einen 3D‑Drucker und Erfahrung im Design von 3D‑Objekten?
  - Dann freue ich mich über ein schönes Case‑Design für den E‑Paper‑Raumluft‑Monitor.
- Hast du Ideen für weitere Sensoren?
  - Schreibe einen Kommentar und/oder sponsere den entsprechenden Sensor.
- Hast du Hinweise, Feedback oder sonstige Kommentare?
  - Hinterlasse einen Kommentar oder melde dich direkt bei mir.