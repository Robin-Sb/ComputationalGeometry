Run: python3 prune_and_search.py

- Durch Eingabe einer Zahl in das Eingabefeld und anschließendem Drücken auf "Generate" wird ein zufälliges LP 
erzeugt mit der gesetzten Anzahl an Constraints
- Durch Klicken der linken + rechten Maustaste wird ein Constraint zwischen den beiden Position erzeugt. 
Linksklick legt die Startposition fest, Rechtsklick die Endposition, die Normale wird entsprechend gesetzt
- Die Constraints werden durch eine schwarze Linie angezeigt, die dazugehörige Normale mit einer kurzen blauen Linie
- Durch Klicken auf "solve" wird das LP gelöst, einmal durch brute force und einmal mit prune and search
Anschließend werden die Lösungsschritte visualisiert: Die roten Linien sind die in dieser Runde gelöschten Constraints,
die roten Punkte die überprüfte Intersection und die weißen Linien repräsentieren bereits gelöschte Constraints
- Durch Klicken auf "Clear everything" wird alles gelöscht, durch Klicken auf "clear visualization steps" nur die Visualisierung des Algorithmus
In der Kommandozeile wird außerdem die Lösung des LP sowie die Berechnungszeit der beiden Algorithmen (in Sekunden) angezeigt.
Ab 300 Constraints wird die Berechnung des brute force Algorithmus sowie die Visualisierung der Constraints deaktiviert.