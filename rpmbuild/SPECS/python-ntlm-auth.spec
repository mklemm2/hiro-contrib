%{?scl:%scl_package python-ntlm-auth}
%{!?scl:%global pkg_name %{name}}

%global pypi_name ntlm-auth

Name:           %{?scl_prefix}python-ntlm-auth
Version:        1.0.2
Release:        1%{?dist}
Summary:        Creates NTLM authentication structures

License:        LGPLv3
URL:            https://github.com/jborean93/ntlm-auth
Source0:        https://files.pythonhosted.org/packages/source/n/%{pypi_name}/%{pypi_name}-%{version}.zip

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-ordereddict}
%{?scl_prefix_python:Requires: %{scl_prefix_python}python-six} >= 1.10.0

%description
This package can create and parse NTLM authorisation tokens with all the
latest standards such as NTLMv2, Extended Protection (CBT), message integrity
and confidentiality (signing and sealing).

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
%{python_sitelib}/ntlm_auth*

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
