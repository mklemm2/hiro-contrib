%{?scl:%scl_package python-mimeparse}
%{!?scl:%global pkg_name %{name}}

%global pypi_name python-mimeparse

Name:           %{?scl_prefix}python-mimeparse
Version:        1.6.0
Release:        1%{?dist}
Summary:        A module provides basic functions for parsing mime-type names and matching them against a list of media-ranges

License:        MIT
URL:            https://github.com/dbtsai/python-mimeparse
Source0:        https://files.pythonhosted.org/packages/source/p/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}

%description
Pythonic argument parser, that will make you smile

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
%{__python} setup.py install -O1 --skip-build --root %{buildroot} --install-purelib %{python_sitelib}
%{?scl:"}

%files
%{python_sitelib}/mimeparse*
%{python_sitelib}/python_mimeparse*
%{python_sitelib}/__pycache__/

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
