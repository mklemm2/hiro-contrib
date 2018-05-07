%{?scl:%scl_package stonebranch-actionhandler}
%{!?scl:%global pkg_name %{name}}

%global pypi_name stonebranch-actionhandler
%{!?rel:%global rel 1}

Name:           %{?scl_prefix}%{pypi_name}
Version:        1.0.0
Release:        %{rel}%{?dist}
Summary:        ActionHandler for Stonebranch Universal Controller
Source0:        %{pypi_name}-%{version}.tar.gz

License:        MIT
URL:            https://github.com/arago/python-hiro-stonebranch-actionhandler

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-arago-pyactionhandler}
%{?scl:Requires: %{scl}-python-requests}


%description
Execute commands through Stonebranch Universal Controller

%define NVdir %{pypi_name}-%{version}

%prep
rm -rf %{NVdir}
git clone %{url}.git %{NVdir}
tar -czvf /home/vagrant/rpmbuild/SOURCES/%{pypi_name}-%{version}.tar.gz %{NVdir} --exclude "%{NVdir}/.git"
cd %{NVdir}
git checkout noTypeHints
scl enable rh-python36 /tmp/sh


%build
cd %{NVdir}
%{?scl:scl enable %{scl} "}
%{__python} setup.py build
%{?scl:"}

%install
# Explicitly specify --install-purelib %{python_sitelib}, which is now overriden
# to point to vt191, otherwise Python will try to install into the python27
# Software Collection site-packages directory
cd %{NVdir}
pwd
%{?scl:scl enable %{scl} "}
%{__python} setup.py install -O1 --skip-build --root %{buildroot} --install-scripts %{python_scriptdir} --install-purelib %{python_sitelib} --install-data %{python_sharedir}
%{?scl:"}

%files
#%attr(0755, arago, arago) %{python_scriptdir}/hiro-winrm-actionhandler.py
#%attr(0755, root, root) /etc/init.d/hiro-winrm-actionhandler
#%config(noreplace) /opt/autopilot/conf/external_actionhandlers/winrm-actionhandler*.conf
#%config(noreplace) /opt/autopilot/conf/external_actionhandlers/capabilities/winrm-actionhandler.*
%{python_sitelib}/arago_hiro_actionhandler_stonebranch-*
%{python_sitelib}/arago/hiro/actionhandler/plugin/stonebranch/*

%post

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
