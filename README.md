# DupDetect

## Prototypische Anwendung ausgewählter Bibliotheken zur Duplikaterkennung im Rahmen meiner Bachelorarbeit

### **Martina Schulz / MatrNr.: 256896 / TH Lübeck** 

**_Thema:_**

Duplikaterkennung bei der Datenbereinigung maritim-meteorologischer Daten

**_Kurzbeschreibung:_**

Zur Erkennung doppelter Datensätze wurden mehrere Bibliotheken getestet.

## Installation

Die folgenden Anweisungen beschreiben die lokale Installation dieser Software.

### Voraussetzungen

Python3, virtualenv (*optional*)

Installation virtualenv:
```
pip install virtualenv
```

Git-Klon:
```
git clone https://github.com/schulzma/DupDetect.git
```

### Installation

Isolierte Python-Umgebung einrichten (*optional*):
```
virtualenv ENVdupDetect
linux:
  . ENVdupDetect/bin/activate
windows:
  ENVdupDetect\Scripts\activate
```

Requiremets:
```
cd ENVdupDetect
pip install --upgrade -r requirements.txt
```


## Eingesetzte Bibliotheken

### dedupe python library 
* Dokumentation: [https://docs.dedupe.io/en/latest/](https://docs.dedupe.io/en/latest/)
* Repository: [http://github.com/dedupeio/dedupe](http://github.com/dedupeio/dedupe) 
* Beispiele: [https://github.com/dedupeio/dedupe-examples.git](https://github.com/dedupeio/dedupe-examples.git)

### pandas-dedupe
* Repository: [https://github.com/Lyonk71/pandas-dedupe.git](https://github.com/Lyonk71/pandas-dedupe.git)

### csvdedupe
* Repository: [https://github.com/dedupeio/csvdedupe.git](https://github.com/dedupeio/csvdedupe.git)

### Python Record Linkage Toolkit
* Dokumentation: [https://recordlinkage.readthedocs.io/en/latest/#](https://recordlinkage.readthedocs.io/en/latest/#)
* Repository: [https://github.com/J535D165/recordlinkage.git](https://github.com/J535D165/recordlinkage.git)