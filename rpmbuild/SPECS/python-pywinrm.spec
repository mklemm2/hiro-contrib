%{?scl:%scl_package python-pywinrm}
%{!?scl:%global pkg_name %{name}}

%global pypi_name pywinrm

Name:           %{?scl_prefix}python-pywinrm
Version:        0.3.0
Release:        1%{?dist}
Summary:        Python library for Windows Remote Management

License:        MIT license
URL:            http://github.com/diyan/pywinrm/
Source0:        https://files.pythonhosted.org/packages/source/p/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-requests}
%{?scl:Requires: %{scl}-python-requests-ntlm}
%{?scl:Requires: %{scl}-python-xmltodict}
%{?scl_prefix_python:Requires: %{scl_prefix_python}python-six} >= 1.10.0
%{?scl:Requires: %{scl}-python-requests-kerberos}
%{?scl:Requires: %{scl}-python-requests-credssp}

%description
pywinrm is a Python client for the Windows Remote Management (WinRM)
service. It allows you to invoke commands on target Windows machines
from any machine that can run Python.

%prep
cp -ax /home/vagrant/compile/pywinrm /tmp/%{pypi_name}-%{version}
cd /tmp
tar -czf /home/vagrant/rpmbuild/SOURCES/%{pypi_name}-%{version}.tar.gz %{pypi_name}-%{version}
rm -rf %{pypi_name}-%{version}
cd -
%setup -q -n %{pypi_name}-%{version}
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
%{__python} setup.py install -O1 --skip-build --root %{buildroot} --install-purelib %{python_sitelib} --install-scripts %{python_scriptdir}
%{?scl:"}

%files
%{python_sitelib}/%{pypi_name}*
%{python_sitelib}/winrm*

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
