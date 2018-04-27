%{?scl:%scl_package python-jsonschema}
%{!?scl:%global pkg_name %{name}}

%global pypi_name jsonschema

Name:           %{?scl_prefix}python-jsonschema
Version:        2.4.0
Release:        1%{?dist}
Summary:        An implementation of JSON Schema validation for Python

License:        MIT
URL:            http://github.com/Julian/jsonschema
Source0:        https://files.pythonhosted.org/packages/source/j/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

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
%{__python} setup.py install -O1 --skip-build --root %{buildroot} --install-purelib %{python_sitelib} --install-scripts %{python_scriptdir}
%{?scl:"}

%files
%{python_sitelib}/%{pypi_name}*
%{python_scriptdir}/%{pypi_name}*

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
