# pdf_tools
pdf_tools is a tool for PDF merging and cropping.
- Combining PDF files to 1 file
- Cropping 4-in-a-page labels

### Tech
pdf_tools uses a number of packages to work properly:
* [PyPDF2](http://mstamy2.github.io/PyPDF2/) - A Pure-Python library built as a PDF toolkit.
* [PyInstaller](https://pyinstaller.readthedocs.io/en/stable/) - PyInstaller bundles a Python application and all its dependencies into a single package. Used to bundle the program into exe file.

### Installation
pdf_tools requires [PyPDF2](http://mstamy2.github.io/PyPDF2/) 1.26.0+ to run.
Install the dependencies and run the program.

```sh
$ cd pdf_tools
$ pip install PyPDF2
$ python merger.py
$ python cropper.py
```

For the release version (pdf_tools.zip, for Windows), put PDF files under "files" folder, double-click run.bat. After "final.pdf" generated, double-click clean.bat.

### Todos
- Accept more flexible inputs
