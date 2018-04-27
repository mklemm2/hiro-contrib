%{?scl:%scl_package python-requests}
%{!?scl:%global pkg_name %{name}}

%global pypi_name requests

Name:           %{?scl_prefix}python-requests
Version:        2.13.0
Release:        1%{?dist}
Summary:        Python HTTP for Humans

License:        Apache 2.0
URL:            http://python-requests.org
Source0:        https://files.pythonhosted.org/packages/source/r/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}

%description
Requests: HTTP for Humans Requests is the only *NonGMO* HTTP library for
Python, safe for human consumption.**Warning:** Recreational use of other HTTP
libraries may result in dangerous sideeffects, including: security
vulnerabilities, verbose code, reinventing the wheel, constantly reading
documentation, depression, headaches, or even death.Behold, the power of
Requests!

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
