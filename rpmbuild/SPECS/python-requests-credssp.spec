%{?scl:%scl_package python-requests-credssp}
%{!?scl:%global pkg_name %{name}}

%global pypi_name requests-credssp

Name:           %{?scl_prefix}python-requests-credssp
Version:        0.1.0
Release:        1%{?dist}
Summary:        An authentication handler for using CredSSP with Python Requests

License:        ISC
URL:            https://github.com/jborean93/requests-credssp
Source0:        https://files.pythonhosted.org/packages/source/r/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-requests}
%{?scl:Requires: %{scl}-python-ntlm-auth}
%{?scl:Requires: %{scl}-python-pyopenssl}

%description
This package allows for HTTPS CredSSP authentication using
the requests library. CredSSP is a Microsoft authentication
that allows your credentials to be delegated to a server
giving you double hop authentication.

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
%{python_sitelib}/requests_credssp*

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
