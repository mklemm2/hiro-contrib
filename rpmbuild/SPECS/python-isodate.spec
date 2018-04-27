%{?scl:%scl_package python-isodate}
%{!?scl:%global pkg_name %{name}}

%global pypi_name isodate

Name:           %{?scl_prefix}python-isodate
Version:        0.5.4
Release:        1%{?dist}
Summary:        An ISO 8601 date/time/duration parser and formatter

License:        BSD
URL:            http://cheeseshop.python.org/pypi/isodate
Source0:        https://files.pythonhosted.org/packages/source/i/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}

%description
This module implements ISO 8601 date, time and
duration parsing. The implementation follows ISO8601:2004 standard, and
implements only date/time representations mentioned in the standard.

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
%{python_sitelib}/%{pypi_name}*

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
