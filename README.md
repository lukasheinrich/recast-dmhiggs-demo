# recast-dmhiggs-demo

.. some more info to come here ..

to setup up the worker that listens for job do this on a fresh VM (where heptools are installed)

    virtualenv --system-site-packages venv
    source venv/bin/activate
    git clone git@github.com:lukasheinrich/recast-dmhiggs-demo.git
    <necessary step to make the binaries... will be makefile/autotools based eventually>
    cd recast-dmhiggs-demo
    pip install -e . --process-dependency-links
    cd recast-dmhiggs-demo/implementation/
    celery worker -A recastdmhiggs.dmhiggs_backendtasks -l debug -Q dmhiggs_queue
