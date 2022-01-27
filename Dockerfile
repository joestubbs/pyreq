# Image: jstubbs/pypkgs
# Run with: 
# (single file) docker run -it --rm -v $(pwd)/testfiles:/data -e path=/data/test1.py jstubbs/pypkgs
# (directory) docker run -it --rm -v $(pwd)/testfiles:/data -e path=/data jstubbs/pypkgs


from tapis/jupyter

ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD pkgs.py /pkgs.py

ENTRYPOINT [ "python", "/pkgs.py" ]