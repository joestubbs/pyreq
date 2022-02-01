# Image: jstubbs/pypkgs
# Run with: 
# (single file) docker run -it --rm -v $(pwd)/testfiles:/data -e path=/data/test1.py jstubbs/pypkgs
# (directory) docker run -it --rm -v $(pwd)/testfiles:/data -e path=/data jstubbs/pypkgs
#
# docker run -it --rm -v /home/jstubbs/Documents/jupyter/nheri_ipynbs_analysis/nheri_published_ipynbs:/data -v $(pwd)/.agpy:/etc/.agpy -e dry_run=true -e convert=true -e path=/data  jstubbs/pypkgs
# docker run -it --rm -v /$(pwd)/testfiles:/data -v $(pwd)/.agpy:/etc/.agpy -e dry_run=true -e convert=true -e path=/data  jstubbs/pypkgs

from taccsciapps/jupyteruser-ds:1.2.24

USER root
ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD pkgs.py /pkgs.py

ENTRYPOINT [ "python", "/pkgs.py" ]