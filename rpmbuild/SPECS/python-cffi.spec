%{?scl:%scl_package python-cffi}
%{!?scl:%global pkg_name %{name}}

%global pypi_name cffi

Name:           %{?scl_prefix}python-cffi
Version:        1.11.2
Release:        1%{?dist}
Summary:        Foreign Function Interface for Python calling C code.

License:        MIT
URL:            http://cffi.readthedocs.org
Source0:        https://files.pythonhosted.org/packages/source/c/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      x86_64
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
BuildRequires:  gcc
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-pycparser}

%description
Foreign Function Interface for Python calling C code. 

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
%{python_sitelib}/_cffi_backend.cpython-*.so

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
