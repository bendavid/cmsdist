### RPM cms asyncstageout 0.1.1pre6
## INITENV +PATH PATH %i/xbin
## INITENV +PATH PYTHONPATH %i/$PYTHON_LIB_SITE_PACKAGES
## INITENV +PATH PYTHONPATH %i/x$PYTHON_LIB_SITE_PACKAGES

%define wmcver 0.9.0

Source0: svn://svn.cern.ch/reps/CMSDMWM/WMCore/tags/%{wmcver}?scheme=svn+ssh&strategy=export&module=WMCore&output=/src_wmc_asyncstageout.tar.gz
Source1: svn://svn.cern.ch/reps/CMSDMWM/AsyncStageout/tags/%{realversion}?scheme=svn+ssh&strategy=export&module=AsyncStageout&output=/src_asyncstageout.tar.gz
Requires: python py2-simplejson py2-sqlalchemy py2-httplib2 py2-zmq rotatelogs pystack py2-sphinx dbs-client couchdb py2-pycurl

Patch0: asyncstageout-setup


%prep
%setup -D -T -b 1 -n AsyncStageout
%setup -T -b 0 -n WMCore
%patch0 -p0

%build
cd ../WMCore
python setup.py build_system -s asyncstageout
cd ../AsyncStageout 
python setup.py build

PYTHONPATH=$PWD/src/python:$PYTHONPATH
cd doc
cat asyncstageout/conf.py | sed "s,development,%{realversion},g" > asyncstageout/conf.py.tmp
mv asyncstageout/conf.py.tmp asyncstageout/conf.py
mkdir -p build
make html

%install
mkdir -p %i/{x,}{bin,lib,data,doc} %i/{x,}$PYTHON_LIB_SITE_PACKAGES
cd ../WMCore
python setup.py install_system -s asyncstageout --prefix=%i
cd ../AsyncStageout
python setup.py install --prefix=%i
cp -pr ../AsyncStageout/src/python/AsyncStageOut %i/$PYTHON_LIB_SITE_PACKAGES/
cp -pr ../AsyncStageout/src/couchapp %i/
cp -pr ../AsyncStageout/bin %i/
cp -pr ../AsyncStageout/configuration %i/
find %i -name '*.egg-info' -exec rm {} \;

# Generate .pyc files.
python -m compileall %i/$PYTHON_LIB_SITE_PACKAGES/AsyncStageOut || true

#mkdir -p %i/bin
cp -pf %_builddir/WMCore/bin/{wmcoreD,wmcore-new-config,wmagent-mod-config,wmagent-couchapp-init} %i/bin/

mkdir -p %i/doc
tar --exclude '.buildinfo' -C doc/build/html -cf - . | tar -C %i/doc -xvf -

# Generate dependencies-setup.{sh,csh} so init.{sh,csh} picks full environment.
mkdir -p %i/etc/profile.d
: > %i/etc/profile.d/dependencies-setup.sh
: > %i/etc/profile.d/dependencies-setup.csh
for tool in $(echo %{requiredtools} | sed -e's|\s+| |;s|^\s+||'); do
  root=$(echo $tool | tr a-z- A-Z_)_ROOT; eval r=\$$root
  if [ X"$r" != X ] && [ -r "$r/etc/profile.d/init.sh" ]; then
    echo "test X\$$root != X || . $r/etc/profile.d/init.sh" >> %i/etc/profile.d/dependencies-setup.sh
    echo "test X\$$root != X || source $r/etc/profile.d/init.csh" >> %i/etc/profile.d/dependencies-setup.csh
  fi
done

%post
%{relocateConfig}etc/profile.d/dependencies-setup.*sh
