%{?scl:%scl_package python-falcon}
%{!?scl:%global pkg_name %{name}}

%global pypi_name falcon

Name:           %{?scl_prefix}python-falcon
Version:        1.2.0
Release:        1%{?dist}
Summary:        An unladen web framework for building APIs and app backends

License:        Apache 2.0
URL:            http://falconframework.org
Source0:        https://files.pythonhosted.org/packages/source/f/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      x86_64
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-mimeparse}
%{?scl_prefix_python:Requires: %{scl_prefix_python}python-six} >= 1.10.0

%description
Falcon is a very fast, very minimal Python web framework for building
microservices, app backends, and higher-level frameworks.

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
%{python_scriptdir}/%{pypi_name}*

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
