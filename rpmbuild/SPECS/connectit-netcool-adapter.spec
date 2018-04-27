%{?scl:%scl_package connectit-netcool-adapter}
%{!?scl:%global pkg_name %{name}}

%global pypi_name connectit-netcool-adapter
%{!?rel:%global rel 1}

Name:           %{?scl_prefix}%{pypi_name}
Version:        0.8
Release:        %{rel}%{?dist}
Summary:        Provide an backsync interface for Netcool
Source0:        %{pypi_name}-%{version}.tar.gz

License:        MIT

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-zeep}
%{?scl:Requires: %{scl}-python-docopt}
%{?scl:Requires: %{scl}-python-gevent}
%{?scl:Requires: %{scl}-python-arago-common-base}
%{?scl:Requires: %{scl}-python-arago-pyconnectit-common-rest}
%{?scl:Requires: %{scl}-python-arago-pyconnectit-connectors-common-base}
%{?scl:Requires: %{scl}-python-arago-pyconnectit-connectors-netcool}
%{?scl:Requires: %{scl}-python-arago-pyconnectit-connectors-snow}

%description
Receive updates in SDF format from ConnectIT
and forward them to NetCool via its SOAP API

%prep
cp -ax /home/vagrant/compile/ActionHandlers/python-actionhandler /tmp/%{pypi_name}-%{version}
cd /tmp
tar -czf /home/vagrant/rpmbuild/SOURCES/%{pypi_name}-%{version}.tar.gz %{pypi_name}-%{version}
rm -rf %{pypi_name}-%{version}
cd -
%setup -q -n %{pypi_name}-%{version}

%build
%{?scl:scl enable %{scl} "}
%{__python} setup-netcool-adapter.py build
%{?scl:"}

%install
# Explicitly specify --install-purelib %{python_sitelib}, which is now overriden
# to point to vt191, otherwise Python will try to install into the python27
# Software Collection site-packages directory
%{?scl:scl enable %{scl} "}
%{__python} setup-netcool-adapter.py install -O1 --skip-build --root %{buildroot} --install-scripts %{python_scriptdir} --install-purelib %{python_sitelib} --install-data %{python_sharedir}
%{?scl:"}

%files
%attr(0755, arago, arago) %{python_scriptdir}/connectit-netcool-adapter.py
%{python_sitelib}/connectit_netcool_adapter-*
%{python_sharedir}/connectit-netcool-adapter/*
%attr(0755, root, root) /etc/init.d/connectit-netcool-adapter
%config(noreplace) /opt/autopilot/connectit/conf/connectit-netcool-adapter*.conf

%post
[[ ! -e /var/log/autopilot/connectit/netcool-adapter.log ]] && touch /var/log/autopilot/connectit/netcool-adapter.log
[[ -f /var/log/autopilot/connectit/netcool-adapter.log ]] && chown arago:arago /var/log/autopilot/connectit/netcool-adapter.log && chmod 644 /var/log/autopilot/connectit/netcool-adapter.log
chkconfig --add connectit-netcool-adapter

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
