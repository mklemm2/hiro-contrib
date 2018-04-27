%{?scl:%scl_package python-arago-pyactionhandler}
%{!?scl:%global pkg_name %{name}}

%global pypi_name arago-pyactionhandler
%{!?rel:%global rel 1}

Name:           %{?scl_prefix}python-%{pypi_name}
Version:        2.5.0
Release:        %{rel}%{?dist}
Summary:        Python module for Arago HIRO ActionHandlers
Source0:        %{pypi_name}-%{version}.tar.gz

License:        MIT

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-zmq}
%{?scl:Requires: %{scl}-python-docopt}
%{?scl:Requires: %{scl}-python-gevent}
%{?scl:Requires: %{scl}-python-protobuf}
%{?scl:Requires: %{scl}-python-arago-common-base}


%description
pyactionhandler is a python module to develop external
ActionHandlers for the arago HIRO automation engine.

An ActionHandler is used to access target systems in
order to execute commands. This is not limited to
shell commands but can be anything that provides some
kind of command line or API, e.g. SQL.

%prep
cp -ax /home/vagrant/compile/hiro-integration/python-arago-pyactionhandler/ /tmp/%{pypi_name}-%{version}
cd /tmp
tar -czf /home/vagrant/rpmbuild/SOURCES/%{pypi_name}-%{version}.tar.gz %{pypi_name}-%{version}
rm -rf %{pypi_name}-%{version}
cd -
%setup -q -n %{pypi_name}-%{version}

%build
%{?scl:scl enable %{scl} "}
%{__python} setup.py build
%{?scl:"}

%install
# Explicitly specify --install-purelib %{python_sitelib}, which is now overriden
# to point to vt191, otherwise Python will try to install into the python27
# Software Collection site-packages directory
%{?scl:scl enable %{scl} "}
%{__python} setup.py install -O1 --skip-build --root %{buildroot} --install-scripts %{python_scriptdir} --install-purelib %{python_sitelib} --install-data %{python_sharedir}
%{?scl:"}

%files
%attr(0755, arago, arago) %{python_scriptdir}/hiro-counting-rhyme-actionhandler.py
%attr(0755, arago, arago) %{python_scriptdir}/ah-client.py
%attr(0755, arago, arago) %{python_scriptdir}/create-zmq-keypair.sh
%{python_sitelib}/arago/pyactionhandler/*
%{python_sitelib}/arago_pyactionhandler-*
%attr(0755, root, root) /etc/init.d/hiro-counting-rhyme-actionhandler
%config(noreplace) /opt/autopilot/conf/external_actionhandlers/counting-rhyme-actionhandler*.conf
%config(noreplace) /opt/autopilot/conf/external_actionhandlers/capabilities/counting-rhyme-actionhandler.*

%post
[[ ! -e /var/log/autopilot/engine/countingrhyme-handler.log ]] && touch /var/log/autopilot/engine/countingrhyme-handler.log
[[ -f /var/log/autopilot/engine/countingrhyme-handler.log ]] && chown arago:arago /var/log/autopilot/engine/countingrhyme-handler.log && chmod 644 /var/log/autopilot/engine/countingrhyme-handler.log

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
