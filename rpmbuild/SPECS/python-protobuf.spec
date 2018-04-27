%{?scl:%scl_package python-protobuf}
%{!?scl:%global pkg_name %{name}}

%global pypi_name protobuf

Name:           %{?scl_prefix}python-protobuf
Version:        3.2.0
Release:        1%{?dist}
Summary:        Protocol Buffers

License:        MIT License
URL:            https://developers.google.com/protocol-buffers/
Source0:        https://files.pythonhosted.org/packages/source/p/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      x86_64
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
BuildRequires:  gcc
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl_prefix_python:Requires: %{scl_prefix_python}python-six} >= 1.10.0

%description
The greenlet package is a spinoff of Stackless, a version of CPython that
supports microthreads called "tasklets". Tasklets run pseudoconcurrently
(typically in a single or a few OSlevel threads) and are synchronized with data
exchanges on "channels".A "greenlet", on the other hand, is a still more
primitive notion of microthread with no implicit scheduling; coroutines, in
other words.

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
%{python_sitelib}/google/protobuf/*
%{python_sitelib}/protobuf-*
#%{python_sitelib}/%{pypi_name}*
#%{python_includedir}/%{pypi_name}*

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
