%{?scl:%scl_package python-jsonmerge}
%{!?scl:%global pkg_name %{name}}

%global pypi_name jsonmerge

Name:           %{?scl_prefix}python-jsonmerge
Version:        1.2.1
Release:        1%{?dist}
Summary:        Merge a series of JSON documents.

License:        MIT
URL:            https://github.com/avian2/jsonmerge
Source0:        https://files.pythonhosted.org/packages/source/z/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-jsonschema}

%description
This Python module allows you to merge a series of JSON documents into a single one.

This problem often occurs for example when different authors fill in different parts
of a common document and you need to construct a document that includes contributions
from all the authors.
It also helps when dealing with consecutive versions of a document where different
fields get updated over time.

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
