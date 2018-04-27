%{?scl:%scl_package python-requests-ntlm}
%{!?scl:%global pkg_name %{name}}

%global pypi_name requests_ntlm

Name:           %{?scl_prefix}python-requests-ntlm
Version:        1.0.0
Release:        1%{?dist}
Summary:        This package allows for HTTP NTLM authentication using the requests library

License:        ISC
URL:            https://github.com/requests/requests-ntlm
Source0:        https://files.pythonhosted.org/packages/source/r/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-requests}
%{?scl:Requires: %{scl}-python-ntlm-auth}

%description
This package allows for HTTP NTLM authentication using the requests library

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
%{python_sitelib}/requests_ntlm*

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
