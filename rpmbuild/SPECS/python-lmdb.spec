%{?scl:%scl_package python-lmdb}
%{!?scl:%global pkg_name %{name}}

%global pypi_name lmdb

Name:           %{?scl_prefix}python-lmdb
Version:        0.92
Release:        1%{?dist}
Summary:        Universal Python binding for the LMDB 'Lightning' Database

License:        OpenLDAP BSD
URL:            https://github.com/dw/py-lmdb
Source0:        https://files.pythonhosted.org/packages/source/g/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      x86_64
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
BuildRequires:  gcc
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}

%description
This is a universal Python binding for the LMDB ‘Lightning’ Database.
Two variants are provided and automatically selected during install:
a CFFI variant that supports PyPy and all versions of CPython >=2.6,
and a C extension that supports CPython 2.5-2.7 and >=3.3.
Both variants provide the same interface.

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
