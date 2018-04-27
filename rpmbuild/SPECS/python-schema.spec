%{?scl:%scl_package python-schema}
%{!?scl:%global pkg_name %{name}}

%global pypi_name schema

Name:           %{?scl_prefix}python-schema
Version:        0.6.5
Release:        1%{?dist}
Summary:        Simple data validation library

License:        MIT
URL:            https://github.com/keleshev/schema
Source0:        https://files.pythonhosted.org/packages/source/s/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}

%description
Schema validation just got Pythonic **schema** is a library for validating
Python data structures, such as those obtained from configfiles, forms,
external services or commandline parsing, converted from JSON/YAML (or
something else) to Python datatypes.

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
%{__python} setup.py install -O1 --skip-build --root %{buildroot} --install-purelib %{python_sitelib} --install-scripts %{python_scriptdir}
%{?scl:"}

%files
%{python_sitelib}/%{pypi_name}*
%{python_sitelib}/__pycache__

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
