%{?scl:%scl_package python-xmltodict}
%{!?scl:%global pkg_name %{name}}

%global pypi_name xmltodict

Name:           %{?scl_prefix}python-xmltodict
Version:        0.10.2
Release:        1%{?dist}
Summary:        Makes working with XML feel like you are working with JSON

License:        MIT
URL:            https://github.com/martinblech/xmltodict
Source0:        https://files.pythonhosted.org/packages/source/x/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}

%description
xmltodict is a Python module that makes working with XML feel
like you are working with JSON.

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
%{python_sitelib}/__pycache__/

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
