%{?scl:%scl_package python-pytz}
%{!?scl:%global pkg_name %{name}}

%global pypi_name pytz

Name:           %{?scl_prefix}python-pytz
Version:        2016.10
Release:        1%{?dist}
Summary:        World timezone definitions, modern and historical

License:        MIT
URL:            http://pythonhosted.org/pytz
Source0:        https://files.pythonhosted.org/packages/source/p/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}

%description
pytz brings the Olson tz database into
Python. This library allows accurate and cross platform timezone calculations
using Python 2.4 or higher. It also solves the issue of ambiguous times at the
end of daylight saving time, which you can read more about in the Python
Library Reference.

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
