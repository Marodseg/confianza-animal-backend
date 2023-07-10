# Memoria del proyecto
La documentación de este proyecto se ha realizado usando LaTeX, y es por ello por lo que se han facilitado
unos comandos para poder obtener el archivo final en formato PDF.

Necesitaremos tener instalados los siguientes paquetes para su compilación:

```bash
sudo apt-get install texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra texlive-lang-spanish
```

Una vez instalado todo correctamente y en el directo ``/doc`` podremos ejecutar:

```bash
pdflatex proyecto.tex
```
o haciendo uso del fichero `Makefile`:

```bash
make 
```

Si el comando se ha ejecutado exitosamente, se habrá generado un archivo en formato PDF 
con el contenido de la documentación en el directorio `/doc`.