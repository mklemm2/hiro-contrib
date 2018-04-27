%{?scl:%scl_package python-paramiko}
%{!?scl:%global pkg_name %{name}}

%global pypi_name paramiko

Name:           %{?scl_prefix}python-paramiko
Version:        2.1.2
Release:        1%{?dist}
Summary:        SSH2 protocol library

License:        OpenLDAP BSD
URL:            https://github.com/nischu7/paramiko/
Source0:        https://files.pythonhosted.org/packages/source/g/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      x86_64
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
BuildRequires:  gcc
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
Requires: %{scl}-python-cryptography

%description
This is a library for making SSH2 connections (client or server). Emphasis is on using SSH2 as an alternative to SSL for making secure connections between python scripts. All major ciphers and hash methods are supported. SFTP client and server mode are both supported too.

%prep
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
%{__python} setup.py install -O1 --skip-build --root %{buildroot} --install-purelib %{python_sitelib} --install-platlib %{python_sitelib} --install-headers %{python_includedir}
%{?scl:"}

%files
%{python_sitelib}/%{pypi_name}*

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
