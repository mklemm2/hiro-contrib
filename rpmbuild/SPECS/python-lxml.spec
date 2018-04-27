%{?scl:%scl_package python-lxml}
%{!?scl:%global pkg_name %{name}}

%global pypi_name lxml

Name:           %{?scl_prefix}python-lxml
Version:        3.7.2
Release:        1%{?dist}
Summary:        Powerful and Pythonic XML processing library combining libxml2/libxslt with the ElementTree API

License:        BSD
URL:            http://lxml.de/
Source0:        https://files.pythonhosted.org/packages/source/l/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      x86_64
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
BuildRequires:  gcc
BuildRequires:  libxml2-devel
BuildRequires:  libxslt-devel
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
Requires:  libxml2
Requires:  libxslt

%description
lxml is a Pythonic, mature binding for the libxml2 and libxslt libraries. It
provides safe and convenient access to these libraries using the ElementTree It
extends the ElementTree API significantly to offer support for XPath, RelaxNG,
XML Schema, XSLT, C14N and much more.

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
