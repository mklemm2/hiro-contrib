%{?scl:%scl_package python-pyopenssl}
%{!?scl:%global pkg_name %{name}}

%global pypi_name pyOpenSSL

Name:           %{?scl_prefix}python-pyopenssl
Version:        16.0.0
Release:        1%{?dist}
Summary:        Python wrapper module around the OpenSSL library

License:        Apache 2.0
URL:            https://pyopenssl.org/
Source0:        https://files.pythonhosted.org/packages/source/f/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-cryptography}
%{?scl_prefix_python:Requires: %{scl_prefix_python}python-six} >= 1.10.0

%description
High-level wrapper around a subset of the OpenSSL library. Includes

- SSL.Connection objects, wrapping the methods of Python’s portable sockets
- Callbacks written in Python
- Extensive error-handling mechanism, mirroring OpenSSL’s error codes

... and much more.

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
%{__python} setup.py install -O1 --skip-build --root %{buildroot} --install-purelib %{python_sitelib} --install-platlib %{python_sitelib} --install-scripts %{python_scriptdir}
%{?scl:"}

%files
%{python_sitelib}/%{pypi_name}*
%{python_sitelib}/OpenSSL*

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
