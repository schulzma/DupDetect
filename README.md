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

Python3

### Installation

Isolierte Python-Umgebung einrichten:
```
python3 -m venv dupdetect-env

Windows:
  dupdetect-env\Scripts\activate.bat

Unix oder MacOS:
  source dupdetect-env/bin/activate
```

Git-Klon:
```
git clone https://github.com/schulzma/DupDetect.git
```

Requirements:
```
cd DupDetect
pip install --upgrade -r requirements.txt
```

### Beispiele ausführen

dedupe:
```
cd dedupe
python csv_example_dedupe.py
```

pandas_dedupe:
```
cd ../pandasdedupe/
python csv_example_pandas_dedupe.py
```

recordlinkage:
```
cd ../recordlinkage/
python csv_example_recordlinkage_SN.py
```

## Eingesetzte Bibliotheken

### dedupe python library 
* Dokumentation: [https://docs.dedupe.io/en/latest/](https://docs.dedupe.io/en/latest/)
* Repository: [http://github.com/dedupeio/dedupe](http://github.com/dedupeio/dedupe) 
* Beispiele: [https://github.com/dedupeio/dedupe-examples.git](https://github.com/dedupeio/dedupe-examples.git)

### pandas-dedupe
* Repository: [https://github.com/Lyonk71/pandas-dedupe.git](https://github.com/Lyonk71/pandas-dedupe.git)

### Python Record Linkage Toolkit
* Dokumentation: [https://recordlinkage.readthedocs.io/en/latest/#](https://recordlinkage.readthedocs.io/en/latest/#)
* Repository: [https://github.com/J535D165/recordlinkage.git](https://github.com/J535D165/recordlinkage.git)
