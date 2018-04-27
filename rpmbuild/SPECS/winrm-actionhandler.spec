%{?scl:%scl_package winrm-actionhandler}
%{!?scl:%global pkg_name %{name}}

%global pypi_name winrm-actionhandler
%{!?rel:%global rel 1}

Name:           %{?scl_prefix}%{pypi_name}
Version:        2.5.0
Release:        %{rel}%{?dist}
Summary:        ActionHandler for Microsoft Windows
Source0:        %{pypi_name}-%{version}.tar.gz

License:        MIT

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-arago-pyactionhandler}
%{?scl:Requires: %{scl}-python-pywinrm}
%{?scl:Requires: %{scl}-python-requests-kerberos}
%{?scl:Obsoletes: %{scl}-python-arago-pyactionhandler-winrm}
%{?scl:Conflicts: %{scl}-python-arago-pyactionhandler-winrm}


%description
Execute cmd.exe and powershell commands on remote
Windows hosts via the WinRM protocol.

%prep
cp -ax /home/vagrant/compile/hiro-integration/hiro-winrm-actionhandler /tmp/%{pypi_name}-%{version}
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
%attr(0755, arago, arago) %{python_scriptdir}/hiro-winrm-actionhandler.py
%attr(0755, root, root) /etc/init.d/hiro-winrm-actionhandler
%config(noreplace) /opt/autopilot/conf/external_actionhandlers/winrm-actionhandler*.conf
%config(noreplace) /opt/autopilot/conf/external_actionhandlers/capabilities/winrm-actionhandler.*
%{python_sitelib}/winrm_actionhandler-*
%{python_sitelib}/arago/pyactionhandler/plugins/winrm/*

%post
[[ ! -e /var/log/autopilot/engine/winrm-handler.log ]] && touch /var/log/autopilot/engine/winrm-handler.log
[[ -f /var/log/autopilot/engine/winrm-handler.log ]] && chown arago:arago /var/log/autopilot/engine/winrm-handler.log && chmod 644 /var/log/autopilot/engine/winrm-handler.log
chkconfig --add hiro-winrm-actionhandler

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
