### RPM external couchdb 0.8.1
Source: http://mirrors.directorymix.com/apache/incubator/%n/%realversion-incubating/apache-%n-%realversion-incubating.tar.gz
Requires: gcc curl spidermonkey openssl icu4c erlang

%prep
%setup -n %n-%{realversion}

%build
./configure
make

%install
make install
# SCRAM ToolBox toolfile
mkdir -p %i/etc/scram.d
cat << \EOF_TOOLFILE >%i/etc/scram.d/%n
<doc type=BuildSystem::ToolDoc version=1.0>
<Tool name=Couchdb version=%v>
<lib name=coucndb>
<client>
 <Environment name=COUCHDB_BASE default="%i"></Environment>
 <Environment name=INCLUDE default="$COUCHDB_BASE/include"></Environment>
 <Environment name=LIBDIR  default="$COUCHDB_BASE/lib"></Environment>
</client>
<Runtime name=PATH value="$COUCHDB_BASE/bin" type=path>
</Tool>
EOF_TOOLFILE

%post
%{relocateConfig}etc/scram.d/%n

