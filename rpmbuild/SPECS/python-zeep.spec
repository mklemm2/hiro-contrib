%{?scl:%scl_package python-zeep}
%{!?scl:%global pkg_name %{name}}

%global pypi_name python-zeep

Name:           %{?scl_prefix}python-zeep
Version:        1.6.0
Release:        1%{?dist}
Summary:        A modern/fast Python SOAP client based on lxml / requests

License:        MIT
URL:            http://docs.python-zeep.org
Source0:        https://files.pythonhosted.org/packages/source/z/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-appdirs}
%{?scl:Requires: %{scl}-python-cached-property}
%{?scl:Requires: %{scl}-python-defusedxml}
%{?scl:Requires: %{scl}-python-isodate}
%{?scl:Requires: %{scl}-python-lxml}
%{?scl:Requires: %{scl}-python-pytz}
%{?scl:Requires: %{scl}-python-requests}
%{?scl:Requires: %{scl}-python-requests-toolbelt}
%{?scl_prefix_python:Requires: %{scl_prefix_python}python-six} >= 1.10.0

%description
A fast and modern Python SOAP client

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

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
