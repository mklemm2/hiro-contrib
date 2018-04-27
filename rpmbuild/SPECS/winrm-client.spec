%{?scl:%scl_package winrm-client}
%{!?scl:%global pkg_name %{name}}

%global pypi_name winrm-client

Name:           %{?scl_prefix}winrm-client
Version:        0.1
Release:        1%{?dist}
Summary:        blah
Source0:        winrm-client-0.1.tar.gz

License:        MIT

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-pywinrm}
%{?scl:Requires: %{scl}-python-docopt}
%{?scl:Requires: %{scl}-python-schema}

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
%{__python} setup.py install -O1 --skip-build --root %{buildroot} --install-scripts %{python_scriptdir} --install-purelib %{python_sitelib}
%{?scl:"}

%files
%{python_scriptdir}/winrm-client.py
%{python_sitelib}/winrm_client*

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
